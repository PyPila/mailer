from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from mock import patch

from mail.models import Email, EmailFields, Recipient


class EmailModelTestCase(TestCase):

    def setUp(self):
        self.template = SimpleUploadedFile(
            'test_template.html',
            (
                'Test Email: {{ test_context }} '
                'Recipient: {{ recipient.name }} '
            )
        )
        self.email = Email.objects.create(
            name='test',
            subject='test',
            from_email='test@pypila.com',
            template=self.template
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

    @patch.object(Email, 'make_template_fields')
    def test_view_create(self, mock_make_template_fields):
        Email.objects.view_create(
            {
                'name': 'test',
                'subject': 'test',
                'from_email': 'test@pypila.com',
                'template': self.template,
            },
            self.rf.post('/'),
        )
        mock_make_template_fields.assert_called_once()

    @patch.object(Email, 'make_template_fields')
    def test_change(self, mock_make_template_fields):
        self.email.change(
            {
                'name': 'changed',
                'subject': 'changed',
                'from_email': 'pypila@stxnext.com',
            },
            self.rf.post(
                '/', data={
                    'template': self.template,
                    'fields_test_context': 'yes',
                    'not_a_field': 'nope',
                }
            ),
        )
        mock_make_template_fields.assert_called_once()
        email = Email.objects.last()
        self.assertEqual(email.name, 'changed')
        self.assertEqual(email.fields.last().value, 'yes')

    @patch.object(Email, 'make_template_fields')
    def test_change_no_template(self, mock_make_template_fields):
        self.email.change(
            {
                'name': 'changed',
                'subject': 'changed',
                'from_email': 'pypila@stxnext.com',
            },
            self.rf.post('/'),
        )
        mock_make_template_fields.assert_not_called()
        self.assertEqual(Email.objects.last().name, 'changed')

    def test_make_email_fields(self):
        email = Email.objects.create(
            name='test',
            subject='test',
            from_email='test@pypila.com',
            template=self.template
        )
        email.make_template_fields()

        fields = email.fields.all()
        self.assertEqual(fields.count(), 1)
        self.assertEqual(fields[0].name, 'test_context')

    def test_render(self):
        mail_content = self.email.render(
            self.rf.get('/'),
            self.recipient,
        )[0]
        self.assertEqual(
            mail_content,
            (
                'Test Email: some content '
                'Recipient: Test Recipient '
            )
        )

    @patch('mail.models.Email.EmailThread')
    def test_send(self, mock_email_thread):
        request = self.rf.get('/')
        request.user = get_user_model().objects.create_superuser(
            'developer', 'developer@mailer.com', 'password'
        )
        self.email.send(request, [self.recipient, ])
        sent_message = mock_email_thread.call_args[0][0]
        self.assertEqual(sent_message.subject, 'test')
        self.assertEqual(sent_message.to, ['test@pypila.com'])
        self.assertIn('some content', sent_message.body)
