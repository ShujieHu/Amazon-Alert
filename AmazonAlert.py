# ----- Plotting Configuration -------------------------------------------------

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
from sendEmail import sendEmail
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

AWS_ACCESS_KEY_ID = 'AKIAS6ERF7OV25AWKWX2'
AWS_SECRET_ACCESS_KEY = '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'
AWS_ASSOCIATE_TAG = 'monicah666-20'
AWS_CREDENTIALS = [AWS_ACCESS_KEY_ID,
                   AWS_SECRET_ACCESS_KEY, AWS_ASSOCIATE_TAG]

AMAZON_ACCESS_KEY = AWS_ACCESS_KEY_ID
AMAZON_SECRET_KEY = AWS_SECRET_ACCESS_KEY
AMAZON_ASSOC_TAG = AWS_ASSOCIATE_TAG


def plotDatePrice(productID, productTitle, data):

    # Data setup
    x, y = [], []
    for datapoint in data:
        date = datapoint.split('|')[0]
        price = float(datapoint.split('|')[1])
        x.append(dt.datetime.strptime(date, '%Y-%m-%d'))
        y.append(price)
    x = matplotlib.dates.date2num(x)
    x_np, y_np = np.array(x), np.array(y)

    # Plot setup
    ax = plt.figure(figsize=(6, 3)).add_subplot(111)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.plot(x_np, y_np, color='lightblue', lw=2)
    ax.margins(0.05)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: ('$%i' % (x))))
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    plt.yticks(fontsize=8)
    plt.ylim(ymin=min(y)*0.7, ymax=max(y)*1.3)
    plt.title('Recent Price History\n'+productTitle,
              weight='light', fontsize=12, y=1.08)
    plt.xticks(rotation=40, fontsize=7)
    plt.tight_layout()
    plt.savefig(productID+'.png')
    return productID+'.png'

# ----- Email Configuration ----------------------------------------------------


def sendEmail(product, graph, receivers):
    '''
    This function allows to send graph to a list of receivers 
    '''
    # This is the test account set up for the project, don't change
    sender = 'cisc593@gmail.com'
    password = os.getenv('PASSWORD')
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
        res = server.login(sender, password)
        print("########## res", res)
        text = msg.as_string()
        server.sendmail(sender, receivers[0], text)
        server.quit()

# ----- Amazon API -------------------------------------------------------------


def readPrices(csvFile):
    priceData = {}
    targetData = {}
    with open(csvFile, 'rb') as infile:
        for line in infile:
            row = line.strip('\n\r').split(',')
            column = row[0].split('|')
            priceData[column[0]] = row[1:]
            targetData[column[0]] = column[1]
    infile.close()
    return priceData, targetData


def updatePrices(newPriceData, oldPriceData):
    for pair in newPriceData:
        product = pair[0]
        price = pair[1]
        try:
            oldPriceData[product].append(price)
        except KeyError:
            print("Product %s was skipped." % (product))
            print("It has not been initalized with an alert price!")
    return oldPriceData


def writePrices(newPriceData, targetData, csvFile):
    with open(csvFile, 'wb') as outfile:
        writer = csv.writer(outfile)
        for product in newPriceData:
            target = targetData[product]
            writer.writerow([product+'|'+target]+newPriceData[product])
        outfile.close()


def getPrice(productID, AWS_CREDENTIALS):
    amazon = AmazonAPI(AWS_CREDENTIALS[0],
                       AWS_CREDENTIALS[1], AWS_CREDENTIALS[2])
    result = amazon.lookup(ItemId=productID)
    return result.title, result.price_and_currency[0]


def addProduct(productID, csvFile, alertWhen, alertType, AWS_CREDENTIALS):
    currentPrice = getPrice(productID, AWS_CREDENTIALS)[1]

    if alertType == "percentChange":
        delta = (float(alertWhen)/100)+1
        alertPrice = currentPrice*delta

    elif alertType == "desiredPrice":
        alertPrice = float(alertWhen)

    else:
        raise ValueError('Invalid alertType')

    with open(csvFile, 'a') as outfile:
        writer = csv.writer(outfile)
        writer.writerow([productID+'|'+str(alertPrice)])
        outfile.close()


def dailyScan(productIDs, csvFile, AWS_CREDENTIALS, receivers):
    prices, targets = readPrices(csvFile)
    alerts = []
    update = []
    for productID in productIDs:
        title, price = getPrice(productID, AWS_CREDENTIALS)
        date = time.strftime("%Y-%m-%d")
        update.append((productID, date+'|'+str(price)))

        try:
            if price <= float(targets[productID]):
                alerts.append(productID)
        except KeyError:
            pass

    updatedPrices = updatePrices(update, prices)
    writePrices(updatedPrices, targets, csvFile)

    for alert in alerts:
        graph = plotDatePrice(alert, title, updatedPrices[alert])
        sendEmail(title, graph, receivers)
