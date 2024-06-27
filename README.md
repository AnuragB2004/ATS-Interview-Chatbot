# ATS Interview Chatbot

This project is an ATS (Applicant Tracking System) Interview Chatbot designed to assist in automating the recruitment process. The chatbot uses Azure services for natural language processing and generates job-specific interview questions based on the job description. It also evaluates candidate responses for fitment and sentiment analysis.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

The ATS Interview Chatbot is designed to streamline the hiring process by automating resume screening, question generation, and candidate evaluation. It uses Azure Cognitive Services for extracting key phrases and performing sentiment analysis.

## Features

- Extract text from resumes in PDF format.
- Preprocess and compare resumes with job descriptions.
- Generate interview questions based on job descriptions.
- Conduct interviews and capture candidate responses.
- Analyze candidate responses for keyword matches and sentiment.
- Verify candidate identity based on resume information.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework.
- **Python**: The programming language used for backend logic.
- **Azure Cognitive Services**: Used for text analytics and sentiment analysis.
- **PyPDF2**: For extracting text from PDF resumes.
- **NLTK**: For natural language processing tasks.
- **Transformers (Hugging Face)**: For text generation using GPT-2.
- **scikit-learn**: For calculating text similarity.
- **dotenv**: For loading environment variables.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/ats-interview-chatbot.git
    cd ats-interview-chatbot
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory with the following content:

    ```plaintext
    AZURE_LANGUAGE_ENDPOINT="https://your-azure-endpoint.cognitiveservices.azure.com/"
    AZURE_LANGUAGE_KEY="your-azure-key"
    ```

5. **Download NLTK data:**

    ```bash
    python -m nltk.downloader stopwords punkt
    ```

6. **Run the application:**

    ```bash
    flask run
    ```

## Usage

1. **Start the Flask server:**

    ```bash
    flask run
    ```

2. **Access the application:**

    Open your web browser and go to `http://127.0.0.1:5000`.

3. **Upload a job description:**

    Enter the job description in the provided form.

4. **Receive the best matching resume and interview questions:**

    The system will provide the best matching resume and generate interview questions based on the job description.

5. **Conduct the interview:**

    Ask the generated questions to the candidate and record their responses.

6. **Analyze candidate responses:**

    The system will analyze the candidate's responses for keyword matches and sentiment to provide an overall fitment score.

## Endpoints

- **GET /**:
  - Render the index page.
- **POST /search_resume**:
  - Search for the best matching resume based on the job description.
- **POST /verify_candidate**:
  - Verify the candidate's identity based on provided information.
- **GET /interview**:
  - Render the interview page.
- **POST /analyze_interview**:
  - Analyze the candidate's interview responses.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- The project utilizes [Azure Cognitive Services](https://azure.microsoft.com/en-us/services/cognitive-services/).
- Special thanks to the contributors of open-source libraries and tools used in this project.

https://github.com/AnuragB2004/ATS-Interview-Chatbot/assets/105806479/fb7985c8-c7dc-4d47-95b6-066f48ed8dc2

