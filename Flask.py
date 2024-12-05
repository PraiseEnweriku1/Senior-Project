from flask import Flask, request, jsonify, render_template, session
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # You need this for session management

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fine-tuned model ID (replace with your actual model ID)
FINE_TUNED_MODEL = 'ft:gpt-4o-mini-2024-07-18:personal::ADXHfnAj'

# Helper function to check for semester and return the schedule
def get_schedule_for_semester(prompt):
    prompt_lower = prompt.lower()
    if '1st semester' in prompt_lower or 'first semester' in prompt_lower:
        session['asked_schedule'] = True  # Remember that the user asked for the schedule
        return "Freshman year (1st semester) Classes:\n" \
               "- COSC 111: Intro to Computer Science I\n" \
               "- ENGL 101: Freshman Composition I\n" \
               "- MATH 241: Calculus I\n" \
               "- XXXX: General Education\n" \
               "- ORNS 106: Freshman Orientation for SCMNS Majors"
    
    if '2nd semester' in prompt_lower or 'second semester' in prompt_lower:
        session['asked_schedule'] = True  # Remember that the user asked for the schedule
        return "Freshman year (2nd semester) Classes:\n" \
               "- COSC 112: Intro to Computer Science II\n" \
               "- ENGL 102: Freshman Composition II\n" \
               "- MATH 242: Calculus II\n" \
               "- XXXX: General Education\n" \
               "- COSC 220: Data Structures"
    
    return None

def test_new_model(prompt):
    try:
        # First check if the prompt is related to the schedule creator
        schedule_response = get_schedule_for_semester(prompt)
        if schedule_response:
            return schedule_response
        
        # If not schedule-related, use OpenAI model
        response = openai.ChatCompletion.create(
            model=FINE_TUNED_MODEL,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant that assists with Python (coding) and only Python.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/')
def index():
    return render_template('index.html')

# Route to handle chat requests
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()

    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request. 'message' field is required."}), 400

    user_message = data['message']
    
    # Check if the user has asked for the schedule before
    asked_schedule = session.get('asked_schedule', False)
    
    # Get response from the model
    assistant_response = test_new_model(user_message)

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if the user requested the Morgan State logo
    image_url = ''
    if 'show logo' in user_message.lower():  # Adjust the keyword as needed
        image_url = 'https://upload.wikimedia.org/wikipedia/en/8/8f/Morgan_State_Bears_logo.svg'  # Logo URL

    return jsonify({
        "message": assistant_response,
        "imageUrl": image_url,
        "timestamp": timestamp,
        "asked_schedule": asked_schedule  # Return if the user already asked for the schedule
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
