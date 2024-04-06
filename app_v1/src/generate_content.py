import os
import asyncio
from h2o_wave import on, ui, Q
from h2ogpte import H2OGPTE
from loguru import logger
from h2ogpte.types import ChatMessage, PartialChatMessage
from wave_utils import clear_cards
import logging
logging.basicConfig(level=logging.DEBUG)

#default number shown when app start
def initialize_generate_content_client(q):
    logger.info("")
    q.client.chapter_number = '1'
    q.client.question_quantity = '1'

#range of number availbale for selection
async def side_input_generate_content(q):
    logger.info("")
    clear_cards(q)
    chapters = [str(i) for i in range(1, 11)]
    quantities = [str(i) for i in range(1, 11)]

    #main ui for USER INPUT on the left
    q.page['help'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Generate Questions</b>"),
            ui.text("Select the chapter number and the number of questions to generate."),
            ui.dropdown(name='chapter_number', label='Chapter Number', value=q.client.chapter_number, choices=[ui.choice(name=c, label=c) for c in chapters]),
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
    #logger.info("Generating questions")
    #prompt = f"Generate {q.client.question_quantity} questions for Chapter {q.client.chapter_number}."
    #q.client.prompt = prompt
    #q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)
    #q.client.llm_response = await q.run(chat, q.client.chatbot_interaction)
    
    q.client.llm_response = [
        [["What was the objective of Total War according to the document?"],
         ["1. The partial defeat of enemy physical power", "2. The complete defeat of enemy physical power",
          "3. The defeat of enemy economy", "4. The defeat of enemy military power"], [2]],
        [["What was the means of Total War according to the document?"], 
         ["1. Using minimal force", "2. Using whatever is required to achieve victory", "3. Avoiding battle", "4. Negotiating with the enemy"], [2]], 
        [["Question 3"], 
         ["1. 3A", "2. 3B", "3. 3C", "4. 3D"], [4]], 
        [["Question 4"], 
         ["1. 4A", "2. 4B", "3. 4C", "4. 4D"], [2]], 
    ] 

    items = []
    for index, (question, options, correct_answer_index) in enumerate(q.client.llm_response):
        items.append(ui.text(f"**{question[0]}**"))
        for option in options:
            items.append(ui.text(option))
        correct_option = options[correct_answer_index[0] - 1] 
        items.append(ui.text(f"Correct answer: {correct_option}"))  
        items.append(ui.checkbox(name=f'select_{index}', label='Select this question', value=False))
        items.append(ui.text("<br/>"))
        
    items.append(ui.button(name='submit_selections', label='Submit Selections', primary=True))

    q.page["questions_with_selections"] = ui.form_card(box="center", items=items)
    await q.page.save()

@on('submit_selections')
async def submit_selections(q: Q):
    current_selected_questions = []

    for index, (question, options, correct_answer_index) in enumerate(q.client.llm_response):
        try:
            selected = q.args[f'select_{index}']
        except KeyError:
            selected = False

        if selected:
            question_text = f"**{index + 1}. {question[0]}**\n"
            options_text = "\n".join([f"   {opt}" for opt in options])
            correct_option = options[correct_answer_index[0] - 1]
            correct_answer_text = f"\nCorrect answer: {correct_option}"

            selected_question_details = f"{question_text}{options_text}\n\n{correct_answer_text}\n\n"
            current_selected_questions.append(selected_question_details)
            
    if current_selected_questions:
        items = [ui.text(question) for question in current_selected_questions]
        q.page['selected_questions'] = ui.form_card(box='right', items=items)
    else:
        q.page['selected_questions'] = ui.form_card(box='right', items=[ui.text('No questions selected.')])

    # Reset checkboxes
    items = []
    for index, (question, options, correct_answer_index) in enumerate(q.client.llm_response):
        items.append(ui.text(f"{index + 1}. {question[0]}"))
        for option in options:
            items.append(ui.text(option))
        items.append(ui.checkbox(name=f'select_{index}', label='Select this question', value=False))
        correct_option = options[correct_answer_index[0] - 1]
        items.append(ui.text(f"Correct answer: {correct_option}"))
    
    items.append(ui.button(name='submit_selections', label='Submit Selections', primary=True))


    q.page["questions_with_selections"] = ui.form_card(box="center", items=items)

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

        chat_session_id = client.create_chat_session_on_default_collection()
        
        with open('../../backend_api/prompts/system_prompt.txt', 'r') as file:
            system_prompt = file.read()

        with open('../../backend_api/prompts/pre_prompt_query.txt', 'r') as file:
            pre_prompt_query = file.read()

        with open('../../backend_api/prompts/prompt_query.txt', 'r') as file:
            prompt_query = file.read()

        #save the session into "response" 
        with client.connect(chat_session_id) as session:
            response = session.query(
                message = chatbot_interaction.user_message,
                system_prompt = system_prompt,
                pre_prompt_query = pre_prompt_query,
                prompt_query = prompt_query,
                timeout=60,
                callback=stream_response,
            )

        client.delete_chat_sessions([chat_session_id])

        return response

    except Exception as e:
        logger.error(e)
        return f"Some error occur :(("


class ChatBotInteraction:
    def __init__(self, user_message) -> None:
        self.user_message = user_message
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
                
                

