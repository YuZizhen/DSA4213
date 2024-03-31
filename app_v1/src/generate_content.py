import os
import asyncio
from h2o_wave import on, ui, Q
from h2ogpte import H2OGPTE
from loguru import logger
from h2ogpte.types import ChatMessage, PartialChatMessage
from wave_utils import clear_cards

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

#######################Different types of ui samples.###########################
##            ui.textbox(
##                name='weight',
##                label='Your weight in pounds',
##                width='100%',
##                value=q.client.weight,
##
##            ),
##
##            ui.label(label='How tall are you?'),
##
##            ui.inline(justify='around',
##                      items=[
##                          ui.textbox(
##                              name='heightFT',
##                              label='Feet',
##                              width='49%',
##                              value=q.client.heightFt,
##
##                          ),
##                          ui.textbox(
##                              name='heightInch',
##                              label='Inches',
##                              width='49%',
##                              value=q.client.heightInch,
##
##                          ),
##                      ]),
##
##            ui.dropdown(name='conditionLevel', label='How experienced are you?', value=q.client.conditionLevel, choices=[
##                ui.choice(name=i, label=i) for i in conditionLevel]),
##
##            ui.dropdown(name='weekFreq', label='How often do you want to get training per week?', value=q.client.weekFreq, choices=[
##                ui.choice(name=i, label=i) for i in weekFreq]),
##
##            ui.toggle(
##                name='reduceWeight',
##                label='Do you want reduce weight recommendation?',
##                value=q.client.reduceWeight),
##
##            ui.toggle(
##                name='setFtp',
##                label='Do you want improve your FTP?',
##                trigger=True,
##                value=q.client.setFtp),
##
##            ui.inline(
##                justify='center',
##                items=[
##                    ui.textbox(
##                        name='currentFTP',
##                        label='Your current FTP',
##                        width='49%',
##                        value=q.client.currentFTP,
##                        visible=q.client.setFtp
##                    ),
##                    ui.textbox(
##                        name='targetFTP',
##                        label='Your target FTP',
##                        width='49%',
##                        value=q.client.targetFTP,
##                        visible=q.client.setFtp
##                    ),
##                ]
##            ),
##
##            ui.toggle(
##                name='timeGoal',
##                trigger=True,
##                label='Do you want training for a certain number of weeks?',
##                value=q.client.timeGoal),
##
##            ui.inline(
##                justify='center',
##                items=[
##                    ui.textbox(
##                        name='weeks',
##                        label='How many weeks do you want a training plan?',
##                        width='100%',
##                        value=q.client.weeks,
##                        visible=q.client.timeGoal
##                    ),
##                ]
##            ),
##
##
##
##            ui.inline(justify='center', items=[
##                ui.button(
##                      name='generate_prompt',
##                      label='Generate Training Plan',
##                      primary=True)
##            ]),
##
##        ]
##    )
##############################################################################

#on clicking button, send USER prompt to GPT
@on()
async def generate_prompt(q: Q):
    logger.info("")


    prompt = f"Generate {q.client.question_quantity} questions for Chapter {q.client.chapter_number}."
    q.client.prompt = prompt

    q.page["generated_questions"] = ui.form_card(
        box="right",
        items=[
            ui.text(content="", name="generated_questions")
        ]
    )
    
    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt)

    # Prepare our UI-Streaming function so that it can run while the blocking LLM message interaction runs
    update_ui = asyncio.ensure_future(stream_updates_to_ui(q))

    #save the LLM responses in the variable to use parser later on
    q.client.llm_response = await q.run(chat, q.client.chatbot_interaction)
    await update_ui
    await q.page.save()


async def stream_updates_to_ui(q: Q):
    """
    Update the app's UI every 0.1 second with values from our chatbot interaction
    :param q: The query object stored by H2O Wave with information about the app and user behavior.
    """

    while q.client.chatbot_interaction.responding:
        q.page["generated_questions"].generated_questions.content = q.client.chatbot_interaction.content_to_show
        await q.page.save()
        await q.sleep(0.1)

    q.page["generated_questions"].generated_questions.content = q.client.chatbot_interaction.content_to_show
    await q.page.save()


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
