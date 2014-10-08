# -*- coding: utf-8 -*-
from __future__ import unicode_literals, with_statement
from mock import patch
from testcase import TrannyTestCase
import smtplib
from unittest import main
from tranny.notification import email


class MailTest(TrannyTestCase):
    tmp_dir = None

    def setUp(self):
        self.p_smtp = patch('smtplib.SMTP', autospec=True)
        self.p_smtp_ssl = patch('smtplib.SMTP_SSL', autospec=True)

    def tearDown(self):
        pass

    @patch("smtplib.SMTP", **{'sendmail.return_value': 'OK', 'starttls.return_value': True})
    def test_send_message(self, mock):
        mock.connect.return_value = (220, "ok!")
        res = email.send_message("test body", "test subject",
                                 'test@cudd.li', 'leigh.macdonald@gmail.com')
        self.assertEqual(res['Subject'], "test subject")


if __name__ == '__main__':
    main()

