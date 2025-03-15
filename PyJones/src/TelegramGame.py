# Importing Necessary Libraries
import requests
import time
import json
import os

import google.generativeai as genai

from utils.Messages import WelcomeMessage

# Defining Bot Toekn, Set of Authorized Users and the Telegram HTTP Interface API URL
BOT_TOKEN = os.environ.get("TELEGRAM_API_KEY")
AUTHORIZED_USER_IDS = {497372480}  # Retrieve User ID by Sending a Message to userinfobot in Telegram
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'

GEMINI_TOKEN = os.environ.get("GOOGLE_API_KEY")

hasUserSarted = {}  # Track if User Has Started
hasAdventureStarted = {}

def get_updates(offset=None):
    url = API_URL + 'getUpdates'
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(url, params=params)
    return response.json()

def send_message(chat_id, text):
    url = API_URL + 'sendMessage'
    params = {'chat_id': chat_id, 'text': text}
    requests.post(url, params=params)

def handle_updates(updates):
    for update in updates['result']:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']

            if user_id in AUTHORIZED_USER_IDS:
                if 'text' in message:
                    text = message['text']

                    if user_id not in hasUserSarted:
                        if text != "/start":
                            send_message(chat_id, WelcomeMessage)

                        else:
                            hasUserSarted[user_id] = True
                            send_message(chat_id, "You've started.")
                
                    else:
                        if text == "/start":
                            send_message(chat_id, "Dawg you Already Started")

                        else:
                            #print(f"Message from {user_id} in {chat_id}: {text}")
            
                            if user_id not in hasAdventureStarted:
                                if text != "/begin":
                                    send_message(chat_id, WelcomeMessage)
                                else:
                                    hasAdventureStarted[user_id] = True
                                    send_message(chat_id, "Let's Start this Adventure!")
                            else:
                                if text == "/begin":
                                    send_message(chat_id, "Dawg the Adventure has Already Started")

                                else:
                                    client = genai.configure(api_key=GEMINI_TOKEN)
                                    model = genai.GenerativeModel("gemini-2.0-flash")
                                    response = model.generate_content(contents="Explain how AI works in simple terms")
                                    print( response.text)
                                    send_message(chat_id, response.text)



                                    print(f"Message from {user_id} in {chat_id}: {text}")
            else:
                send_message(chat_id, "You are not authorized to use this bot.")

def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates['result']:
            handle_updates(updates)
            offset = updates['result'][-1]['update_id'] + 1
        time.sleep(0.1)

if __name__ == '__main__':
    main()