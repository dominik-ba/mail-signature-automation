import os
import os
from datetime import datetime, timezone, timedelta
import pickle
import argparse

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
            try:
                creds.refresh(Request())
            except:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)


def find_next_urlaub_event(service):
    now = datetime.now(timezone.utc).isoformat() # 'Z' indicates UTC time
    print(f"Now: {now}")
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=20, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    for event in events:
        if event['summary'].lower().startswith('urlaub'):
            return event
    return None


def find_next_urlaub_dates(event):
    start = datetime.strptime(event['start'].get('date'), '%Y-%m-%d')
    end = datetime.strptime(event['end'].get('date'), '%Y-%m-%d')
    return start, end
    start = datetime.strptime(event['start'].get('date'), '%Y-%m-%d')
    end = datetime.strptime(event['end'].get('date'), '%Y-%m-%d')
    return start, end


def read_template(signature_name, ext):
    path = os.path.join(os.path.dirname(__file__),
                        'templates', f"{signature_name}.{ext}")

    encoding = 'cp1252'
    if ext == 'txt':
        encoding = 'utf-16-le'

    with open(path, 'r', encoding=encoding) as f:
        return f.read()

# function to modify the template - replacing dd1 mm1 yy1 dd2 mm2 yy2 with parameters


def modify_template(template, dd1, mm1, yy1, dd2, mm2, yy2):
    new_date = f"{dd1}.{mm1}.{yy1}-{dd2}.{mm2}.{yy2}"
    return template.replace("DD.MM.YYYY-DD.MM.YYYY", new_date)


def update_signature(signature_name, ext, content, signatures_path):

    # Construct the full path to the signature files
    signatures = {}
    signatures['htm'] = os.path.join(signatures_path, f'{signature_name}.htm')
    signatures['rtf'] = os.path.join(signatures_path, f'{signature_name}.rtf')
    signatures['txt'] = os.path.join(signatures_path, f'{signature_name}.txt')

    if not os.path.exists(signatures[ext]):
        print(f"Signature file {signatures[ext]} does not exist.")
        return
    # Write the new content to the HTML file
    print(f"Updating {signatures[ext]}...")

    encoding = 'utf-8'
    if ext == 'txt':
        encoding = 'utf-16-le'
    with open(signatures[ext], 'w', encoding=encoding) as f:
        f.write(content)


def algorithm(signature_name, ext, start, end):
    content = read_template(signature_name, ext)
    content = modify_template(content, str(start.day), str(start.month), str(
        start.year), str(end.day), str(end.month), str(end.year))
    # print(content)
    return content


def blank(signature_name, ext):
    content = read_template(signature_name, ext)
    content = modify_template(content, "-", "", "", "-", "", "")
    # print(content)
    return content


if __name__ == "__main__":
    # parsing argparse for signature name
    parser = argparse.ArgumentParser()
    # adjust name to grant the possibility to provide more then one name

    parser.add_argument("name", help="Name of the signature")
    # optionally provide a path to the signature file, when not provided, use null
    parser.add_argument("--path", "-p", default=None,
                        help='Path to the signature file (default: %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Signatures)')
    args = parser.parse_args()
    name = args.name
    if not args.path:
        signatures_path = os.path.expanduser(
            r'~\AppData\Roaming\Microsoft\Signatures')
    else:
        signatures_path = args.path

    service = get_calendar_service()
    next_event = find_next_urlaub_event(service)
    extensions = ['htm', 'rtf', 'txt']
    if next_event:
        start, end = find_next_urlaub_dates(next_event)
        last_day = end - timedelta(days=1)
        print(
            f"Next 'urlaub' event is from {str(start.day)}.{str(start.month)}.{str(start.year)} to {str(last_day.day)}.{str(last_day.month)}.{str(last_day.year)} (incl.)")
        for ext in extensions:
            content = algorithm(name, ext, start, last_day)
            update_signature(name, ext, content, signatures_path)
    else:
        print(f"Found no 'urlaub' event")

        for ext in extensions:
            content = blank(name, ext)
            update_signature(name, ext, content, signatures_path)
