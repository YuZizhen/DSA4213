# Request body for creating a form

def create_new_form(title):
    NEW_FORM = {
        "info": {
            "title": str(title)
            }
        }
    return NEW_FORM



def create_gform_question(question_obj):
    """
    Takes a question python object and returns the JSON
    ready to use building the Google Form

    Args:
        question_obj: A Question object

    """

    return {
        "createItem": {
            "item": {
                "title": question_obj.get_question(),
                "questionItem": {
                    "question": {
                        "required": True,
                        "grading": {
                            "pointValue": 1,
                            "correctAnswers": {
                                "answers":
                                [{"value": question_obj.get_correct_answer()}]
                            },
                        },
                        "choiceQuestion": {
                            "type": "RADIO",
                            "options": [
                                    {"value":
                                     question_obj.get_correct_answer()},
                                    {"value":
                                     question_obj.get_incorrect_answers()[0]},
                                    {"value":
                                     question_obj.get_incorrect_answers()[1]},
                                    {"value":
                                     question_obj.get_incorrect_answers()[2]}
                            ],
                            "shuffle": True
                        }
                    }
                },
            },
            "location": {
                "index": 0
            }
        }
    }
