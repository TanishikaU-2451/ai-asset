/**
 * ChatUI.js — Compliance chat interface for the NAAC Intelligence System.
 *
 * Displays:
 *  - User query and full LLM answer
 *  - NAAC Requirement excerpt
 *  - MVSR Evidence excerpt
 *  - Criterion Mapping
 *  - Compliance Status badge
 */

import React, { useState, useRef, useEffect } from "react";
import { submitQuery } from "./api";

const STATUS_COLORS = {
  Supported: "#22c55e",
  "Partially Supported": "#f59e0b",
  "Gap Identified": "#ef4444",
};

function StatusBadge({ status }) {
  const color = STATUS_COLORS[status] || "#6b7280";
  return (
    <span
      style={{
        display: "inline-block",
        padding: "3px 12px",
        borderRadius: "12px",
        backgroundColor: color,
        color: "#fff",
        fontWeight: "600",
        fontSize: "0.85rem",
      }}
    >
      {status}
    </span>
  );
}

function ComplianceCard({ result }) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "8px",
        padding: "16px",
        marginTop: "12px",
        backgroundColor: "#f9fafb",
      }}
    >
      {/* Header row */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "12px",
        }}
      >
        <span style={{ fontWeight: "600", color: "#1e3a5f", fontSize: "0.9rem" }}>
          📋 {result.naac_mapping}
        </span>
        <StatusBadge status={result.status} />
      </div>

      {/* Answer */}
      <div style={{ marginBottom: "12px" }}>
        <p
          style={{
            margin: "0 0 4px",
            fontWeight: "600",
            color: "#374151",
            fontSize: "0.85rem",
          }}
        >
          🤖 Analysis
        </p>
        <p style={{ margin: 0, color: "#4b5563", whiteSpace: "pre-wrap", fontSize: "0.9rem" }}>
          {result.answer}
        </p>
      </div>

      {/* Two-column layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
        {/* NAAC Requirement */}
        <div
          style={{
            backgroundColor: "#eff6ff",
            border: "1px solid #bfdbfe",
            borderRadius: "6px",
            padding: "12px",
          }}
        >
          <p
            style={{
              margin: "0 0 6px",
              fontWeight: "600",
              color: "#1d4ed8",
              fontSize: "0.8rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            📘 NAAC Requirement
          </p>
          <p style={{ margin: 0, color: "#1e40af", fontSize: "0.85rem" }}>
            {result.naac_requirement || "No NAAC context retrieved."}
          </p>
        </div>

        {/* MVSR Evidence */}
        <div
          style={{
            backgroundColor: "#f0fdf4",
            border: "1px solid #bbf7d0",
            borderRadius: "6px",
            padding: "12px",
          }}
        >
          <p
            style={{
              margin: "0 0 6px",
              fontWeight: "600",
              color: "#15803d",
              fontSize: "0.8rem",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            🏫 MVSR Evidence
          </p>
          <p style={{ margin: 0, color: "#166534", fontSize: "0.85rem" }}>
            {result.mvsr_evidence || "No MVSR evidence retrieved."}
          </p>
        </div>
      </div>
    </div>
  );
}

function Message({ role, text, result }) {
  const isUser = role === "user";
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: isUser ? "flex-end" : "flex-start",
        marginBottom: "16px",
      }}
    >
      <div
        style={{
          maxWidth: "85%",
          backgroundColor: isUser ? "#1e3a5f" : "#ffffff",
          color: isUser ? "#fff" : "#111827",
          borderRadius: "12px",
          padding: "12px 16px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}
      >
        {text}
      </div>
      {result && <ComplianceCard result={result} />}
    </div>
  );
}

export default function ChatUI() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;

    setInput("");
    setError("");
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setLoading(true);

    try {
      const result = await submitQuery(query);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: result.answer, result },
      ]);
    } catch (err) {
      const msg =
        err?.response?.data?.detail || err.message || "Unknown error";
      setError(`Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        fontFamily: "'Segoe UI', system-ui, sans-serif",
      }}
    >
      {/* Messages area */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px",
          backgroundColor: "#f3f4f6",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              textAlign: "center",
              color: "#6b7280",
              marginTop: "60px",
              fontSize: "1rem",
            }}
          >
            <p style={{ fontSize: "1.5rem" }}>🎓</p>
            <p>Ask a compliance question, e.g.:</p>
            <p style={{ fontStyle: "italic" }}>
              "Do we meet NAAC student support standards?"
            </p>
            <p style={{ fontStyle: "italic" }}>
              "What proof exists for governance?"
            </p>
            <p style={{ fontStyle: "italic" }}>
              "Where do we align with teaching-learning guidelines?"
            </p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <Message key={idx} {...msg} />
        ))}
        {loading && (
          <div style={{ textAlign: "center", color: "#6b7280", padding: "12px" }}>
            ⏳ Analyzing compliance…
          </div>
        )}
        {error && (
          <div
            style={{
              textAlign: "center",
              color: "#ef4444",
              padding: "8px",
              fontSize: "0.9rem",
            }}
          >
            {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div
        style={{
          padding: "12px 16px",
          borderTop: "1px solid #e5e7eb",
          backgroundColor: "#ffffff",
          display: "flex",
          gap: "8px",
        }}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about NAAC compliance…"
          rows={2}
          style={{
            flex: 1,
            resize: "none",
            border: "1px solid #d1d5db",
            borderRadius: "8px",
            padding: "10px 12px",
            fontSize: "0.95rem",
            outline: "none",
            fontFamily: "inherit",
          }}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          style={{
            padding: "10px 20px",
            backgroundColor: loading || !input.trim() ? "#9ca3af" : "#1e3a5f",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: loading || !input.trim() ? "not-allowed" : "pointer",
            fontWeight: "600",
            fontSize: "0.95rem",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
