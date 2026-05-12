import React, { useState } from "react";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages([...messages, userMsg]);

    const res = await fetch("http://localhost:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });
    const data = await res.json();

    const botMsg = { sender: "bot", text: data.reply || data.error };
    setMessages((msgs) => [...msgs, botMsg]);
    setInput("");
  };

  const clearChat = async () => {
    await fetch("http://localhost:5000/clear", { method: "POST" });
    setMessages([]);
  };

  return (
    <div className="chat-container">
      <h2 className="hh2">MongoDB Chat Agent</h2>
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.sender}`}>
            <b>{msg.sender === "user" ? "You" : "Assistant"}:</b> {msg.text}
          </div>
        ))}
      </div>

      <div className="controls">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
        <button onClick={clearChat} className="clear-btn">Clear</button>
      </div>
    </div>
  );
}

export default App;
