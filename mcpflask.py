import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

app = Flask(__name__)
CORS(app)  

config_file = "mongodb.json"
client = MCPClient.from_config_file(config_file)
llm = ChatGroq(model="llama-3.3-70b-versatile")

agent = MCPAgent(
    llm=llm,
    client=client,
    max_steps=15,
    memory_enabled=True,
)

@app.route("/chat", methods=["POST"])
def chat():
    """Receive user message and return LLM response."""
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "Message required"}), 400

    try:
        response = asyncio.run(agent.run(user_input))
        return jsonify({"reply": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear():
    """Clear memory (conversation history)."""
    try:
        agent.clear_conversation_history()
        return jsonify({"message": "History cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
