from h2o_wave import on, ui, Q
from h2ogpte import H2OGPTE
from loguru import logger
from h2ogpte.types import ChatMessage, PartialChatMessage
from wave_utils import clear_cards
import ast
import json
import subprocess

# Show default value when app start
def initialize_generate_content_client(q):
    """
    Iinitialize the default values seen by user in the interface.

    Initialize a list for final output. 
    """
    logger.info("")
    q.client.chapter_name = 'War On Cities Manlia'
    q.client.question_quantity = '3'
    if 'current_selected_questions' not in q.client:
        q.client.current_selected_questions = []


# Range of values availbale for selection
async def side_input_generate_content(q):
    """
    Writes in the loaded chapters into the drop-down list for user to select and defines the range of question numbers user could generate.
    """
    logger.info("")
    clear_cards(q)
    chapters = ['War On Cities Manlia', 'Hundred Years War', 'War and the Other', 'The Vikings', 'The Holocaust']
    quantities = [str(i) for i in range(3, 11)]

    # Main UI for *USER INPUT* on the left
    q.page['help'] = ui.form_card(
        box='left',
        items=[
            ui.text_l("<b>Generate Questions</b>"),
            ui.text("Select the chapter name and the number of questions to generate."),
            ui.dropdown(name='chapter_name', label='Chapter Name', value=q.client.chapter_name, choices=[ui.choice(name=c, label=c) for c in chapters]),
            ui.dropdown(name='question_quantity', label='Number of Questions', value=q.client.question_quantity, choices=[ui.choice(name=q, label=q) for q in quantities]),
            ui.inline(justify='center', items=[ui.button(name='generate_prompt', label='Generate Questions', primary=True)]),
        ]
    )


# main function to generate prompt
@on()
async def generate_prompt(q: Q):
    """
    Create the "Generate Questions" button.

    Defines what is send to the LLM generator for question generation.

    If there is any error in the LLM response, LLM prompt would be send in again to try to get the correct response.

    Parse the LLM response into the middle section of the screen for viewing.

    Checkbox is there for user to select the questions they want.
    """
    if q.page["questions_with_selections"]: #This part here is to ensure the loading screen display correctly when multiple generation is executed
        del q.page["questions_with_selections"]

    logger.info("Generating questions")

    prompt = f"Generate {q.client.question_quantity} MCQ questions based on given documents."
    q.client.prompt = prompt
    q.client.chatbot_interaction = ChatBotInteraction(user_message=q.client.prompt, chapter_name=q.client.chapter_name, question_quantity=q.client.question_quantity)

    max_attempts = 5 #Number of re-tries in case of failure (including initial one)
    attempt_count = 0

    q.page["loading_indicator"] = ui.form_card(
        box="center",
        items=[
            ui.image(path=q.app.load, width="470px", title=""),  
            ui.label("Brewing up some fascinating questions... ☕"),
        ]
    ) # Display the custom loading icon
    
    await q.page.save()

    while attempt_count < max_attempts:
        attempt_count += 1
        await q.run(chat, q.client.chatbot_interaction)

        try:
            response = ast.literal_eval(q.client.chatbot_interaction.llm_response)
            q.client.llm_response = response
        
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

            del q.page["loading_indicator"]

            await q.page.save()

            break

        except (ValueError, IndexError, KeyError):
            if attempt_count < max_attempts:
                logger.warning(f"Attempt {attempt_count}: Incorrect response format. Retrying...")
            else:
                logger.error("Maximum attempts reached. Unable to generate valid questions.")

                del q.page["loading_indicator"]

                q.page["error_message"] = ui.form_card(box="center", items=[ui.text("Error: Unable to generate valid questions. Please try again.")])

                await q.page.save()

#allow user to preview selected questions
@on('submit_selections')
async def submit_selections(q: Q):
    """
    Create the "Submmit Selections" button.

    Pass the checked question to the right side of the app for final review.

    These questions would again come with checkbox for user to remove the selected questions if they wish.
    """
    new_selections = []

    for index, question_data in enumerate(q.client.llm_response):
        try:
            selected = q.args[f'select_{index}']
            if selected:
                question_text = f"**{question_data[0]}**"  # Question text
                options_text = "\n\n".join([f"   {opt_index + 1}. {option}" for opt_index, option in enumerate(question_data[1])])  # Options list
                correct_option = question_data[2]  
                correct_answer_index = question_data[1].index(correct_option) + 1 # Correct option
                
                # Construct the details for the selected question
                selected_question_details = f"{question_text}\n\n{options_text}\n\nCorrect answer: {correct_answer_index}\n\n"                 
                new_selections.append(selected_question_details)

        except KeyError:
            continue
    
    # Update the list of selected questions with any new selections
    q.client.current_selected_questions.extend(new_selections)

    items = []
    for index, question_details in enumerate(q.client.current_selected_questions):
        question_lines = question_details.split('\n\n')
        question_text = question_lines[0]
        options_text = '\n\n'.join(question_lines[1:-2])
        correct_answer_index = question_lines[-2].split(': ')[1]
        
        items.append(ui.inline(items=[
            ui.checkbox(name=f'remove_{index}', label='', value=False),
            ui.text(question_text)
        ]))
        items.append(ui.text(options_text))
        items.append(ui.text(f"Correct answer: {correct_answer_index}"))
        items.append(ui.separator())
    
    if items:
        items.append(ui.button(name='remove_selections', label='Remove Selected', primary=False)) # Add the "Remove Selected" button
        items.append(ui.button(name='generate_file', label='Generate Google Form', primary=True))  # Add the "Generate Google Form" button

        q.page['selected_questions'] = ui.form_card(box='right', items=items)
    else:
        q.page['selected_questions'] = ui.form_card(box='right', items=[ui.text('No questions selected.')])

    await q.page.save()


#function to remove selection
@on('remove_selections')
async def remove_selections(q: Q):
    """
    Create the "Remove Selected" button.

    Removed the checked question on the right side of the app.

    The preview section on the right would be updated.
    """
    updated_selections = []

    for index, question_details in enumerate(q.client.current_selected_questions):
        try:
            remove = q.args[f'remove_{index}']
            if not remove:
                updated_selections.append(question_details)
        except KeyError:
            updated_selections.append(question_details)  # If the checkbox was not found, keep the question
    
    # Update the list of selected questions
    q.client.current_selected_questions = updated_selections
    
    # Display the updated list of selected questions with inline checkboxes
    items = []
    
    for index, question_details in enumerate(q.client.current_selected_questions):
        question_lines = question_details.split('\n\n')
        question_text = question_lines[0]
        options_text = '\n\n'.join(question_lines[1:-2])
        correct_answer_index = question_lines[-2].split(': ')[1]
        
        items.append(ui.inline(items=[
            ui.checkbox(name=f'remove_{index}', label='', value=False),
            ui.text(question_text)
        ]))
        items.append(ui.text(options_text))
        items.append(ui.text(f"Correct answer: {correct_answer_index}"))
        items.append(ui.separator())
    
    if items:
        items.append(ui.button(name='remove_selections', label='Remove Selected', primary=False))
        items.append(ui.button(name='generate_file', label='Generate Google Form', primary=True))

        q.page['selected_questions'] = ui.form_card(box='right', items=items)
    else:
        q.page['selected_questions'] = ui.form_card(box='right', items=[ui.text('No questions selected.')])

    await q.page.save()


#google form generation
@on('generate_file')
async def generate_file(q: Q):
    """
    Create the "Generate Google Form" button.

    Parsed all the preview question into a .txt file named "selected_questions.txt"

    gform_generate.py will be called to start the generation of Google Form
    """
    file_path = '../../backend_api/gform/gform_generate.py'
    save_path = '../../backend_api/gform/selected_questions.txt'

    try:
        with open(save_path, 'w') as file:
            file.write(json.dumps(q.client.current_selected_questions))

        # Run the Python file in a separate process
        subprocess.Popen(['python', file_path])

        # Display a success message
        print("Generation Starting")
    except Exception as e:
        # Display an error message if any exception occurs
        print(f'Error starting file generation: {str(e)}')

    # Remove the loading indicator
    del q.page['loading_indicator']

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

    api_key = 'sk-s664ThZtgjVvGG3Fl1mGN9gOVnfpg85dZBwMWQhb8YBqXbOT'

    try:
        client = H2OGPTE(address='https://h2ogpte.genai.h2o.ai', api_key=api_key)
        target_chapter_name =  chatbot_interaction.chapter_name
        curr_collection_id = [item.id for item in client.list_recent_collections(0, 1000) if item.name == target_chapter_name][0]
        chat_session_id = client.create_chat_session(curr_collection_id)
        
        with open('../../backend_api/prompts_4/system_prompt.txt', 'r') as file:
            system_prompt = file.read()

        with open('../../backend_api/prompts_4/pre_prompt_query.txt', 'r') as file:
            pre_prompt_query = file.read()

        with open('../../backend_api/prompts_4/prompt_query.txt', 'r') as file:
            prompt_query = file.read()

        # Save the session into "response" 
        with client.connect(chat_session_id) as session:
            session.query(
                message = chatbot_interaction.user_message,
                system_prompt = system_prompt,
                pre_prompt_query = pre_prompt_query,
                prompt_query = prompt_query,
                timeout=60,
                callback=stream_response,
                llm_args={"temperature": 0.5},
                llm = 'gpt-4-1106-preview',
            )
        output = chatbot_interaction.llm_response
        return output

    except Exception as e:
        logger.error(e)
        return f"Some error occur :(("

#Defining a chatbotinteraction class
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
