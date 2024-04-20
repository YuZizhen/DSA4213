import pandas as pd
import gform_functions as gf
import question_format_conversion as qnformat
from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import os
import ast

# Import questions, update here for actual input
#### For testing #############
with open('sample_output_selected.txt', 'r') as input_file:
    llm_output = input_file.read()

content = ast.literal_eval(llm_output)

#### For connection #############
# content = ast.literal_eval(llm_output.content)

# question_list = qnformat.format_question(content)

question_list = qnformat.format_question_from_selected(content)



######################################
####### Authentication ###############
######################################

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
####### Authentication Done #########
######################################

result = gf.create_new_quiz('test function', form_service = form_service)
form_id = result["formId"]

for question in question_list:
    cur_qn = gf.create_new_qn(question)
    cur_result = gf.add_qn(cur_qn, form_service = form_service, form_id=form_id)
