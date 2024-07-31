from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from concurrent.futures import ThreadPoolExecutor, as_completed

# Google Sheets setup
def setup_google_sheets(json_keyfile_name, sheet_url, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    print("Google Sheets setup complete")
    return sheet

# Function to calculate the exact date based on the "weeks ago" text
def calculate_posting_date(relative_date_str):
    num, unit = relative_date_str.split()[:2]
    num = int(num)
    if 'week' in unit:
        return (datetime.now() - timedelta(weeks=num)).strftime('%Y-%m-%d')
    elif 'day' in unit:
        return (datetime.now() - timedelta(days=num)).strftime('%Y-%m-%d')
    else:
        return 'Unknown date'

# Function to extract job details from each individual job link
def extract_job_details(link):
    options = Options()
    options.headless = True
    chromedriver_path = '/opt/homebrew/bin/chromedriver'
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.get(link)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'description__text')))
    except:
        driver.quit()
        return 'No description available', 'No date available'

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_description = soup.find('div', class_='description__text').text.strip() if soup.find('div', class_='description__text') else 'No description available'

    posting_date_element = soup.find('span', class_='t-14 t-black--light t-normal')
    posting_date = calculate_posting_date(posting_date_element.text.strip()) if posting_date_element else 'No date available'

    driver.quit()
    return job_description, posting_date

# Scraping LinkedIn Jobs
def scrape_linkedin_jobs(url):
    options = Options()
    options.headless = True
    chromedriver_path = '/opt/homebrew/bin/chromedriver'
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    driver.get(url)

    input("Please log in to LinkedIn and then press Enter here to continue...")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_listings = []

    print("Page title:", soup.title.string)

    jobs = soup.find_all('div', class_='job-card-container--clickable')
    print(f"Found {len(jobs)} job containers")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_job, job) for job in jobs]
        for future in as_completed(futures):
            job_details = future.result()
            if job_details:
                job_listings.append(job_details)

    driver.quit()
    print(f"Scraped {len(job_listings)} jobs")
    return job_listings

def process_job(job):
    try:
        title_element = job.find('a', class_='job-card-list__title')
        company_element = job.find('a', class_='job-card-container__company-name')
        link_element = job.find('a', class_='job-card-list__title')
        location_element = job.find('li', class_='job-card-container__metadata-item')

        if title_element and link_element:
            title = title_element.text.strip()
            link = "https://www.linkedin.com" + link_element['href']

            if company_element:
                company = company_element.text.strip()
            else:
                company_element_alt = job.find('span', class_='job-card-container__primary-description')
                company = company_element_alt.text.strip() if company_element_alt else "Company not listed"

            location = location_element.text.strip() if location_element else "Location not listed"
            job_description, job_posting_date = extract_job_details(link)

            return [title, company, f'=HYPERLINK("{link}", "Link")', location, job_posting_date, job_description]
        else:
            print("Missing one of the required elements: title or link.")
            return None
    except Exception as e:
        print(f"Error parsing job: {e}")
        return None

def main():
    json_keyfile_name = '<path to your json key file>'
    sheet_url = '<your sheet url>'
    sheet_name = '<your sheet name>'
    urls = [
        '<linked in urls you want to extract>'
    ]

    print("Starting Google Sheets setup...")
    sheet = setup_google_sheets(json_keyfile_name, sheet_url, sheet_name)

    for url in urls:
        print(f"Starting LinkedIn jobs scraping for {url}...")
        jobs = scrape_linkedin_jobs(url)

        # Print the scraped jobs for debugging
        print("Scraped Jobs:")
        for job in jobs:
            print(job)

        # Write to Google Sheets
        if jobs:
            for job in jobs:
                sheet.append_row(job, value_input_option='USER_ENTERED')
            print("Data written to Google Sheets")

if __name__ == '__main__':
    main()