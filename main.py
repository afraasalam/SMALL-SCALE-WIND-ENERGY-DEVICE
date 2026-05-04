from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector
import time
from datetime import datetime

# ✅ MySQL Connection (XAMPP)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # XAMPP default empty
    database="wind_db",
    port=3306
)

cursor = db.cursor()

# ✅ Start Browser
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def fetch_and_store():
    try:
        driver.get("https://iotwebserver.in/table.php?id=8pxthe76")
        time.sleep(5)

        rows = driver.find_elements(By.TAG_NAME, "tr")

        for row in rows[1:]:
            cols = row.find_elements(By.TAG_NAME, "td")

            if len(cols) >= 4:
                try:
                    voltage = float(cols[1].text.strip())
                    current = float(cols[2].text.strip())
                    time_str = cols[3].text.strip()

                    time_val = datetime.strptime(time_str, "%B %d %Y %H:%M")

                    # check duplicate
                    check_query = """
                    SELECT id FROM power_data 
                    WHERE voltage=%s AND current=%s AND time=%s
                    """
                    cursor.execute(check_query, (voltage, current, time_val))

                    if cursor.fetchone() is None:
                        insert_query = """
                        INSERT INTO power_data (voltage, current, time) 
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_query, (voltage, current, time_val))
                        db.commit()

                        print("Inserted:", voltage, current, time_val)

                except Exception as e:
                    print("Row Error:", e)

    except Exception as e:
        print("Page Error:", e)


# ✅ Run continuously
while True:
    fetch_and_store()
    time.sleep(10)
