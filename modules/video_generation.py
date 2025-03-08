from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random
import os

# ================== Set up WebDriver ==================

def get_driver(download_dir="output/video_outputs"):
    options = webdriver.ChromeOptions()
    
    # Set Chrome preferences to download without prompt
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Stealth mode to avoid bot detection
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Uncomment for GitHub Actions

    driver = webdriver.Chrome(options=options)
    return driver

# ================== Login Function ==================

def login(driver, email, password):
    driver.get("https://pixverse.ai/login")
    time.sleep(3)

    # Enter email
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email or Username']"))
    ).send_keys(email)

    # Enter password
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
    ).send_keys(password + Keys.RETURN)
    
    time.sleep(5)  # Allow login to process

# ================== Check Available Credits ==================

def get_credits(driver):
    try:
        credit_element = driver.find_element(By.XPATH, "//span[@class='text-sm text-text-warning']")
        credits = int(credit_element.text.strip().split(" ")[0])  # Extract number
        return credits
    except:
        return 0  # Default to 0 if not found

# ================== Upload Image & Generate Video ==================

def generate_video(driver, image_path, model):
    driver.get("https://pixverse.ai/create")
    time.sleep(3)

    # Upload image
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    ).send_keys(image_path)
    time.sleep(5)

    # Enter prompt
    prompt = "A cinematic sci-fi scene with a futuristic city and flying cars."
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Describe the content you want to create']"))
    ).send_keys(prompt)
    time.sleep(2)

    # Select model if needed
    if model == "V4":
        driver.find_element(By.XPATH, "//button[text()='V4']").click()
        time.sleep(2)

    # Click Generate
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Generate']"))
    ).click()
    
    time.sleep(60)  # Wait for video generation

# ================== Download Video ==================

def download_video(driver, output_folder, expected_filename):
    # Click the download button
    download_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Download')]"))
    )
    download_button.click()
    
    # Wait for the file to appear in the output folder
    video_path = os.path.join(output_folder, expected_filename)
    timeout = 60  # Wait up to 60 seconds for download
    start_time = time.time()

    while time.time() - start_time < timeout:
        if os.path.exists(video_path):
            print(f"Downloaded video: {video_path}")
            return video_path
        time.sleep(1)

    print("Download timed out or failed.")
    return None

# ================== Logout Function ==================

def logout(driver):
    driver.get("https://pixverse.ai/logout")
    time.sleep(3)
    
# ================== Main Automation Loop ==================

def video_generation(sh):
    sheet = sh.worksheet("accounts")
    accounts = sheet.get_all_records()  # Read all accounts from the sheet

    INPUT_FOLDER = "output/image_outputs"  # Change this to the actual path
    OUTPUT_FOLDER = "output/video_outputs"  # Change this to the actual path

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    images = [f for f in os.listdir(INPUT_FOLDER) if f.endswith((".png", ".jpg", ".jpeg"))]
    
    if not images:
        print("No images found in the input folder.")
        return
    
    for image in images:
        image_path = os.path.join(INPUT_FOLDER, image)
        print(f"Processing image: {image_path}")
        
        for account in accounts:
            email = account["username"]
            password = account["password"]

            driver = get_driver()  # Start browser

            try:
                login(driver, email, password)
                credits_available = get_credits(driver)

                # Use V4 if credits are below 30
                model = "V4" if credits_available < 30 else "V5"
                
                generate_video(driver, image_path, model)

                print(f"Completed video generation for {email}, switching account...")

                video_filename = image.replace(".png", ".mp4").replace(".jpg", ".mp4").replace(".jpeg", ".mp4")
                video_path = download_video(driver, OUTPUT_FOLDER, video_filename)

                if video_path:
                    print(f"Video saved: {video_path}")
                else:
                    print("Failed to download video.")

            except Exception as e:
                print(f"Error: {e}")

            finally:
                logout(driver)
                driver.quit()
                time.sleep(random.randint(10, 30))  # Random delay before switching accounts
