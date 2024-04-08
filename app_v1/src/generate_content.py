import ast
import os
import asyncio
from h2o_wave import on, ui, Q
from h2ogpte import H2OGPTE
from loguru import logger
from h2ogpte.types import ChatMessage, PartialChatMessage
from wave_utils import clear_cards
import logging
import json
# logging.basicConfig(level=logging.DEBUG)

#default number shown when app start
def initialize_generate_content_client(q):
    logger.info("")
    q.client.chapter_name = ''
    q.client.question_quantity = '1'
    if 'current_selected_questions' not in q.client:
        q.client.current_selected_questions = []

#range of number availbale for selection
async def side_input_generate_content(q):
    logger.info("")
    clear_cards(q)
    chapters = ['The Holocaust', 'Hundred Years War', 'War and the Other', 'The Vikings']
    quantities = [str(i) for i in range(1, 11)]

    #main ui for USER INPUT on the left
    q.page['help'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Generate Questions</b>"),
            ui.text("Select the chapter name and the number of questions to generate."),
            ui.dropdown(name='chapter_name', label='Chapter Name', value=q.client.chapter_name, choices=[ui.choice(name=c, label=c) for c in chapters]),
            ui.dropdown(name='question_quantity', label='Number of Questions', value=q.client.question_quantity, choices=[ui.choice(name=q, label=q) for q in quantities]),
            ui.inline(justify='center', items=[
                ui.button(name='generate_prompt', label='Generate Questions', primary=True)
            ]),
        ]
    )

#PREVIOUS DIAPLAYING CONTENT DIRECTYLY ON WEBPAGE 'generate_prompt'
#on clicking button, send USER prompt to GPT
#@on()
#async def generate_prompt(q: Q):
#    logger.info("")
#    prompt = f"Generate {q.client.question_quantity} questions for Chapter {q.client.chapter_number}."
#    q.client.prompt = prompt
#   q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)
#   q.client.llm_response = await q.run(chat, q.client.chatbot_interaction)
#
#    items = [ui.text('Select the questions you are interested in:')]
#    for index, question in enumerate(q.client.llm_response):
#        question_text = question[0][0]  # Assuming the question is the first element
#        items.append(ui.checkbox(name=f'select_{index}', label=question_text, value=False))

#    items.append(ui.button(name='submit_selections', label='Submit Selections', primary=True))
    
#    q.page["questions_with_selections"] = ui.form_card(box="center", items=items)
#    await q.page.save()

@on()
async def generate_prompt(q: Q):
    logger.info("Generating questions")
    prompt = f"Generate {q.client.question_quantity} MCQ questions based on given documents."
    q.client.prompt = prompt
    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt, chapter_name=q.client.chapter_name, question_quantity=q.client.question_quantity)
    await q.run(chat, q.client.chatbot_interaction)
    print(q.client.chatbot_interaction.llm_response)
    print(type(q.client.chatbot_interaction.llm_response))
    response = ast.literal_eval(q.client.chatbot_interaction.llm_response)
    print(type(response))
    q.client.llm_response = response
    
    #q.client.llm_response = [
    #     ["What was the objective of Total War according to the document?",
    #      ["1. The partial defeat of enemy physical power", "2. The complete defeat of enemy physical power",
    #       "3. The defeat of enemy economy", "4. The defeat of enemy military power"], "4. The defeat of enemy military power"]] 

    # items = []
    # for index, (question, options, correct_answer_index) in enumerate(q.client.llm_response):
    #     items.append(ui.text(f"**{question[0]}**"))
    #     for option in options:
    #         items.append(ui.text(option))
    #     correct_option = options[correct_answer_index[0] - 1] 
    #     items.append(ui.text(f"Correct answer: {correct_option}"))  
    #     items.append(ui.checkbox(name=f'select_{index}', label='Select this question', value=False))
    #     items.append(ui.text("<br/>"))
        
    # items.append(ui.button(name='submit_selections', label='Submit Selections', primary=True))

    # q.page["questions_with_selections"] = ui.form_card(box="center", items=items)
    # await q.page.save()

    items = []
    for question_index in range(0, len(q.client.llm_response)):
        question = q.client.llm_response[question_index]
        label = 'Question ' + str(question_index + 1) + ": " + question[0]
        
        items.append(ui.checkbox(name=f'select_{question_index}', label=f"{label}", value=False))
        correct_option = question[2]
        correct_option_index = 0
        for option_index in range(0, len(question[1])):
            items.append(ui.text(str(option_index + 1) + ". " + question[1][option_index]))
            if question[1][option_index] == correct_option:
                correct_option_index = str(option_index + 1)
        
        items.append(ui.text("Correct answer: " + correct_option_index))  
        
        items.append(ui.text("<br/>"))
        
    items.append(ui.button(name='submit_selections', label='Submit Selections', primary=True))

    q.page["questions_with_selections"] = ui.form_card(box="center", items=items)
    await q.page.save()

@on('submit_selections')
async def submit_selections(q: Q):
    new_selections = []

    for index, question_data in enumerate(q.client.llm_response):
        try:
            selected = q.args[f'select_{index}']
            if selected:
                question_text = f"**{question_data[0]}**\n\n"  # Question text
                options_text = "\n\n".join([f"   {opt_index + 1}. {option}" for opt_index, option in enumerate(question_data[1])])  # Options list
                correct_option = question_data[2]  # Correct option is now directly a string
                correct_answer_text = f"\nCorrect answer: {correct_option}"

                
                # Construct the details for the selected question
                selected_question_details = f"{question_text}{options_text}\n\n{correct_answer_text}\n\n"
                
                # Check if this selected question detail is already in the list to avoid duplication
                if selected_question_details not in q.client.current_selected_questions:
                    new_selections.append(selected_question_details)
        except KeyError:
            continue  # If the checkbox was not found, just continue to the next
    
    # Update the list of selected questions with any new selections
    q.client.current_selected_questions.extend(new_selections)
    
    # Display the updated list of selected questions
    if q.client.current_selected_questions:
        items = [ui.text(question) for question in q.client.current_selected_questions]
        items.append(ui.button(name='reset_selections', label='Reset Selections', primary=False))
        q.page['selected_questions'] = ui.form_card(box='right', items=items)
    else:
        q.page['selected_questions'] = ui.form_card(box='right', items=[ui.text('No questions selected.')])

    await q.page.save()









#async def stream_updates_to_ui(q: Q):
#    """
#    Update the app's UI every 0.1 second with values from our chatbot interaction
#    :param q: The query object stored by H2O Wave with information about the app and user behavior.
#    """
#    while q.client.chatbot_interaction.responding:
#        q.page["generated_questions"].generated_questions.content = q.client.chatbot_interaction.content_to_show
#        await q.page.save()
#        await q.sleep(0.1)
#
#    q.page["generated_questions"].generated_questions.content = q.client.chatbot_interaction.content_to_show
#    await q.page.save()





def chat(chatbot_interaction):
    """
    Send the user's message to the LLM and save the response
    :param chatbot_interaction: Details about the interaction between the user and the LLM
    :param chat_session_id: Chat session for these messages
    """

    def stream_response(message):
        """
        This function is called by the blocking H2OGPTE function periodically for updating the UI
        :param message: response from the LLM, this is either a partial or completed response
        """
        chatbot_interaction.update_response(message)

    # api_key = 'sk-xjaaELLATk2Z8apfbv1nozXFTrHmQDuQHOLsOv5V3SR6wy0U'
    api_key = 'sk-s664ThZtgjVvGG3Fl1mGN9gOVnfpg85dZBwMWQhb8YBqXbOT'
    # client = H2OGPTE(address=os.getenv("H2OGPTE_URL"), api_key=os.getenv("H2OGPTE_API_TOKEN"))

    try:
        client = H2OGPTE(address='https://h2ogpte.genai.h2o.ai', api_key=api_key)

        # collection_id = client.create_collection("temp", "")
        # chat_session_id = client.create_chat_session(collection_id)
        collection_names = [item.name for item in client.list_recent_collections(0, 1000)]
        target_chapter_name =  chatbot_interaction.chapter_name
        curr_collection_id = [item.id for item in client.list_recent_collections(0, 1000) if item.name == target_chapter_name][0]
        chat_session_id = client.create_chat_session(curr_collection_id)
        
        with open('../../backend_api/prompts_4/system_prompt.txt', 'r') as file:
            system_prompt = file.read()

        with open('../../backend_api/prompts_4/pre_prompt_query.txt', 'r') as file:
            pre_prompt_query = file.read()

        with open('../../backend_api/prompts_4/prompt_query.txt', 'r') as file:
            prompt_query = file.read()

        #save the session into "response" 
        with client.connect(chat_session_id) as session:
            session.query(
                message = chatbot_interaction.user_message,
                system_prompt = system_prompt,
                pre_prompt_query = pre_prompt_query,
                prompt_query = prompt_query,
                timeout=60,
                callback=stream_response,
                llm_args={"temperature": 0.9},
                llm = 'gpt-35-turbo-1106',
            )

        #client.delete_chat_sessions([chat_session_id])
        output = chatbot_interaction.llm_response
        # print(output)

        return output

    except Exception as e:
        logger.error(e)
        return f"Some error occur :(("


class ChatBotInteraction:
    def __init__(self, user_message, chapter_name, question_quantity) -> None:
        self.user_message = user_message
        self.chapter_name = chapter_name
        self.question_quantity = question_quantity
        self.responding = True

        self.llm_response = ""
        self.content_to_show = "🟡"

    def update_response(self, message):
        if isinstance(message, ChatMessage):
            self.content_to_show = message.content
            self.responding = False
        elif isinstance(message, PartialChatMessage):
            if message.content != "#### LLM Only (no RAG):\n":
                self.llm_response += message.content
                self.content_to_show = self.llm_response + " 🟡"
