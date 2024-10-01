import requests
import os
import yaml
from utils import take_screenshot_of_app, load_yaml_config

# Load webhooks from config.yaml
def load_webhooks():
    config = load_yaml_config()
    return config['webhooks']

# Send message to Discord
def send_message_to_discord(message, noimage, win, debug):
    screenshot_path = None
    if not noimage:
        screenshot_path = take_screenshot_of_app("Trade Automation Tool", win)
    
    message_ids = []
    webhooks = load_webhooks()  # Load webhooks from config.json

    for webhook in webhooks:
        url = webhook["url"]
        thread_id = webhook.get("thread_id")
        if thread_id:
            url += f"?thread_id={thread_id}"

        payload = {"content": message}
        response = None  # Initialize response variable

        try:
            if screenshot_path and os.path.isfile(screenshot_path):
                with open(screenshot_path, "rb") as image_file:
                    files = {"file": (os.path.basename(screenshot_path), image_file)}
                    response = requests.post(url, data=payload, files=files)
            else:
                response = requests.post(url, data=payload)

            # Check if response is successful
            if response.status_code in [200, 204]:
                print(f"Message sent successfully to webhook: {url}")
                try:
                    response_data = response.json()
                    message_id = response_data.get('id')
                    print(f"Message ID: {message_id}")
                    message_ids.append(message_id)
                except ValueError:
                    print("Could not extract Message ID from the response.")
                    message_ids.append(None)
            else:
                print(f"Failed to send message to webhook {url}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                message_ids.append(None)

        except Exception as e:
            print(f"Exception occurred while sending message to webhook {url}: {e}")
            message_ids.append(None)

    return message_ids

# Delete messages from Discord
def delete_messages(message_ids):
    webhooks = load_webhooks()  # Load webhooks from config.json
    for msg_id in message_ids:
        url = f"{webhooks[0]['url']}/messages/{msg_id}"
        requests.delete(url)
