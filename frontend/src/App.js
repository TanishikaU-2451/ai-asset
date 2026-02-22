/**
 * App.js — Root component for the NAAC Compliance Intelligence System.
 */

import React, { useState, useEffect } from "react";
import ChatUI from "./ChatUI";
import { getHealth, getLastSync, forceUpdate } from "./api";

function HealthIndicator({ status }) {
  const color = status === "up" ? "#22c55e" : status === "down" ? "#ef4444" : "#f59e0b";
  return (
    <span
      style={{
        display: "inline-block",
        width: "8px",
        height: "8px",
        borderRadius: "50%",
        backgroundColor: color,
        marginRight: "4px",
      }}
    />
  );
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [lastSync, setLastSync] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [syncMsg, setSyncMsg] = useState("");

  const fetchStatus = async () => {
    try {
      const [h, s] = await Promise.all([getHealth(), getLastSync()]);
      setHealth(h);
      setLastSync(s);
    } catch {
      /* ignore on initial load */
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleForceUpdate = async () => {
    setUpdating(true);
    setSyncMsg("");
    try {
      const result = await forceUpdate();
      setSyncMsg(
        `✅ Sync complete — ${result.documents_downloaded ?? 0} documents downloaded, ` +
          `${result.chunks_added ?? 0} chunks added.`
      );
      await fetchStatus();
    } catch (err) {
      setSyncMsg(`❌ Update failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const formatSync = (sync) => {
    if (!sync?.last_sync) return "Never";
    return new Date(sync.last_sync).toLocaleString();
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        margin: 0,
        fontFamily: "'Segoe UI', system-ui, sans-serif",
      }}
    >
      {/* Header */}
      <header
        style={{
          backgroundColor: "#1e3a5f",
          color: "#fff",
          padding: "12px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "1.2rem", fontWeight: "700" }}>
            🎓 NAAC Compliance Intelligence System
          </h1>
          <p style={{ margin: 0, fontSize: "0.8rem", color: "#93c5fd" }}>
            MVSR Engineering College — IQAC RAG Platform
          </p>
        </div>

        {/* Status bar */}
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          {health && (
            <div style={{ fontSize: "0.78rem", color: "#e2e8f0" }}>
              <HealthIndicator status={health.ollama} />
              Ollama&nbsp;&nbsp;
              <HealthIndicator status={health.chromadb} />
              ChromaDB&nbsp;
              {health.naac_chunks !== undefined && (
                <span style={{ color: "#93c5fd" }}>
                  ({health.naac_chunks} NAAC / {health.mvsr_chunks} MVSR chunks)
                </span>
              )}
            </div>
          )}

          <div style={{ fontSize: "0.78rem", color: "#e2e8f0" }}>
            Last sync: {formatSync(lastSync)}
          </div>

          <button
            onClick={handleForceUpdate}
            disabled={updating}
            style={{
              padding: "6px 14px",
              backgroundColor: updating ? "#475569" : "#2563eb",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: updating ? "not-allowed" : "pointer",
              fontSize: "0.8rem",
              fontWeight: "600",
            }}
          >
            {updating ? "Updating…" : "🔄 Force Update"}
          </button>
        </div>
      </header>

      {/* Sync message banner */}
      {syncMsg && (
        <div
          style={{
            backgroundColor: syncMsg.startsWith("✅") ? "#f0fdf4" : "#fef2f2",
            color: syncMsg.startsWith("✅") ? "#166534" : "#991b1b",
            padding: "8px 24px",
            fontSize: "0.85rem",
            borderBottom: "1px solid #e5e7eb",
          }}
        >
          {syncMsg}
        </div>
      )}

      {/* Main chat area */}
      <main style={{ flex: 1, overflow: "hidden" }}>
        <ChatUI />
      </main>
    </div>
  );
}
