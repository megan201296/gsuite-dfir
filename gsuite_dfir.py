# https://developers.google.com/admin-sdk/reports/v1/reference/

from __future__ import print_function
import pickle
import os.path
import geoip2.database
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import csv

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

def gsuite_session():
    """Shows basic usage of the Admin SDK Reports API.
    Prints the time, email, and name of the last 10 login events in the domain.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('admin', 'reports_v1', credentials=creds)
    
    return service

def logins(service):

    # Call the Admin SDK Reports API
    results = service.activities().list(userKey='all', applicationName='login').execute()
    activities = results.get('items', [])

    if not activities:
        print('No logins found.')
    else:
        print('Login Details:')
        for activity in activities:
            print(u'{0}: {1} ({2}) {3}'.format(activity['id']['time'],
                activity['actor']['email'], activity['events'][0]['name'], activity['ipAddress']))
    
        print('Logins by Country:')
        for activity in activities:
            country = get_geoip(activity['ipAddress'])
            print(u'{0} {1} {2}'.format(country, activity['id']['time'],
                activity['actor']['email']))

        print('Login Failures:')
        for activity in activities:
            if activity['events'][0]['name'] == "login_failure":
                print(u'{1} {2}'.format(country, activity['id']['time'],
                    activity['actor']['email']))

def get_logs(service, app):
    results = service.activities().list(userKey='all', applicationName=app).execute()
    activities = results.get('items', [])

    for activity in activities:
        with open('summary.csv', 'a', newline='') as summary:
            summary_write = csv.writer(summary, delimiter=',')
            try:
                summary_write.writerow([activity['id']['time'], activity['id']['applicationName'], activity['actor']['email'], activity['ipAddress'], activity['events'][0]['type'], activity['events'][0]['name']])
            except KeyError: 
                summary_write.writerow([activity['id']['time'], activity['id']['applicationName'], activity['actor']['email'], None, activity['events'][0]['type'], activity['events'][0]['name']])
        
    # print('Downloaded Files:')
    # for activity in activities:
    #    if activity['events'][0]['name'] == "download":
    #        if activity['actor']['email'] is not "":
    #            print(u'{0} downloaded by {1}'.format(activity['events'][0]['parameters'][4]['value'], activity['actor']['email']))
    #        else:
    #            print(u'{0} downloaded by unauthenticated user'.format(activity['events'][0]['parameters'][4]['value'], activity['actor']['email']))


def get_geoip(ipAddress):
    reader = geoip2.database.Reader('/Users/meganroddie/Documents/gsuite_dfir/GeoLite2-City.mmdb')
    response = reader.city(ipAddress)
    return response.country.iso_code


if __name__ == '__main__':

    with open('summary.csv', 'w', newline='') as summary:
        fields = ['time', 'app', 'email', 'ip', 'event type', 'event name']
        summary_writer = csv.writer(summary, delimiter=',')
        summary_writer.writerow(fields)

    session = gsuite_session()
    logins(session)
    get_logs(session, 'admin')
    get_logs(session, 'calendar')
    get_logs(session, 'drive')
    get_logs(session, 'login')
    get_logs(session, 'user_accounts')
