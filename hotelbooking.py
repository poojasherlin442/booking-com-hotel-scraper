from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import smtplib
from email.message import EmailMessage
import mimetypes
import os
from email.utils import make_msgid

def send_email(df, mailid, image_files):
    sender = "REPLACE WITH SENDER EMAIL ID"
    app_password = "REPLACE with APP PASSWORD"  

    msg = EmailMessage()
    msg["Subject"] = "Hotel options for your trip"
    msg["From"] = sender
    msg["To"] = mailid

    html = """
    <html>
    <body>
        <p>Hi,</p>
        <p>Here are the hotel options matching your request:</p>
    """

    
    cids = [make_msgid(domain="hotelimage")[1:-1] for _ in range(len(df))]

    for (i, row), cid in zip(df.iterrows(), cids):
        html += f"""
        <hr>
        <h3>{i+1}. {row['Hotel Name']}</h3>
        <p>
            <b>Check-in:</b> {row['Check-in']}<br>
            <b>Check-out:</b> {row['Check-out']}
        </p>
        <img src="cid:{cid}" style="width:400px;"><br>
        """

    html += """
        <p>Regards,<br>Hotel Bot</p>
    </body>
    </html>
    """

    msg.set_content("Your email client does not support HTML.")
    msg.add_alternative(html, subtype="html")

    for img_path, cid in zip(image_files, cids):
        with open(img_path, "rb") as f:
            img_data = f.read()

        mime_type, _ = mimetypes.guess_type(img_path)
        maintype, subtype = mime_type.split("/")

        msg.get_payload()[1].add_related(
            img_data,
            maintype=maintype,
            subtype=subtype,
            cid=f"<{cid}>",
            filename=os.path.basename(img_path)
        )


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)

    print("Email sent with inline hotel images!")

    
    for img in image_files:
        os.remove(img)

import requests

def download_hotel_image(image_url, hotel_name, index):
    safe_name = hotel_name.replace(" ", "_").replace("/", "_")
    filename = f"hotel_{index}_{safe_name}.jpg"

    response = requests.get(image_url, timeout=20)
    response.raise_for_status()

    with open(filename, "wb") as f:
        f.write(response.content)

    return filename




df=pd.read_excel("input.xlsx")

driver=webdriver.Chrome()
wait = WebDriverWait(driver, 10)
for _,row in df.iterrows():

    location=row["Location"]
    price=row["Price"]
    mailid=row["Email"]

    driver=webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.booking.com/")
    driver.maximize_window()
    time.sleep(5)

    dismiss_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss sign-in info.']")))
    dismiss_btn.click()


    wait = WebDriverWait(driver, 10)

    search = wait.until(EC.element_to_be_clickable((By.NAME, "ss")))
    search.clear()
    search.send_keys(location)
    time.sleep(1)
    search.send_keys(Keys.ARROW_DOWN)
    search.send_keys(Keys.ENTER)

    search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Search']]")))
    search_btn.click()
    time.sleep(6)

    filter_by = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//h2[normalize-space()='Filter by:']")))
    filter_by.click()
    time.sleep(6)
    cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='property-card']")))
    main_tab=driver.current_window_handle
    extracted_count=0
    hotels_data=[]
    image_files=[]
    for i in range(len(cards)):
        if extracted_count == 3:
            break

        #cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='property-card']"))) 
        card = cards[i]
        link = card.find_element(By.XPATH, ".//a[@data-testid='title-link']")

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});",link)
        link.click()

    
        wait.until(lambda d: len(d.window_handles) > 1)

        new_tab = [h for h in driver.window_handles if h != main_tab][0]
        driver.switch_to.window(new_tab)

        
        wait = WebDriverWait(driver, 20)
        name = wait.until(EC.visibility_of_element_located((By.XPATH, "//h1 | //h2[contains(@class,'pp-header__title')]"))).text
        print(f"Hotel{i+1} - ", name)

        image_url = wait.until(EC.presence_of_element_located((By.XPATH, "(//img[contains(@src,'/xdata/images/hotel/')])[1]"))).get_attribute("src")
        img_path = download_hotel_image(image_url,name, extracted_count)
        image_files.append(img_path)

        house_rules = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-testid='Property-Header-Nav-Tab-Trigger-policies']")))
        house_rules.click()

        checkin_raw = wait.until(EC.presence_of_element_located((By.XPATH,"//div[normalize-space()='Check-in']/following::*[1]"))).text
        checkin_time = checkin_raw.split("\n")[0]
        print("Check-in time:", checkin_time)

        checkout_raw = wait.until(EC.presence_of_element_located((By.XPATH,"//div[normalize-space()='Check-out']/following::*[1]"))).text
        checkout_time=checkout_raw.split("\n")[0]
        print("Check-out time:", checkout_time,"\n")
        hotel = {
            "Hotel Name": name,
            "Check-in": checkin_time,
            "Check-out": checkout_time
        }

        hotels_data.append(hotel)



        driver.close()
        driver.switch_to.window(main_tab)

        extracted_count += 1
    df=pd.DataFrame(hotels_data)
    send_email(df,mailid,image_files)
    driver.quit()
