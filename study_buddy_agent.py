import streamlit as st
import google.generativeai as genai
import logging
import PyPDF2
import json
import difflib
import time
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Neural RAG Tutor", page_icon="🧠", layout="wide")
logging.basicConfig(level=logging.INFO)

# --- CONSTANTS ---
SESSION_FILE = "user_session_state.json"

# --- STATE MANAGEMENT & PERSISTENCE ---
class SessionManager:
    """Handles saving/loading state to disk for persistence across reloads."""
    
    @staticmethod
    def save_state():
        """Saves critical session data to a local JSON file."""
        state_data = {
            "score": st.session_state.get("score", 0),
            "chat_history": st.session_state.get("chat_history", []),
            "quiz_history": st.session_state.get("quiz_history", []),
            "rag_docs": st.session_state.get("rag_docs", ""),
            "agent_metrics": st.session_state.get("agent_metrics", {"calls": 0, "avg_latency": 0.0, "positive_feedback": 0, "negative_feedback": 0}),
            "chat_summary": st.session_state.get("chat_summary", "") # Persist the summary too
        }
        try:
            with open(SESSION_FILE, "w") as f:
                json.dump(state_data, f)
            logging.info("State saved to disk.")
        except Exception as e:
            logging.error(f"Failed to save state: {e}")

    @staticmethod
    def load_state():
        """Loads session data from disk if available."""
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r") as f:
                    data = json.load(f)
                
                # Restore state
                if 'score' not in st.session_state: st.session_state.score = data.get("score", 0)
                if 'chat_history' not in st.session_state: st.session_state.chat_history = data.get("chat_history", [])
                if 'quiz_history' not in st.session_state: st.session_state.quiz_history = data.get("quiz_history", [])
                if 'rag_docs' not in st.session_state: st.session_state.rag_docs = data.get("rag_docs", "")
                if 'agent_metrics' not in st.session_state: st.session_state.agent_metrics = data.get("agent_metrics", {"calls": 0, "avg_latency": 0.0, "positive_feedback": 0, "negative_feedback": 0})
                if 'chat_summary' not in st.session_state: st.session_state.chat_summary = data.get("chat_summary", "")
                
                st.toast("🔄 Session Restored from Memory")
            except Exception as e:
                logging.error(f"Failed to load state: {e}")
        else:
            # Initialize defaults if no file exists
            if 'score' not in st.session_state: st.session_state.score = 0
            if 'chat_history' not in st.session_state: st.session_state.chat_history = []
            if 'quiz_history' not in st.session_state: st.session_state.quiz_history = []
            if 'rag_docs' not in st.session_state: st.session_state.rag_docs = ""
            if 'agent_metrics' not in st.session_state: st.session_state.agent_metrics = {"calls": 0, "avg_latency": 0.0, "positive_feedback": 0, "negative_feedback": 0}
            if 'chat_summary' not in st.session_state: st.session_state.chat_summary = ""

# Load state immediately on startup
SessionManager.load_state()

# Initialize transient UI state (things that don't need to be saved to disk)
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = None
if 'quiz_answered' not in st.session_state: st.session_state.quiz_answered = False
if 'active_hint' not in st.session_state: st.session_state.active_hint = None
if 'current_user_answer' not in st.session_state: st.session_state.current_user_answer = None

# --- NEW: CONTEXT COMPRESSOR (Latency Reduction) ---
class ContextCompressor:
    """Summarizes older context to reduce token usage and latency."""
    
    def compress_chat_history(self, history):
        """Compresses chat history if it's too long."""
        # Only compress if we have more than 5 messages
        if len(history) <= 5:
            return None, history # No summary needed yet

        # Keep last 3 messages raw, summarize the rest
        older_msgs = history[:-3]
        recent_msgs = history[-3:]
        
        # Prepare text to summarize
        text_to_compress = "\n".join([f"{msg['role']}: {msg['content']}" for msg in older_msgs])
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Summarize the following conversation history into a concise paragraph. 
        Focus on the key topics studied and the user's learning gaps.
        
        CONVERSATION:
        {text_to_compress}
        """
        try:
            summary = model.generate_content(prompt).text.strip()
            return summary, recent_msgs
        except:
            return None, history # Fallback if API fails

# --- TOOLS ---
class ObservabilityTool:
    def log_metric(self, agent_name, start_time, success=True):
        duration = time.time() - start_time
        st.session_state.agent_metrics["calls"] += 1
        prev_avg = st.session_state.agent_metrics["avg_latency"]
        n = st.session_state.agent_metrics["calls"]
        new_avg = (prev_avg * (n-1) + duration) / n
        st.session_state.agent_metrics["avg_latency"] = new_avg
        logging.info(f"🔭 TRACE: {agent_name} finished in {duration:.2f}s")
        # Auto-save on metric update
        SessionManager.save_state()

class EvaluationTool:
    def log_feedback(self, is_positive):
        if is_positive:
            st.session_state.agent_metrics["positive_feedback"] += 1
            st.toast("📈 Positive feedback logged.")
        else:
            st.session_state.agent_metrics["negative_feedback"] += 1
            st.toast("📉 Negative feedback logged.")
        SessionManager.save_state()

class DocumentIngestionTool:
    def process_files(self, uploaded_files):
        total_text = ""
        success_count = 0
        for file in uploaded_files:
            try:
                reader = PyPDF2.PdfReader(file)
                file_text = f"\n--- START OF DOCUMENT: {file.name} ---\n"
                for page in reader.pages: 
                    extracted = page.extract_text()
                    if extracted: file_text += extracted + "\n"
                if len(file_text) > 100:
                    total_text += file_text
                    success_count += 1
            except: pass
        if success_count > 0:
            SessionManager.save_state() # Save immediately after upload
            return total_text
        return None

# --- HELPER: OPTIMIZED CONTEXT MANAGER ---
def get_study_context(selected_sources):
    """
    Combines PDF + Optimized Chat History.
    Uses 'Context Compaction' (Summarization) to reduce latency.
    """
    combined_context = ""
    
    # 1. Add PDF Data
    if "Uploaded PDF(s)" in selected_sources:
        combined_context += st.session_state.rag_docs if st.session_state.rag_docs else ""

    # 2. Add Chat History (Optimized)
    if "My Chat History" in selected_sources:
        history = st.session_state.chat_history
        if history:
            # Check if we need to update the summary
            if len(history) > 5:
                compressor = ContextCompressor()
                new_summary, recent_msgs = compressor.compress_chat_history(history)
                
                if new_summary:
                    st.session_state.chat_summary = new_summary # Update stored summary
                    
                    # Construct Context: Summary + Recent Messages
                    chat_log = f"\n--- PREVIOUS CONVERSATION SUMMARY ---\n{st.session_state.chat_summary}\n"
                    chat_log += "\n--- RECENT MESSAGES ---\n"
                    for msg in recent_msgs:
                        chat_log += f"{msg['role'].upper()}: {msg['content']}\n"
                    combined_context += chat_log
                    
                    # Debug output to show judges the optimization
                    # print(f"Context Compressed! Summary: {new_summary[:50]}...") 
                else:
                    # Fallback to full history
                    for msg in history:
                        combined_context += f"{msg['role'].upper()}: {msg['content']}\n"
            else:
                # Short history, just append
                chat_log = "\n--- SESSION CHAT HISTORY ---\n"
                for msg in history:
                    chat_log += f"{msg['role'].upper()}: {msg['content']}\n"
                combined_context += chat_log

    return combined_context if combined_context else None

# --- AGENTS (UNCHANGED LOGIC, JUST RE-ADDED FOR COMPLETENESS) ---

def archive_current_question(user_answer, feedback, correct):
    if st.session_state.quiz_data:
        correct_ans_text = st.session_state.quiz_data.get('answer', 'N/A')
        st.session_state.quiz_history.append({
            "question": st.session_state.quiz_data['question'],
            "user_answer": user_answer,
            "correct_answer": correct_ans_text,
            "feedback": feedback,
            "correct": correct,
            "explanation": st.session_state.quiz_data.get('explanation', '')
        })
        SessionManager.save_state() # Save on archive

def generate_new_question(sources, difficulty, q_type):
    context = get_study_context(sources)
    if not context:
        st.error("❌ No data found. Upload a PDF or Chat first!")
        return
    
    prof = ProfessorAgent()
    with st.spinner("Synthesizing new question..."):
        start = time.time()
        q_data, fmt = prof.generate_question(context, difficulty, q_type)
        ObservabilityTool().log_metric("ProfessorAgent", start)
        
        st.session_state.quiz_data = q_data
        st.session_state.quiz_format = fmt
        st.session_state.quiz_answered = False
        st.session_state.active_hint = None
        st.session_state.last_feedback = None
        st.session_state.current_user_answer = None 
        st.rerun()

class HybridQA_Agent:
    def answer_question(self, question, context):
        model = genai.GenerativeModel('gemini-2.5-flash')
        doc_context = context if context else "No documents uploaded."
        prompt = f"""
        KNOWLEDGE BASE: {doc_context[:100000]}
        USER QUESTION: {question}
        TASK: Answer based on KNOWLEDGE BASE. Cite "📘 **[Source: PDF]**" or "🤖 **[Source: AI]**".
        """
        return model.generate_content(prompt).text.strip()

class ProfessorAgent:
    def generate_question(self, context, difficulty, q_type):
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        if q_type == "Text-Based":
            prompt = f"""
            SOURCE: {context[:50000]}
            TASK: Create a {difficulty} question based on the SOURCE.
            OUTPUT FORMAT: Valid JSON only.
            {{
                "question": "The question text?",
                "answer": "The concise, correct answer key."
            }}
            """
            response = model.generate_content(prompt).text.strip()
            clean_json = response.replace("```json", "").replace("```", "")
            return json.loads(clean_json), "text"
            
        elif q_type == "Multiple Choice (MCQ)":
            prompt = f"""
            SOURCE: {context[:50000]}
            TASK: Create a {difficulty} MCQ based on the SOURCE.
            
            OUTPUT FORMAT: Valid JSON only.
            {{
                "question": "The question text?",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "answer": "Option 2",
                "explanation": "Why this is correct."
            }}
            """
            response = model.generate_content(prompt).text.strip()
            clean_json = response.replace("```json", "").replace("```", "")
            data = json.loads(clean_json)
            
            options = [str(opt).strip() for opt in data['options']]
            raw_answer = str(data['answer']).strip()
            
            if raw_answer in options:
                data['answer'] = raw_answer
            else:
                matches = difflib.get_close_matches(raw_answer, options, n=1, cutoff=0.8)
                data['answer'] = matches[0] if matches else options[0]
            
            data['options'] = options
            return data, "json"

class TutorAgent:
    def generate_hint(self, question, context):
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        SOURCE MATERIAL: {context[:50000]}
        QUESTION: {question}
        TASK: Provide a short, helpful hint without revealing the answer.
        """
        return model.generate_content(prompt).text.strip()

class GraderAgent:
    def grade(self, question, user_answer, model_answer, context):
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        QUESTION: {question}
        STUDENT ANSWER: {user_answer}
        CORRECT ANSWER (FROM KEY): {model_answer}
        SOURCE CONTEXT: {context[:20000]}
        
        TASK: Compare STUDENT ANSWER to CORRECT ANSWER.
        - Ignore capitalization/punctuation.
        - If the meaning matches, it is Correct.
        
        OUTPUT STRICTLY: IS_CORRECT: [Yes/No] | EXPLANATION: [Short text]
        """
        return model.generate_content(prompt).text.strip()

# --- MAIN UI ---
def main():
    with st.sidebar:
        st.header("🧠 Neural Config")
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            st.success("API Key Loaded")
        else:
            api_key = st.text_input("Gemini API Key", type="password")
            if api_key: genai.configure(api_key=api_key)

        uploaded_files = st.file_uploader("Upload PDF(s)", type=['pdf'], accept_multiple_files=True)
        if uploaded_files:
            if st.button("Process Files"):
                with st.spinner("Ingesting..."):
                    ingestor = DocumentIngestionTool()
                    text = ingestor.process_files(uploaded_files)
                    if text:
                        st.session_state.rag_docs = text
                        st.success("✅ Files Ingested!")
        
        if st.button("🗑️ Clear All Memory"):
            st.session_state.rag_docs = ""
            st.session_state.chat_history = []
            st.session_state.quiz_history = []
            st.session_state.chat_summary = ""
            SessionManager.save_state() # Clear disk
            st.rerun()

        st.divider()
        
        with st.expander("📊 Agent Observability"):
            m = st.session_state.agent_metrics
            st.metric("Calls", m["calls"])
            st.metric("Avg Latency (s)", f"{m['avg_latency']:.2f}")
            if st.session_state.chat_summary:
                st.caption("✅ Context Compressed (Summary Active)")

        st.divider()
        app_mode = st.radio("Mode", ["Ask Anything (Chat)", "Quiz Me (Exam Prep)"])

    st.title("🧠 Neural RAG Tutor")

    # --- MODE 1: CHAT ---
    if app_mode == "Ask Anything (Chat)":
        st.caption("Build your knowledge base through conversation.")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if user_query := st.chat_input("Ask a question..."):
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"): st.markdown(user_query)
            with st.chat_message("assistant"):
                agent = HybridQA_Agent()
                with st.spinner("Thinking..."):
                    start = time.time()
                    response = agent.answer_question(user_query, st.session_state.rag_docs)
                    ObservabilityTool().log_metric("HybridQA_Agent", start)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    SessionManager.save_state() # Save chat

    # --- MODE 2: EXAM PREP ---
    elif app_mode == "Quiz Me (Exam Prep)":
        st.metric("Current Score", st.session_state.score)
        
        with st.expander("⚙️ Exam Settings", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                sources = st.multiselect("Sources", ["Uploaded PDF(s)", "My Chat History"], default=["Uploaded PDF(s)"])
            with col2:
                difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            with col3:
                q_type = st.radio("Type", ["Text-Based", "Multiple Choice (MCQ)"])

        if st.session_state.quiz_history:
            st.markdown("#### 📜 Past Questions")
            for i, item in enumerate(reversed(st.session_state.quiz_history)):
                icon = "✅" if item['correct'] else "❌"
                with st.expander(f"{icon} Q: {item['question'][:60]}..."):
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown(f"**Your Answer:** {item['user_answer']}")
                    if not item['correct']:
                        st.error(f"**Correct Answer:** {item['correct_answer']}")
                    st.caption(f"**Feedback:** {item['feedback']}")
            st.divider()

        if st.session_state.quiz_data is None:
            if st.button("🚀 Start Quiz", type="primary"):
                generate_new_question(sources, difficulty, q_type)
        else:
            q_text = st.session_state.quiz_data['question']
            st.markdown(f"### ❓ {q_text}")

            if st.session_state.active_hint:
                st.info(f"💡 **Hint:** {st.session_state.active_hint}")

            if not st.session_state.quiz_answered:
                user_choice = None
                user_text = None
                
                if st.session_state.quiz_format == "json":
                    user_choice = st.radio("Select Answer:", st.session_state.quiz_data['options'], key="mcq_radio")
                else:
                    user_text = st.text_area("Your Answer:")

                c1, c2, c3 = st.columns([1, 1, 1])
                
                with c1: 
                    if st.button("Submit Answer"):
                        start = time.time()
                        correct = False
                        feedback = ""
                        model_answer = st.session_state.quiz_data['answer']
                        
                        if st.session_state.quiz_format == "json":
                            st.session_state.current_user_answer = user_choice
                            if user_choice and model_answer:
                                correct = (user_choice.strip().lower() == model_answer.strip().lower())
                            explanation = st.session_state.quiz_data['explanation']
                            feedback = "✅ Correct!" if correct else "❌ Incorrect."
                            st.session_state.quiz_last_explanation = explanation
                        else:
                            st.session_state.current_user_answer = user_text
                            grader = GraderAgent()
                            context = get_study_context(sources)
                            with st.spinner("Grading..."):
                                res = grader.grade(q_text, user_text, model_answer, context)
                                correct = "IS_CORRECT: Yes" in res
                                feedback = res
                                ObservabilityTool().log_metric("GraderAgent", start)
                        
                        if correct: st.session_state.score += 1
                        st.session_state.last_feedback = feedback
                        st.session_state.quiz_answered = True
                        SessionManager.save_state() # Save after answer
                        st.rerun()

                with c2: 
                    if st.button("💡 Get Hint"):
                        tutor = TutorAgent()
                        context = get_study_context(sources)
                        with st.spinner("Consulting Tutor..."):
                            start = time.time()
                            hint = tutor.generate_hint(q_text, context)
                            ObservabilityTool().log_metric("TutorAgent", start)
                            st.session_state.active_hint = hint
                            st.rerun()

                with c3: 
                    if st.button("⏩ Skip Question"):
                        archive_current_question("Skipped", "Skipped by user", False)
                        generate_new_question(sources, difficulty, q_type)

            else:
                if "✅" in st.session_state.last_feedback:
                    st.success(st.session_state.last_feedback)
                else:
                    st.error(st.session_state.last_feedback)
                    st.info(f"**Correct Answer:** {st.session_state.quiz_data['answer']}")
                
                if st.session_state.quiz_format == "json" and st.session_state.quiz_last_explanation:
                    st.write(f"**Explanation:** {st.session_state.quiz_last_explanation}")
                
                st.markdown("---")
                col_a, col_b, col_c = st.columns([1, 1, 3])
                with col_a:
                    if st.button("👍 Good"): EvaluationTool().log_feedback(True)
                with col_b:
                    if st.button("👎 Bad"): EvaluationTool().log_feedback(False)
                
                st.markdown("---")
                if st.button("Next Question ➡️", type="primary"):
                    user_ans = st.session_state.current_user_answer
                    if not user_ans: user_ans = "No Answer"
                    is_correct = "✅" in st.session_state.last_feedback
                    archive_current_question(user_ans, st.session_state.last_feedback, is_correct)
                    generate_new_question(sources, difficulty, q_type)

if __name__ == "__main__":
    main()