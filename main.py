import os
import argparse
import re
import time
import random
import threading
from appium import webdriver
from selenium.webdriver.common.by import By

def get_target_urls():
    parser = argparse.ArgumentParser(description="Script to control devices and perform actions.")
    parser.add_argument('-url', nargs='+', required=True, help="List of target URLs.")
    args = parser.parse_args()
    return args.target_urls

def set_airplane_mode(device_udid):
    os.system(f"adb -s {device_udid} shell settings put global airplane_mode_on 1")
    time.sleep(5)  # Wait for a few seconds to observe the change
    os.system(f"adb -s {device_udid} shell settings put global airplane_mode_on 0")

def set_fake_location(device_udid, latitude, longitude):
    os.system(f"adb -s {device_udid} shell monkey -p com.lexa.fakegps -c android.intent.category.LAUNCHER 1")
    time.sleep(2)
    # Start the service to set the fake location
    os.system(f"adb -s {device_udid} shell am startservice -a com.lexa.fakegps.START -e lat {latitude} -e long {longitude}")

def clear_chrome_browsing_data(device_udid):
    # Stop Chrome
    os.system(f"adb -s {device_udid} shell am force-stop com.android.chrome")

    # Clear Chrome app data
    os.system(f"adb -s {device_udid} shell pm clear com.android.chrome")

class AppiumGoogleSearch:
    def __init__(self, driver, keywords, target_urls):
        self.driver = driver
        self.keywords = keywords
        self.target_urls = target_urls

    def perform_searches(self):
        while True:
            for keyword in self.keywords:
                time.sleep(random.randint(3, 6))
                search_url = f"https://www.google.com/search?q={keyword}"
                self.driver.get(search_url)
                time.sleep(random.randint(1, 4))
                divs = self.driver.find_elements(By.CSS_SELECTOR, "div[data-text-ad]")
                for div in divs:
                    try:
                        a = div.find_element(By.TAG_NAME, "a")
                        href = a.get_attribute("href")
                    except:
                        print("No link found")
                        continue
                    if any(pattern.search(href) for pattern in self.target_patterns):  # Use regex search
                        print(href)
                        try:
                            a.click()
                            time.sleep(random.randint(7, 12))
                        except:
                            print("No Clickable Link Found")
                        
                        time.sleep(2)

def run_browser_handler(device_udid, port):
    casablanca_bounds = {
        "latitude_min": 33.5174,
        "latitude_max": 33.6362,
        "longitude_min": -7.6875,
        "longitude_max": -7.5042
    }

    keywords = ["medecin a domicile casablanca", "medecin de nuit casablanca", "sos medecin casablanca", "docteur a domicile casablanca"]
    target_urls = get_target_urls()

    latitude = random.uniform(casablanca_bounds["latitude_min"], casablanca_bounds["latitude_max"])
    longitude = random.uniform(casablanca_bounds["longitude_min"], casablanca_bounds["longitude_max"])
    set_airplane_mode(device_udid)
    time.sleep(1)  # Optional: Wait for a second to observe the change
    set_fake_location(device_udid, latitude, longitude)
    time.sleep(1)  # Optional: Wait for a second to observe the change
    clear_chrome_browsing_data(device_udid)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("androidPackage", "com.android.chrome")
    
    capabilities = {
        "platformName": "Android",
        "deviceName": device_udid,
        "automationName": "UiAutomator2",
        "browserName": "Chrome",
        "chromeOptions": options
    }

    driver = webdriver.Remote(f"http://0.0.0.0:{port}/wd/hub", capabilities)
    searcher = AppiumGoogleSearch(driver, keywords, target_urls)
    searcher.perform_searches()
    driver.quit()

if __name__ == "__main__":
    device_udids = ['28e5d21f0504']  # Add more device UDIDs as needed
    server_ports = [4723, 4724]  # Corresponding ports for each device

    num_threads = len(device_udids)
    threads = []

    for device_udid, port in zip(device_udids, server_ports):
        thread = threading.Thread(target=run_browser_handler, args=(device_udid, port))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
