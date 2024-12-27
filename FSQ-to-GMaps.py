# import required modules
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options

import selenium
import keyboard
import random
from rapidfuzz import fuzz, process
import re
import logging

from dotenv import load_dotenv
import os
from datetime import datetime


chromedriver_path = r"d:\Users\pbaro\Downloads\Temp\chromedriver-win64\chromedriver-win64\chromedriver.exe"
load_dotenv()

csv_file = 'output.csv'
executionTimeStamp = current_time_and_date = datetime.now().strftime("%Y-%m-%d %H:%M")

USER_DIR = os.getenv('USER_DIR')

logger = logging.getLogger('urllib3.connectionpool')
logger.setLevel(logging.INFO)

logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.WARNING)

from processCSV import processCSV
from processCSV import write_to_csv


mapURL = "https://www.google.com/maps"

def openGoogleMaps():
    userDataDir = f"user-data-dir={USER_DIR}"
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("log-level=3")
    chrome_options.add_argument("disable-logging")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False})
    chrome_options.add_argument(userDataDir)


    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to Google
    driver.get(mapURL)
    driver.implicitly_wait(0.1)

    sleep(2)
    return driver


def waitForAddedConfirmation(driver, timeout=10):
    """
    Wait until a div with XPath '//*[@id="Ng57nc"]/div' is visible,
    then wait for it to disappear.

    Parameters:
        driver: Selenium WebDriver instance.
        timeout: Maximum wait time in seconds for each condition.

    Returns:
        True if the div appeared and disappeared as expected, else False.
    """
    xpath = '//*[@id="Ng57nc"]/div'
    sleep(0.2)

    try:
        print("Waiting for Div!")
        # Wait for the div to become visible
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        print("Div is now visible!")
        
        sleep(0.2)


        #click on the popup
        driver.find_element(By.XPATH, '//*[@id="Ng57nc"]/div/button/span').click()

        # Wait for the div to disappear
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, xpath))
        )
        print("Div has disappeared!")

        return True

    except Exception as e:
        print(f"Timeout or error: {e}")
        return False
    
def OpenListsPage(driver):

    driver.get(mapURL)
    sleep(3)

    #click on the menu button
    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[1]/ul/li[1]/button').click()
    sleep(0.1)

    #click on the "Saved" button
    driver.find_element(By.XPATH, '//*[@id="settings"]/div/div[2]/ul/div[4]/li[1]/button').click()

    sleep(3)

def extractListName(input_string):
    # Use regex to match text between the first '\n' and the second '\n'
    pat = '\\n(.*?)\\n'
    match = re.search(pat, input_string)
    return match.group(1) if match else None   


def FindGMLists(driver):

    scrollable_element = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
    scroll_specific_element(scrollable_element, driver, pause_time=0.2)

    lists = driver.find_elements(By.CLASS_NAME, "CsEnBe")

    listNames = []
    for list in lists:
        listNames.append(extractListName(list.text))
    
    return listNames

def create_GMapList(listName):
    addListButton = driver.find_element(By.CLASS_NAME, "M77dve")
    addListButton.click()
    sleep(1)

    listNameField = driver.find_element(By.CSS_SELECTOR, '[aria-label="List name"]')
    for k in listName:
        listNameField.send_keys(k)
        sleep(random.uniform(0, 0.1))

    createButtton = driver.find_element(By.CLASS_NAME, "okDpye")
    createButtton.click()
    sleep(1)

    driver.find_element(By.CSS_SELECTOR, '[aria-label="Back"]').click()
    sleep(1)



def get_unique_items(FSQLists, GMapLists):
    """
    Get the lists in the FSQList that are not present in the GMapLists

    :param FSQLists: Forsquare lists
    :param GMapLists: Google Maps lists
    :return: List that are in FSQ but not in GMaps
    """
    
    return [item for item in FSQLists if item not in GMapLists]


def findElementByText(driver, elementsArray, text):
    
    for element in elementsArray:
        if element.text.startswith(text):
            return element


def scroll_specific_element(element, driver, pause_time=0.2):
    last_height = driver.execute_script("return arguments[0].scrollHeight", element)
    
    while True:
        # Scroll the container to the bottom
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", element)
        sleep(pause_time)  # Pause to allow content to load
        
        # Check if new content is loaded
        new_height = driver.execute_script("return arguments[0].scrollHeight", element)
        if new_height == last_height:  # Exit the loop if no new content is loaded
            break
        last_height = new_height

def combine_places_and_addresses(place_names, place_addresses):
    combined_list = []
    
    for name, address in zip(place_names, place_addresses):
        # Get the part of the address before the first comma, or set it to None if the address is empty
        first_address_part = address.split(',')[0].strip() if address else None
        combined_list.append({'name': name, 'address': first_address_part})
    
    return combined_list


def find_match_with_score(place_name, place_address, combined_list, name_threshold=70, address_threshold=70):
    """
    Finds the best match for a given place name and address from a combined list of places.

    Args:
        place_name (str): The name of the place to match.
        place_address (str): The address of the place to match.
        combined_list (list): A list of dictionaries with 'name' and 'address'.
        name_threshold (int): The minimum similarity score for names to consider a match.
        address_threshold (int): The minimum similarity score for addresses to consider a match.

    Returns:
        tuple: A tuple containing the matching dictionary, the combined score, and the index in the list,
               or (None, 0, -1) if no match is found.
    """
    place_name = place_name.lower()
    place_address = place_address.lower()

    best_match = None
    highest_score = 0
    best_index = -1

    for index, entry in enumerate(combined_list):
        entry_name = entry['name'].lower()
        entry_address = entry['address'].lower() if entry['address'] else ""

        # Compare names and addresses
        name_score = fuzz.partial_ratio(place_name, entry_name)
        address_score = fuzz.partial_ratio(place_address, entry_address)

        # Combine scores
        combined_score = (name_score + address_score) / 2

        # Check thresholds
        if combined_score > highest_score and ((name_score >= name_threshold and address_score >= address_threshold) or (name_score == 100)):
            highest_score = combined_score
            best_match = entry
            best_index = index

    return best_match, highest_score, best_index


def get_elements_text_safe(elements: list[WebElement]) -> list[str]:
    """
    Safely fetch text from a list of WebElements, skipping elements that raise errors.

    Args:
        elements (list[WebElement]): A list of Selenium WebElement objects.

    Returns:
        list[str]: A list of text from elements, converted to lowercase, with problematic elements skipped.
    """
    texts = []
    for element in elements:
        try:
            if element.text:
                texts.append(element.text.lower())
        except Exception:
            pass  # Skip elements that raise any error
    return texts

if __name__ == "__main__":

    csv_file_path = "allplaces.csv"

    driver = openGoogleMaps()
    OpenListsPage(driver)

    GMaplists = FindGMLists(driver)
    print("Google lists")
    print(GMaplists)



    CSV_processor = processCSV('allplaces.csv')
    FSQLists = CSV_processor.distinct_values('ListName')

    print("FSQ lists")
    print(FSQLists)

    # get a list of lists that are in FSQ but not in GMaps
    newLists = get_unique_items(FSQLists, GMaplists)
    print("New lists")
    print(newLists)

    #loop through all FSQ Lists
    
    for FSQList in FSQLists:
        #reopen the lists page to make sure we are in the right place
        OpenListsPage(driver)
        
        # scroll down the places list so all are loaded
        scrollable_element = driver.find_element(By.CLASS_NAME, "DxyBCb")
        scroll_specific_element(scrollable_element, driver, pause_time=0.2)
        sleep(0.5)

        print(f"Processing list: {FSQList}")
        
        #if the list does not exist in GMap, add it
        if FSQList not in GMaplists:
            print(f"List {FSQList} does not exist in GMap. Creating it")
            create_GMapList(FSQList)
            sleep(1)

            # scroll down the places list so all are loaded
            scrollable_element = driver.find_element(By.CLASS_NAME, "DxyBCb")
            scroll_specific_element(scrollable_element, driver, pause_time=0.2)
            sleep(0.5)

        else:
            print(f"List {FSQList} exists in GMap opening it")
            
        listDivs = driver.find_elements(By.CLASS_NAME, "rogA2c")

        for listDiv in listDivs:
            listDivText = listDiv.text

            before_newline = listDivText.split('\n')[0]

            if before_newline == FSQList:
                listDiv.click()
                sleep(.2)
                break

        
        sleep(1)

        try:
            scrollable_element = driver.find_element(By.CLASS_NAME, "DxyBCb")
        except selenium.common.exceptions.NoSuchElementException as e:
            sleep(2)
            scrollable_element = driver.find_element(By.CLASS_NAME, "DxyBCb")

        scroll_specific_element(scrollable_element, driver, pause_time=0.2)
        sleep(0.5)

        placesDiv = driver.find_elements(By.CLASS_NAME, "BsJqK")
        placesNames = [div.text.split('\n')[0].upper() for div in placesDiv]

        # Get the list page URL
        current_url = driver.current_url

        # now enter edit mode
        EditListButton = driver.find_element(By.CLASS_NAME, "NmQc4")
        EditListButton.click()
        sleep(.1)

        EditListMenu = driver.find_elements(By.CLASS_NAME, "fxNQSd")
        findElementByText(driver, EditListMenu, "Edit list").click()
        sleep(.1)


        places = CSV_processor.filter_by_column('ListName', FSQList)
        for index, row in places.iterrows():

            place_name = row['name']
            place_address = row['address']
            fullSearchTerm = place_name + " " + place_address
            print(f" - Place name: {place_name} - {place_address}")

            keywords = place_name.split()

            # Custom scorer function
            def custom_score(s1, s2, **kwargs):  # Add **kwargs to handle additional arguments
                # Primary score using token_sort_ratio
                primary = fuzz.token_sort_ratio(s1, s2)
                # Keyword boost: Add points for each keyword match
                keyword_matches = sum(1 for kw in keywords if kw.lower() in s2.lower())
                keyword_boost = 15 * keyword_matches  # Adjust boost value if needed
                return primary + keyword_boost

            if len(placesNames) > 0:
                # check if the place already exists
                best_match, score, y = process.extractOne(place_name, placesNames, scorer=custom_score)
                if score > 60:
                    write_to_csv(csv_file, {'List name':FSQList, 'Place name': place_name, 'Place address': place_address, 'Result': 'ALREADY IN LIST', 'Date': executionTimeStamp})
                    print(f" - Place already exists in list: {best_match}")
                    continue

            sleep(0.5)
            #click on the ADD a place button

            max_attempts = 5  # Number of attempts
            attempts = 0

            while attempts < max_attempts:
                try: 
                    #driver.find_element(By.CSS_SELECTOR, '[aria-label="Add a place"]').click()
                    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[4]/div').click()
                    break

                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed: {e}")
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    sleep(1)  # Wait a moment before retrying
                
            
            if attempts == max_attempts:
                print("Failed to click the element after 5 attempts.")
                raise RuntimeError(f"Failed to click 'Add a place' button after {max_attempts} attempts")
            sleep(.1)

            #Enter in the search place field and type the place name
            if len(driver.find_elements(By.CLASS_NAME, "LxoNjd")) == 0:
                driver.find_element(By.CSS_SELECTOR, '[aria-label="Add a place"]').click()
                sleep(.1)

            try:
                SearchField = driver.find_element(By.CLASS_NAME, "LxoNjd")
            except selenium.common.exceptions.NoSuchElementException as e:
                if len(driver.find_elements(By.CLASS_NAME, "LxoNjd")) == 0:
                    driver.find_element(By.CSS_SELECTOR, '[aria-label="Add a place"]').click()
                    sleep(.1)

                SearchField = driver.find_element(By.CLASS_NAME, "LxoNjd")
            
            SearchField.click()
            sleep(.1)
            SearchField.send_keys(Keys.CONTROL + "a")
            SearchField.clear()
            sleep(.5)

            for k in place_name:
                SearchField.send_keys(k)
                sleep(random.uniform(0, 0.1))
            
            sleep(2)


            searchResults = driver.find_elements(By.CLASS_NAME, 'cGyruf')

            searchResultsPlacesNames = driver.find_elements(By.XPATH, '//*[@id="cell-1x0"]/span[2]')

            if len(searchResultsPlacesNames) == 0:
                write_to_csv(csv_file, {'List name':FSQList, 'Place name': place_name, 'Place address': place_address, 'Result': 'NOT FOUND', 'Date': executionTimeStamp})
                print(f" - Place not found in GMap: {place_name}")
                continue

            if len(searchResultsPlacesNames) > 1:
                for k in " " + place_address:
                    SearchField.send_keys(k)
                    sleep(random.uniform(0, 0.1))
                
                searchResultsPlacesNames = driver.find_elements(By.XPATH, '//*[@id="cell-1x0"]/span[2]')
            
            sleep(2)

            searchResultsPlacesAddress = driver.find_elements(By.XPATH, '//*[@id="cell-1x0"]/span[3]')
            searchResultsPlacesNamesText = get_elements_text_safe(searchResultsPlacesNames)
            searchResultsPlacesAddressText = get_elements_text_safe(searchResultsPlacesAddress)

            #searchResultsPlacesNamesText = [div.text.lower() for div in searchResultsPlacesNames]
            #searchResultsPlacesAddressText = [div.text.lower() for div in searchResultsPlacesAddress]

            combined = combine_places_and_addresses(searchResultsPlacesNamesText , searchResultsPlacesAddressText )

            match, score, placeIndex = find_match_with_score(place_name, place_address, combined)

            if placeIndex == -1:
                write_to_csv(csv_file, {'List name':FSQList, 'Place name': place_name, 'Place address': place_address, 'Result': 'NOT FOUND', 'Date': executionTimeStamp})
                print(f" - Place not found in GMap: {place_name}")
                continue
            

            # place found in the search results, click on it
            print(f" - Place found in GMap: {place_name}")
            
            try:
                searchResults[placeIndex].click()
                write_to_csv(csv_file, {'List name':FSQList, 'Place name': place_name, 'Place address': place_address, 'Result': 'ADDED', 'Date': executionTimeStamp})
                waitForAddedConfirmation(driver, 10 )
                sleep(1)
            except Exception as e:
                print(f"Error: {e}")
                print("If you see the place in the results dropdown you can add it by clicking on it.")
                print("Press any key to continur...")
                key = keyboard.read_event().name
                write_to_csv(csv_file, {'List name':FSQList, 'Place name': place_name, 'Place address': place_address, 'Result': 'ERROR', 'Date': executionTimeStamp})
                

    exit(1)

