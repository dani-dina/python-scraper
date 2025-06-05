import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re

CHROME_DRIVER_PATH = r"C:\Users\Kibret\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
LOGIN_URL = "https://Login"
MEMBER_DIR_URL = "https://"
USERNAME = ""
PASSWORD = ""
OUTPUT_TXT_FILE = "name_address_map.txt"

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=options)

def login(driver):
    print("[Login] Logging in...")
    driver.get(LOGIN_URL)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dnn_ctr463_Login_txtUsername"))).send_keys(USERNAME)
    driver.find_element(By.ID, "dnn_ctr463_Login_txtPassword").send_keys(PASSWORD)
    driver.find_element(By.ID, "dnn_ctr463_Login_cmdLogin").click()
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dnn_dnnSEARCH_txtSearch")))
    print("[Login] Success!")

def get_country_options(driver):
    print("[Info] Fetching country list...")
    driver.get(MEMBER_DIR_URL)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, "@IP_COUNTRY")))
    select = Select(driver.find_element(By.NAME, "@IP_COUNTRY"))
    countries = []
    for option in select.options:
        value = option.get_attribute("value")
        text = option.text.strip()
        if value and value != "[ALL]":
            countries.append((value, text))
    print(f"[Info] Total countries to scrape: {len(countries)}")
    return countries

def parse_result_count(text):
    match = re.search(r'(\d+)-(\d+) of (\d+)', text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 0, 0, 0

def scrape_name_address_map(driver, country_code, country_name, index, total):
    print(f"\n[Scrape] [{index}/{total}] Scraping '{country_name}'...")
    driver.get(MEMBER_DIR_URL)
    wait = WebDriverWait(driver, 30)

    try:
        try:
            more_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "More Search Options")))
            more_btn.click()
            time.sleep(1)
        except:
            pass

        Select(wait.until(EC.element_to_be_clickable((By.NAME, "@IP_COUNTRY")))).select_by_value(country_code)
        wait.until(EC.element_to_be_clickable((By.ID, "dnn_ctr2729_DNNWebControlContainer_ctl00_btnSubmitBtn"))).click()
        time.sleep(2)

        if "Sorry, no results were found" in driver.page_source:
            print("[Warning] No members found.")
            return {}

        all_html = driver.page_source
        while True:
            try:
                result_count_div = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.membership-dir-resultcount"))
                )
                text = result_count_div.text.strip()
                _, end, total_results = parse_result_count(text)
                if end >= total_results:
                    break

                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "dnn_ctr2729_DNNWebControlContainer_ctl00_Next"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                next_btn.click()
                time.sleep(2)
                all_html += driver.page_source
            except Exception:
                break

        soup = BeautifulSoup(all_html, "html.parser")
        containers = soup.select("div.membership-dir-result-details-container")
        name_address_map = {}

        for container in containers:
            name_div = container.select_one("div.LABEL_NAME")
            address_div = container.select_one("div.membership-dir-result-detail.DISPLAY_LINE_1")  # Updated line
            if name_div and address_div:
                name = name_div.get_text(strip=True)
                address = address_div.get_text(strip=True)
                name_address_map[name] = address

        print(f"[Success] {len(name_address_map)} members found in {country_name}")
        return name_address_map

    except Exception as e:
        print(f"[Error] While processing {country_name}: {e}")
        traceback.print_exc()
        return {}

def save_incremental(name_address_map):
    with open(OUTPUT_TXT_FILE, "a", encoding="utf-8") as f:
        for name, addr in name_address_map.items():
            f.write(f'    {repr(name)}: {repr(addr)},\n')
        f.flush()

def main():
    driver = None
    collected_count = 0
    try:
        driver = initialize_driver()
        login(driver)
        countries = get_country_options(driver)

        # Start new file
        with open(OUTPUT_TXT_FILE, "w", encoding="utf-8") as f:
            f.write("name_address_map = {\n")

        for index, (code, name) in enumerate(countries, start=1):
            try:
                country_map = scrape_name_address_map(driver, code, name, index, len(countries))
                if country_map:
                    save_incremental(country_map)
                    collected_count += len(country_map)
            except KeyboardInterrupt:
                print("\n[Exit] Manually stopped. Finalizing save...")
                break
            except Exception as e:
                print(f"[Error] Skipping {name}: {e}")
                traceback.print_exc()

        with open(OUTPUT_TXT_FILE, "a", encoding="utf-8") as f:
            f.write("}\n")

        print(f"\n[Done] Saved {collected_count} total entries to '{OUTPUT_TXT_FILE}'.")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
