from flask import Flask, render_template, request, jsonify
import os
import re
import random
import PyPDF2
import nltk
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from dotenv import load_dotenv
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline, set_seed
import secrets
from flask import session

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

AZURE_LANGUAGE_ENDPOINT = "https://eychatbot.cognitiveservices.azure.com/"
AZURE_LANGUAGE_KEY = "c6c221ee17044fa9bf5f3ee1eb105814"

# Load environment variables from .env file
load_dotenv()

# Download required NLTK data
nltk.download('stopwords')
nltk.download('punkt')

# Set default resume folder path
RESUME_FOLDER = r"D:\EY\ATS Chatbot\Resumes"

# Load a pre-trained text generation model (e.g., GPT-2)
generator = pipeline('text-generation', model='gpt2')
set_seed(42)  # for reproducibility

# Initialize the Text Analytics client
credential = AzureKeyCredential(AZURE_LANGUAGE_KEY)
text_analytics_client = TextAnalyticsClient(endpoint=AZURE_LANGUAGE_ENDPOINT, credential=credential)


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    return ' '.join(filtered_tokens)


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ' '.join(page.extract_text() for page in pdf_reader.pages)
        print(f"Extracted text from PDF: {text[:500]}...")  # Print first 500 characters
        return text


def calculate_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]


def find_best_resume(job_description):
    processed_job_description = preprocess_text(job_description)
    best_resume = None
    best_similarity_score = 0

    for filename in os.listdir(RESUME_FOLDER):
        if filename.endswith('.pdf'):
            file_path = os.path.join(RESUME_FOLDER, filename)
            resume_text = extract_text_from_pdf(file_path)
            processed_resume = preprocess_text(resume_text)
            similarity_score = calculate_similarity(processed_job_description, processed_resume)
            if similarity_score > best_similarity_score:
                best_similarity_score = similarity_score
                best_resume = filename

    return best_resume, best_similarity_score


def generate_questions(job_description):
    # Extract key phrases from the job description
    key_phrase_response = text_analytics_client.extract_key_phrases([job_description])[0]
    if not key_phrase_response.is_error:
        key_phrases = key_phrase_response.key_phrases
    else:
        print(key_phrase_response.error)
        return []

    # Question templates
    templates = [
        "What experience do you have with {}?",
        "Can you describe a challenging situation you've faced related to {} and how you resolved it?",
        "What do you think are the biggest challenges in {} and how would you address them?",
        "How do you stay updated with the latest trends in {}?",
        "Can you give an example of a successful project you've worked on that involved {}?",
        "How would you explain {} to someone with no technical background?",
        "What strategies do you use when working on {} to ensure high-quality results?",
        "How do you see the future of {} evolving in the next few years?",
        "What tools or methodologies do you prefer when working with {}?"
    ]

    # Generate questions
    questions = []
    for _ in range(5):  # Generate 5 questions
        template = random.choice(templates)
        key_phrase = random.choice(key_phrases)
        questions.append(template.format(key_phrase))

    return questions


def conduct_interview(questions):
    print("\nInterview starting. Please provide detailed answers to the following questions:\n")
    answers = []
    for i, question in enumerate(questions, 1):
        print(f"Q{i}: {question}")
        answer = input("Your answer: ")
        while len(answer.split()) < 20:
            print("Please provide a more detailed answer (at least 20 words).")
            answer = input("Your answer: ")
        answers.append(answer)
        print()
    return questions, answers


def analyze_answers(job_description, questions, answers):
    # Prepare the text to analyze
    full_text = f"Job Description: {job_description}\n\n"
    for q, a in zip(questions, answers):
        full_text += f"Q: {q}\nA: {a}\n\n"

    # Perform key phrase extraction
    key_phrase_response = text_analytics_client.extract_key_phrases([full_text])[0]

    if not key_phrase_response.is_error:
        response_key_phrases = set(key_phrase_response.key_phrases)
    else:
        print(key_phrase_response.error)
        return 0, "Error in analysis"

    # Perform sentiment analysis
    sentiment_response = text_analytics_client.analyze_sentiment([full_text])[0]

    if not sentiment_response.is_error:
        sentiment = sentiment_response.sentiment
        confidence_scores = sentiment_response.confidence_scores
    else:
        print(sentiment_response.error)
        return 0, "Error in analysis"

    # Extract key phrases from job description
    job_key_phrase_response = text_analytics_client.extract_key_phrases([job_description])[0]
    job_key_phrases = set(job_key_phrase_response.key_phrases)

    # Calculate score based on key phrase matches and sentiment
    matched_phrases = job_key_phrases.intersection(response_key_phrases)
    keyword_score = len(matched_phrases) / len(job_key_phrases) if job_key_phrases else 0

    sentiment_score = confidence_scores.positive

    overall_score = (keyword_score + sentiment_score) / 2
    percentage = round(overall_score * 100, 2)

    # Generate analysis text
    analysis = f"The candidate's responses matched {len(matched_phrases)} out of {len(job_key_phrases)} key job requirements. "
    analysis += f"The overall sentiment of the responses was {sentiment}. "

    if percentage >= 80:
        analysis += "The candidate shows strong alignment with the job requirements and positive engagement."
    elif percentage >= 60:
        analysis += "The candidate has a good foundation but may need some additional development in certain areas."
    else:
        analysis += "The candidate may need significant development to meet the job requirements."

    return percentage, analysis


# def main():
# try:
#     job_description = input("Enter job description: ")
#     best_resume, similarity_score = find_best_resume(job_description)
#     print(f"\nBest matching resume: {best_resume}")
#     print(f"Similarity score: {similarity_score:.2f}")
#
#     candidate_name = input("Enter candidate's name: ")
#     questions = generate_questions(job_description)
#
#     questions, answers = conduct_interview(questions)
#
#     print("\nInterview Summary:")
#     for q, a in zip(questions, answers):
#         print(f"Q: {q}")
#         print(f"A: {a}")
#         print()
#
#     percentage, analysis = analyze_answers(job_description, questions, answers)
#     print("Evaluation:")
#     print(f"Candidate fit: {percentage}%")
#     print(f"Analysis: {analysis}")
#
# except Exception as e:
#     print(f"An error occurred: {str(e)}")


# Helper functions (preprocess_text, extract_text_from_pdf, calculate_similarity, find_best_resume,
# generate_questions, analyze_answers) Copy these functions from your original code

@app.route('/')
def index():
    return render_template('index.html')


def extract_basic_info(best_resume):
    file_path = os.path.join(RESUME_FOLDER, best_resume)
    resume_text = extract_text_from_pdf(file_path)

    # Split the text into lines
    lines = resume_text.split('\n')

    # Look for a name in the first few lines
    name = "Unknown"
    for line in lines[:5]:  # Check first 5 lines
        name_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b', line)
        if name_match:
            name = name_match.group(1)
            break

    # If no name found, use the fallback method
    if name == "Unknown":
        words = resume_text.split()
        capitalized_words = [word for word in words if word[0].isupper() and word.isalpha()]
        if len(capitalized_words) >= 2:
            name = f"{capitalized_words[0]} {capitalized_words[1]}"

    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    email = email_match.group(0) if email_match else "Unknown"

    print(f"Extracted info - Name: {name}, Email: {email}")
    print(f"First 5 lines of resume text:")
    for line in lines[:5]:
        print(line)
    return {"name": name, "email": email}


@app.route('/search_resume', methods=['POST'])
def search_resume():
    job_description = request.form['job_description']
    best_resume, similarity_score = find_best_resume(job_description)
    questions = generate_questions(job_description)

    session['interview_token'] = secrets.token_urlsafe(16)
    resume_info = extract_basic_info(best_resume)
    session['resume_info'] = resume_info
    print(f"Stored in session: {session['resume_info']}")  # Add this for debugging

    interview_token = secrets.token_urlsafe(16)
    session['interview_token'] = interview_token
    print(f"Generated interview token: {interview_token}")  # Debug print

    return jsonify({
        'best_resume': best_resume,
        'similarity_score': similarity_score,
        'questions': questions,
        'job_description': job_description,
        'interview_token': interview_token
    })


@app.route('/verify_candidate', methods=['POST'])
def verify_candidate():
    data = request.json
    provided_info = data['candidate_info']
    stored_info = session.get('resume_info', {})

    print(f"Provided info: {provided_info}")
    print(f"Stored info: {stored_info}")

    # Split names into words and check for partial matches
    provided_name_parts = provided_info['name'].lower().split()
    stored_name_parts = stored_info['name'].lower().split()
    name_match = any(part in stored_name_parts for part in provided_name_parts)

    email_match = provided_info['email'].lower() == stored_info['email'].lower()

    if name_match and email_match:
        return jsonify({'verified': True})
    else:
        return jsonify({'verified': False,
                        'message': 'Verification failed. Please ensure you are the candidate whose resume was selected.'})


@app.route('/interview')
def interview():
    return render_template('interview.html')


@app.route('/analyze_interview', methods=['POST'])
def analyze_interview():
    data = request.json
    received_token = data.get('interview_token')
    stored_token = session.get('interview_token')
    print(f"Received token: {received_token}")
    print(f"Stored token: {stored_token}")

    if received_token != stored_token:
        return jsonify({'error': 'Invalid interview session'}), 403

    job_description = data['job_description']
    questions = data['questions']
    answers = data['answers']
    percentage, analysis = analyze_answers(job_description, questions, answers)
    return jsonify({
        'percentage': percentage,
        'analysis': analysis
    })


if __name__ == '__main__':
    def main():
        try:
            job_description = input("Enter job description: ")
            best_resume, similarity_score = find_best_resume(job_description)
            print(f"\nBest matching resume: {best_resume}")
            print(f"Similarity score: {similarity_score:.2f}")

            candidate_name = input("Enter candidate's name: ")
            questions = generate_questions(job_description)

            questions, answers = conduct_interview(questions)

            print("\nInterview Summary:")
            for q, a in zip(questions, answers):
                print(f"Q: {q}")
                print(f"A: {a}")
                print()

            percentage, analysis = analyze_answers(job_description, questions, answers)
            print("Evaluation:")
            print(f"Candidate fit: {percentage}%")
            print(f"Analysis: {analysis}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")


    #main()
    app.run(debug=True)