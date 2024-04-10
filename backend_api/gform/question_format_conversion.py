import pandas as pd

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
