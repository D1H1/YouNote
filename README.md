# YouNote

## Project Overview
YouNote is a dynamic web application designed to help users manage their notes efficiently. Built with Flask, this application supports note-taking, question submission, and real-time note updates. It leverages MongoDB for database operations and integrates OpenAI's GPT model to enhance note-related queries through natural language processing.

## Key Features
- **Note Management:** Create, view, and manage notes dynamically.
- **Question Submission:** Submit questions and get relevant note suggestions based on content.
- **Docker Integration:** Easy deployment with Docker for consistent development and production environments.

## Prerequisites
Before you begin, ensure you have the following installed:
- [Python 3](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Configuration Files
- `config.json`: This file contains sensitive information such as API keys and database URIs. Fill in your specific details here. 
- `resourses/younote-422915-7c24e96257f5.json`: This file contains sensitive information about your google cloud api. Fill in your specific details here. 


## Installation

Clone the repository:

`git clone https://github.com/username/YouNote.git
cd YouNote`

Setting Up a Virtual Environment
(Optional) Set up a Python virtual environment to manage dependencies:

`python -m venv venv`
`source venv/bin/activate`  # On Windows use `venv\Scripts\activate`

Install Dependencies
Install the required Python packages:

`pip install -r requirements.txt`

Deploying with Docker
To deploy the application using Docker, follow these steps:

`docker build -t younote .`

`docker run -p 5000:5000 younote`

Usage
After deployment, navigate to `http://localhost:5000` in your web browser to access the YouNote application. You can add notes, view them, and submit questions through the user interface.

