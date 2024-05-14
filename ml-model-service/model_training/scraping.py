from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ordered_set import OrderedSet
import pandas as pd
import re
import os


def get_driver(url):
    # Initialize Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    if os.environ.get('DOCKER_ENV') == 'true':
        # Running inside Docker, use Selenium Grid
        print('using selenium docker')
        driver = webdriver.Remote(command_executor='http://selenium-chrome:4444/wd/hub', options=chrome_options)
    else:
        # Running using chrome driver
        print('using chrome driver')
        driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    return driver


def web_scrap(url, website_id):
    all_text = []
    driver = get_driver(url)

    # Use explicit wait for elements to be present in the DOM
    wait = WebDriverWait(driver, 25)
    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))

    # Fetch page source after the wait
    data = driver.page_source
    soup = BeautifulSoup(data, 'html.parser')

    # Old logic for finding all div tags
    # div_tags = soup.find_all('div')

    # # Print id and class attributes in sequence
    # for div_tag in div_tags:
    #     # Iterate through nested tags inside the div
    #     for nested_tag in div_tag.find_all(recursive=False):
    #         text = nested_tag.get_text(strip=True)
    #         all_text.append(text)

    # For all tags 
    th_tags = soup.find_all('th')
    for th_tag in th_tags:
        for nested_tag in th_tag:
            text = nested_tag.text
            all_text.append(text)

    td_tags = soup.find_all('td')
    for td_tag in td_tags:
        for nested_tag in td_tag:
            text = nested_tag.text
            all_text.append(text)
            
    li_tags = soup.find_all('li')
    for li_tag in li_tags:
        for nested_tag in li_tag:
            text = nested_tag.text
            all_text.append(text)

    p_tags = soup.find_all('p')
    for p_tag in p_tags:
        for nested_tag in p_tag:
            text = nested_tag.text
            all_text.append(text)

    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        for nested_tag in a_tag:
            text = nested_tag.text
            all_text.append(text)

    span_tags = soup.find_all('span')
    for span_tag in span_tags:
        for nested_tag in span_tag:
            text = nested_tag.text
            all_text.append(text)

    h1_tags = soup.find_all('h1')
    for h1_tag in h1_tags:
        for nested_tag in h1_tag:
            text = nested_tag.text
            all_text.append(text)

    h2_tags = soup.find_all('h2')
    for h2_tag in h2_tags:
        for nested_tag in h2_tag:
            text = nested_tag.text
            all_text.append(text)

    div_tags = soup.find_all('div')
    for div_tag in div_tags:
        for nested_tag in div_tag:
            text = nested_tag.text
            all_text.append(text)


    # To filter empty list or lines from fetched data
    filtered_list = [item for item in all_text if item.strip() != '']
    for i in range(len(filtered_list)):
        filtered_list[i] = filtered_list[i].replace('\n', '')

    # Remove duplicate elements
    filtered_list = list(OrderedSet(filtered_list))

    # Remove text based on length of list element 
    def filter_by_count(string_list):
        text = [string for string in string_list if sum(c.isalpha() for c in string) >= 20]
        text = [string for string in text if sum(c.isalpha() for c in string) <= 500]
        return text

    filtered_list = filter_by_count(filtered_list)

    # Remove unwanted text from the list elements
    def filter_alphabets(strings):
        pattern = re.compile('[a-zA-Z]')
        filtered_strings = [s for s in strings if pattern.search(s)]
        return filtered_strings

    def remove_numbers(input_str):
        return re.sub(r'\d', '', input_str)

    filtered_list = filter_alphabets(filtered_list)
    filtered_list = [remove_numbers(item) for item in filtered_list]

    current_script_path = os.path.dirname(os.path.abspath(__file__))
    output_directory = os.path.join(current_script_path, "scraped_data")

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    df = pd.DataFrame({"Text": filtered_list})
    output_file_path = os.path.join(output_directory, "{}.csv".format(website_id))

    try:
        df.to_csv(output_file_path, index=False, encoding='utf-8')
        # TODO use regex to save only certain text
        print(f'Data has been successfully written to {output_file_path}')
    except Exception as e:
        print(f'Error writing to the file: {e}')

    # Close browser window
    driver.quit()

    return 'Done'


# Delete the files in scraped_data directory before running the code of web scraping
def delete_files_in_scraped_data():
    script_directory = os.path.dirname(__file__)
    scraped_data_directory = os.path.join(script_directory, 'scraped_data')

    # Check if the directory exists
    if not os.path.exists(scraped_data_directory):
        print(f"The directory '{scraped_data_directory}' does not exist.")
        return 'Not deleted'
    
    # List all files in the directory
    files = os.listdir(scraped_data_directory)
    if files:
        for file in files:
            file_path = os.path.join(scraped_data_directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
        return 'Deleted'
    else:
        print("No files exist in the directory.")
        return 'Not deleted'

   
    