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






    🔑 Key Features (Rubric Alignment)
This project demonstrates mastery of 5 Key Concepts from the Agent course:

1. Multi-Agent System (Sequential & Specialized)
Professor Agent: Uses "One-Shot Prompting" to generate structured JSON questions (Text or MCQ) strictly from the provided context. Includes self-correction logic to ensure the answer key matches the options.

HybridQA Agent: A router that decides whether to answer from the PDF (citing sources) or use General Knowledge.

Tutor Agent: Provides pedagogical scaffolding (hints) without revealing answers.

Grader Agent: Performs semantic evaluation, comparing the user's input against the model's answer key using fuzzy matching logic.

2. Custom Tools
DocumentIngestionTool: A custom Python class that handles binary PDF stream processing, sanitizes text, and prepares it for the context window.

ObservabilityTool: A custom instrumentation class that tracks agent latency (speed) and execution frequency, visualizing real-time metrics in a sidebar dashboard.

EvaluationTool: Implements "Human-in-the-loop" reinforcement, allowing users to rate questions (Thumbs Up/Down) to log quality metrics.

3. Sessions & Memory (Persistence)
Persistence: Uses a SessionManager to serialize user state (user_session_state.json) to disk. This ensures that scores, chat history, and uploaded documents survive page reloads.

Memory Bank: Maintains a rigorous history of past quiz questions, allowing users to review their mistakes.

4. Context Engineering (Compaction)
Context Fusion: Dynamically merges textbook data with conversation history based on user selection.

Compression: A background logic (ContextCompressor) summarizes chat logs if they exceed 5 turns, ensuring the LLM context window remains optimized for speed and cost.

5. Observability & Evaluation
Real-time Dashboard: A sidebar panel shows Total Agent Calls, Average Latency, and an "Agent Quality Score".

Feedback Loop: Users can rate generated questions (Thumbs Up/Down), providing signal for future fine-tuning.
