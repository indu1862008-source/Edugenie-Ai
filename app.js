// EduGenie AI - Frontend JavaScript
// Connects the HTML frontend to the FastAPI backend.

const API_BASE = "";

// --------------------------------------------------
// DOM Elements
// --------------------------------------------------

const taskSelect = document.getElementById("task");
const levelSelect = document.getElementById("level");
const inputText = document.getElementById("inputText");
const runButton = document.getElementById("runButton");

const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");
const resultBox = document.getElementById("resultBox");

// --------------------------------------------------
// Utility Functions
// --------------------------------------------------

function showLoading(show) {
    if (loading) {
        loading.style.display = show ? "block" : "none";
    }

    if (runButton) {
        runButton.disabled = show;
        runButton.textContent = show ? "Processing..." : "Generate";
    }
}

function showError(message) {
    if (!errorBox) return;

    errorBox.textContent = message;
    errorBox.style.display = "block";
}

function hideError() {
    if (!errorBox) return;

    errorBox.textContent = "";
    errorBox.style.display = "none";
}

function showResult() {
    if (resultBox) {
        resultBox.style.display = "block";
    }
}

function clearResult() {
    if (resultBox) {
        resultBox.innerHTML = "";
        resultBox.style.display = "none";
    }
}

function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function formatText(text) {
    if (!text) return "";

    return escapeHtml(text)
        .replace(/\n\n/g, "<br><br>")
        .replace(/\n/g, "<br>");
}

// --------------------------------------------------
// API Request
// --------------------------------------------------

async function apiRequest(endpoint, method = "POST", body = null) {
    const options = {
        method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (body !== null) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);

    let data;

    try {
        data = await response.json();
    } catch (error) {
        throw new Error(
            `Server returned an invalid response (${response.status}).`
        );
    }

    if (!response.ok) {
        let message = "Something went wrong.";

        if (data.detail) {
            if (typeof data.detail === "string") {
                message = data.detail;
            } else {
                message = JSON.stringify(data.detail);
            }
        }

        throw new Error(message);
    }

    return data;
}

// --------------------------------------------------
// Q&A
// --------------------------------------------------

async function runQA() {
    const question = inputText.value.trim();

    if (!question) {
        throw new Error("Please enter a question.");
    }

    const data = await apiRequest("/qa", "POST", {
        question: question,
        learner_level: levelSelect.value
    });

    resultBox.innerHTML = `
        <div class="result-card">
            <h2>Answer</h2>
            <div class="answer">
                ${formatText(data.answer)}
            </div>
        </div>
    `;

    showResult();
}

// --------------------------------------------------
// Explanation
// --------------------------------------------------

async function runExplanation() {
    const concept = inputText.value.trim();

    if (!concept) {
        throw new Error("Please enter a concept to explain.");
    }

    const data = await apiRequest("/explain", "POST", {
        concept: concept,
        learner_level: levelSelect.value
    });

    resultBox.innerHTML = `
        <div class="result-card">
            <h2>Explanation</h2>

            <div class="answer">
                ${formatText(data.explanation)}
            </div>
        </div>
    `;

    showResult();
}

// --------------------------------------------------
// Quiz
// --------------------------------------------------

async function runQuiz() {
    const topic = inputText.value.trim();

    if (!topic) {
        throw new Error("Please enter a topic for the quiz.");
    }

    const data = await apiRequest("/quiz", "POST", {
        topic: topic,
        learner_level: levelSelect.value
    });

    renderQuiz(data);
}

// --------------------------------------------------
// Render Quiz
// --------------------------------------------------

function renderQuiz(data) {
    const questions = data.questions || [];

    if (questions.length === 0) {
        throw new Error("No quiz questions were returned.");
    }

    let html = `
        <div class="result-card">
            <h2>Quiz</h2>

            <div id="quizContainer">
    `;

    questions.forEach((question, index) => {
        html += `
            <div class="quiz-question">
                <h3>
                    ${index + 1}. ${escapeHtml(question.question)}
                </h3>
        `;

        const options = question.options || [];

        options.forEach((option, optionIndex) => {
            const optionId = `question-${index}-option-${optionIndex}`;

            html += `
                <div class="quiz-option">
                    <input
                        type="radio"
                        id="${optionId}"
                        name="question-${index}"
                        value="${optionIndex}"
                    >

                    <label for="${optionId}">
                        ${escapeHtml(option)}
                    </label>
                </div>
            `;
        });

        html += `
                <div
                    id="feedback-${index}"
                    class="quiz-feedback"
                    style="display:none;"
                ></div>
            </div>
        `;
    });

    html += `
            </div>

            <button
                type="button"
                id="checkQuizButton"
                class="primary-button"
            >
                Check Answers
            </button>

            <div id="quizScore"></div>
        </div>
    `;

    resultBox.innerHTML = html;
    showResult();

    document
        .getElementById("checkQuizButton")
        .addEventListener("click", () => {
            checkQuizAnswers(questions);
        });
}

// --------------------------------------------------
// Check Quiz Answers
// --------------------------------------------------

function checkQuizAnswers(questions) {
    let score = 0;

    questions.forEach((question, index) => {
        const selected = document.querySelector(
            `input[name="question-${index}"]:checked`
        );

        const feedback = document.getElementById(
            `feedback-${index}`
        );

        if (!selected) {
            feedback.textContent = "Please select an answer.";
            feedback.style.display = "block";
            return;
        }

        const selectedIndex = Number(selected.value);

        // Backend may return either correct_answer as an index
        // or the actual answer text.
        const correctAnswer = question.correct_answer;

        let isCorrect = false;

        if (typeof correctAnswer === "number") {
            isCorrect = selectedIndex === correctAnswer;
        } else {
            const selectedText =
                question.options[selectedIndex];

            isCorrect =
                selectedText &&
                String(selectedText).trim().toLowerCase() ===
                    String(correctAnswer).trim().toLowerCase();
        }

        if (isCorrect) {
            score++;

            feedback.textContent = "Correct!";
            feedback.className = "quiz-feedback correct";
        } else {
            feedback.textContent =
                `Incorrect. Correct answer: ${escapeHtml(
                    getCorrectAnswerText(question)
                )}`;

            feedback.className = "quiz-feedback incorrect";
        }

        feedback.style.display = "block";
    });

    const scoreBox = document.getElementById("quizScore");

    const answeredQuestions = questions.filter(
        (_, index) =>
            document.querySelector(
                `input[name="question-${index}"]:checked`
            )
    ).length;

    if (answeredQuestions === questions.length) {
        scoreBox.innerHTML = `
            <div class="quiz-score">
                Score: ${score} / ${questions.length}
            </div>
        `;
    }
}

function getCorrectAnswerText(question) {
    const answer = question.correct_answer;

    if (
        typeof answer === "number" &&
        question.options &&
        question.options[answer]
    ) {
        return question.options[answer];
    }

    return answer || "Unknown";
}

// --------------------------------------------------
// Summary
// --------------------------------------------------

async function runSummary() {
    const text = inputText.value.trim();

    if (!text) {
        throw new Error("Please enter text to summarize.");
    }

    const data = await apiRequest("/summarize", "POST", {
        text: text,
        learner_level: levelSelect.value
    });

    resultBox.innerHTML = `
        <div class="result-card">
            <h2>Summary</h2>

            <div class="answer">
                ${formatText(data.summary)}
            </div>
        </div>
    `;

    showResult();
}

// --------------------------------------------------
// Learning Path
// --------------------------------------------------

async function runLearningPath() {
    const topic = inputText.value.trim();

    if (!topic) {
        throw new Error("Please enter a topic for the learning path.");
    }

    const data = await apiRequest(
        "/learn/recommendations",
        "POST",
        {
            topic: topic,
            learner_level: levelSelect.value
        }
    );

    renderLearningPath(data);
}

// --------------------------------------------------
// Render Learning Path
// --------------------------------------------------

function renderLearningPath(data) {
    const stages = data.stages || [];

    let html = `
        <div class="result-card">
            <h2>${escapeHtml(
                data.title || "Learning Path"
            )}</h2>
    `;

    if (data.description) {
        html += `
            <p class="learning-description">
                ${formatText(data.description)}
            </p>
        `;
    }

    if (stages.length > 0) {
        html += `
            <div class="learning-stages">
        `;

        stages.forEach((stage, index) => {
            html += `
                <div class="learning-stage">
                    <div class="stage-number">
                        ${index + 1}
                    </div>

                    <div class="stage-content">
                        <h3>
                            ${escapeHtml(
                                stage.stage ||
                                stage.title ||
                                `Stage ${index + 1}`
                            )}
                        </h3>
            `;

            if (stage.timeline) {
                html += `
                    <p>
                        <strong>Timeline:</strong>
                        ${escapeHtml(stage.timeline)}
                    </p>
                `;
            }

            if (stage.description) {
                html += `
                    <p>
                        ${formatText(stage.description)}
                    </p>
                `;
            }

            if (stage.resources && stage.resources.length) {
                html += `
                    <h4>Resources</h4>
                    <ul>
                `;

                stage.resources.forEach(resource => {
                    html += `
                        <li>
                            ${escapeHtml(resource)}
                        </li>
                    `;
                });

                html += `
                    </ul>
                `;
            }

            html += `
                    </div>
                </div>
            `;
        });

        html += `
            </div>
        `;
    }

    html += `
        </div>
    `;

    resultBox.innerHTML = html;
    showResult();
}

// --------------------------------------------------
// Main Task Handler
// --------------------------------------------------

async function runSelectedTask() {
    hideError();
    clearResult();

    const task = taskSelect.value;

    showLoading(true);

    try {
        switch (task) {
            case "qa":
                await runQA();
                break;

            case "explain":
                await runExplanation();
                break;

            case "quiz":
                await runQuiz();
                break;

            case "summarize":
                await runSummary();
                break;

            case "learning":
                await runLearningPath();
                break;

            default:
                throw new Error("Please select a valid task.");
        }
    } catch (error) {
        console.error("EduGenie error:", error);

        showError(
            error.message ||
            "An unexpected error occurred."
        );
    } finally {
        showLoading(false);
    }
}

// --------------------------------------------------
// Task Description
// --------------------------------------------------

function updateInputPlaceholder() {
    if (!inputText || !taskSelect) return;

    const task = taskSelect.value;

    const placeholders = {
        qa: "Ask your educational question...",
        explain: "Enter a concept you want explained...",
        quiz: "Enter a topic for the quiz...",
        summarize: "Paste the text you want summarized...",
        learning: "Enter a topic you want to learn..."
    };

    inputText.placeholder =
        placeholders[task] ||
        "Enter your text here...";
}

// --------------------------------------------------
// Copy Result
// --------------------------------------------------

async function copyResult() {
    if (!resultBox) return;

    const text = resultBox.innerText.trim();

    if (!text) {
        return;
    }

    try {
        await navigator.clipboard.writeText(text);

        const originalText = copyButton.textContent;

        copyButton.textContent = "Copied!";

        setTimeout(() => {
            copyButton.textContent = originalText;
        }, 1500);
    } catch (error) {
        console.error("Copy failed:", error);
    }
}

// --------------------------------------------------
// Event Listeners
// --------------------------------------------------

if (runButton) {
    runButton.addEventListener("click", runSelectedTask);
}

if (taskSelect) {
    taskSelect.addEventListener(
        "change",
        updateInputPlaceholder
    );
}

if (inputText) {
    inputText.addEventListener("keydown", event => {
        // Ctrl + Enter to run
        if (event.ctrlKey && event.key === "Enter") {
            runSelectedTask();
        }
    });
}

// --------------------------------------------------
// Initial Setup
// --------------------------------------------------

updateInputPlaceholder();

console.log("EduGenie AI frontend loaded successfully.");