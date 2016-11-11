from __future__ import print_function
import httplib2
import os

from urllib.parse import urlencode

import requests

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/admin-directory_v1-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/admin.directory.user'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Directory API Python Quickstart'

SLACK_TOKEN = os.environ['SLACK_TOKEN']
TRELLO_TOKEN = os.environ['TRELLO_TOKEN']
TRELLO_KEY = os.environ['TRELLO_KEY']

GITHUB_USER = os.environ['GITHUB_USER']
GITHUB_KEY = os.environ['GITHUB_KEY']
GITHUB_ORG = os.environ['GITHUB_ORG']


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'admin-directory_v1-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_google_user(first_name, last_name, temporary_password):
    print('Creating user in Google Apps')
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('admin', 'directory_v1', http=http)

    primary_email = first_name.lower() + "." + last_name.lower()
    + '@connected-ventures.com'

    user_json = {
        "primaryEmail": primary_email,
        "name": {
          "givenName": first_name,
          "fullName": first_name + " " + last_name,
          "familyName": last_name,
        },
        "password": temporary_password,
        "changePasswordAtNextLogin": True
      }

    results = service.users().insert(body=user_json).execute()
    print(results)

    return primary_email


def invite_to_slack(first_name, last_name, email_address):
    print('Inviting %s %s (%s) to Slack', first_name, last_name, email_address)
    query = {
        'token': SLACK_TOKEN,
        'email': email_address,
        'first_name': first_name,
        'last_name': last_name
        }

    query_string = urlencode(query)
    url = 'https://slack.com/api/users.admin.invite?' + query_string
    response = requests.get(url)
    print(response.text)


def invite_to_trello_org(trello_username):
    print('Inviting %s to Trello org %s', trello_username, TRELLO_ORG)
    query = {
        'token': TRELLO_TOKEN,
        'key': TRELLO_KEY,
        'type': 'normal'
    }

    query_string = urlencode(query)

    url = 'https://api.trello.com/1/organizations/' + TRELLO_ORG + '/members/'
    + trello_username + '?' + query_string

    response = requests.put(url)
    print(response.text)


def invite_to_github_org(github_username):
    print('Inviting %s to Github org %s', github_username, GITHUB_ORG)
    headers = {'Accept': 'application/vnd.github.v3+json'}

    url = 'https://' + GITHUB_USER + ':' + GITHUB_KEY + '@api.github.com/orgs/'
    + GITHUB_ORG + '/memberships/' + github_username

    response = requests.put(url, headers=headers)
    print(response.text)


def main():
    # Defaults
    first_name = ''
    last_name = ''
    temporary_password = ''
    github_username = ''
    trello_username = ''

    do_gmail = input('Create Gmail account (y/n): ').strip()
    if (do_gmail == 'y'):
        first_name = input('Enter employee first name: ')
        first_name = first_name.strip()

        last_name = input('Enter employee last name: ')
        last_name = last_name.strip()

        temporary_password = input('Enter temporary password: ')
        temporary_password = temporary_password.strip()

    do_github = input('Add Github account to org (y/n): ')
    if (do_github == 'y'):
        github_username = input('Enter employee Github username: ')
        github_username = github_username.strip()

    do_trello = input('Add Trello account to org (y/n): ')
    if (do_trello == 'y'):
        trello_username = input('Enter employee Trello username: ')
        trello_username = trello_username.strip()

    if (
            first_name != '' and
            last_name != '' and
            temporary_password != '' and
            do_gmail == 'y'):

        email_address = create_google_user(
                                            first_name,
                                            last_name,
                                            temporary_password)

        invite_to_slack(first_name, last_name, email_address)

    if (github_username != '' and do_github == 'y'):
        invite_to_github_org(github_username)

    if (trello_username != '' and do_trello == 'y'):
        invite_to_trello_org(trello_username)

if __name__ == '__main__':
    main()
