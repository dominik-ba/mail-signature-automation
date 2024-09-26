import os
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

def read_template(signature_name, ext):
    path = os.path.join(os.path.dirname(__file__), 'templates', f"{signature_name}.{ext}")

    encoding= 'cp1252'
    if ext == 'txt':
        encoding = 'utf-16-le'

    with open(path, 'r', encoding=encoding) as f:
        return f.read()

# function to modify the template - replacing dd1 mm1 yy1 dd2 mm2 yy2 with parameters
def modify_template(template, dd1, mm1, yy1, dd2, mm2, yy2):
    return template.replace("dd1", dd1).replace("mm1", mm1).replace("yy1", yy1).replace("dd2", dd2).replace("mm2", mm2).replace("yy2", yy2)

def update_signature(signature_name):
    # Path to the signatures folder
    signatures_path = os.path.expanduser(r'~\AppData\Roaming\Microsoft\Signatures')

    # Construct the full path to the signature files
    signatures = {}
    signatures['htm'] = os.path.join(signatures_path, f'{signature_name}.htm')
    signatures['rtf'] = os.path.join(signatures_path, f'{signature_name}.rtf')
    signatures['txt'] = os.path.join(signatures_path, f'{signature_name}.txt')

    for ext, file in signatures.items():
        if not os.path.exists(file):
            continue
        # # Write the new content to the HTML file
        # print(f"Updating {file}...")
        # with open(file, 'w', encoding='utf-8') as f:
        #f.write(read_template(template_file))
        # update...


def algorithm(signature_name):
    extensions = ['htm']#, 'rtf', 'txt']
    for ext in extensions:
        content = read_template(signature_name, ext)
        content = modify_template(content, "01", "01", "24", "31", "12", "24")
        #print(content)
        #update_signature(signature_name, content)


if __name__ == "__main__":
    service = get_calendar_service()
    next_event_date = find_next_urlaub_event(service)
    if next_event_date:
        print(f"Next 'urlaub' event is on: {next_event_date}")
    algorithm("def")
