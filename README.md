# 🧠 Neural RAG Tutor: The Active Recall Agent

> **Capstone Project Submission**
> **Track:** Freestyle / Agents for Good (Education)
> **Tech Stack:** Python, Streamlit, Google Gemini 1.5 Flash

![Status](https://img.shields.io/badge/Status-Deployed-success) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red) ![AI](https://img.shields.io/badge/Gemini-1.5%20Flash-orange)

## 📖 Overview
**Neural RAG Tutor** is an autonomous "Exam Prep" engine that transforms static PDF textbooks into interactive exams. Unlike standard chatbots, it utilizes a **Multi-Source Data Fusion** engine to combine your "Static Context" (uploaded PDFs) with your "Dynamic Context" (chat history), creating a personalized study loop.

It solves **"Passive Review Syndrome"** by enforcing Active Recall through generated quizzes, pedagogical hints, and semantic grading.

## 🚀 Live Demo
**[Click here to view the Deployed App]** *(Replace this text with your Streamlit Share URL)*

---

## ⚙️ System Architecture

The system utilizes a **Sequential Multi-Agent Architecture** with a human-in-the-loop feedback mechanism.

```mermaid
graph TD
    User((User)) -->|Uploads PDF| Ingestion[Document Ingestion Tool]
    Ingestion --> VectorStore[Session Memory]
    
    User -->|Selects Sources| Fusion[Context Fusion Engine]
    VectorStore --> Fusion
    ChatLog[Chat History] --> Fusion
    
    Fusion --> Professor[🎓 Professor Agent]
    
    subgraph "Agent Workflow"
    Professor -->|Generates JSON| Validator[JSON Validator]
    Validator -->|Renders| QuizUI[Quiz Interface]
    User -->|Submits Answer| Grader[📝 Grader Agent]
    User -->|Request Hint| Tutor[💡 Tutor Agent]
    end
    
    Grader -->|Log Metric| Observability[📊 Observability Tool]
    Tutor -->|Log Metric| Observability


# 📚 Neural RAG Tutor — Multi-Agent Study Buddy

## 🔑 Key Features (Rubric Alignment)

This project demonstrates mastery of **5 Key Concepts** from the Agent course:

### **1. Multi-Agent System (Sequential & Specialized)**
- **Professor Agent:** Uses *One-Shot Prompting* to generate structured JSON questions (Text or MCQ) strictly from the provided context. Includes *self-correction logic* to ensure the answer key always matches the options.
- **HybridQA Agent:** Routes queries, deciding whether to answer using PDF context (with citations) or General Knowledge.
- **Tutor Agent:** Provides learning hints without revealing answers.
- **Grader Agent:** Performs semantic evaluation using fuzzy matching to compare the user's answer against the correct one.

### **2. Custom Tools**
- **DocumentIngestionTool:** Processes binary PDF streams, sanitizes text, and prepares it for model context inputs.
- **ObservabilityTool:** Logs agent latency & execution frequency and displays real-time metrics via a sidebar dashboard.
- **EvaluationTool:** Enables *Human-in-the-loop reinforcement* by storing user feedback (👍 / 👎) on question quality.

### **3. Sessions & Memory (Persistence)**
- **SessionManager:** Saves user state (`user_session_state.json`) to preserve chat history, scores, and uploaded files across reloads.
- **Memory Bank:** Stores past quiz questions and answers for later review.

### **4. Context Engineering (Compaction)**
- **Context Fusion:** Dynamically merges PDF textbook data and chat history based on user selection.
- **ContextCompressor:** Summarizes long chat logs when >5 turns to reduce token cost and improve speed.

### **5. Observability & Evaluation**
- **Real-time Dashboard:** Shows Total Agent Calls, Average Latency, and *Agent Quality Score*.
- **Feedback Loop:** User ratings influence future training via quality logging.

---

## 🛠️ Installation & Setup

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/neural-rag-tutor.git
cd neural-rag-tutor

### **2️⃣ Install Dependencies**

pip install -r requirements.txt


### **3️⃣ Configure API Key**

📌 Option A — Local file
Create .streamlit/secrets.toml:
GEMINI_API_KEY = "your_key_here"

### **4️⃣ Run the App**
streamlit run study_buddy.py

### 🎮 Usage Guide
##Mode 1 — Ask Anything (Chat)

Upload a PDF textbook.

Chat with the document — the agent will cite sources (e.g., 📘 [Source: PDF]).

This builds your Dynamic Context for the quiz.

##Mode 2 — Quiz Me (Exam Prep)

Select sources: Uploaded PDF, My Chat History, or both (Data Fusion).

Choose difficulty: Easy / Medium / Hard.

Choose type: Text / MCQ.

Click Start Quiz.

| Action       | Outcome                                                         |
| ------------ | --------------------------------------------------------------- |
| **Get Hint** | Tutor Agent provides a clue without revealing the answer        |
| **Skip**     | Archives the question and fetches a new one                     |
| **Submit**   | Grader Agent evaluates the answer and gives instant feedback    |
| **Review**   | View all past questions and answers in the *Past Questions Log* |


📦 neural-rag-tutor
 ┣ 📜 study_buddy.py             # Main Streamlit app, UI, and all Agent classes
 ┣ 📜 requirements.txt           # Python dependencies
 ┣ 📜 user_session_state.json    # Auto-created session persistence file
 ┣ 📂 .streamlit                 # Optional folder for secrets.toml
 ┗ 📄 README.md                  # Project documentation



