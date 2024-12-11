import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime,timedelta
from seleniumbase import Driver
from bs4 import BeautifulSoup
import re
import json,csv
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
load_dotenv()

class WhatsAppScrape:
    starting_key=0
    older_message_days = int(os.getenv("DAYS", 20))
    
    try:
        os.mkdir("Contacts")
    except:
        pass
    def _get_driver(self, is_headless=False):
        driver = Driver(uc=True, undetectable=True, user_data_dir="chrome")
        return driver
    
    
    def Runner(self):
        print("")
        print("*"*50)
        print("")
        print(">> WhatsApp Web Scraper")
        print(">> Starting WhatsApp Web Scraper")
        print(">> Make sure old instance of chrome is closed, if scraper not opening web.whatsapp.com then close all chrome instances, and restart the script.")
        print(f">> Extracting message from last {self.older_message_days} days.")
        print("")
        print("*"*50)
        driver = self._get_driver()
        driver.get("https://web.whatsapp.com/")
        driver.maximize_window()
        WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='listitem']"))
    )
        
        Messages = self.load_existing_messages()
        extracted_contact = []
        last_contact = None
        
        contact_skip_count = 0
        while True:
            visible_contacts = driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")
            list_vise = []
            count=0
            names = [f.text for f in visible_contacts]
            
            # Stop if no new contacts are visible for 10 iterations
            if last_contact == names:
                contact_skip_count += 1
            else:
                contact_skip_count = 0
            if contact_skip_count >= 10:
                break
            last_contact = names
            
            for contact in self._get_visible_element(driver,visible_contacts):
                old_messages_list = []
                self.starting_key = 3
                contact = contact[2]
                try:
                    soup = BeautifulSoup(contact.get_attribute("innerHTML"), "html.parser")
                    user_group_name = soup.find(attrs={"role": "gridcell"}).find("div").text
        
                    #user_group_name = soup.find_all("span")[1].text
                    
                    if "default" in user_group_name:
                        user_group_name = soup.find_all("span")[0].text
                        
                    if user_group_name in extracted_contact:
                        continue
                    try:
                        contact.click()
                    except:
                        continue
                    print(f">> Extracting messages from: {user_group_name}")
                    time.sleep(2)
                    extracted_contact.append(user_group_name)
                    # Track current chats and their content
                    current_chats = []
                    old_content_count = 0
                    scroll_attempts = 0

                    while True:
                        # Scroll the chat window
                        try:
                            el = driver.find_element(By.CSS_SELECTOR,"[role='application']")
                            el.send_keys(Keys.HOME) 
                        except:
                            pass
                        
                        message_elements = driver.find_element(By.CSS_SELECTOR, "[role='application']").find_elements(By.CSS_SELECTOR, "[role='row']")
                        message_count = len(message_elements)
                        if old_content_count == message_count:
                            scroll_attempts += 1
                        else:
                            scroll_attempts = 0
                        old_content_count = message_count

                        # Break scrolling if no new messages are found after multiple attempts
                        if scroll_attempts >= 30:
                            break

                        # Extract the message timestamp and compare
                        co = 0
                        date_time_object = self.get_last_read_stamp("Unknown")
                        try:
                            element = driver.find_element(By.XPATH, "//*[text()='Click here to get older messages from your phone.']")
                            element.click()
                        except Exception as e:
                            pass
                        # while True:
                        #     try:
                        #         try:
                        #             last_message = message_elements[0]
                        #             date_time_string, date_time_object = self.get_read_date(last_message)
                        #         except:
                        #             last_message = message_elements[1]
                        #             date_time_string, date_time_object = self.get_read_date(last_message)
                        #         break
                        #     except:
                        #         break
                        last_read_timestamp = self.get_last_read_stamp(user_group_name)
                        # if date_time_object < last_read_timestamp:
                        #     break  # Stop scrolling if messages are old
                        el = driver.find_element(By.CSS_SELECTOR, "[role='application']")
                        time.sleep(0.4)
                    
                        # Handle "Click here to get older messages from your phone."
                        err = 0
                        try:
                            element = driver.find_element(By.XPATH, "//*[text()='Click here to get older messages from your phone.']")
                            element.click()
                            time.sleep(1)
                        except Exception as e:
                            pass
                        old_messages_list = []
                        
                        try:
                            first_message = message_elements[0]
                            is_custom_time_filter = self.is_custom_time_filter(self.older_message_days,self._get_message_content(first_message.get_attribute("innerHTML"))["datetime"])
                            if is_custom_time_filter == "yes":
                                break
                        except Exception as e:
                            pass
                        
                        try:
                            last_message = message_elements[-1]
                            old_messages_list.append(self._get_message_content(last_message.get_attribute("innerHTML")))
                        except Exception as e:
                            pass
                        if old_messages_list:
                            old_messages_list.sort(key=lambda x: x["datetime"])
                            try:
                                date_object = datetime.strptime(old_messages_list[-1]["datetime"], "%Y-%m-%dT%H:%M:%S")
                            except:
                                try:
                                    date_object = datetime.strptime(old_messages_list[-1]["datetime"], "%m/%d/%Y %H:%M")
                                except:
                                    date_object = datetime.strptime(old_messages_list[-1]["datetime"], "%d/%m/%Y %I:%M %p")
                            if date_object <= last_read_timestamp:
                                print(f">> Messages are up to date for {user_group_name}.")
                                break  # Stop scrolling if messages are old
                            
                    # Extract message content
                    for html in driver.find_element(By.CSS_SELECTOR, "[role='application']").find_elements(By.CSS_SELECTOR, "[role='row']"):
                        try:
                            current_chats.append(self._get_message_content(html.get_attribute("innerHTML")))
                        except:
                            pass

                    # Append messages to the list and update the last read timestamp
                    if current_chats:
                        
                        filepath = os.path.join(os.getcwd(),"Contacts",self.sanitize_filename(user_group_name)+".csv")
                        found = False
                        
                        try:
                            for c in range(len(Messages)):
                                if Messages[c]["Contact"]==user_group_name:
                                    found = c
                                    break
                        except:
                            pass
                        
                        if not found:
                            Messages.append({"Contact": user_group_name, "messages": current_chats})
                        else:
                            Messages[found]["messages"].extend(current_chats)
                        
                        if found:
                            unique_messages = [json.dumps(msg) for msg in Messages[found]["messages"]]  # Convert to a list of strings
                            unique_messages = list(set(unique_messages))  # Remove duplicates
                            # Convert back to a list of dictionaries
                            unique_messages = [json.loads(msg) for msg in unique_messages]
                            unique_messages.sort(key=lambda x: x["datetime"])  # Sort by datetime
                            Messages[found]["messages"] = unique_messages
                            self.save_to_csv(Messages[found]["messages"],filepath)
                            print(f">> Messages updated for {user_group_name}.")
                        else:
                            self.save_to_csv(current_chats,filepath)
                        last_message = current_chats[-1]  # Get the last message in the list
                        date_time_string, date_time_object = self.get_read_date(last_message,False)
                        self.up_date_last_read_stamp(user_group_name, date_time_object)
                        self.save_messages(Messages)
                except Exception as e:
                    continue
            # Scroll the main contact list
            el = driver.find_element(By.ID, "pane-side").find_element(By.CSS_SELECTOR, "div")
            el.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)
        # Save messages to JSON
        
        self.save_messages(Messages)
        print(">> All Message extraction complete.")
        try:
            driver.quit()
        except:
            pass
    
    def is_custom_time_filter(self,days=60,custom_date_str="2024-11-25T01:27:00"):
        # Calculate the date 'days' ago
        today = datetime.today()
        past_date = today - timedelta(days=days)  # Date 'days' ago

        # Parse the custom date
        try:
            custom_date_object = datetime.strptime(custom_date_str, "%Y-%m-%dT%H:%M:%S")
        except:
            try:
                custom_date_object = datetime.strptime(custom_date_str, "%m/%d/%Y %H:%M")
            except:
                try:
                    custom_date_object = datetime.strptime(custom_date_str, "%d/%m/%Y %I:%M %p")
                except:
                    custom_date_object = datetime.strptime(custom_date_str, "%Y-%m-%d")
        
        # Check if the custom date is older than 'days' ago
        return "yes" if custom_date_object < past_date else "good"
        
    
    def _get_message_content(self,html):
        soup = BeautifulSoup(str(html),"html.parser")
        msg = soup.find(class_="selectable-text").text
        data =soup.find(class_="copyable-text").get_attribute_list("data-pre-plain-text")[0]
        date_time, user = data.split("]")
        mdate = date_time.split(",")[1].strip()
        mtime = date_time.split(",")[0].split("[")[-1]
        mdate,mtime,user.replace(":","").strip(),msg
        datetime_string = f"{mdate} {mtime}"
        try:
            datetime_object = datetime.strptime(datetime_string, '%d/%m/%Y %I:%M %p')
        except:
            datetime_object = datetime.strptime(datetime_string, '%m/%d/%Y %H:%M')
        return {"user":user.replace(":","").strip(),"message":msg,"time":mtime,"date":mdate,"datetime":datetime_object.isoformat()}  
    
    
    def _get_visible_element(self,driver,visible_contacts):
        visible_elements = []
        
        # Get the size of the viewport (height)
        viewport_height = driver.execute_script("return window.innerHeight")
        
        # Loop through the elements and check if they are visible in the viewport
        for count, item in enumerate(visible_contacts):
            try:
                # Use JavaScript to get the bounding box and visibility status
                rect = driver.execute_script("""
                    var elem = arguments[0];
                    var rect = elem.getBoundingClientRect();
                    return {
                        top: rect.top,
                        bottom: rect.bottom,
                        left: rect.left,
                        right: rect.right,
                        height: rect.height,
                        width: rect.width
                    };
                """, item)
                
                # Check if the element is within the visible part of the viewport
                top = rect['top']
                bottom = rect['bottom']
                
                # If the element is within the viewport (even partially)
                if bottom > 0 and top < viewport_height:
                    visible_elements.append([count, top, item])
        
            except Exception as e:
                continue
        
        # If no elements are visible, print a message
        if not visible_elements:
            print("No visible elements found.")
        
        # Sort the visible elements by their 'top' position (from top to bottom)
        visible_elements.sort(key=lambda x: x[1])
        
        return visible_elements
    
    def save_to_csv(self,data,filepath="test.csv"):
        with open(filepath, mode='w', newline='',encoding='utf-8') as file:
            # Get the fieldnames from the keys of the first dictionary
            fieldnames = data[0].keys()
            
            # Create a DictWriter object and write the header
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write the rows
            writer.writerows(data)
            
    def sanitize_filename(self,text):
        # Define the invalid characters for Windows and Linux
        # Windows invalid characters: \ / : * ? " < > |
        # Linux/macOS invalid characters: /
        invalid_chars = r'[\\/*?:"<>|/]'

        # Replace invalid characters with an underscore (_)
        sanitized = re.sub(invalid_chars, '_', text)
        
        # Optionally, remove leading/trailing spaces and check length limits
        sanitized = sanitized.strip()
        
        # Optionally, you can ensure the filename is not too long (e.g., 255 characters)
        # if len(sanitized) > 255:
        #     sanitized = sanitized[:255]
        
        return sanitized    
    
    def up_date_last_read_stamp(self,key, datetime_object):
        # print(key,datetime_object)
        
        try:
            with open("last_read.json", "r") as d:
                data = json.load(d)
        except FileNotFoundError:
            data = {}

        data[key] = datetime_object.isoformat()

        # Write back to file
        with open("last_read.json", "w") as d:
            json.dump(data, d)
            
    def get_last_read_stamp(self,key):
        try:
            with open("last_read.json", "r") as d:
                data = json.load(d)
            return datetime.fromisoformat(data.get(key, "1970-01-01T00:00:00"))
        except (FileNotFoundError, ValueError):
            return datetime.fromisoformat("1970-01-01T00:00:00")  # Default to epoch time if not found
        
    def get_read_date(self,last_message,bl=True):
        if bl:
            # input(last_message)
            last_message = self._get_message_content(last_message.get_attribute("innerHTML"))
        t = last_message["time"]
        d = last_message["date"]
        datetime_string = f"{d} {t}"
        try:
            datetime_object = datetime.strptime(datetime_string, '%d/%m/%Y %I:%M %p')
        except:
            datetime_object = datetime.strptime(datetime_string, '%m/%d/%Y %H:%M')
        return datetime_object.isoformat(), datetime_object
    
    def load_existing_messages(self):
        try:
            with open("messages.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        
    def save_messages(self,messages):
        with open("messages.json", "w") as f:
            json.dump(messages, f, indent=4)
            
        
        
if __name__=="__main__":
    w = WhatsAppScrape()
    w.Runner()
