from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import unicodedata

NUM_SAMPLES = 150

# Initialize Chrome with ChromeDriverManager
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless")  # Runs in background (no window pop-up)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)  # Explicit wait to avoid missing elements

url = "https://my.jobstreet.com/AI-Engineer-jobs"
driver.get(url)
time.sleep(5)  

job_urls = []

# Step 1: Collect all job URLs from the listing pages
print("\n📌 Collecting job post URLs...\n")
while len(job_urls) < NUM_SAMPLES:
    try:
        job_posts = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@data-automation='job-list-item-link-overlay']")))
    except:
        print("⚠️ No job posts found on this page.")
        break

    for job in job_posts:
        job_url = job.get_attribute("href")
        if job_url and job_url not in job_urls:
            job_urls.append(job_url)

        if len(job_urls) >= NUM_SAMPLES:
            break

    # Click "Next" if more jobs are needed
    if len(job_urls) < NUM_SAMPLES:
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@aria-label, 'Next')]")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)
        except:
            print("⚠️ No more pages found. Stopping.")
            break

print(f"\n✅ Collected {len(job_urls)} job post URLs.\n")

# Step 2: Visit each URL and extract job details
job_data = []

# Function to clean text (normalize and handle encoding issues)
def clean_text(text):
    text = unicodedata.normalize("NFKC", text)  # Normalize Unicode characters
    text = text.encode("utf-8", "ignore").decode("utf-8")  # Properly encode/decode text    
    return " ".join(text.replace("\n", " ").split())

# Function to extract job details
def extract_job_details(job_url):
    driver.get(job_url)
    time.sleep(3)  # Allow page to load

    try:
        title = wait.until(EC.presence_of_element_located((By.XPATH, "//h1[@data-automation='job-detail-title']"))).text
        title = clean_text(title)
    except:
        title = "N/A"

    try:
        company = driver.find_element(By.XPATH, "//span[@data-automation='advertiser-name']").text
        company = clean_text(company)
    except:
        company = "N/A"

    try:
        location = driver.find_element(By.XPATH, "//span[@data-automation='job-detail-location']").text
        location = clean_text(location)
    except:
        location = "N/A"

    try:
        sector = driver.find_element(By.XPATH, "//span[@data-automation='job-detail-classifications']").text
        sector = clean_text(sector)
    except:
        sector = "N/A"

    try:
        job_type = driver.find_element(By.XPATH, "//span[@data-automation='job-detail-work-type']").text
        job_type = clean_text(job_type)
    except:
        job_type = "N/A"
    
    try:
        salary = driver.find_element(By.XPATH, "//span[@data-automation='job-detail-salary']").text
        salary = clean_text(salary)
    except:
        salary = "N/A"

    try:
        responsibilities = driver.find_element(By.XPATH, "//div[@data-automation='jobAdDetails']").text
        responsibilities = clean_text(responsibilities)  # Convert to one row and normalize
    except:
        responsibilities = "N/A"

    return {
        "Job Title": title,
        "Company Name": company,
        "Location": location,
        "Sector": sector,
        "Job Type": job_type,
        "Salary": salary,
        "Job Responsibilities": responsibilities,
        "URL Link": job_url  # Store the job URL
    }

print("\n🚀 Scraping job details...\n")
for index, job_url in enumerate(job_urls):
    job_details = extract_job_details(job_url)
    job_data.append(job_details)

    print(f"✅ {index+1}/{len(job_urls)} - Scraped: {job_details['Job Title']} at {job_details['Company Name']}")
    print(f"🔗 Job URL: {job_url}")
    print("Scraped Successfully!!\n")

# Save data to CSV
df = pd.DataFrame(job_data)
df.to_csv("Dataset/Jobstreet/AI_Engineer_sample.csv", index=False, encoding='utf-8-sig')
print(f"\n🎉 All Data Scraped Successfully!! Total: {len(job_data)} jobs.")
print("📁 Data saved Successfully")

# Close browser
driver.quit()