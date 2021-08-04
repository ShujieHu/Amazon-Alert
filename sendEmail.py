from amazon.api import AmazonAPI
import smtplib
import os
import ssl
import time
import csv
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime as dt
import numpy as np
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class Config:
    def sendEmail(self, product, graph, receivers):
        '''
        This function allows to send graph to a list of receivers 
        '''
        # This is the test account set up for the project, don't change
        sender = 'cisc593@gmail.com'
        password = 'test'
        if password is None:
            password = input('Enter password')

        context = ssl.create_default_context()

        # Handle base
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ", ".join(receivers)
        msg['Subject'] = "Price Alert: " + product
        msgText = MIMEText(
            '<center><br><img src="cid:image"><br></center>', 'html')
        msg.attach(msgText)

        # Embed image
        image = open(graph, 'rb')
        msgImage = MIMEImage(image.read())
        msgImage.add_header('Content-ID', '<image>')
        msg.attach(msgImage)
        image.close()

        # Use google smtp server to send email for simplicity purposes
        server = 'smtp.gmail.com'
        port = 465
        with smtplib.SMTP_SSL(server, port, context=context) as server:
            server.login(sender, password)
            text = msg.as_string()
            server.sendmail(sender, receivers[0], text)
            server.quit()


if __name__ == 'main':
    # For integration test
    product = 'test1'
    graph = 'AlertEmail.png'
    receivers = ['monicabuy@gmail.com']
    receiver = 'monicabuy@gmail.com'
    config = Config()
    config.sendEmail(product, graph, receivers)
