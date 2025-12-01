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
