# from googleapiclient.discovery import build
# from google.oauth2.service_account import Credentials
# from datetime import datetime, timezone
# from urllib.parse import urlencode
# import webbrowser
# import os
# import requests
# from flask import Flask, request
# import json
# import base64

# import os
# import json
# import base64
# from googleapiclient.discovery import build
# from google.oauth2.service_account import Credentials

# # Strava config
# CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
# CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
# REDIRECT_URI = os.environ.get(
#     "REDIRECT_URI",
#     "http://127.0.0.1:5000/auth/strava/callback",
# )

# # Google Sheets config
# GOOGLE_SA_B64 = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
# GOOGLE_SA_INFO = json.loads(
#     base64.b64decode(GOOGLE_SA_B64).decode("utf-8")
# )
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
# SHEET_RANGE = "Sheet1!A1"

# # ==== EDIT THESE ====
# # CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
# # CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
# # # CLIENT_ID = "205431"
# # # CLIENT_SECRET = "ba0ee74ffeb7b8c2692eb4ffe00c475b80979ce9"
# # REDIRECT_URI = "http://127.0.0.1:5000/auth/strava/callback"

# # CHALLENGE_START = datetime(2026, 1, 1, tzinfo=timezone.utc)
# # # =====================

# # STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
# # STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
# # STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"


# # GOOGLE_SA_B64 = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
# # GOOGLE_SA_INFO = json.loads(base64.b64decode(GOOGLE_SA_B64).decode("utf-8"))
# # # SERVICE_ACCOUNT_FILE = "strava-automation-489013-2501a54777ce.json"  # your JSON filename
# # SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# # SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
# # SHEET_RANGE = "Sheet1!A2"


# app = Flask(__name__)

# @app.route("/")
# def index():
#     # params = {
#     #     "client_id": CLIENT_ID,
#     #     "redirect_uri": REDIRECT_URI,
#     #     "response_type": "code",
#     #     "approval_prompt": "auto",
#     #     "scope": "read,activity:read,activity:read_all",
#     # }
#     # auth_link = f"{STRAVA_AUTH_URL}?{urlencode(params)}"
#     # return f'<a href="{auth_link}">Connect Strava</a>'
#     params = {
#         "client_id": CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": REDIRECT_URI,
#         "scope": "read,activity:read,activity:read_all",
#     }
#     auth_link = "https://www.strava.com/oauth/authorize?" + urlencode(params)
#     return f'<a href="{auth_link}">Connect Strava</a>'


# @app.route("/auth/strava/callback")
# def strava_callback():
#     error = request.args.get("error")
#     if error:
#         return f"Error from Strava: {error}", 400

#     code = request.args.get("code")
#     if not code:
#         return "No code provided", 400

#     # 1) Exchange code for token
#     token_resp = requests.post(
#         STRAVA_TOKEN_URL,
#         data={
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "code": code,
#             "grant_type": "authorization_code",
#         },
#         timeout=10,
#     )
#     token_resp.raise_for_status()
#     token_data = token_resp.json()
#     access_token = token_data["access_token"]

#     athlete = token_data.get("athlete", {})
#     athlete_id = athlete.get("id")
#     athlete_firstname = athlete.get("firstname") or ""
#     athlete_lastname = athlete.get("lastname") or ""
#     display_name = (athlete_firstname + " " + athlete_lastname).strip() or f"Athlete {athlete_id}"
    

#     after_ts = int(CHALLENGE_START.timestamp())

#     # 2) List summary activities
#     activities = []
#     page = 1
#     per_page = 50

#     while True:
#         resp = requests.get(
#             STRAVA_ACTIVITIES_URL,
#             headers={"Authorization": f"Bearer {access_token}"},
#             params={"after": after_ts, "page": page, "per_page": per_page},
#             timeout=10,
#         )
#         resp.raise_for_status()
#         batch = resp.json()
#         if not batch:
#             break
#         activities.extend(batch)
#         page += 1

#     print("\n=== Detailed activities since 2026-01-01 ===")

#     detailed_rows = []

#     # 3) For each activity, get details (with calories) and build rows
#     for a in activities:
#         activity_id = a.get("id")

#         detail_resp = requests.get(
#             f"https://www.strava.com/api/v3/activities/{activity_id}",
#             headers={"Authorization": f"Bearer {access_token}"},
#             timeout=10,
#         )
#         detail_resp.raise_for_status()
#         detail = detail_resp.json()

#         start_date_local = detail.get("start_date_local")
#         sport_type = detail.get("sport_type") or detail.get("type")
#         distance_km = (detail.get("distance") or 0) / 1000.0
#         moving_time_sec = detail.get("moving_time") or 0
#         calories = detail.get("calories")

#         dist_str = f"{distance_km:.2f}km"
#         mins, secs = divmod(moving_time_sec, 60)
#         hrs, mins = divmod(mins, 60)
#         if hrs > 0:
#             time_str = f"{hrs}hr {mins}min {secs}s"
#         else:
#             time_str = f"{mins}min {secs}s"

#         cal_str = f"{calories:.0f}" if calories is not None else "0"

#         print(
#             f"{start_date_local} | {sport_type:10} | {dist_str:8} | "
#             f"{time_str:15} | {cal_str} Cal"
#         )

#         detailed_rows.append([
#             display_name,
#             start_date_local.split("T")[0],
#             sport_type,
#             f"{distance_km:.2f}",
#             time_str,
#             cal_str,
#         ])

#     # 4) Write to Google Sheets
#     # headers = ["Name", "Date", "Activity", "Distance (km)", "Time", "Calories"]
#     values = detailed_rows  # no header row here

#     creds = Credentials.from_service_account_info(
#         GOOGLE_SA_INFO,
#         scopes=SCOPES,
#     )
#     service = build("sheets", "v4", credentials=creds)
#     sheet = service.spreadsheets()

#     body = {"values": values}
#     sheet.values().append(
#         spreadsheetId=SPREADSHEET_ID,
#         range=SHEET_RANGE,
#         valueInputOption="RAW",
#         insertDataOption="INSERT_ROWS",
#         body=body,
#     ).execute()

#     return f"Synced {len(detailed_rows)} activities and appended them to Google Sheets."



# if __name__ == "__main__":
#     url = "http://127.0.0.1:5000/"
#     webbrowser.open(url)
#     app.run(port=5000, debug=True)      


# # @app.route("/")
# # def index():
# #     params = {
# #         "client_id": CLIENT_ID,
# #         "redirect_uri": REDIRECT_URI,
# #         "response_type": "code",
# #         "approval_prompt": "auto",
# #         "scope": "read,activity:read,activity:read_all",
# #     }
# #     auth_link = f"{STRAVA_AUTH_URL}?{urlencode(params)}"
# #     return f'<a href="{auth_link}">Connect Strava</a>'


# # @app.route("/auth/strava/callback")
# # def strava_callback():
# #     error = request.args.get("error")
# #     if error:
# #         return f"Error from Strava: {error}", 400

# #     code = request.args.get("code")
# #     if not code:
# #         return "No code provided", 400

# #     # 1) Exchange code for token
# #     token_resp = requests.post(
# #         STRAVA_TOKEN_URL,
# #         data={
# #             "client_id": CLIENT_ID,
# #             "client_secret": CLIENT_SECRET,
# #             "code": code,
# #             "grant_type": "authorization_code",
# #         },
# #         timeout=10,
# #     )
# #     token_resp.raise_for_status()
# #     token_data = token_resp.json()
# #     access_token = token_data["access_token"]

# #     after_ts = int(CHALLENGE_START.timestamp())

# #     # 2) List summary activities
# #     activities = []
# #     page = 1
# #     per_page = 50  # small page size is fine for testing

# #     while True:
# #         resp = requests.get(
# #             STRAVA_ACTIVITIES_URL,
# #             headers={"Authorization": f"Bearer {access_token}"},
# #             params={"after": after_ts, "page": page, "per_page": per_page},
# #             timeout=10,
# #         )
# #         resp.raise_for_status()
# #         batch = resp.json()
# #         if not batch:
# #             break
# #         activities.extend(batch)
# #         page += 1

# #     print("\n=== Detailed activities since 2026-01-01 ===")

# #     for a in activities:
# #         activity_id = a.get("id")

# #         # 3) Get detailed activity (has calories)
# #         detail_resp = requests.get(
# #             f"https://www.strava.com/api/v3/activities/{activity_id}",
# #             headers={"Authorization": f"Bearer {access_token}"},
# #             timeout=10,
# #         )
# #         detail_resp.raise_for_status()
# #         detail = detail_resp.json()

# #         start_date_local = detail.get("start_date_local")
# #         sport_type = detail.get("sport_type") or detail.get("type")
# #         distance_km = (detail.get("distance") or 0) / 1000.0
# #         moving_time_sec = detail.get("moving_time") or 0
# #         calories = detail.get("calories")  # more reliable here [web:12]

# #         # format distance
# #         dist_str = f"{distance_km:.2f}km"

# #         # format time
# #         mins, secs = divmod(moving_time_sec, 60)
# #         hrs, mins = divmod(mins, 60)
# #         if hrs > 0:
# #             time_str = f"{hrs}hr {mins}min {secs}s"
# #         else:
# #             time_str = f"{mins}min {secs}s"

# #         cal_str = f"{calories:.0f}" if calories is not None else "Nil"

# #         print(
# #             f"{start_date_local} | {sport_type:10} | {dist_str:8} | "
# #             f"{time_str:15} | {cal_str} Cal"
# #         )
        

# #     return f"Synced {len(activities)} activities with detailed calories. Check your terminal."




# from datetime import datetime, timezone
# from urllib.parse import urlencode
# import webbrowser
# import os
# import json
# import base64

# import requests
# from flask import Flask, request
# from googleapiclient.discovery import build
# from google.oauth2.service_account import Credentials

# # ---------- Strava config ----------
# CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
# CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
# REDIRECT_URI = os.environ.get(
#     "REDIRECT_URI",
#     "https://strava-challenge-2026.onrender.com/auth/strava/callback",  # local default
# )

# # Optional local fallbacks (you can remove these if you want to force env vars)
# # if not CLIENT_ID:
# #     CLIENT_ID = "205431"
# # if not CLIENT_SECRET:
# #     CLIENT_SECRET = "YOUR_LOCAL_DEV_SECRET_HERE"

# STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
# STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
# STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
# CHALLENGE_START = datetime(2026, 1, 1, tzinfo=timezone.utc)

# # ---------- Google Sheets config ----------
# GOOGLE_SA_B64 = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
# if GOOGLE_SA_B64:
#     GOOGLE_SA_INFO = json.loads(
#         base64.b64decode(GOOGLE_SA_B64).decode("utf-8")
#     )
# else:
#     GOOGLE_SA_INFO = {}

# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")
# SHEET_RANGE = "Sheet1!A1"

# app = Flask(__name__)


# @app.route("/")
# def index():
#     # Build Strava OAuth URL
#     params = {
#         "client_id": CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": REDIRECT_URI,
#         "scope": "read,activity:read,activity:read_all",
#     }
#     auth_link = STRAVA_AUTH_URL + "?" + urlencode(params)
#     return f'<a href="{auth_link}">Connect Strava</a>'

# @app.route("/")
# def index():
#     params = {
#         "client_id": CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": REDIRECT_URI,
#         "scope": "read,activity:read,activity:read_all",
#     }
#     auth_link = STRAVA_AUTH_URL + "?" + urlencode(params)
#     return f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>2026 Fitness Challenge</title>
#         <style>
#             body {{
#                 font-family: Arial, sans-serif;
#                 display: flex;
#                 flex-direction: column;
#                 align-items: center;
#                 justify-content: center;
#                 min-height: 100vh;
#                 margin: 0;
#                 background-color: #f5f5f5;
#             }}
#             h1 {{ color: #333; }}
#             p {{ color: #666; max-width: 400px; text-align: center; }}
#             .powered {{
#                 margin-top: 40px;
#                 font-size: 12px;
#                 color: #999;
#             }}
#             .powered a {{ color: #FC4C02; text-decoration: none; }}
#         </style>
#     </head>
#     <body>
#         <h1>2026 Fitness Challenge</h1>
#         <p>Connect your Strava account to sync your activities to the challenge leaderboard.</p>
#         <a href="{auth_link}">
#             <img src="https://developers.strava.com/images/btn_strava_connectwith_orange.svg"
#                  alt="Connect with Strava" width="193" height="48"/>
#         </a>
#         <p class="powered">Powered by <a href="https://www.strava.com">Strava</a></p>
#     </body>
#     </html>
#     """

# # @app.route("/auth/strava/callback")
# # def strava_callback():
# #     error = request.args.get("error")
# #     if error:
# #         return f"Error from Strava: {error}", 400

# #     code = request.args.get("code")
# #     if not code:
# #         return "No code provided", 400

#     # 1) Exchange code for token
#     token_resp = requests.post(
#         STRAVA_TOKEN_URL,
#         data={
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "code": code,
#             "grant_type": "authorization_code",
#         },
#         timeout=10,
#     )
#     token_resp.raise_for_status()
#     token_data = token_resp.json()
#     access_token = token_data["access_token"]

#     athlete = token_data.get("athlete", {})
#     athlete_id = athlete.get("id")
#     athlete_firstname = athlete.get("firstname") or ""
#     athlete_lastname = athlete.get("lastname") or ""
#     display_name = (athlete_firstname + " " + athlete_lastname).strip() or f"Athlete {athlete_id}"

#     after_ts = int(CHALLENGE_START.timestamp())

#     # 2) List summary activities since challenge start
#     activities = []
#     page = 1
#     per_page = 50

#     while True:
#         resp = requests.get(
#             STRAVA_ACTIVITIES_URL,
#             headers={"Authorization": f"Bearer {access_token}"},
#             params={"after": after_ts, "page": page, "per_page": per_page},
#             timeout=10,
#         )
#         resp.raise_for_status()
#         batch = resp.json()
#         if not batch:
#             break
#         activities.extend(batch)
#         page += 1

#     detailed_rows = []

#     # 3) For each activity, get details and build rows
#     for a in activities:
#         activity_id = a.get("id")

#         detail_resp = requests.get(
#             f"https://www.strava.com/api/v3/activities/{activity_id}",
#             headers={"Authorization": f"Bearer {access_token}"},
#             timeout=10,
#         )
#         detail_resp.raise_for_status()
#         detail = detail_resp.json()

#         start_date_local = detail.get("start_date_local")
#         sport_type = detail.get("sport_type") or detail.get("type")
#         distance_km = (detail.get("distance") or 0) / 1000.0
#         moving_time_sec = detail.get("moving_time") or 0
#         calories = detail.get("calories")

#         dist_str = f"{distance_km:.2f}km"
#         mins, secs = divmod(moving_time_sec, 60)
#         hrs, mins = divmod(mins, 60)
#         if hrs > 0:
#             time_str = f"{hrs}hr {mins}min {secs}s"
#         else:
#             time_str = f"{mins}min {secs}s"

#         cal_str = f"{calories:.0f}" if calories is not None else "0"

#         detailed_rows.append(
#             [
#                 display_name,
#                 start_date_local.split("T")[0] if start_date_local else "",
#                 sport_type,
#                 f"{distance_km:.2f}",
#                 time_str,
#                 cal_str,
#             ]
#         )

#     # 4) Write to Google Sheets
#     if not GOOGLE_SA_INFO or not SPREADSHEET_ID:
#         return "Google Sheets configuration is missing", 500

#     creds = Credentials.from_service_account_info(
#         GOOGLE_SA_INFO,
#         scopes=SCOPES,
#     )
#     service = build("sheets", "v4", credentials=creds)
#     sheet = service.spreadsheets()

#     body = {"values": detailed_rows}
#     sheet.values().append(
#         spreadsheetId=SPREADSHEET_ID,
#         range=SHEET_RANGE,
#         valueInputOption="RAW",
#         insertDataOption="INSERT_ROWS",
#         body=body,
#     ).execute()

#     return f"Synced {len(detailed_rows)} activities and appended them to Google Sheets."


# if __name__ == "__main__":
#     url = "http://127.0.0.1:5000/"
#     webbrowser.open(url)
#     app.run(port=5000, debug=True)

from datetime import datetime, timezone
from urllib.parse import urlencode
import webbrowser
import os
import json
import base64

import requests
from flask import Flask, request
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# ---------- Strava config ----------
CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.environ.get(
    "REDIRECT_URI",
    "https://strava-challenge-2026.onrender.com/auth/strava/callback",
)

STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
CHALLENGE_START = datetime(2026, 1, 1, tzinfo=timezone.utc)

# ---------- Google Sheets config ----------
GOOGLE_SA_B64 = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
if GOOGLE_SA_B64:
    GOOGLE_SA_INFO = json.loads(
        base64.b64decode(GOOGLE_SA_B64).decode("utf-8")
    )
else:
    GOOGLE_SA_INFO = {}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")
SHEET_RANGE = "Sheet1!A1"

app = Flask(__name__)


@app.route("/")
def index():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "read,activity:read,activity:read_all",
    }
    auth_link = STRAVA_AUTH_URL + "?" + urlencode(params)
    html = """<!DOCTYPE html>
<html>
<head>
    <title>2026 Fitness Challenge</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        h1 { color: #333; }
        p { color: #666; max-width: 400px; text-align: center; }
        .powered { margin-top: 40px; font-size: 12px; color: #999; }
        .powered a { color: #FC4C02; text-decoration: none; }
    </style>
</head>
<body>
    <h1>2026 Fitness Challenge</h1>
    <p>Connect your Strava account to sync your activities to the challenge leaderboard.</p>
    <a href="AUTH_LINK">
        <img src="https://developers.strava.com/images/btn_strava_connectwith_orange.svg"
             alt="Connect with Strava" width="193" height="48"/>
    </a>
    <p class="powered">Powered by <a href="https://www.strava.com">Strava</a></p>
</body>
</html>"""
    html = html.replace("AUTH_LINK", auth_link)
    return html


@app.route("/auth/strava/callback")
def strava_callback():
    error = request.args.get("error")
    if error:
        return f"Error from Strava: {error}", 400

    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    # 1) Exchange code for token
    token_resp = requests.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    access_token = token_data["access_token"]

    athlete = token_data.get("athlete", {})
    athlete_id = athlete.get("id")
    athlete_firstname = athlete.get("firstname") or ""
    athlete_lastname = athlete.get("lastname") or ""
    display_name = (athlete_firstname + " " + athlete_lastname).strip() or f"Athlete {athlete_id}"

    after_ts = int(CHALLENGE_START.timestamp())

    # 2) Read existing activity IDs from sheet to avoid duplicates
    creds = Credentials.from_service_account_info(GOOGLE_SA_INFO, scopes=SCOPES)
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="Sheet1!A1:H10000",
    ).execute()
    existing_rows = result.get("values", [])
    existing_ids = set()
    for r in existing_rows:
        if len(r) >= 8 and r[7]:
            existing_ids.add(str(r[7]))

    # 3) Fetch all activities since challenge start
    activities = []
    page = 1
    per_page = 50

    while True:
        resp = requests.get(
            STRAVA_ACTIVITIES_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            params={"after": after_ts, "page": page, "per_page": per_page},
            timeout=10,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        activities.extend(batch)
        page += 1

    detailed_rows = []

    # 4) For each activity, get details and build rows
    for a in activities:
        activity_id = a.get("id")
        if activity_id is None:
            continue
        if str(activity_id) in existing_ids:
            continue  # skip duplicates

        detail_resp = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        detail_resp.raise_for_status()
        detail = detail_resp.json()

        start_date_local = detail.get("start_date_local")
        sport_type = detail.get("sport_type") or detail.get("type")
        distance_km = (detail.get("distance") or 0) / 1000.0
        moving_time_sec = detail.get("moving_time") or 0
        calories = detail.get("calories")

        # Format time
        mins, secs = divmod(moving_time_sec, 60)
        hrs, mins = divmod(mins, 60)
        if hrs > 0:
            time_str = f"{hrs}hr {mins}min {secs}s"
        else:
            time_str = f"{mins}min {secs}s"

        # Format pace (min/km) - only meaningful for running/walking
        if distance_km > 0:
            pace_sec_per_km = moving_time_sec / distance_km
            pace_min, pace_sec = divmod(int(pace_sec_per_km), 60)
            pace_str = f"{pace_min}:{pace_sec:02d} /km"
        else:
            pace_str = ""

        cal_str = f"{calories:.0f}" if calories is not None else "0"

        detailed_rows.append([
            display_name,                                          # Name
            start_date_local.split("T")[0] if start_date_local else "",  # Date
            sport_type,                                            # Activity
            f"{distance_km:.2f}",                                 # Distance (km)
            time_str,                                             # Time
            cal_str,                                              # Calories
            pace_str,                                             # Pace
            str(activity_id),                                     # ActivityID (hidden, for dedup)
        ])

    # 5) Write new rows to Google Sheets
    if not GOOGLE_SA_INFO or not SPREADSHEET_ID:
        return "Google Sheets configuration is missing", 500

    if detailed_rows:
        body = {"values": detailed_rows}
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    return f"Synced {len(detailed_rows)} new activities and appended them to Google Sheets."


if __name__ == "__main__":
    url = "http://127.0.0.1:5000/"
    webbrowser.open(url)
    app.run(port=5000, debug=True)
