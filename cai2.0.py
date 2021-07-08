# from requests_html import HTML, HTMLSession
from selenium import webdriver
import telepot, gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from multiprocessing import Process
import creds

# start_time = time.perf_counter()

url = 'https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/submit-profile/rounds-invitations.html'

driver = webdriver.Chrome()
driver.get(url)

xpath_elements = [

    "//div[@class='mwsgeneric-base-html parbase section']/p[2]",
    "//div[@class='mwsgeneric-base-html parbase section']/p[4]",
    "//div[@class='mwsgeneric-base-html parbase section']/p[5]",
    "//div[@class='mwsgeneric-base-html parbase section']/p[6]",
    "//div[@class='mwsgeneric-base-html parbase section']/p[7]",
    "//div[@class='mwsgeneric-base-html parbase section']/p[8]"

]

def latest_reading():
    # session = HTMLSession()
    # r = session.get('https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/submit-profile/rounds-invitations.html')

    # sel = [ 'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(2) > strong',
    #         'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(4)', 
    #         'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(5)',
    #         'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(6)', 
    #         'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(7)', 
    #         'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(8)']

    # date_and_time_of_draw = 'body > main > div:nth-child(2) > div:nth-child(6) > p:nth-child(6)'


    date_and_time_of_draw = "//div[@class='mwsgeneric-base-html parbase section']/p[6]"

    invitations = []
    for i in xpath_elements:
        invitations.append(driver.find_element_by_xpath(i).text)

    invitations[1] = invitations[1].rsplit('Foo')
    invitations[1] = invitations[1][0]

    latest_reading.copy_of_invitations = invitations
    latest_reading.copy_of_invitations.insert(0, '')

    latest_reading.invitations = '\n'.join(invitations) #For message format in Telegram

    latest_reading.date_and_time_of_draw = driver.find_element_by_xpath(date_and_time_of_draw).text

def google_api():

    scope = ["https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"]

         

    google_creds = ServiceAccountCredentials.from_json_keyfile_dict(creds.keyfile_dict, scope)
    client = gspread.authorize(google_creds)

    google_api.sheet = client.open("Canada").worksheet('Invitations')

    google_api.numRows = len(google_api.sheet.get_all_records()) + 1 # Getting the count of existing rows so new reading could be appended in next row.
    google_api.previous_reading = google_api.sheet.row_values(google_api.numRows)

def main():
    
    # google_api() 
    if __name__ == '__main__':
        p1 = Process(target=latest_reading)   
        p2 = Process(target=google_api)

        p1.start()
        p2.start()

        # p1.join()
        # p2.join()
    
    # google_api() 

    if google_api.previous_reading[7] == latest_reading.date_and_time_of_draw:
        pass
    else:

        invitations2 = []
        for i in latest_reading.copy_of_invitations:
            if ':' in i:
                i = i.split(':') 
                i = i[1].strip(' ')
            else:
                i = i
            invitations2.append(i)
        
        invitations2[4] = invitations2[4].split('at')
        invitations2[4] = invitations2[4][0].strip(' ')

        invitations2.append(latest_reading.date_and_time_of_draw)

        google_api.sheet.insert_row(invitations2, google_api.numRows+1)
       
        bot = telepot.Bot(creds.TELEGRAM_BOT_PAM_ID) # calling Pam on Telegram
        bot.sendMessage(creds.TELEGRAM_MY_PERSONAL_ID, latest_reading.invitations) # my personal ID on telegram.        
        # bot.sendMessage(creds.TELEGRAM_VISHAL_ID, invitations) # Vishal's Telegram Chat ID

main()

# finish_time = time.perf_counter()

# print(round(finish_time - start_time, 2))