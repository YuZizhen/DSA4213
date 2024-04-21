import pandas as pd
import re

# count
def format_question(list_of_list):
    '''
    convert a list of list into list of dictionaries
    [[x,[x,x,x],x],...] ---> [{xxx:xxx, xxx:[x,x,x],xxx:x},...]
    
    Input: A list of list, refer to prompts set 4 formatting 1
    Output: A list of dictionaries, as required by gform_funcitons.py
    
    '''
    count_questions = len(list_of_list)
    output_list = []
    dict_tempt = {"title":"", "correct_answer":"", "incorrect_answer":[]}
    for i in range(0,count_questions):
        cur_dict = dict_tempt.copy()
        cur_dict["title"] = list_of_list[i][0]
        cur_dict["correct_answer"] = list_of_list[i][2]
        cur_dict["incorrect_answer"] = [item for item in list_of_list[i][1] if item != list_of_list[i][2]]
        output_list += [cur_dict,]

    return output_list

def format_question_from_selected(list_of_string):
    '''
    convert a list of string into list of dictionaries
    [xxxx,xxxx,xxxx,...] ---> [{xxx:xxx, xxx:[x,x,x],xxx:x},...]
    
    Input: A list of string, selected MCQ from the LLM, printing format on web app
    Output: A list of dictionaries, as required by gform_funcitons.py
    
    '''

    # count_questions = len(list_of_string)
    output_list = []
    for question in list_of_string:
        split_items = re.split(r'\n\n', question)
        split_items_cleaned = [item.strip() for item in split_items if item.strip()]

        # Extract title
        title = split_items_cleaned[0].strip('*')

        # Extract correct answer index and text
        correct_answer_index = int(split_items_cleaned[-1].split(':')[-1].strip()) - 1
        correct_answer_text = split_items_cleaned[correct_answer_index + 1].split('. ')[1]

        # Extract incorrect answers and remove the correct answer from the list
        incorrect_answers = []
        for i, item in enumerate(split_items_cleaned[1:-1]):
            if i != correct_answer_index:
                incorrect_answers.append(item.split('. ')[1])

        # Construct dictionary
        question_dict = {
            "title": title,
            "correct_answer": correct_answer_text,
            "incorrect_answer": incorrect_answers
        }
        output_list += [question_dict,]
    return output_list


