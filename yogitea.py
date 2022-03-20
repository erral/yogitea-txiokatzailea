# -*- coding: utf-8 -*-
import json
import os.path
import random

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from TwitterAPI import TwitterAPI

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1GOUUGRmhvmzrPT_Dpw7FHYsfXw70xEK2m37zE2XwuTQ"
SAMPLE_RANGE_NAME = "YogiTea!A:C"


def get_yogitea_text():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        tweetables = [row for row in values if len(row) == 2]
        row = random.choice(tweetables)

        range_ = "A{num}:C{num}".format(num=row[0])
        value_input_option = "RAW"
        value_range_body = {
            "values": [[row[0], row[1], "X"]],
        }
        # Mark as tweeted
        request = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range_,
                valueInputOption=value_input_option,
                body=value_range_body,
            )
        )
        response = request.execute()
        return row[1]

    except HttpError as err:
        print(err)


def translate_text(text):
    payload = {
        "mkey": "8d9016025eb0a44215c7f69c2e10861d",
        "model": "generic_en2eu",
        "text": text,
    }
    headers = {
        "Accept": "application/json",
        "Origin": "https://www.euskadi.eus",
    }
    response = requests.post(
        "https://api.euskadi.eus/itzuli/en2eu/translate",
        json=payload,
        headers=headers,
    )

    result = response.json()
    if result.get("success", None):
        return result.get("message", "")

    return ""


def tweet_text(text, original):
    text = "{text} #yogitea".format(text=text)
    original_text = "{text} #yogitea".format(text=original)

    with open("credentials.twitter.json") as fp:
        credentials = json.load(fp)

        api = TwitterAPI(
            credentials["API_KEY"],
            credentials["API_SECRET"],
            credentials["ACCESS_TOKEN_KEY"],
            credentials["ACCESS_TOKEN_SECRET"],
        )
        res = api.request("statuses/update", {"status": text})
        if res.response.ok:
            print('Tweeted: "{}"'.format(text))
            original_tweet_id = res.response.json().get("id")
            res = api.request(
                "statuses/update",
                {
                    "status": original_text,
                    "in_reply_to_status_id": original_tweet_id,
                },
            )
            if res.response.ok:
                print('Tweeted: "{}"'.format(original_text))


def main():
    text = get_yogitea_text()
    translated_text = translate_text(text)
    tweet_text(translated_text, text)


if __name__ == "__main__":
    main()
