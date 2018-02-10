from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from selenium import webdriver

def create_driver():
	options = webdriver.ChromeOptions()
	options.add_argument('--disable-cache')
	options.add_argument('--headless')
	options.add_argument('--incognito')
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--start-maximized')
	options.add_argument('--safebrowsing-disable-download-protection')
	browser = webdriver.Chrome('path_to_chromedriver', chrome_options=options)
	return browser


url="http://vancouver.itamaraty.gov.br/pt-br/documentos_militares_para_retirada.xml"
print("Determing if ["+url+"] has been updated")
try:
    print("Ensuring that Chrome runs in headless state")
    print("Initializing the web driver")
    driver = create_driver()
    print("Setting it to wait for 10 seconds before timing out")
    driver.implicitly_wait(10)
    print("Attempting to access the url")
    driver.get(url)
    print("Locating the username field on the webpage to indicate that redirect was successful")
    elems=driver.find_element_by_xpath('//*[@id="mainContentNews"]/span/div/span')
    print(elems.text)

    if (elems.text == "Atualizado em 11/julho/2017"):
    	print("*********************************")
    	print("*** SITE HAS NOT BEEN UPDATED ***")
    	print("***                           ***")
    	print("*********************************")
    else:
    	print("*****************************")
    	print("*** SITE HAS BEEN UPDATED ***")
    	print("***                       ***")
    	print("*****************************")		
except Exception as e:
    print("********************************************************************")
    print("*** FAILURE: unable to obtain webpage due to the following error ***")
    print("***                                                              ***")
    print("********************************************************************")
    print("{}".format(e))
    redirect_url="REDIRECT_URL is not available"
finally:

    try:#first checks to ensure the driver is defined because in certain cases it fails to intialize it after having it crash
      driver
    except NameError:
      print("Driver is undefined, unable to close it")
    else:
        if (driver is not None):
            print("Closing driver")
            try:
                driver.close()
            except Exception as e:
                print("Unable to close the driver due to the following error: {}".format(e))
                display = None
                driver.quit()
