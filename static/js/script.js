document.addEventListener('DOMContentLoaded', function() {
    const jobDescriptionForm = document.getElementById('job-description-form');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const startInterviewButton = document.getElementById('start-interview');

    let interviewToken = '';
    let questions = [];
    let jobDescription = '';

    if (jobDescriptionForm) {
        jobDescriptionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            jobDescription = document.getElementById('job-description').value;

            // Show loading screen
            loadingDiv.style.display = 'block';
            resultDiv.style.display = 'none';

            fetch('/search_resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'job_description': jobDescription
                })
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading screen
                loadingDiv.style.display = 'none';

                document.getElementById('best-resume').textContent = data.best_resume;
                document.getElementById('similarity-score').textContent = data.similarity_score.toFixed(2);
                resultDiv.style.display = 'block';
                questions = data.questions;
                interviewToken = data.interview_token;
                sessionStorage.setItem('interviewToken', interviewToken);
                console.log("Stored interview token:", data.interview_token);  // Debug log
            })
            .catch(error => {
                console.error('Error:', error);
                loadingDiv.style.display = 'none';
                alert('An error occurred while searching for the best resume. Please try again.');
            });
        });

        startInterviewButton.addEventListener('click', function() {
            // Store questions and job description in session storage
            sessionStorage.setItem('questions', JSON.stringify(questions));
            sessionStorage.setItem('jobDescription', jobDescription);
            window.location.href = '/interview';
        });
    }

    // Interview page logic
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        const verificationForm = document.getElementById('verification-form');
        const candidateVerificationForm = document.getElementById('candidate-verification-form');

        interviewToken = sessionStorage.getItem('interviewToken');

        function verifyCandidate() {
        verificationForm.style.display = 'block';
        chatContainer.style.display = 'none';

        candidateVerificationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const candidateName = document.getElementById('candidate-name').value.trim();
            const candidateEmail = document.getElementById('candidate-email').value.trim();

            fetch('/verify_candidate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    candidate_info: {
                        name: candidateName,
                        email: candidateEmail
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.verified) {
                    verificationForm.style.display = 'none';
                    chatContainer.style.display = 'block';
                    askQuestion();  // Start the interview
                } else {
                    alert(data.message);
                }
            });
        });
    }

    // Call verifyCandidate instead of askQuestion at the start
        verifyCandidate();

        const chatMessages = document.getElementById('chat-messages');
        const userInputForm = document.getElementById('user-input-form');
        const userInput = document.getElementById('user-input');

        let currentQuestionIndex = 0;
        let answers = [];

        // Retrieve questions and job description from session storage
        questions = JSON.parse(sessionStorage.getItem('questions') || '[]');
        jobDescription = sessionStorage.getItem('jobDescription') || '';

        function addMessage(content, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', sender);
            messageDiv.textContent = content;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function askQuestion() {
            if (currentQuestionIndex < questions.length) {
                addMessage(questions[currentQuestionIndex], 'bot');
            } else {
                addMessage("Thank you for completing the interview. We'll now analyze your responses.", 'bot');
                userInputForm.style.display = 'none';
                analyzeInterview();
            }
        }

function analyzeInterview() {
    const interviewToken = sessionStorage.getItem('interviewToken');
    console.log("Sending interview token:", interviewToken);  // Debug log

    fetch('/analyze_interview', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            job_description: jobDescription,
            questions: questions,
            answers: answers,
            interview_token: interviewToken
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            document.getElementById('result').style.display = 'block';
            document.getElementById('candidate-fit').textContent = data.percentage.toFixed(2) + '%';
            document.getElementById('analysis').textContent = data.analysis;
        }
    });
}

        userInputForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const answer = userInput.value;
            addMessage(answer, 'user');
            answers.push(answer);
            userInput.value = '';
            currentQuestionIndex++;
            askQuestion();
        });

        // Start the interview
        askQuestion();
    }
});