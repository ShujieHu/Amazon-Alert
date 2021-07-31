from smtplib import SMTP
import unittest
from mock import patch, Mock, MagicMock
from AmazonAlert import *


class TestSendEmail(unittest.TestCase):
    @patch('smtplib.SMTP')
    def testSendEmail(self, mock_smtp):
        title = 'testTitle'
        graph = 'alertEmail.png'
        email_credentials = ['usename', 'pass', 'fromAddr', 'toAddr']
        sendEmail(title, graph, email_credentials)
        mock_smtp.assert_called_with('smtp.gmail.com', 587)
