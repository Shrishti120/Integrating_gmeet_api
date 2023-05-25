## Importing Libraries

from pathlib import Path
from pickle import load,dump
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


## creating a class to generate an email with an event

class EventPlanner:
    """ 
    Here I am creating a Class where following process will happen,
    1.  The first thing I will do is initialise a class where I will initialise all the required variables.
    2. Next I will create a authorize function which will be used to connect to the google calender and edit it and add items to it.
    3. And then I will create a create event function which will have all the details of the event and using this detail our function will schedule an event.
    """

    ##initializing the class
    def __init__(self, guests_list, schedule, token_path, credential_path, calender_id, location):
        self.guests_list = guests_list
        self.schedule = schedule
        self.token_path = token_path
        self.credential_path = credential_path
        self.calender_id = calender_id
        self.location = location

    ## 
    def _authorize(self):
        """
        The first thing happening here is getting all the details which will be used to connect us to the google calender, next
        if we checked and verified weather the credentials are correct or not, if they are I loaded them in a token file and last I constructed a resource
        which gave me an access to use the calender.
        """
        scopes = ["https://www.googleapis.com/auth/calendar"]
        credentials = None
        token_file = Path(self.token_path)

        if token_file.exists():
            with open(token_file, "rb") as token:
                credentials = load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credential_path, scopes)
                credentials = flow.run_console(port=0)
            with open(token_file, "wb") as token:
                dump(credentials, token)
    
        calendar_service = build("calendar", "v3", credentials=credentials)

        return calendar_service
    

    ##
    def _create_event(self):
        """
        In this function I considered all the important things that I needed to create an event, created an event
        and Inserted this event in my calender.
        """
        attendees = [{"email": email} for email in self.guests_list]
        event = {
            "summary": "Appointment meeting",
            'location': self.location,
            'description': 'Doctors Appointment',
            "start": {
                "dateTime": self.schedule["start"] , 
                "timeZone": 'Asia/Kolkata',
            },
            "end": {
                "dateTime": self.schedule["end"],
                "timeZone": 'Asia/Kolkata',
            },
            "attendees": attendees,
            "conferenceData": {
                "createRequest": {
                    "requestId": "SecureRandom.uuid",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            }
        }

        service = self._authorize()

        event = service.events().insert(
            calendarId=self.calender_id, 
            sendNotifications=True, 
            body=event, 
            conferenceDataVersion=1
        ).execute()


        return event
    
    
if __name__ == "__main__":
    
    guest_list=["sangeeta.gupta.dev@gmail.com"]
    schedule={"start": "2023-05-2T07:30:00",  "end": "2023-05-2T07:30:00"}

    ## creating a class instance and initializing a object
    event_planner = EventPlanner(
        guests_list=guest_list, 
        schedule=schedule, 
        token_path="token.pkl",
        credential_path="client_secret.json",
        calender_id="pshrishti325@gmail.com",
        location="Raipur"
    )

    event = event_planner._create_event()
    print(event['htmlLink'])

