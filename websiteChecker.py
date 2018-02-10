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

def getInputFrom(logger):
    url=input("What webpage do you want to check? Enter full URL complete with \"https\": ")
    logger.info("URL extracted: "+url)
    text=input("Ehat text you want to search for on the webpage? ")
    logger.info("SEARCH text extracted: "+text)
    xpath=input("Enter XPath for the element here: ")
    logger.info("XPATH extracted: "+xpath)
    fromPerson=input("Enter From address: ")
    logger.info("Sender email extracted: "+fromPerson)
    toPerson=input("Enter To address: ")
    logger.info("To email extracted: "+toPerson)
    password=input("Enter the password for ["+fromPerson+"]: ")
    blankingPassword=""
    for x in range(0, len(password)-1):
        blankingPassword=blankingPassword+"*"
    logger.info("Password extracted: "+password[0:2]+blankingPassword+password[len(password)-5:2])
    return url,text,xpath, fromPerson, toPerson, password

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-cache')
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--start-maximized')
    options.add_argument('--safebrowsing-disable-download-protection')
    browser = webdriver.Chrome(chrome_options=options)
    return browser

def output(text,body,logger,logtype=False):
    if (logtype):
        logger.error(text)
    else:
        logger.info(text)
    return body+text+"\n"

def checkSite(url,text,xpath,logger):
    logger.info("Determing if ["+url+"] has been updated")
    try:
        logger.info("Ensuring that Chrome runs in headless state")
        logger.info("Initializing the web driver")
        driver = create_driver()
        logger.info("Setting it to wait for 10 seconds before timing out")
        driver.implicitly_wait(10)
        logger.info("Attempting to access the url")
        driver.get(url)
        logger.info("Locating the username field on the webpage to indicate that redirect was successful")
        elems=driver.find_element_by_xpath(xpath)
        logger.info("Request element has been found")
        error=None
        subject="Site last updated on "+elems.text

        border=""
        whiteSpace=""
        body=""
        if (elems.text == text):
            for x in range(0, len (elems.text)-18):
                border=border+"*"
                whiteSpace=whiteSpace+" "
            text="*********************************"+border
            body=output(text,body,logger)
            text="*** SITE HAS NOT BEEN UPDATED "+whiteSpace+"***"
            body=output(text,body,logger)
            text="*** Date=["+elems.text+"] ***"
            body=output(text,body,logger)
            text="*********************************"+border
            body=output(text,body,logger)
        else:
            for x in range(0, len (elems.text)-14):
                border=border+"*"
                whiteSpace=whiteSpace+" "
            text="*****************************"+border
            body=output(text,body,logger)
            text="*** SITE HAS BEEN UPDATED "+whiteSpace+"***"
            body=output(text,body)
            text="*** Date=["+elems.text+"] ***"
            body=output(text,body,logger)
            text="*****************************"+border
            body=output(text,body,logger)
    except Exception as e:
        text="********************************************************************"
        body=output(text,body,logger,True)
        text="*** FAILURE: unable to obtain webpage due to the following error ***"
        body=output(text,body,True)
        text="***                                                              ***"
        body=output(text,body,logger,True)
        text="********************************************************************"
        body=output(text,body,logger,True)
        text="{}".format(e)
        body=output(text,body,logger,True)
        error=e
    finally:
        try:#first checks to ensure the driver is defined because in certain cases it fails to intialize it after having it crash
          driver
        except NameError:
          text="Driver is undefined, unable to close it"
          body =output(text,body,logger)
        else:
            if (driver is not None):
                text="Closing driver"
                body =output(text,body,logger)
                try:
                    driver.close()
                except Exception as e:
                    text="Unable to close the driver due to the following error: {}".format(e)
                    body =output(text,body,logger)
                    display = None
                    driver.quit()
        if (error is None):
            return subject, body
        else:
            return "Unable to check consulate site","{}".format(error)


def createLogFile(formatter,logger):
    DATE=datetime.datetime.now(pytz.timezone('US/Pacific')).strftime("%Y_%m_%d_%H_%M_%S")
    FILENAME="{}_website_checker_report".format(DATE)
    filehandler=logging.FileHandler("{}.log".format(FILENAME), mode="w")
    filehandler.setLevel(logging.INFO)
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    return "{}.log".format(FILENAME)

def emailResults(subject,body,fromPerson,toPerson,password,attachments,logger):

    logger.info("Setting up MIMEMultipart object")
    msg = MIMEMultipart()
    msg['From']=fromPerson
    msg['To']=toPerson
    msg['Subject']=subject
    msg.attach(MIMEText(body))

    try:
        logger.info("Attaching logs to email")
        package = open(attachments, 'rb')
        payload = MIMEBase('application','octet-stream')
        payload.set_payload(package.read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Disposition','attachment; filename={}'.format(attachments))
        msg.attach(payload)
        logger.info("{} has been attached".format(attachments))
    except Exception as e:
        logger.error("{} could not be attached. Error {}".format())

    logger.info("Connecting to smtp.gmail.com:587")
    server = smtplib.SMTP()
    server.connect("smtp.gmail.com:587")
    server.ehlo()
    server.starttls()
    logger.info("Logging into your gmail")
    server.login(fromPerson,password)
    logger.info("Sending email...")
    server.send_message(from_addr=fromPerson,to_addrs=toPerson,msg=msg)
    server.close()

def main():
    formatter, logger = initalizeLogger()

    attachment = createLogFile(formatter,logger)

    logger.info("Extracting info from User")
    url,text,xpath,fromPerson,toPerson,password = getInputFrom(logger)
    logger.info("Info extracted from User")

    url="http://vancouver.itamaraty.gov.br/pt-br/documentos_militares_para_retirada.xml"
    text="Atualizado em 11/julho/2017"
    xpath="//*[@id=\"mainContentNews\"]/span/div/span"
    
    subject, body = checkSite(url,text,xpath,logger)

    emailResults(subject, body,fromPerson,toPerson,password,attachment,logger)  

if __name__ == '__main__':
    main()