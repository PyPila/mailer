from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.http import HttpResponse

from mail.models import Recipient, RecipientGroup, Email, Log
from utils.views import ModelView


class BaseTemplateView(TemplateView):
    template_name = 'app.html'

    def get_context_data(self, **kwargs):
        ctx = super(BaseTemplateView, self).get_context_data(**kwargs)
        ctx.update({
            'emails': Email.objects.all(),
            'groups': RecipientGroup.objects.all(),
        })
        return ctx

    def post(self, request):
        if 'group' in request.POST:
            recipients = RecipientGroup.objects.get(
                pk=request.POST['group']
            ).recipients.all()
        else:
            recipients = Recipient.objects.filter(
                pk__in=request.POST.getlist('recipients')
            )
        return render(
            request, 'confirm_send.html', {
                'recipients': recipients,
                'email': request.POST['email'],
            }
        )


class WebView(View):

    def get(self, request, url_token):
        log = Log.objects.get(url_token=url_token)
        return HttpResponse(log.email_content)


class EmailsView(TemplateView):
    template_name = 'emails.html'

    def get_context_data(self, **kwargs):
        ctx = super(EmailsView, self).get_context_data(**kwargs)
        ctx.update({
            'emails': Email.objects.all(),
        })
        return ctx

    def add_email(self):
        email = Email.objects.create(
            name=self.request.POST['name'],
            subject=self.request.POST['subject'],
            from_email=self.request.POST['from_email'],
            template=self.request.FILES['template'],
        )
        email.make_template_fields()

    def edit_email(self):
        email = Email.objects.get(pk=self.request.POST['pk'])

        email.name = self.request.POST['name']
        email.subject = self.request.POST['subject']
        email.from_email = self.request.POST['from_email']

        if self.request.FILES.get('template'):
            email.template = self.request.FILES['template']
            email.make_template_fields()

        email.save()

        for key, value in self.request.POST.iteritems():
            if key.startswith('fields_'):
                email.fields.filter(name=key[7:]).update(value=value)

        return email

    def post(self, request, *args, **kwargs):
        if 'pk' in request.POST:
            email = self.edit_email()
            if 'test_send' in request.POST:
                recipient, __ = Recipient.objects.get_or_create(
                    name=request.user.get_full_name(),
                    email=request.user.email,
                )
                email.send(request, [recipient])
        elif 'delete' in request.POST:
            self.delete_email()
        else:
            self.add_email()
        return self.get(request, *args, **kwargs)


class RecipientsView(ModelView):
    template_name = 'recipients'
    namespace = 'recipients'
    model = Recipient

    def get_obj_context(self, extra_context=None):
        ctx = super(RecipientsView, self).get_obj_context(extra_context)
        ctx.update({'groups': RecipientGroup.objects.all()})
        return ctx


def email_preview(request, email_pk):
    recipient, __ = Recipient.objects.get_or_create(
        name=request.user.get_full_name(),
        email=request.user.email,
    )
    email = Email.objects.get(pk=email_pk)
    return HttpResponse(email.render(request, recipient)[0])


def send_emails(request):
    email = Email.objects.get(pk=request.POST['email'])
    recipients = Recipient.objects.filter(
        pk__in=request.POST.getlist('recipients')
    )
    email.send(request, recipients)
    return redirect('/')
