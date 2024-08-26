# ToDoGenie: A Voice-Enabled To-Do List Application

## Project Overview

ToDoGenie is an innovative to-do list application designed to streamline task management using both traditional text input and advanced voice recognition technology. The application leverages Flask for server-side logic, Semantic UI for a sleek and responsive user interface, and SQLite for efficient task storage and management. Key features include converting voice recordings to text, enriching task descriptions with detailed instructions using the Ollama LLM, and managing tasks effectively.

![image](https://github.com/user-attachments/assets/9e5e1ad0-e6d2-4142-8bec-5ae5845e8b7c)


## Key Features

- **Voice Input for Tasks**: Record and send voice recordings that are converted into text and added as tasks to your to-do list.
- **Text Input for Tasks**: Directly enter tasks into a text field and add them to the list.
- **Task Enrichment**: Generate detailed, step-by-step instructions for tasks using the Ollama LLM to enhance task descriptions.
- **Task Management**: View, update, and delete tasks from the list.
- **User Feedback**: Provides real-time error handling and informative messages.

## Technologies Used

- **Frontend**: 
  - **HTML** and **CSS**: Basic web technologies used to create and style the user interface.
  - **JavaScript**: Enhances interactivity, including handling voice recording and playback.
  - **Semantic UI**: A CSS framework for creating a responsive and user-friendly interface.

- **Backend**: 
  - **Flask**: A lightweight Python web framework used for handling HTTP requests and managing server-side logic.

- **Database**: 
  - **SQLite**: A serverless, self-contained SQL database engine used to store and manage to-do tasks.

- **Voice Processing**: 
  - **SpeechRecognition**: Python library used to convert speech to text.
  - **FFmpeg**: A multimedia framework used to handle audio file formats and conversions.

- **Text Generation**: 
  - **Ollama LLM**: A language model used to generate detailed instructions and enhance task descriptions.

## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/todogenie.git
   cd todogenie
