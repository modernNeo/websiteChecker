from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from selenium import webdriver
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import smtplib
import logging
import datetime
import pytz
import argparse


import http.client
import socket
from selenium.webdriver.remote.command import Command
def get_status(driver):
    try:
        driver.execute(Command.STATUS)
        return "Alive"
    except (socket.error, http.client.CannotSendRequest):
        return "Dead"

def initalizeLogger():
    # setting up log requirements
    logger = logging.getLogger('websiteChecker')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s = %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return formatter, logger

def getInputFrom(logger, args):
    logger.info("[getInputFrom] Extracting info from User")
    if (args.url is None):
        url=input("What webpage do you want to check? Enter full URL complete with \"https\": ")
    else:
        url=args.url
    logger.info("[getInputFrom] URL extracted: ["+url+"]")

    if (args.text is None):
        text=input("What text you want to search for on the webpage? ")
    else:
        text=args.text
    logger.info("[getInputFrom] SEARCH text extracted: ["+text+"]")

    if (args.xpath is None):
        xpath=input("Enter XPath for the element here: ")
    else:
        xpath=args.xpath
    logger.info("[getInputFrom] XPATH extracted: ["+xpath+"]")

    if (args.sender_email is None):
        fromPersonEmail=input("Enter From address: ")
    else:
        fromPersonEmail=args.sender_email
    logger.info("[getInputFrom] Sender email extracted: ["+fromPersonEmail+"]")

    if (args.sender_name is None):
        fromPersonName=input("Enter From Name: ")
    else:
        fromPersonName=args.sender_name
    logger.info("[getInputFrom] Sender name extracted: ["+fromPersonName+"]")

    if (args.reciever_name is None):
        toPersonName=input("Enter To address: ")
    else:
        toPersonName=args.reciever_name;
    logger.info("[getInputFrom] To email extracted: ["+toPersonName+"]")

    if (args.reciever_email is None):
        toPersonEmail=input("Enter To address: ")
    else:
        toPersonEmail=args.reciever_email;
    logger.info("[getInputFrom] To email extracted: ["+toPersonEmail+"]")

    if (args.password is None):
        password=input("Enter the password for ["+fromPerson+"]: ")
    else:
        password=args.password
    blankingPassword=""
    for x in range(0, len(password)-1):
        blankingPassword=blankingPassword+"*"
    logger.info("[getInputFrom] Password extracted: "+password[0:2]+blankingPassword+password[len(password)-2:])
    return url,text,xpath, fromPersonName,fromPersonEmail, toPersonName, toPersonEmail, password

def create_driver(logger):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-cache')
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--start-maximized')
    options.add_argument('--safebrowsing-disable-download-protection')
    options.add_argument('no-sandbox')
    browser = webdriver.Chrome(chrome_options=options)
    return browser

def closeDriver(driver,logger):
    if (driver is not None):
        logger.info("[checkSite] Closing driver")
        try:
            driver.quit()
        except Exception as e:
            logger.error("[checkSite] Unable to quit the driver due to the following error: {}".format(e))

def checkSite(url,text,xpath,logger):
    logger.info("[checkSite] Determing if ["+url+"] has been updated")
    try:
        logger.info("[checkSite] Ensuring that Chrome runs in headless state")
        logger.info("[checkSite] Initializing the web driver")
        driver = create_driver(logger)
        logger.info("[checkSite] Setting it to wait for 10 seconds before timing out")
        driver.implicitly_wait(20)
        logger.info("[checkSite] Attempting to access the url")
        driver.get(url)
        logger.info("[checkSite] Locating the username field on the webpage to indicate that redirect was successful")
        elems=driver.find_element_by_xpath(xpath)
        logger.info("[checkSite] Request element has been found")
        error=None

        border=""
        whiteSpace=""
        if (elems.text == text):
            subject="[SCRIPT] Text not changed from="+elems.text
            for x in range(0, len (elems.text)-18):
                border=border+"*"
                whiteSpace=whiteSpace+" "
            logger.info("[checkSite] *********************************"+border)
            logger.info("[checkSite] *** SITE HAS NOT BEEN UPDATED "+whiteSpace+"***")
            logger.info("[checkSite] *** Text=["+elems.text+"] ***")
            logger.info("[checkSite] *********************************"+border)
        else:
            subject="[SCRIPT] Text changed to="+elems.text
            for x in range(0, len (elems.text)-14):
                border=border+"*"
                whiteSpace=whiteSpace+" "
            logger.info("[checkSite] *****************************")
            logger.info("[checkSite] *** SITE HAS BEEN UPDATED "+whiteSpace+"***")
            logger.info("[checkSite] *** Text=["+elems.text+"] ***")
            logger.info("[checkSite] *****************************"+border)
    except Exception as e:
        logger.error("[checkSite] ********************************************************************")
        logger.error("[checkSite] *** FAILURE: unable to obtain webpage due to the following error ***")
        logger.error("[checkSite] ***                                                              ***")
        logger.error("[checkSite] ********************************************************************")
        logger.error("[checkSite] {}".format(e))
        error=e
    finally:
        closeDriver(driver,logger)
        #print(get_status(driver))
        try: #now checking to see if the script was able to pull anything from the site
            subject
        except NameError:
            return "[SCRIPT ERROR] Could not get text","Email sent from websiteChecker script on AWS"
        else:
            if (error is None):
                return subject, "Email sent from websiteChecker script on AWS"
            else:
                return "[checkSite] Unable to check site","{}".format(error)      

def createLogFile(formatter,logger):
    DATE=datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y_%m_%d_%H_%M_%S")
    FILENAME="logs/{}_website_checker_report".format(DATE)
    filehandler=logging.FileHandler("{}.log".format(FILENAME), mode="w")
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return "{}.log".format(FILENAME)

def emailResults(subject,body,fromPersonName,fromPersonEmail,toPersonName,toPersonEmail,password,attachments,logger):

    logger.info("[emailResults] Setting up MIMEMultipart object")
    msg = MIMEMultipart()
    msg['From']=fromPersonName+" <"+fromPersonEmail+">"
    msg['To']=toPersonName+" <"+toPersonEmail+">"
    msg['Subject']=subject
    msg.attach(MIMEText(body))

    try:
        logger.info("[emailResults] Attaching "+attachments+" to email")
        package = open(attachments, 'rb')
        logger.info("1")
        payload = MIMEBase('application','octet-stream')
        logger.info("2")
        payload.set_payload(package.read())
        logger.info("3")
        encoders.encode_base64(payload)
        logger.info("4")
        payload.add_header('Content-Disposition','attachment; filename={}'.format(attachments))
        logger.info("5")
        msg.attach(payload)
        logger.info("6")
        logger.info("[emailResults] {} has been attached".format(attachments))
        logger.info("7")
    except Exception as e:
        logger.error("[emailResults] {} could not be attached. Error {}".format())

    logger.info("[emailResults] Connecting to smtp.gmail.com:587")
    server = smtplib.SMTP()
    server.connect("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    logger.info("[emailResults] Logging into your gmail")
    server.login(fromPersonEmail,password)
    logger.info("[emailResults] Sending email...")
    server.send_message(from_addr=fromPersonEmail,to_addrs=toPersonEmail,msg=msg)
    server.close()

def initalizeParser():
    parser = argparse.ArgumentParser('Checks site to see if particular text has been updated and then emails it')
    parser.add_argument('--sender_name',help='Name of Sender')
    parser.add_argument('--sender_email',help="Email of Sender")
    parser.add_argument('-p', '--password', help="password for sender's email")
    parser.add_argument('--reciever_name', help='Name of Reciever')
    parser.add_argument('--reciever_email', help="Email of Reciever")
    parser.add_argument('-u', '--url', help='url to check')
    parser.add_argument('-t', '--text', help="Text to check it if has been updated")
    parser.add_argument('-x', '--xpath', help="XPath of text to check")
    args = parser.parse_args()

    return args
def main():

    formatter, logger = initalizeLogger()

    attachment = createLogFile(formatter,logger)

    args = initalizeParser()
    url,text,xpath,fromPersonName,fromPersonEmail,toPersonName, toPersonEmail,password = getInputFrom(logger, args)
    
    subject, body = checkSite(url,text,xpath,logger)

    emailResults(subject, body,fromPersonName,fromPersonEmail,toPersonName, toPersonEmail,password,attachment,logger)  

if __name__ == '__main__':
    main()
