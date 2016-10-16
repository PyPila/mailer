from django.test import TestCase

from mail.templatetags.mailer import none


class MailerTagTestCase(TestCase):

    def test_none_filter(self):
        self.assertEqual(none(None), '')
        self.assertEqual(none('kaka'), 'kaka')
