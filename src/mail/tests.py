from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from mail.models import Email, EmailFields


class EmailSendTestCase(TestCase):

    def setUp(self):
        self.email = Email.objects.create(
            name='test',
            template=SimpleUploadedFile(
                'test_template.html',
                'Test Email: {{ test_context }}'
            )
        )
        self.email.fields.add(
            EmailFields.objects.create(name='test_context', value='test_value')
        )

    def test_render(self):
        mail_content = self.email.render()
        self.assertEqual(mail_content, 'Test Email: test_value')
