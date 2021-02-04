from selenium import webdriver
from getpass import getpass
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime




def term_to_termcode(term):
	"""
	Translates a human-readable term i.e. "Fall 2010"
	into the "termcode" parameter that the Middlebury
	Course Catalog database URL uses.
	"""
	normalized_term = term.strip().lower()
	season, year = normalized_term.split(' ')[0], normalized_term.split(' ')[1]

	if season == 'winter':
		season = '0'
	elif season == 'spring':
		season = '1'
	elif season == 'summer':
		season = '5'
	elif season == 'fall':
		season = '8'
	else:
		season = 'UNKNOWN'
		print ('Error in determining the season of the given term!')


	return "1" + year + season


if (__name__ == "__main__"):

    netId = input("Enter your netid:")
    password = getpass("Enter your password:")

    term_key = input("Enter the term (ie. Fall 2021, if showing 2021-2022 enter 2022): ")
    banner_term_key = term_to_termcode(term_key)

    # ask for CRNs
    crn_str = input("Enter the CRNs, separate each CRN with a space: ")
    crn_str = str(crn_str)
    crn_list = []
    # convert uses input into a list of CRNs
    for i in crn_str.split():
        crn_list.append(i)

    #Open google chrome and go to self service page
    driver = webdriver.Chrome("/Users/clouddong/Dev/chromedriver")
    driver.get("https://apps.uillinois.edu/selfservice/")
    branch = driver.find_element_by_class_name("self-service-login")
    branch.click()
    print("please wait for a few seconds")
    time.sleep(1)

    #Enter NetID and Password, then click login
    netId_box = driver.find_element_by_id("netid")
    netId_box.send_keys(netId)
    time.sleep(1)
    password_box = driver.find_element_by_id("easpass")
    password_box.send_keys(password)
    time.sleep(1)
    login_btn = driver.find_element_by_class_name("bttn")
    login_btn.click()

    #Navigate to the course registration section
    driver.implicitly_wait(2)
    navTab = driver.find_element_by_link_text("Registration & Records")
    navTab.click()
    driver.implicitly_wait(2)
    enhcedRegist = driver.find_element_by_link_text("Enhanced Registration")
    enhcedRegist.click()

    #Switch to the new tab
    driver.implicitly_wait(2)
    driver.switch_to.window(driver.window_handles[-1])
    element = driver.find_element_by_id("registerLink")
    element.click()

    #activate search bar
    search_init = driver.find_element_by_id("s2id_txt_term")
    search_init.click()

    #insert term code and input term code
    search_box = driver.find_element_by_class_name("select2-input")
    search_box.send_keys(banner_term_key)

    #select the returned value
    search_result = driver.find_element_by_class_name("select2-result-label")
    search_result.click()

    driver.find_element_by_id("term-go").click()

    try:
        flag = 0
        while flag == 0:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "enterCRNs-tab"))
            )



            element.click()
            addAnother = driver.find_element_by_id("addAnotherCRN")


            #fill in the CRN boxes
            for i in crn_list:
                addAnother.click()
                driver.find_element_by_id("txt_crn" + str(crn_list.index(i) + 1)).send_keys(i)


            #add courses
            driver.find_element_by_id("addCRNbutton").click()
            #sumbit the form
            time.sleep(3)
            driver.find_element_by_id("saveButton").click()
            time.sleep(5)

            """
            # check if the table has pending stat
            def check_pending():
                rows = len(driver.find_elements_by_xpath("//*[@id='summaryBody']/div[1]/div/table/tbody/tr"))

                for row in range(1, rows+1):
                    print(row)
                    x_path_b = "//*[@id='summaryBody']/div[1]/div/table/tbody/tr["+str(row)+"]/td[6]/span"
                    b = driver.find_element_by_xpath(x_path_b).text
                    if b == "Pending":
                        return False
                return True

            wait = WebDriverWait(driver, 10)
            pending_out = driver.find_element_by_xpath()
            element = wait.until(check_pending())
            """

            #count table rows
            rows = len(driver.find_elements_by_xpath("//*[@id='summaryBody']/div[1]/div/table/tbody/tr"))
            print(rows)
            dictionary = {}

			#get CRN and Status in summary table
            for row in range(1, rows+1):
                print(row)
                x_path_a = "//*[@id='summaryBody']/div[1]/div/table/tbody/tr["+str(row)+"]/td[4]"
                x_path_b = "//*[@id='summaryBody']/div[1]/div/table/tbody/tr["+str(row)+"]/td[6]"
                a = driver.find_element_by_xpath(x_path_a).text
                print(a)
                b = driver.find_element_by_xpath(x_path_b).text
                print(b)
                dictionary.setdefault(a, []).append(b)

            print(dictionary)
            failed_crn = []

			#check and output courses that failed to add and courses that successfully added
            for crns in crn_list:
                print(dictionary[crns])
                if dictionary[crns] == ['Registered']:
                    print("Successfully registered courses: "+str(crns))
                else:
                    print("Failed to registered courses: "+str(crns))
                    failed_crn.append(crns)
                    print(failed_crn[0])

            if not failed_crn:
                print("Done select")
                flag = 1
            else:
                print("not done but still in the while loop")
                crn_list.clear()
                for i in failed_crn:
                    crn_list.append(i)
                print("looped crn list: " + crn_list[0])
                driver.find_element_by_id("saveButton").click()
                time.sleep(15)
    except:
        print("out of 'try', will quit soon")
        time.sleep(10)
        driver.quit()
