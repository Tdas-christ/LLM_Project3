from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from transformers import AutoTokenizer
from langchain_community.llms import Ollama # Ollama enables us to run large language models locally, automatically does the compression
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
#import torch
import speech_recognition as sr
import subprocess
import os


app = Flask(__name__)

# Initialize tokenizer and model
#tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn', )
#model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')


model = Ollama(model="llama2") # Make sure 'llama2' is the correct model identifier



# Specify device (CPU or GPU)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)


# # Function to generate text
# def generate_text(input_text):
#     # Define the prompt template
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", "You are a task breakdown expert. Break down the task into a detailed step-by-step guide."),
#             ("user", "Task: {question}")
#         ]
#     )


#     # Tokenize and move inputs to the correct device
#     inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
    
#     # # Adjust generation settings to allow more detailed output
#     # summary_ids = model.generate(
#     #     inputs,
#     #     max_length=250,  # Increase the max_length for more detailed output
#     #     length_penalty=2.0,
#     #     num_beams=5,  # Increase num_beams for better quality output
#     #     early_stopping=True,
#     #     no_repeat_ngram_size=2  # To prevent repetition
#     # )
    
def generate_text(input_text):

    model = Ollama(model="llama2") 
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a task breakdown expert. Break down the task into a detailed step-by-step guide. Please format each step as a bullet point."),
            ("user", "Task: {question}\n\nProvide the steps as bullet points.")
        ]
    )

    outputparser = StrOutputParser()
    chainSec = prompt | model | outputparser

    try:
        output_text = chainSec.invoke({'question': input_text})
        print("Generated Text:", output_text)  # Debugging output
        return output_text
    except Exception as e:
        print(f"Error in generate_text: {e}")  # Debugging output
        return "Error generating text"


# Define the function to format the output
def format_output(input_text):
    # Convert numbered steps to bullet points
    text = generate_text(input_text)
    print(f"Generated text: {text}")  # Debugging line
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip().startswith('Step'):
            formatted_lines.append('\n* ' + line)
        else:
            formatted_lines.append(line)
    formatted_text = '\n'.join(formatted_lines)
    print(f"Formatted text: {formatted_text}")  # Debugging line
    return formatted_text

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
with app.app_context():
    db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)

@app.route("/")
def home():
    todo_list = Todo.query.all()
    error_message = request.args.get("error")
    return render_template("base.html", todo_list=todo_list, error=error_message)

@app.route("/tasks", methods=["GET"])
def get_tasks():
    todo_list = Todo.query.all()
    tasks = [{'id': todo.id, 'title': todo.title, 'complete': todo.complete} for todo in todo_list]
    return jsonify(tasks)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    if not title.strip():
        # Optionally: redirect to home with an error message
        return redirect(url_for("home", error="You need to enter a task."))
    
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/enrich/<int:todo_id>")
def enrich(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    
    try:
        gen = format_output(todo.title)
        print(f"Generated breakdown: {gen}")  # Debugging line
        todo.title = todo.title + " (" + gen + ")"
        db.session.commit()
    except Exception as e:
        print(f"Error: {e}")  # Debugging line
        return redirect(url_for("home", error=str(e)))

    return redirect(url_for("home"))

@app.route("/process_voice", methods=["POST"])
def process_voice():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    if not audio_file.filename.endswith('.wav'):
        return jsonify({'error': 'Unsupported audio format. Please upload a .wav file.'}), 400

    # Save the file temporarily
    temp_input_path = "temp_input.wav"
    temp_output_path = "temp_output.wav"
    audio_file.save(temp_input_path)

    # Convert the audio file using FFmpeg
    try:
        subprocess.run(['ffmpeg', '-i', temp_input_path, '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', temp_output_path], check=True)
    except subprocess.CalledProcessError:
        return jsonify({'error': 'Error converting audio file'}), 500

    # Process the converted file
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_output_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'}), 400
    except sr.RequestError:
        return jsonify({'error': 'Error with the speech recognition service'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Clean up temporary files
    os.remove(temp_input_path)
    os.remove(temp_output_path)

    # Create a new task from the recognized text
    new_todo = Todo(title=text, complete=False)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'text': text, 'id': new_todo.id, 'title': new_todo.title}), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
