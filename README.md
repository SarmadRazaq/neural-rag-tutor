# 🧠 Neural RAG Tutor: The Active Recall Agent

> **Capstone Project Submission**  
> **Track:** Freestyle / Agents for Good (Education)  
> **Tech Stack:** Python, Streamlit, Google Gemini 1.5 Flash

![Status](https://img.shields.io/badge/Status-Deployed-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![AI](https://img.shields.io/badge/Gemini-1.5%20Flash-orange)

---

## 📖 Overview
**Neural RAG Tutor** transforms static PDF textbooks into interactive exams.  
It uses **Multi-Source Data Fusion** to merge:
- **Static Context → PDF textbooks**
- **Dynamic Context → Chat history**

The app eliminates *Passive Review Syndrome* by enforcing **Active Recall** through:
✔ automatic quizzes  
✔ hints (without revealing answers)  
✔ semantic grading  

---

## ⚙️ System Architecture

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


### 📚 Neural RAG Tutor — Multi-Agent Study Buddy
### 🔑 Key Features (Rubric Alignment)
### ⭐ 1. Multi-Agent System

Professor Agent – structured JSON question generator w/ self-correction

HybridQA Agent – PDF citation + General Knowledge routing

Tutor Agent – pedagogical hints

Grader Agent – semantic + fuzzy grading

### ⭐ 2. Custom Tools

| Tool                  | Purpose                                   |
| --------------------- | ----------------------------------------- |
| DocumentIngestionTool | Binary PDF processing + text sanitization |
| ObservabilityTool     | Latency + call frequency + dashboard      |
| EvaluationTool        | Human-in-the-loop quality scoring (👍/👎) |


### ⭐ 3. Sessions & Memory

Persists user_session_state.json across reloads

Memory Bank → Past quizzes for review

### ⭐ 4. Context Engineering

Context Fusion (PDF + Chat)

Context Compression after 5+ turns

###⭐ 5. Observability & Evaluation

Agent Quality Score

Real-time metrics dashboard

### 🛠️ Installation & Setup
1️⃣ Clone the Repository

git clone https://github.com/your-username/neural-rag-tutor.git
cd neural-rag-tutor

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Configure API Key

📌 Create .streamlit/secrets.toml:
GEMINI_API_KEY = "your_key_here"

4️⃣ Run the App

streamlit run study_buddy.py


### 🎮 Usage Guide

###🔹 Mode 1 — Ask Anything (Chat)

Upload a PDF

Ask questions — agent cites PDF sources

Builds Dynamic Context for quizzes

### 🔹 Mode 2 — Quiz Me (Active Recall)

Configure:

| Setting       | Options                    |
| ------------- | -------------------------- |
| Source        | PDF / Chat / Both (Fusion) |
| Difficulty    | Easy / Medium / Hard       |
| Question Type | Text / MCQ                 |


##🔄 During Quiz

| Action       | Outcome                        |
| ------------ | ------------------------------ |
| **Get Hint** | Tutor Agent provides guidance  |
| **Skip**     | Move to next, current archived |
| **Submit**   | Instant evaluation             |
| **Review**   | Full question history retained |


###📂 File Structure

📦 neural-rag-tutor
 ┣ 📜 study_buddy.py             # Main app + all Agents
 ┣ 📜 requirements.txt           # Dependencies
 ┣ 📜 user_session_state.json    # Auto-generated session persistence
 ┣ 📂 .streamlit                 # For secrets.toml (optional)
 ┗ 📄 README.md                  # Documentation
