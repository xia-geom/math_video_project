import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. Load your Excel data
# Ensure your Excel has columns 'Permanent_Code' and 'Final_Grade'
df = pd.read_excel("grades_MAT0339.xlsx")

# 2. Setup the Browser
options = webdriver.ChromeOptions()
# Adding this to reduce 'bot' detection
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def enter_grades():
    driver.get("https://portail.uqam.ca") # Navigate to UQAM portal
    
    print("ACTION REQUIRED:")
    print("1. Log in manually to the UQAM portal.")
    print("2. Navigate to the grade entry page for MAT0339-30.")
    input("3. Once the grid is visible, press Enter here to start automation...")

    for index, row in df.iterrows():
        perm_code = str(row['Permanent_Code']).strip()
        grade = str(row['Final_Grade']).strip()

        try:
            # Finding the row based on the Permanent Code text
            # This is the 'Anchor' that prevents transcription errors
            xpath_expression = f"//tr[contains(., '{perm_code}')]//input[@type='text']"
            grade_input = driver.find_element(By.XPATH, xpath_expression)

            # Clear any existing value (like an accidental 68)
            grade_input.clear()
            
            # Type the new grade (like 91)
            grade_input.send_keys(grade)
            
            print(f"Success: Entered {grade} for {perm_code}")
            
            # Small delay to mimic human typing and avoid system lag
            time.sleep(0.5) 

        except Exception as e:
            print(f"Error: Could not find input for {perm_code}. Skipping...")

    print("\nAutomation complete. Please review the page before clicking 'Submit' on the website.")

if __name__ == "__main__":
    enter_grades()