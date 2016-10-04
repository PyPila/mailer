from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

from mail.models import Email, EmailFields, Recipient


class EmailSendTestCase(TestCase):

    def setUp(self):
        self.email = Email.objects.create(
            name='test',
            subject='test',
            from_email='test@pypila.com',
            template=SimpleUploadedFile(
                'test_template.html',
                (
                    'Test Email: {{ test_context }} '
                    'Recipient: {{ recipient.name }} '
                    '{{ web_view_url }} '
                )
            )
        )
        self.email.make_template_fields()
        field = EmailFields.objects.last()
        field.value = 'some content'
        field.save()
        self.recipient = Recipient.objects.create(
            name='Test Recipient',
            email='test@pypila.com',
        )
        self.rf = RequestFactory()

    def test_make_email_fields(self):
        email = Email.objects.create(
            name='test',
            subject='test',
            from_email='test@pypila.com',
            template=SimpleUploadedFile(
                'test_template.html',
                'Test Email: {{ content }}',
            )
        )
        email.make_template_fields()

        fields = email.fields.all()
        self.assertEqual(fields.count(), 1)
        self.assertEqual(fields[0].name, 'content')

    def test_render(self):
        mail_content, token = self.email.render(
            self.rf.get('/'),
            self.recipient,
        )
        self.assertEqual(
            mail_content,
            (
                'Test Email: some content '
                'Recipient: Test Recipient '
                'http://testserver/web_view/'
                '{} '.format(token)
            )
        )
