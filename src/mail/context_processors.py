from mail.models import Recipient, RecipientGroup, Email


def counts(request):
    return {
        'emails_count': Email.objects.all().count(),
        'groups_count': RecipientGroup.objects.all().count(),
        'recipients_count': Recipient.objects.all().count(),
    }
