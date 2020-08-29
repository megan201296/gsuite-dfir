from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Gsuite(object):
    """
    Class for doing bulk of operations related to GSuite DFIR activities
    """

    def __init__(self):
        self.service = gsuite_session()

    def gsuite_session(self):
        """
        Establish connection to GSuite.
        """
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

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

    def get_logins(self):

        # Call the Admin SDK Reports API
        results = self.service.activities().list(
            userKey='all', applicationName='login').execute()
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

    def get_logs(self, app):
        results = self.service.activities().list(
            userKey='all', applicationName=app).execute()
        activities = results.get('items', [])

        for activity in activities:
            with open('summary.csv', 'a', newline='') as summary:
                summary_write = csv.writer(summary, delimiter=',')
                try:
                    summary_write.writerow([activity['id']['time'], activity['id']['applicationName'], activity['actor']
                                            ['email'], activity['ipAddress'], activity['events'][0]['type'], activity['events'][0]['name']])
                except KeyError:
                    summary_write.writerow([activity['id']['time'], activity['id']['applicationName'], activity['actor']
                                            ['email'], None, activity['events'][0]['type'], activity['events'][0]['name']])

    def get_geoip(self, ipAddress):
        reader = geoip2.database.Reader(
            '/Users/meganroddie/Documents/gsuite_dfir/GeoLite2-City.mmdb')
        response = reader.city(ipAddress)
        return response.country.iso_code
