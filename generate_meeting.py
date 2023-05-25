
        
from pathlib import Path
from pickle import load
from pickle import dump
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from uuid import uuid4
from typing import Dict, List
from oauth2client import file, client, tools


class EventPlanner:

    def __init__(self, guests , schedule):
        guests = [{"email": email} for email in guests]
        service = self._authorize()
        self.event_states = self._plan_event(guests, schedule, service)

    @staticmethod
    def _authorize():
        scopes = ["https://www.googleapis.com/auth/calendar"]
        credentials = None
        token_file = Path("token.pkl")

        if token_file.exists():
            with open(token_file, "rb") as token:
                credentials = load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes)
                credentials = flow.run_local_server(port=0)
            with open(token_file, "wb") as token:
                dump(credentials, token)

        calendar_service = build("calendar", "v3", credentials=credentials)

        return calendar_service

    @staticmethod
    def _plan_event(attendees: List[Dict[str, str]], event_time, service: build):
        event = {"summary": "test meeting",
                 'location': 'Raipur',
                 'description': 'Doctors Apointment',
                 "start": {"dateTime": event_time["start"] , 
                           'timeZone': 'Asia/Kolkata',},
                 "end": {"dateTime": event_time["end"],
                         'timeZone': 'Asia/Kolkata',},
                 
                 "attendees": attendees,
                 "conferenceData": {"createRequest": {"requestId": "SecureRandom.uuid",
                                                      "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
                 'reminders': {
                    'useDefault': False,
                    'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                    ],
                 }
        }
        event = service.events().insert(calendarId="pshrishti325@gmail.com", sendNotifications=True, body=event, conferenceDataVersion=1).execute()

        return (event.get('htmlLink'))


if __name__ == "__main__":
    plan = EventPlanner(["rohitkashyap8925@gmail.com","sangeeta.gupta.dev@gmail.com","pshreyasi325@gmail.com"], {"start": "2023-05-29T07:30:00",
                                                                          "end": "2023-05-29T07:30:00"})
    print(plan.event_states)