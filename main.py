import argparse
import glob
import json
import logging
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

CLIENT_SECRETS_FILE = "credentials_file.json"
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/youtube'
]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server()
    creds_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    session = flow.authorized_session()
    profile_info = session.get(
        'https://www.googleapis.com/userinfo/v2/me').json()

    with open("tokens/" + profile_info['name'] + ".json", 'w') as outfile:
        json.dump(creds_data, outfile)

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds)


def video_rate(**kwargs):
    try:
        for token in glob.glob("tokens/*.json"):
            with open(token, 'r') as f:
                creds_data = json.load(f)
            creds = Credentials(
                token=creds_data['token'],
                refresh_token=creds_data['refresh_token'],
                token_uri=creds_data['token_uri'],
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret'],
            )

            service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
            service.videos().rate(**kwargs).execute()
            print('{} đã {} thành công.'.format(get_user_info(creds)['name'], kwargs.get('rating')))

    except HttpError as err:
        if err.resp.status == 404:
            print('khong tim thay video')
        else:
            print('video rate error HttpError')
        logging.error('An error occurred: %s', err)
    except Exception as err:
        print(err)
        logging.error('An error occurred: %s', err)


def subscriptions(channelId):
    try:
        for token in glob.glob("tokens/*.json"):
            with open(token, 'r') as f:
                creds_data = json.load(f)
            creds = Credentials(
                token=creds_data['token'],
                refresh_token=creds_data['refresh_token'],
                token_uri=creds_data['token_uri'],
                client_id=creds_data['client_id'],
                client_secret=creds_data['client_secret'],
            )

            service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
            service.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "channelId": channelId,
                            "kind": "youtube#channel"
                        }
                    }
                }
            ).execute()
            print('OK')

    except HttpError as err:
        if err.resp.status == 404:
            print('khong tim thay video')
        else:
            print('video rate error HttpError')
        logging.error('An error occurred: %s', err)
    except Exception as err:
        print(err)
        logging.error('An error occurred: %s', err)


def get_info_video(_id, _creds):
    service = build(API_SERVICE_NAME, API_VERSION, credentials=_creds)
    result = service.videos().list(
        part="snippet",
        id=_id
    ).execute()
    return result['items'][0]['snippet']['title']


def get_user_info(_creds):
    user_info_service = build(
        serviceName='oauth2', version='v2',
        credentials=_creds)
    user_info = None
    try:
        user_info = user_info_service.userinfo().get().execute()
    except HttpError as e:
        logging.error('An error occurred: %s', e)

    if user_info and user_info.get('id'):
        return user_info
    else:
        print('user not found')


def options():
    parser = argparse.ArgumentParser(description='Blah blah')
    parser.add_argument("--login", help="Login google", action="store_true")
    parser.add_argument("--rate",
                        help="Rate video",
                        nargs='+')
    parser.add_argument("--sub",
                        help="Subscriptions channel")
    args = parser.parse_args()
    if args.login:
        get_authenticated_service()
    if args.rate:
        if args.rate[0] not in ['none', 'dislike', 'like']:
            print("choose from 'none', 'dislike', 'like'")

        video_rate(id=args.rate[1], rating=args.rate[0])
    if args.sub:
        subscriptions(args.sub)
    else:
        print('--help')


if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    options()
