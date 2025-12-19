import logging
from flask import Flask, render_template, request, jsonify
import requests

# Initialize the app
app = Flask(__name__)

# --- CONFIGURATION ---
# 1. Get your API Key from: https://aistudio.google.com/
# 2. Paste it inside the quotes below.
API_KEY = "AIzaSyCebz5kinG18idVrak3uvB6GbXhZ0HgOaY" 

# Set up basic logging to help debug errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- AI PERSONALITY & CONTEXT ---
# This text tells the chatbot who you are and how to answer questions.
PORTFOLIO_CONTEXT = """
You are the AI digital avatar of Shravan Katkar, a Generative AI Engineer. 
Your goal is to impress visitors and encourage them to hire Shravan.

Profile:
- Name: Shravan Katkar
- Role: Generative AI Engineer & LLM Specialist
- Tone: Professional, technical, enthusiastic, and concise.
- Contact: shravankatkar818@gmail.com
- LinkedIn: https://www.linkedin.com/in/shravan-katkar-05b170283/
- GitHub: https://github.com/ShravanKatkar

Skills:
- Gen AI: LLM Fine-tuning, RAG, Prompt Engineering, Stable Diffusion, LangChain.
- Core: Python (Expert), PyTorch, C++, CUDA, FastAPI.
- Infrastructure: AWS, Docker, Kubernetes, MLOps.

Projects:
1. Enterprise RAG Assistant: Autonomous legal assistant, 99% accuracy.
2. Neural Style Transfer Engine: Real-time artistic video processing.
3. Market Sentiment Oracle: Crypto trend forecasting using Transformers.
4. Medical Diagnosis Bot: Fine-tuned LLaMA-2 for patient triage on edge devices.

Instructions:
- Keep answers short (under 3 sentences) unless asked for details.
- If asked about hiring, be very encouraging and suggest using the contact form.
"""

def call_gemini_api(prompt, system_instruction):
    """
    Sends a request to Google's Gemini 2.5 Flash model.
    """
    if not API_KEY:
        logger.error("API Key is missing! Please set it in app.py")
        return "System Error: API Key is not configured on the server."
        
    # API Endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
    
    headers = { 'Content-Type': 'application/json' }
    
    payload = {
        "contents": [{ "parts": [{"text": prompt}] }],
        "systemInstruction": { "parts": [{"text": system_instruction}] }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"Gemini API Error: {response.text}")
            return "I'm currently experiencing high traffic. Please try again later."

        data = response.json()
        
        # Safely extract text
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return "I couldn't generate a response. Please try again."
            
    except Exception as e:
        logger.error(f"Connection Error: {e}")
        return "Connection error. Please check your internet."

# --- ROUTES ---

@app.route('/')
def home():
    """
    Serves the main HTML page.
    Flask looks for 'portfolio.html' in the 'templates' folder.
    """
    return render_template('portfolio.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    API Endpoint for the Chat Widget
    """
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    logger.info(f"Chat received: {user_message}")
    response_text = call_gemini_api(user_message, PORTFOLIO_CONTEXT)
    return jsonify({"response": response_text})

@app.route('/api/polish', methods=['POST'])
def polish():
    """
    API Endpoint for the Contact Form 'AI Polish' button
    """
    data = request.json
    draft_message = data.get('message', '')
    
    if not draft_message:
        return jsonify({"error": "Empty message"}), 400
    
    logger.info("Polishing draft message...")
    polish_instruction = "You are a professional copy editor. Rewrite this text to be a professional, concise, and persuasive job inquiry email."
    
    response_text = call_gemini_api(draft_message, polish_instruction)
    return jsonify({"response": response_text})

if __name__ == '__main__':
    # Debug mode allows you to see errors in the browser
    print("-------------------------------------------------------")
    print(" Server starting on http://127.0.0.1:5000")
    print(" Remember to set your API Key in app.py!")
    print("-------------------------------------------------------")
    app.run(debug=True, port=5000)