import os
import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def find_next_urlaub_event(service):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        if event['summary'].lower().startswith('urlaub'):
            return event['start'].get('dateTime', event['start'].get('date'))
    return None

def update_signature_with_date(signature_name, template_file, event_date):
    signatures_path = os.path.expanduser(r'~\AppData\Roaming\Microsoft\Signatures')
    html_file = os.path.join(signatures_path, f'{signature_name}.htm')

    # Adjust the path to the template file
    template_path = os.path.join(os.path.dirname(__file__), 'template', template_file)

    with open(template_path, 'r', encoding='utf-8') as template:
        new_content = template.read().replace("{urlaub_date}", event_date)

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    service = get_calendar_service()
    next_event_date = find_next_urlaub_event(service)
    if next_event_date:
        print(f"Next 'urlaub' event is on: {next_event_date}")
        update_signature_with_date("YourSignatureName", "your_template.html", next_event_date)
    else:
        print("No upcoming 'urlaub' events found.")

if __name__ == '__main__':
    main()
