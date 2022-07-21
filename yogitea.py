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
            # creds = flow.run_local_server(port=0)
            creds = flow.run_console()

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


def translate_text_itzuli_eus(text):
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


def translate_text_elia_eus(text):
    session = requests.Session()
    data = session.get("https://elia.eus")
    payload = {
        "source_language": "en",
        "input_text": text,
        "translation_engine": "1",
        "target_language": "eu",
        "csrfmiddlewaretoken": data.cookies.get("csrftoken"),
    }
    session.headers.update(
        {
            "Referer": "https://elia.eus/itzultzailea",
            "Origin": "https://elia.eus",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        }
    )
    session.cookies.update({"cookies_accepted": "0"})
    response = session.post(
        "https://elia.eus/ajax/translate_string",
        data=payload,
    )

    if response.ok:
        result = response.json()
        return result.get("plain_translated_text", "")

    return ""


def tweet_text(translations, original):
    original_text = "{text} #yogitea #yogiteaquotes".format(text=original)

    with open("credentials.twitter.json") as fp:
        credentials = json.load(fp)

        api = TwitterAPI(
            credentials["API_KEY"],
            credentials["API_SECRET"],
            credentials["ACCESS_TOKEN_KEY"],
            credentials["ACCESS_TOKEN_SECRET"],
        )
        res = api.request("statuses/update", {"status": original_text})
        if res.response.ok:
            print('Tweeted: "{}"'.format(original_text))
            previous_tweet_id = res.response.json().get("id")
            for item in translations:
                text = item.get("text")
                source = item.get("source")
                translated_text = (
                    "{text} #yogitea #yogiteaquotes #itzultzailea #{source}"
                    .format(text=text, source=source)
                )
                res = api.request(
                    "statuses/update",
                    {
                        "status": translated_text,
                        "in_reply_to_status_id": previous_tweet_id,
                    },
                )
                if res.response.ok:
                    print('Tweeted: "{}"'.format(translated_text))
                    previous_tweet_id = res.response.json().get("id")


def main():
    text = get_yogitea_text()
    translated_text_itzuli = translate_text_itzuli_eus(text)
    translated_text_elia = translate_text_elia_eus(text)
    tweet_text(
        [
            {"text": translated_text_itzuli, "source": "itzulieus"},
            {"text": translated_text_elia, "source": "eliaeus"},
        ],
        text,
    )


if __name__ == "__main__":
    main()
