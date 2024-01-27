from datetime import datetime, timedelta, timezone
import os
import pickle
from apiclient import discovery
from dateutil.parser import parse, isoparse
from httplib2 import Http
from oauth2client import client, file, tools
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/forms.responses.readonly", "https://www.googleapis.com/auth/forms.body.readonly"]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

FORM_URL = os.getenv('CHECK_IN_FORM')
FORM_ID = FORM_URL.replace('https://', '').split('/')[3]

# def get_gform_service(self):
#     # authorise user
#     # https://developers.google.com/calendar/api/guides/auth
#     creds = None

#     # The file token.pickle stores the user's tokens, and is created automatically
#     #  when the authorization flow completes for the first time.
#     filename = self.token_path
#     if filename and os.path.exists(filename):
#         with open(filename, 'rb') as token:
#             creds = pickle.load(token)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             try:
#                 creds.refresh(Request())
#                 # print('credentials refreshed')
#             except Exception as e:
#                 print(e)
#         else:
#             if self.token_path is not None:
#                 #     creds = default_credentials(scopes=None, quota_project_id=None)
#                 # else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     self.api_credentials_path, scopes=self.scopes)
#                 creds = flow.run_local_server(port=50547)

#                 # Save the credentials for the next run
#                 with open(filename, 'wb') as token:
#                     pickle.dump(creds, token)





# try:
#     # prepare file paths
#     client_secret_location = 'credentials/gcal_client_secret.json'
#     CREDENTIALS_FILE = os.path.join(
#         os.path.dirname(__file__), client_secret_location)
#     token_location = 'credentials/token.pickle'
#     TOKEN_FILE = os.path.join(os.path.dirname(__file__), token_location)

#     # create a Google Calendar API service object
#     # cal = GoogleCalendarAccount(CREDENTIALS_FILE, TOKEN_FILE)
#     # events_from_all_calendars = cal.get_all_events(
#     #     # maxResults=10,
#     #     timeMin=today_start,
#     #     timeMax=today_end,
#     #     singleEvents=True,
#     #     orderBy='startTime',
#     #     timeZone='America/Toronto'
#     # )
# except Exception as e:
#     print("Error with Google API", e)
#     # log_error(f'Error with GCal API', e)



store = file.Storage("credentials/token.pickle")
creds = None
# The file token.pickle stores the user's tokens, and is created automatically
#  when the authorization flow completes for the first time.
# filename = 'credentials/token.pickle'
if store:
    # with open(filename, 'rb') as token:
    creds = store.locked_get()
if creds and not creds.invalid and creds.refresh_token:
    try:
        creds.refresh(Request())
        # print('credentials refreshed')
    except Exception as e:
        print(e)
else:
    flow = client.flow_from_clientsecrets("credentials/client_secret_daily_automations.json", SCOPES)
    creds = tools.run_flow(flow, store)

# generate the service object using the credentials
service = discovery.build(
    "forms",
    "v1",
    http=creds.authorize(Http()),
    discoveryServiceUrl=DISCOVERY_DOC,
    static_discovery=False,
)

# Prints the responses of your specified form:
# form_id = FORM_URL.replace('https://', '').split('/')[3]
# result = service.forms().responses().list(formId=form_id).execute()
# print(result)


def get_form_responses(form_id=FORM_ID):
    result = service.forms().responses().list(formId=form_id).execute()
    return result.get('responses', [])


def get_form_data(form_id=FORM_ID):
    result = service.forms().get(formId=form_id).execute()
    return result

def get_form_questions(form_id=FORM_ID):
    result = service.forms().get(formId=form_id).execute()
    question_list_items = result.get('items', [])
    return question_list_items


def filter_recent_form_responses(cutoff_date: datetime = None, filter_respondent: str = None):
    responses = get_form_responses()

    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    # cutoff_date = cutoff_date or yesterday

    filtered_responses = []
    for response in responses:
        reponse_datetime = isoparse(response['lastSubmittedTime'])
        if cutoff_date is None or reponse_datetime.replace(tzinfo=None) > cutoff_date:
            if filter_respondent is None or response['respondentEmail'] == filter_respondent:
                filtered_responses.append(response)
    return filtered_responses


# helper utils

def merge_form_questions_and_responses(questions, responses):
    merged_data = []

    # for each question, pull each person's response
    for question in questions:
        merged_question_data = {
            'questionTitle': question['title'],
            'questionId': question['questionItem']['question']['questionId'],
            'responses': {}
            # TODO: add scale for scaleQuestions
        }

        for response in responses:
            respondent = response['respondentEmail']
            raw_q_ans = response['answers'].get(merged_question_data['questionId'], None)
            ans = raw_q_ans.get('textAnswers', {})['answers'][0]['value']

            merged_question_data['responses'][respondent] = ans

        merged_data.append(merged_question_data)

    return merged_data

if __name__ == '__main__':
    responses = filter_recent_form_responses()
    # check both answered
    if (len(responses) >= 2):
        print(merge_form_questions_and_responses(get_form_questions(), responses))