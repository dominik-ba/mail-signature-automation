# Mail Signature Automation

Automates Outlook signatures by pulling your next vacation (`urlaub`) event from Google Calendar and injecting the date range into pre-made signature templates. The script updates `.htm`, `.rtf`, and `.txt` signature files in your Outlook signatures folder (or a custom path).

## How It Works
- Authenticates with Google Calendar (readonly scope) using `credentials/credentials.json` and stores a `token.pickle` for reuse.
- Looks for the next upcoming event whose summary starts with `urlaub` (case-insensitive).
- Fills `DD.MM.YYYY-DD.MM.YYYY` in the matching templates under `templates/` for each extension (`htm`, `rtf`, `txt`).
- Writes the updated content into your Outlook signatures directory. If no `urlaub` event is found, the placeholders are blanked with dashes.
- The end date received from Calendar is treated as exclusive; the script subtracts one day so signatures show inclusive dates.

## Prerequisites
- Python 3 and `pipenv` installed.
- Google OAuth client secrets at `credentials/credentials.json` (see below for how to create and download).
- Existing Outlook signatures matching the template names you plan to update.

## Setup
1. Install dependencies:
     ```bash
     pipenv install
     ```
2. Create and place your Google OAuth client secret file at `credentials/credentials.json`:
    - Open Google Cloud Console → APIs & Services → Credentials.
    - Create OAuth 2.0 Client ID → Application type: **Desktop app**.
    - Download the client configuration JSON and save it as `credentials/credentials.json`.
    - Make sure Google Calendar API is enabled in the same project.
3. Ensure your Outlook signature files already exist. On Windows the default path is `%USERPROFILE%\AppData\Roaming\Microsoft\Signatures`.
4. First run will open a browser window to authorize Google Calendar access and will create `token.pickle` locally.

## Usage
Run the script for a given signature name (matching the template filenames in `templates/`):

```bash
pipenv run python3 main.py "<signature name>" [--path <signatures_dir>]
```

- `--path/-p` (optional): Override the target signatures directory. Defaults to the Outlook signatures folder on Windows.

### Examples
- Windows host (uses default Outlook signatures folder):
    ```bash
    pipenv run python3 main.py "name (email@adress.com)"
    pipenv run python3 main.py "other-name (email@adress.com)"
    ```

- Devcontainer / Linux path override:
    ```bash
    pipenv run python3 main.py "name (email@adress.com)" -p /workspace/signatures/
    pipenv run python3 main.py "other-name (email@adress.com)" -p /workspace/signatures/
    ```

## Templates
- Located in `templates/` and must be named exactly like the signature name plus extension (e.g., `name (email@adress.com).htm`).
- `.htm` and `.rtf` templates are read as `cp1252`; `.txt` is read/written as `utf-16-le` to match Outlook expectations.
- Replaceable placeholder in templates: `DD.MM.YYYY-DD.MM.YYYY`. There is potential to make this customizable, but no demand for that currently.

## Notes & Troubleshooting
- If you change Google scopes, delete `token.pickle` so re-authentication occurs.
- Ensure the target signature files exist before running; otherwise the script will log and skip updates.
