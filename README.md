# 🧠 Neural RAG Tutor: The Active Recall Agent

> **Capstone Project Submission** > **Track:** Freestyle / Agents for Good (Education)  
> **Tech Stack:** Python, Streamlit, Google Gemini 1.5 Flash

![Banner Image](https://img.shields.io/badge/Status-Deployed-success) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)

## 📖 Overview
**Neural RAG Tutor** transforms static PDF textbooks into interactive exams using a multi-agent system. Unlike standard chatbots, it fuses "Static Context" (uploaded PDFs) with "Dynamic Context" (your chat history) to create a personalized study loop.

It addresses the problem of **"Passive Review"** by forcing Active Recall through generated quizzes, hints, and immediate semantic grading.

## 🚀 Live Demo
**[Click here to view the Deployed App]** *(Replace this text with your Streamlit Share URL)*

---

## ⚙️ System Architecture

The system utilizes a **Sequential Multi-Agent Architecture** orchestrated by Streamlit's state engine.

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
