// src/components/ChatBox.jsx
import React, { useRef, useState } from "react";

export default function ChatBox({ language, onSchemes }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [listening, setListening] = useState(false);
  const [lastMessage, setLastMessage] = useState("");
  const recognitionRef = useRef(null);
  const suggestions = [
    "Scholarships for students",
    "Pension schemes",
    "Farmer support",
  ];

  const sendMessage = async (overrideMessage) => {
    const message = (overrideMessage || input).trim();
    if (!message || loading) return;
    const userMsg = { role: "user", content: message };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setError("");
    setLoading(true);
    setLastMessage(message);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, language }),
      });
      if (!res.ok) {
        throw new Error(`The server returned ${res.status}.`);
      }
      const data = await res.json();
      const aiMsg = {
        role: "assistant",
        content: typeof data.answer === "string" ? data.answer : "I could not generate a response.",
      };
      setMessages([...newMessages, aiMsg]);
      onSchemes(Array.isArray(data.schemes) ? data.schemes : []);
    } catch (e) {
      console.error(e);
      setError("Unable to get a response. Please check that the backend is running.");
      setMessages([...newMessages, {
        role: "assistant",
        content: "Sorry, I could not complete your request.",
      }]);
      onSchemes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startVoice = async () => {
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Voice typing needs Chrome or Edge. You can still type your question.");
      return;
    }
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      setError("Microphone access requires localhost or a secure HTTPS connection.");
      return;
    }
    setError("");
    let microphone;
    try {
      microphone = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      setError(error.name === "NotAllowedError"
        ? "Microphone permission is blocked. Allow microphone access for this site in your browser settings."
        : "No microphone was found. Connect a microphone and try again.");
      return;
    }
    microphone.getTracks().forEach((track) => track.stop());

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = language === "hi" ? "hi-IN" : language === "te" ? "te-IN" : "en-IN";
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onstart = () => setListening(true);
    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };
    recognition.onerror = (event) => {
      setListening(false);
      recognitionRef.current = null;
      const messages = {
        "not-allowed": "Microphone permission is blocked. Allow microphone access for this site in your browser settings.",
        "service-not-allowed": "The browser speech service is blocked. Try Chrome or Edge and allow its speech service.",
        "audio-capture": "No microphone was found. Connect a microphone and try again.",
        "no-speech": "No speech was detected. Try again and speak closer to the microphone.",
        network: "The browser's speech-to-text service is unreachable. Use Chrome or Edge with internet access. Your transcript will appear here; press Send to submit it.",
        "language-not-supported": "Speech recognition does not support this language in your browser.",
      };
      setError(messages[event.error] || `Voice input failed (${event.error}). Check microphone permission and try again.`);
    };
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript;
      if (transcript) {
        setInput((current) => `${current}${current ? " " : ""}${transcript}`);
        setError("");
      }
    };
    try {
      recognition.start();
    } catch (error) {
      setListening(false);
      recognitionRef.current = null;
      setError(`Could not start voice input: ${error.message}`);
    }
  };

  const uploadDocument = async (event) => {
    const fileInput = event.currentTarget;
    const file = fileInput.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setError("This file is larger than 10 MB. Choose a smaller file.");
      fileInput.value = "";
      return;
    }
    const isPdf = file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
    const isImage = file.type.startsWith("image/") || /\.(png|jpe?g|webp|gif)$/i.test(file.name);
    if (!isPdf && !isImage) {
      setError("Choose a PDF or image file.");
      fileInput.value = "";
      return;
    }
    setLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/documents/analyze", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `The server returned ${res.status}.`);
      setMessages((current) => [
        ...current,
        { role: "user", content: `Analyze document: ${file.name}` },
        { role: "assistant", content: data.summary || "The document could not be summarized." },
      ]);
    } catch (e) {
      setError(e.message || "Unable to analyze this document. Check the backend connection and try again.");
    } finally {
      setLoading(false);
      fileInput.value = "";
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-heading">
        <div className="assistant-avatar" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M7 18.5V21L10.5 18.5H16.5C18.4 18.5 20 16.9 20 15V8C20 6.1 18.4 4.5 16.5 4.5H7C5.1 4.5 3.5 6.1 3.5 8V15C3.5 16.9 5.1 18.5 7 18.5Z" stroke="currentColor" strokeWidth="1.6"/>
            <circle cx="8.5" cy="11" r="1" fill="currentColor"/><circle cx="12" cy="11" r="1" fill="currentColor"/><circle cx="15.5" cy="11" r="1" fill="currentColor"/>
          </svg>
        </div>
        <div>
          <h3>JanSahay Assistant</h3>
          <p><span></span> Ready to help</p>
        </div>
        {messages.length > 0 && (
          <button type="button" className="new-chat-button" onClick={() => { setMessages([]); setError(""); onSchemes([]); }}>New chat</button>
        )}
      </div>

      <div className="chat-panel" aria-live="polite">
        {messages.length === 0 && (
          <div className="empty-chat">
            <div className="empty-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M12 3V5M5.6 5.6L7 7M18.4 5.6L17 7M4 12H6M18 12H20M7 17H17" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
                <path d="M8 12C8 9.8 9.8 8 12 8C14.2 8 16 9.8 16 12C16 14.2 14.2 16 12 16C9.8 16 8 14.2 8 12Z" stroke="currentColor" strokeWidth="1.6"/>
              </svg>
            </div>
            <h4>How can I help you today?</h4>
            <p>Tell me about yourself and I’ll find relevant government schemes.</p>
            <div className="suggestion-list">
              {suggestions.map((suggestion) => (
                <button key={suggestion} type="button" onClick={() => setInput(suggestion)}>
                  {suggestion}
                  <svg viewBox="0 0 20 20" fill="none"><path d="M4 10H16M11 5L16 10L11 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`message-row ${m.role}`}>
            <div className="message-label">{m.role === "assistant" ? "JanSahay AI" : "You"}</div>
            <div className="message-bubble">{m.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message-row assistant">
            <div className="message-label">JanSahay AI</div>
            <div className="message-bubble muted">Thinking...</div>
          </div>
        )}
      </div>
      {error && (
        <div className="chat-error" role="alert">
          <span>{error}</span>
          {lastMessage && <button type="button" onClick={() => sendMessage(lastMessage)}>Retry</button>}
        </div>
      )}
      <div className="chat-compose">
        <label className={`tool-button upload-button ${loading ? "disabled" : ""}`} title="Upload document">
          <input type="file" accept=".pdf,image/*" onChange={uploadDocument} disabled={loading} />
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 16V4M7.5 8.5L12 4L16.5 8.5M5 14V19H19V14" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"/></svg>
        </label>
        <button type="button" onClick={startVoice} className={`tool-button ${listening ? "listening" : ""}`} title={listening ? "Stop voice input" : "Voice input"} aria-label={listening ? "Stop voice input" : "Start voice input"} aria-pressed={listening}>
          <svg viewBox="0 0 24 24" fill="none"><rect x="9" y="3" width="6" height="11" rx="3" stroke="currentColor" strokeWidth="1.7"/><path d="M5.5 11.5C5.5 15.1 8.4 18 12 18C15.6 18 18.5 15.1 18.5 11.5M12 18V21M9 21H15" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"/></svg>
        </button>
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Type your question..."
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="send-button"
          aria-label="Send message"
        >
          {loading ? (
            <span className="send-spinner"></span>
          ) : (
            <svg viewBox="0 0 24 24" fill="none"><path d="M20 4L10.5 13.5M20 4L14 20L10.5 13.5M20 4L4 10L10.5 13.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round"/></svg>
          )}
        </button>
      </div>
      <p className="compose-hint">Upload a PDF or image · Voice transcription needs an online speech service and appears here before you send.</p>
    </div>
  );
}
