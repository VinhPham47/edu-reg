import re
import nodriver as uc
from faker import Faker
import random
import string
import requests

BASE_URL = 'https://tempmail.id.vn/api'
TOKEN = 'tempmail_token'  # Replace with your actual token
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Define character pools
uppercase = string.ascii_uppercase
lowercase = string.ascii_lowercase
digits = string.digits
special_chars = "~!@#$%&*"

def generate_username(length=9):
    # Create a string with all uppercase, lowercase letters and digits
    characters = string.ascii_letters + string.digits
    # Randomly choose characters from the available characters
    username = ''.join(random.choice(characters) for _ in range(length))
    return username

def generate_password(user_name="", length=12):
    # Ensure minimum length
    if length < 8:
        raise ValueError("Password must be at least 8 characters long.")

    while True:
        categories = {
            'upper': random.choice(uppercase),
            'lower': random.choice(lowercase),
            'digit': random.choice(digits),
            'special': random.choice(special_chars),
        }

        # Randomly pick 3 out of 4 character types
        chosen_types = random.sample(list(categories.keys()), 3)

        # Start the password with one char from each chosen category
        password_chars = [categories[typ] for typ in chosen_types]

        # Fill the rest with a mix of all characters
        all_chars = ''
        if 'upper' in chosen_types: all_chars += uppercase
        if 'lower' in chosen_types: all_chars += lowercase
        if 'digit' in chosen_types: all_chars += digits
        if 'special' in chosen_types: all_chars += special_chars

        remaining_length = length - len(password_chars)
        password_chars += random.choices(all_chars, k=remaining_length)
        random.shuffle(password_chars)
        password = ''.join(password_chars)

        # Check if the password contains part of the user's name
        if user_name.lower() not in password.lower():
            return password

def list_messages(mail_id):
    response = requests.get(f"{BASE_URL}/email/{mail_id}", headers=HEADERS)
    return response.json()

def read_message(message_id):
    response = requests.get(f"{BASE_URL}/message/{message_id}", headers={'Authorization': f'Bearer {TOKEN}'})
    return response.json()

def delete_email(mail_id):
    response = requests.delete(f"{BASE_URL}/email/{mail_id}", headers={'Authorization': f'Bearer {TOKEN}'})
    return response.status_code == 200

def create_email(user=None, domain=None):
    payload = {}
    if user and domain:
        payload = {
            "user": user,
            "domain": domain
        }
    response = requests.post(f"{BASE_URL}/email/create", headers=HEADERS, json=payload)
    return response.json()

def extractCode(data_dict):
    try:
        # Access the body field from the dictionary
        body = data_dict['data']['body']
        
        # Use regex to find the application code (a sequence of digits between <strong> tags)
        match = re.search(r'<strong>(\d+)</strong>', body)
        
        if match:
            code = match.group(1)
            return code
        else:
            # Fallback to check for <b> tags in case the format changes
            match_b = re.search(r'<b>(\d+)</b>', body)
            if match_b:
                return match_b.group(1)
            return "No code found in the email body"
            
    except KeyError as e:
        return f"Error accessing key in the dictionary: {str(e)}"

def fake_profile(locale='en_US'):
    fake = Faker(locale)

    profile = {
        # Personal
        "first_name":fake.first_name(),
        "last_name":fake.last_name(),
        "gender": fake.random_element(["Male", "Female"]),
        "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=30),
        "ssn": fake.ssn(),
        "phone": fake.phone_number(),

        # Address
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip": fake.zipcode(),

    }

    return profile

async def main():
    for _ in range(10):
        new_email = create_email(generate_username(), "tempmail.id.vn")

        email = new_email["data"]["email"]
        email_id = new_email["data"]["id"]
        print("temp mali:", email)
        print("mail id:", email_id)

        profile = fake_profile()
        profile2 = fake_profile()
        passwordGen = generate_password(profile["first_name"])
        print("password:", passwordGen)
        

        browser = await uc.start(
            user_data_dir="/",
            lang="en-US"
        )

        page = await browser.get('https://ss2.sfcollege.edu/sr/AdmissionApplication/#/citizenship#top')
        a = await page.find("United States")
        await a.click()

        a = await page.find("Next")
        await a.click()

        a = await page.find("First Time in College")
        await a.click()

        a = await page.find("Next")
        await a.click()

        a = await page.find("No Diploma")
        await a.click()

        a = await page.find("Next")
        await a.click()

        a = await page.find("input[id=fstNameSTR]")
        await a.send_keys(profile["first_name"])

        a = await page.find("input[id=lstNameSTR]")
        await a.send_keys(profile["last_name"])

        a = await page.find("select[id=month]")
        await a.send_keys(profile["birthdate"].strftime('%b'))

        a = await page.find("select[id=day]")
        await a.send_keys(str(profile["birthdate"].strftime("%d")))

        a = await page.find("select[id=year]")
        await a.send_keys(str(profile["birthdate"].year))

        a = await page.find("input[name=emailAddrsSTR]")
        await a.send_keys(email)

        a = await page.find("input[name=cemailAddrsSTR]")
        await a.send_keys(email)

        a = await page.find("select[name=birthctrySTR]")
        await a.send_keys("United States Of America")

        a = await page.find("input[id=ssn]")
        await a.send_keys(profile["ssn"])

        a = await page.find("input[id=ssnC]")
        await a.send_keys(profile["ssn"])

        a = await page.find("label[for=ssnNoticeCB]")
        await a.click()

        a = await page.find("Next")
        await a.click()

        print("wait for 35 seconds...")

        await page.sleep(35)
        messages = list_messages(email_id)
        readMsg = read_message(messages["data"]["items"][0]["id"])
        code = extractCode(readMsg)
        print("verify code:", code)

        a = await page.find("input[id=tokenInput]")
        await a.send_keys(str(code))

        a = await page.find("Next")
        await a.click()

        a = await page.find("input[id=psdSTR]")
        await a.send_keys(str(passwordGen))

        a = await page.find("input[id=cpsdSTR]")
        await a.send_keys(str(passwordGen))

        a = await page.find("Next")
        await a.click()

        a = await page.find("Create Account")
        await a.click()

        studentId = await page.find("strong[class=ng-binding]")
        print(studentId.text)

        a = await page.find("Continue Your Application")
        await a.click()

        a = await page.find("select[name=countryCdSTR]")
        await a.send_keys("United States Of America")

        a = await page.find("input[id=street-name]")
        await a.send_keys(str(profile["street"]))

        a = await page.find("input[id=city-name]")
        await a.send_keys(str(profile["city"]))


        a = await page.find("select[name=stateCdSTR]")
        await a.send_keys(str(profile["state"]))

        a = await page.find("input[id=zip-cd]")
        await a.send_keys(str(profile["zip"]))

        a = await page.find("input[id=primary-phone]")
        await a.send_keys(str(profile["phone"]))

        a = await page.find("input[id=emergency-phone]")
        await a.send_keys(str(profile2["phone"]))

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("label[for=same-curr-add]")
        await a.click()

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("input[id=first-name]")
        await a.send_keys(str(profile2["first_name"]))

        a = await page.find("input[id=last-name]")
        await a.send_keys(str(profile2["last_name"]))

        a = await page.find("select[id=relationship]")
        await a.send_keys("Parent")

        a = await page.find("label[for=samePermAdd]")
        await a.click()

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("select[name=hsCountryNamSTR]")
        await a.send_keys("United States Of America")

        a = await page.find("select[name=hsStateNamSTR]")
        await a.send_keys(str(profile["state"]))

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("select[name=firstTermCdSTR]")
        await a.send_keys("Fall")

        a = await page.find("select[name=firstYrNumSTR]")
        await a.send_keys("2025")

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("select[name=degreeSelect]")
        await a.send_keys("Adult Basic Education")

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        await page.sleep(1)


        a = await page.find("Yes")
        await a.click()

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        await page.sleep(1)

        a = await page.find("label[for=disciplinaryViolenceIndNo]")
        await a.click()

        await page.sleep(1)

        a = await page.find_all("button[type=submit]")# button[type=submit]
        await a[2].click()


        a = await page.find("select[name=educationSelect1]")
        await a.send_keys("Unknown")

        a = await page.find("select[name=educationSelect2]")
        await a.send_keys("Unknown")

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("select[name=statusSelect]")
        await a.send_keys("No Military History")

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        a = await page.find("select[name=genderCdSTR]")
        await a.send_keys(str(profile["gender"]))

        a = await page.find("select[id=ethnicity]")
        await a.send_keys("Prefer not to answer")

        a = await page.find("label[for=white]")
        await a.click()

        await page.sleep(1)

        a = await page.find("Next")
        await a.click()

        await page.sleep(1)

        a = await page.find("Agree and Submit")
        await a.click()


        a = await page.find("Continue")
        await a.click()
        
        with open("info.txt", "a") as f:
            f.write(f"{email}\n{email_id}\n{studentId.text}\n{passwordGen}\n---------------\n")

        print("Done!\n----------------")

        await page.close()

if __name__ == '__main__':
    uc.loop().run_until_complete(main())
    # input("Enter to exit...")
