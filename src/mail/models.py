from __future__ import unicode_literals
import base64
import hashlib
import time
import threading

from django.db import models
from django.template import Context, Template
from django.core.mail import EmailMessage
from django.urls import reverse
from django.conf import settings
from django.template.base import VariableNode


RESTRICTED_EMAIL_FIELDS = ('web_view_url', )


class RecipientGroup(models.Model):
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class Recipient(models.Model):
    name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(RecipientGroup, related_name='recipients')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Email(models.Model):
    name = models.CharField(max_length=64)
    subject = models.CharField(max_length=256)
    from_email = models.EmailField()
    template = models.FileField(upload_to='email_templates/')

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def template_content(self):
        if not hasattr(self, '_template_content'):
            try:
                self._template_content = self.template.read()
            except IOError:
                self._template_content = ''
        return self._template_content

    @property
    def email_data(self):
        if not hasattr(self, '_email_data'):
            self._email_data = dict(self.fields.values_list('name', 'value'))
        return self._email_data

    def get_template(self):
        return Template(self.template_content)

    def __is_field_node(self, node):
        if all([
            isinstance(node, VariableNode),
            '.' not in node.token.contents,
            node.token.contents not in RESTRICTED_EMAIL_FIELDS,
        ]):
            return True
        return False

    def make_template_fields(self):
        template = self.get_template()
        self.fields.all().delete()
        for node in template.nodelist:
            if self.__is_field_node(node):
                self.fields.create(name=node.token.contents)

    def render(self, request, recipient):
        url_token = hashlib.sha256(
            '{}{}{}'.format(recipient.pk, self.pk, time.time())
        ).hexdigest()
        context_data = self.email_data
        context_data.update({
            'recipient': recipient,
            'url_token': url_token,
            'request': request,
            'web_view_url': request.build_absolute_uri(
                reverse('web_view', kwargs={'url_token': url_token})
            ),
        })
        ctx = Context(context_data)
        template = self.get_template()
        return template.render(ctx), url_token

    class EmailThread(threading.Thread):
        def __init__(self, msg):
            self.msg = msg
            threading.Thread.__init__(self)

        def run(self):
            self.msg.send(fail_silently=False)

    def send(self, request, recipients):

        for recipient in recipients:
            email_content, url_token = self.render(request, recipient)
            Log.objects.create(
                email=self,
                recipient=recipient,
                url_token=url_token,
                email_content=email_content,
                sent_by=request.user
            )
            msg = EmailMessage(
                subject=self.subject,
                body=email_content,
                from_email=self.from_email,
                to=[recipient.email]
            )
            msg.content_subtype = 'html'
            self.EmailThread(msg).start()


class EmailFields(models.Model):
    email = models.ForeignKey(Email, related_name='fields')
    name = models.CharField(max_length=64)
    value = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('email', 'name',)


class Log(models.Model):
    email = models.ForeignKey(Email, related_name='logs')
    recipient = models.ForeignKey(Recipient, related_name='logs')
    url_token = models.CharField(max_length=64, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    _email_content = models.TextField(db_column='email_content')

    def set_email_content(self, data):
        self._email_content = base64.encodestring(data.encode('utf-8'))

    def get_email_content(self):
        return base64.decodestring(self._email_content)

    email_content = property(get_email_content, set_email_content)
