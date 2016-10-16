from django.test import TestCase, RequestFactory

from mail.context_processors import counts


class ContextProcessorsTestCase(TestCase):

    def test_counts(self):
        rf = RequestFactory()
        self.assertEqual(
            counts(rf.get('/')),
            {
                'emails_count': 0,
                'groups_count': 0,
                'recipients_count': 0,
            }
        )
