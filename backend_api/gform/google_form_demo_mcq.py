from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import gform_functions as gf

SCOPES = "https://www.googleapis.com/auth/forms.body"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage("token.json")
creds = None
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
  creds = tools.run_flow(flow, store)

form_service = discovery.build(
    "forms",
    "v1",
    http=creds.authorize(Http()),
    discoveryServiceUrl=DISCOVERY_DOC,
    static_discovery=False,
)

######################################
######################################

result = gf.create_new_quiz('test function', form_service = form_service)
form_id = result["formId"]
# form_id = "1WZlajQ0OsB_t6aUVUqPJd48Y0utRlRQyTfFVn2tt0v0"
sample_qn = {
  "title" : "qn1: select number 1",
  "correct_answer": "1",
  "incorrect_answer":["2", "3", "4"]

}

new_qn = gf.create_new_qn(sample_qn)
qn1_result = gf.add_qn(new_qn, form_service = form_service, form_id=form_id)



# form = {
#     "info": {
#         "title": "My new quiz",
#     }
# }
# # Creates the initial form
# result = form_service.forms().create(body=form).execute()

# # JSON to convert the form into a quiz
# update = {
#     "requests": [
#         {
#             "updateSettings": {
#                 "settings": {"quizSettings": {"isQuiz": True}},
#                 "updateMask": "quizSettings.isQuiz",
#             }
#         }
#     ]
# }

# # Converts the form into a quiz
# question_setting = (
#     form_service.forms()
#     .batchUpdate(formId=result["formId"], body=update)
#     .execute()
# )

# # Print the result to see it's now a quiz
# getresult = form_service.forms().get(formId=result["formId"]).execute()
# print(getresult)

# ############################3

# # Request body to add a video item to a Form
# update = {
#     "requests": [
#         {
#             "createItem": {
#                 "item": {
#                     "title": "Homework video",
#                     "description": "Quizzes in Google Forms",
#                     "videoItem": {
#                         "video": {
#                             "youtubeUri": (
#                                 "https://www.youtube.com/watch?v=Lt5HqPvM-eI"
#                             )
#                         }
#                     },
#                 },
#                 "location": {"index": 0},
#             }
#         }
#     ]
# }

# # Add the video to the form
# question_setting = (
#     form_service.forms()
#     .batchUpdate(formId=getresult["formId"], body=update)
#     .execute()
# )

# ###########################

NEW_QUESTION = {
    "requests": [
        {
            "createItem": {
                "item": {
                    "title": "Which of these singers was not a member of Destiny's Child?",
                    "questionItem": {
                        "question": {
                            "required": True,
                            "grading": {
                                "pointValue": 2,
                                "correctAnswers": {
                                    "answers": [{"value": "Rihanna"}]
                                },
                                "whenRight": {"text": "You got it!"},
                                "whenWrong": {"text": "Sorry, that's wrong"}
                            },
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [
                                    {"value": "Kelly Rowland"},
                                    {"value": "Beyoncé"},
                                    {"value": "Rihanna"},
                                    {"value": "Michelle Williams"}
                                ]
                            }
                        }
                    }
                },
                "location": {"index": 0}, 
            }

        }
    ]
}


# # Adds the question to the form
# question_setting = (
#     form_service.forms()
#     .batchUpdate(formId=getresult["formId"], body=NEW_QUESTION )
#     .execute()
# )


# # Prints the result to show the question has been added
# result = form_service.forms().get(formId=getresult["formId"]).execute()
# print(result)