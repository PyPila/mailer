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


class EmailsView(ModelView):
    template_name = 'emails'
    namespace = 'emails'
    model = Email


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
