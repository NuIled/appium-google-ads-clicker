import tkinter as tk
from tkinter import messagebox
from appium import webdriver
import time
import random
import os
from selenium.webdriver.common.by import By
from appium.options.common.base import AppiumOptions
from selenium.webdriver.support import expected_conditions as EC
import subprocess

subprocess.check_call(['pip', 'install', '-r', 'req.txt'])

def grant_location_permission(device_id):
    package_name = 'com.android.chrome'
    adb_command = f'adb -s {device_id} shell pm grant {package_name} android.permission.ACCESS_FINE_LOCATION'
    os.system(adb_command)

def set_airplane_mode(device_udid):
    os.system(f"adb -s {device_udid} shell settings put global airplane_mode_on 1")
    time.sleep(3)
    os.system(f"adb -s {device_udid} shell settings put global airplane_mode_on 0")
    time.sleep(3)

def set_fake_location(device_udid, latitude, longitude):
    os.system(f"adb -s {device_udid} shell monkey -p com.lexa.fakegps -c android.intent.category.LAUNCHER 1")
    time.sleep(2)
    os.system(f"adb -s {device_udid} shell am startservice -a com.lexa.fakegps.START -e lat {latitude} -e long {longitude}")
    time.sleep(1)

def clear_chrome_browsing_data(device_udid):
    os.system(f"adb -s {device_udid} shell am force-stop com.android.chrome")
    os.system(f"adb -s {device_udid} shell pm clear com.android.chrome")

def check_license(license_key):
    url = "https://nuiled.github.io/licences/licenses.json"  # Replace with your GitHub Pages URL
    response = requests.get(url)
    if response.status_code == 200:
        valid_licenses = response.json().get("valid_licenses", [])
        return license_key in valid_licenses
    return False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Appium Automation GUI")

        # URL Entry
        self.label_url = tk.Label(root, text="Enter URL:")
        self.label_url.pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        # Keywords Entry
        self.label_keywords = tk.Label(root, text="Enter Keywords (separated by commas):")
        self.label_keywords.pack()
        self.keywords_entry = tk.Entry(root, width=50)
        self.keywords_entry.pack()

        # Device IDs and Platform Names Entry
        self.label_devices = tk.Label(root, text="Enter Device IDs and Platform Names (format: id1,platform1):")
        self.label_devices.pack()
        self.devices_entry = tk.Entry(root, width=50)
        self.devices_entry.pack()

        # Port Entry
        self.label_port = tk.Label(root, text="Enter Appium Server Port:")
        self.label_port.pack()
        self.port_entry = tk.Entry(root, width=50)
        self.port_entry.pack()
        # License Key Entry
        self.label_license_key = tk.Label(root, text="Enter License Key:")
        self.label_license_key.pack()
        self.license_key_entry = tk.Entry(root, width=50)
        self.license_key_entry.pack()

        # Run Button
        self.run_button = tk.Button(root, text="Run Automation", command=self.run_automation)
        self.run_button.pack()

        # Close Button
        self.close_button = tk.Button(root, text="Close", command=root.destroy)
        self.close_button.pack(pady=20)

    def run_automation(self):
        license_key = self.license_key_entry.get()

        if not check_license(license_key):
            messagebox.showerror("Error", "Invalid license key")
            return
    
        casablanca_bounds = {
            "latitude_min": 33.5174,
            "latitude_max": 33.6362,
            "longitude_min": -7.6875,
            "longitude_max": -7.5042
        }
        while True:
            latitude = random.uniform(casablanca_bounds["latitude_min"], casablanca_bounds["latitude_max"])
            longitude = random.uniform(casablanca_bounds["longitude_min"], casablanca_bounds["longitude_max"])
            devices = self.devices_entry.get()
            device_id, platform_name = devices.split(',')
            set_airplane_mode(device_id)
            set_fake_location(device_id, latitude, longitude)
            clear_chrome_browsing_data(device_id)
            grant_location_permission(device_id)
            time.sleep(1)  # Optional: Wait for a
            url = self.url_entry.get()
            keywords = self.keywords_entry.get().split(',')
            port = self.port_entry.get()

            if not url or not keywords or not devices or not port:
                messagebox.showerror("Error", "Please fill in all fields")
                return

            try:
                # device_id, platform_name = device.split(',')
                options = AppiumOptions()
                options.load_capabilities({
                    "platformName": platform_name,
                    "deviceName": device_udid,
                    "automationName": "UiAutomator2",
                    "autoGrantPermissions": "true",
                    "noReset": "true",
                    "browserName": "Chrome"
                    })

                driver = webdriver.Remote(f'http://127.0.0.1:{port}/wd/hub', options=options)
                try:
                    driver.get("https://www.google.com/search?q=bank+atm+near+me&oq=atmnear")
                    time.sleep(2)
                    driver.find_element(By.XPATH,'//omnient-visibility-control/div/div/div/div[2]/div/update-location').click()
                    driver.switch_to.context("NATIVE_APP")
                    time.sleep(5)
                    driver.find_element(By.XPATH,'//android.widget.Button[@resource-id="com.android.chrome:id/positive_button"]').click()
                except Exception as e:
                    print(e)
                    pass
                driver.switch_to.context("CHROMIUM")
                for keyword in keywords:
                    time.sleep(random.randint(3, 6))
                    search_url = f"https://www.google.com/search?q={keyword}"
                    driver.get(search_url)
                    time.sleep(random.randint(3, 8))
                    divs = driver.find_elements(By.CSS_SELECTOR, "div[data-text-ad]")
                    for div in divs:
                        try:
                            a = div.find_element(By.TAG_NAME, "a")
                            href = a.get_attribute("href")
                            print(href)
                            if url in href:
                                try:
                                    a.click()
                                    time.sleep(random.randint(3, 8))
                                except:
                                    print("No Clickable Link Found")
                        except:
                            print("No link found")

                    time.sleep(5)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred with device {device_id}: {e}")
                driver.quit()

        messagebox.showinfo("Success", "Automation completed successfully")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    
