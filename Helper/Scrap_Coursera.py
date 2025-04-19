from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Chrome options (Headless Mode)
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Fully headless mode
chrome_options.add_argument("--disable-gpu")  # Prevent GPU-related crashes
chrome_options.add_argument("--no-sandbox")  # Prevent sandbox issues
chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent memory-related crashes
chrome_options.add_argument("--log-level=3")  # Reduce logging noise

# Initialize WebDriver (Headless Mode)
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

number_of_samples = 100

url = "https://www.coursera.org/search?query=AI%20Engineer&sortBy=BEST_MATCH"
driver.get(url)
time.sleep(5)  # Allow page to load

print(f"Starting to scrape {number_of_samples} courses... (Running in background)")

data = []  
scroll_attempts = 0
max_scroll_attempts = 50  # Prevent infinite loop
last_height = driver.execute_script("return document.body.scrollHeight")

while len(data) < number_of_samples and scroll_attempts < max_scroll_attempts:
    # Find all course elements
    courses = driver.find_elements(By.XPATH, "//a[contains(@class, 'cds-CommonCard-titleLink')]")
    
    for course in courses:
        try:
            # Ensure valid course by checking if aria-label exists
            aria_label = course.get_attribute("aria-label")
            if not aria_label:
                continue  # Skip invalid elements

            course_name = course.text.strip()
            course_link = course.get_attribute("href")
            
            # Avoid duplicate courses
            if any(item["Course Link"] == course_link for item in data):
                continue

            try:
                image_url = course.find_element(By.XPATH, "./ancestor::li//img").get_attribute("src")
            except:
                image_url = "N/A"
            
            try:
                provider_image = course.find_element(By.XPATH, "./ancestor::li//img[contains(@src, 'coursera-university-assets')]").get_attribute("src")
            except:
                provider_image = "N/A"

            details = aria_label.split(", ")

            provider = details[0].split(" by ")[-1]  # Extract Provider Name
            rating_reviews = details[1] if len(details) > 1 else "N/A"
            
            # Extract the skills from the aria-label (skills come after "provide skills")
            if "provide skills" in aria_label:
                skills_section = aria_label.split("provide skills")[-1].strip()
                skills_gained = skills_section.split(",")  # Split skills by commas
                skills_gained = ", ".join([skill.strip() for skill in skills_gained]) 
            else:
                skills_gained = "N/A"
            # Remove everything starting from "etc..." and onwards
            if "etc..." in skills_gained:
                skills_gained = skills_gained.split("etc...")[0].strip()

            # If skills_gained is empty or only contains "etc...", set it to "N/A"
            if not skills_gained or skills_gained.lower() == "etc...":
                skills_gained = "N/A"

            level_duration = details[-1] if len(details) > 1 else "N/A"

            # Append course data
            data.append({
                "Course Name": course_name,
                "Provider": provider,
                "Skills Gained": skills_gained,
                "Rating & Reviews": rating_reviews,
                "Level & Duration": level_duration,
                "Course Image": image_url,
                "Provider Image": provider_image,  
                "Course Link": course_link
            })

            print(f"Data {len(data)} Scraped Successfully: {course_name}")

            # Stop if we have enough courses
            if len(data) >= number_of_samples:
                break

        except Exception as e:
            print(f"Error extracting data: {e}")

    # 🔥 Scroll in Small Steps Instead of Full Scroll**
    for i in range(5):  # Scroll 5 small steps to ensure full content loads
        driver.execute_script("window.scrollBy(0, 600);")  # Scroll down slightly
        time.sleep(1)

    # Wait for new elements to load
    time.sleep(2)

    # Check if new content is loaded
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        print("No more new courses detected. Stopping scroll.")
        break  # Stop scrolling if no new content appears

    last_height = new_height
    scroll_attempts += 1

# Convert to DataFrame and save as CSV
df = pd.DataFrame(data)
df.to_csv("./Dataset/Coursera/coursera_AI_Engineer.csv", index=False)

print(f"\nScraped {len(data)} courses successfully!! (Headless mode completed)")
print(df.head())  # Print first few rows to verify output

# Close the browser
driver.quit()