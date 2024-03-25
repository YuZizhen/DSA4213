###################################################
############ Below for quiz generation ############
###################################################


def create_new_quiz(title, form_service):
    '''
    Input str  `title`, initialized form_services.
    Output new form info with quiz setting.
    Access new form ID by output["formId"] for further operations.
    
    '''
    NEW_FORM = {
        "info": {
            "title": str(title)
            }
        }
    # Creates the initial form
    result = form_service.forms().create(body=NEW_FORM).execute()


    # JSON to convert the form into a quiz
    quiz_update = {
        "requests": [
            {
                "updateSettings": {
                    "settings": {"quizSettings": {"isQuiz": True}},
                    "updateMask": "quizSettings.isQuiz",
                }
            }
        ]
    }

    # Converts the form into a quiz
    question_setting = (
        form_service.forms()
        .batchUpdate(formId=result["formId"], body=quiz_update)
        .execute()
    )

    # Print the result to see it's now a quiz
    getresult = form_service.forms().get(formId=result["formId"]).execute()

    return getresult




def create_new_qn(qn_dict):
    '''
    Input question in dictionary form.
    Sample qn:
        {"title":"str xxx",
        "correct_answer":"str xxx",
        "incorrect_answer":["str1", "str2", "str3"]        
        }

    Output a NEW_QUESTION Object for google form.
    '''

    qn_title = qn_dict["title"]
    correct_answer = qn_dict["correct_answer"]
    incorrect_answer = qn_dict["incorrect_answer"]

    NEW_QUESTION = {
        "requests":[
            {
                "createItem":{
                    "item":{
                        "title":qn_title,
                        "questionItem":{
                            "question":{
                                "required":True,
                                "grading":{
                                    "pointValue": 1,
                                    "correctAnswers":{
                                        "answers":[
                                            {"value":correct_answer}
                                        ]
                                    }

                                },
                                "choiceQuestion":{
                                    "type":"RADIO",
                                    "options":[
                                        {"value": incorrect_answer[0]},
                                        {"value": incorrect_answer[1]},
                                        {"value": incorrect_answer[2]} ,
                                        {"value":correct_answer}
                                    ],
                                    "shuffle": True
                                }

                            }
                        }
                    },
                    "location":{"index" : 0},
                }
            }
        ]
    }
    return NEW_QUESTION


def add_qn(qn, form_service, form_id):
    '''
    Adding a quiz item to existing google form.
    input `qn` is the output from create_new_question. `form_id` being an existing quiz form id.
    Update google form.
    Output google form result, access by output]["formID].

    '''
    # Adds the question to the form
    question_setting = (
        form_service.forms()
        .batchUpdate(formId=form_id, body=qn )
        .execute()
    )


    # Prints the result to show the question has been added
    result = form_service.forms().get(formId=form_id).execute()
    return result

###################################################
############ Below for quiz retrieval ############
###################################################