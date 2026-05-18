"use client";

import React, { useState, useEffect, useRef } from "react";
import InputPanel from "@/components/InputPanel";
import ExplanationCard from "@/components/ExplanationCard";
import NeuralLoader from "@/components/NeuralLoader";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [explanation, setExplanation] = useState<Record<string, unknown> | null>(null);
  const [retrievalMeta, setRetrievalMeta] = useState<Record<string, unknown> | null>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  const handleExplain = async (query: string) => {
    setIsLoading(true);
    setExplanation(null);
    setRetrievalMeta(null);

    try {
      const response = await fetch("http://localhost:8000/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.body) return;

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6);
            if (dataStr === "[DONE]") {
              setIsLoading(false);
              continue;
            }

            try {
              const data = JSON.parse(dataStr);
              if (data.type === "context_ready") {
                setRetrievalMeta(data);
              } else if (data.type === "done") {
                setExplanation(data.explanation);
                setIsLoading(false);
              } else if (data.type === "error") {
                console.error("Model error:", data.message);
                setIsLoading(false);
              }
            } catch (e) {
              console.error("Failed to parse SSE data:", e);
            }
          }
        }
      }
    } catch (err) {
      console.error("Fetch error:", err);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (explanation && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [explanation]);

  return (
    <main className="container">
      <div className="hero-section fade-in">
        <h1 className="title">Biological legacy of our<br/>ancient brain</h1>

        <div className="search-container">
          <InputPanel onSubmit={handleExplain} isLoading={isLoading} />
        </div>

        <div className="suggestion-chips">
          <button onClick={() => handleExplain("Social Rejection")} disabled={isLoading}>Social Rejection</button>
          <button onClick={() => handleExplain("Sugar Cravings")} disabled={isLoading}>Sugar Cravings</button>
          <button onClick={() => handleExplain("Fear of the Dark")} disabled={isLoading}>Fear of the Dark</button>
          <button onClick={() => handleExplain("Doomscrolling")} disabled={isLoading}>Doomscrolling</button>
        </div>

        <p className="description">
          Platform designed to be your <strong>personal AI-powered companion</strong> for tracing modern fears,
          anxieties, and behaviors back to their ancestral survival origins. Prefrontal, powered by 
          advanced RAG technology, simplifies the process of understanding evolutionary psychology using
          <strong> Pinecone</strong> and <strong>Groq LLMs</strong>.
        </p>
      </div>

      <div className="main-content">
        {isLoading && !explanation && <NeuralLoader />}

        {explanation && (
          <div className="result-area" ref={resultRef}>
            <div className="meta-info fade-in">
              {retrievalMeta && (
                <span>
                  Retrieved {retrievalMeta.chunks_used} survival patterns in {retrievalMeta.retrieval_ms}ms
                </span>
              )}
            </div>
            <ExplanationCard data={explanation} />
          </div>
        )}
      </div>

      <style jsx>{`
        .container {
          max-width: 900px;
          margin: 0 auto;
          padding: 4rem 2rem;
          display: flex;
          flex-direction: column;
          min-height: 100vh;
          align-items: center;
        }

        .hero-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          text-align: center;
          width: 100%;
          margin-bottom: 2rem;
        }

        .title {
          font-family: var(--font-inter);
          font-size: 3rem;
          font-weight: 600;
          line-height: 1.2;
          letter-spacing: -1px;
          color: #ffffff;
          margin-bottom: 3rem;
        }

        .search-container {
          width: 100%;
          max-width: 700px;
          margin-bottom: 2rem;
        }

        .suggestion-chips {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 0.75rem;
          margin-bottom: 4rem;
        }

        .suggestion-chips button {
          background: rgba(255, 255, 255, 0.03);
          border: 1px solid rgba(255, 255, 255, 0.08);
          padding: 0.6rem 1.2rem;
          border-radius: 100px;
          color: var(--text-muted);
          font-family: var(--font-inter);
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .suggestion-chips button:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.08);
          color: #ffffff;
        }

        .suggestion-chips button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .description {
          max-width: 750px;
          font-family: var(--font-inter);
          font-size: 1rem;
          line-height: 1.6;
          color: #888899;
        }

        .description strong {
          color: #dddded;
          font-weight: 500;
        }

        .main-content {
          width: 100%;
          max-width: 800px;
          display: flex;
          flex-direction: column;
          gap: 3rem;
        }

        .result-area {
          margin-top: 1rem;
        }

        .meta-info {
          font-family: var(--font-inter);
          font-size: 0.65rem;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: rgba(255, 255, 255, 0.2);
          margin-bottom: 1rem;
          text-align: center;
        }
      `}</style>
    </main>
  );
}
