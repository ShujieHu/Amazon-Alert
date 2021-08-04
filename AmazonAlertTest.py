from mock import patch, Mock, MagicMock
import unittest
from smtplib import SMTP
from sendEmail import *
import smtplib
import os
os.environ['PASSWORD'] = 'testPass'


class TestSendEmail(unittest.TestCase):
    @patch('sendEmail.ssl.create_default_context')
    @patch('sendEmail.smtplib.SMTP_SSL')
    def testSendEmail(self, mock_smtp, mock_context):
        title = 'testTitle'
        graph = 'alertEmail.png'
        receivers = ['test1@gmail.com']
        # tmp = MagicMock()
        # mock_smtp.return_value.login = tmp
        config = Config()
        config.sendEmail(title, graph, receivers)
        login_return = MagicMock()
        mock_smtp.assert_called()
        mock_smtp.login = login_return

        mock_smtp.assert_called_with(
            'smtp.gmail.com', 465, context=mock_context.return_value)


# class TestAddProduct(unittest.TestCase):
#     def testDesiredPrice(self):
#         productID = 'B00DB9JV5W'
#         csvFile = 'priceHistory.csv'
#         alertWhen = 19.99
#         alertType = 'desiredPrice'
#         AWS_ACCESS_KEY_ID = 'AKIA6ELRG2GG2NUYXY77'
#         AWS_SECRET_ACCESS_KEY = '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'
#         AWS_ASSOCIATE_TAG = 'kzhu07-20'
#         AWS_CREDENTIALS = [AWS_ACCESS_KEY_ID,
#                            AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG]
#         addProduct(productID, csvFile, alertWhen, alertType, AWS_CREDENTIALS)
#         with open(csvFile, 'rb') as infile:
#             for line in infile:
#                 column = line.split('|')
#             productID_test = column[0]
#             alertWhen_test = column[1]
#         infile.close()
#         self.assertEqual(productID_test, productID)
#         self.assertEqual(alertWhen_test, alertWhen)

#     def testOtherAlertType(self):
#         productID = 'B01GW3H3U8'
#         csvFile = 'priceHistory.csv'
#         alertWhen = -50
#         alertType = 'OtherType'
#         AWS_ACCESS_KEY_ID = 'AKIA6ELRG2GG2NUYXY77'
#         AWS_SECRET_ACCESS_KEY = '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'
#         AWS_ASSOCIATE_TAG = 'kzhu07-20'
#         AWS_CREDENTIALS = [AWS_ACCESS_KEY_ID,
#                            AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG]
#         self.assertRaises(ValueError, addProduct, productID,
#                           csvFile, alertWhen, alertType, AWS_CREDENTIALS)
