"use client";

import React, { useEffect, useState } from "react";
import SourceBadge from "./SourceBadge";

export interface ExplanationData {
  title: string;
  modern_trigger: string;
  ancestral_mechanism: string;
  brain_chemistry: string;
  the_insight: string;
  confidence: string;
  sources: string[];
}

interface ExplanationCardProps {
  data: ExplanationData;
}

export default function ExplanationCard({ data }: ExplanationCardProps) {
  const [visibleSections, setVisibleSections] = useState<number>(0);

  useEffect(() => {
    // Staggered reveal of sections
    const interval = setInterval(() => {
      setVisibleSections((prev) => {
        if (prev >= 5) {
          clearInterval(interval);
          return 5;
        }
        return prev + 1;
      });
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glow-card fade-in">
      <h2 className="title">{data.title}</h2>
      
      <div className="content-grid">
        <section className={`section ${visibleSections >= 1 ? "visible" : ""}`}>
          <div className="tag">Modern Trigger</div>
          <p>{data.modern_trigger}</p>
        </section>

        <section className={`section ${visibleSections >= 2 ? "visible" : ""}`}>
          <div className="tag">Ancestral Mechanism</div>
          <p>{data.ancestral_mechanism}</p>
        </section>

        <section className={`section ${visibleSections >= 3 ? "visible" : ""}`}>
          <div className="tag">Brain Chemistry</div>
          <p>{data.brain_chemistry}</p>
        </section>

        <section className={`section highlighted ${visibleSections >= 4 ? "visible" : ""}`}>
          <div className="tag insight-tag">The Insight</div>
          <p className="insight-text">{data.the_insight}</p>
        </section>
      </div>

      <div className={`footer ${visibleSections >= 5 ? "visible" : ""}`}>
        <SourceBadge sources={data.sources} />
        <div className="confidence">
          Confidence: <span className={data.confidence}>{data.confidence}</span>
        </div>
      </div>

      <style jsx>{`
        .title {
          font-family: var(--font-crimson);
          font-size: 2.2rem;
          margin-bottom: 2rem;
          background: linear-gradient(135deg, #fff 0%, var(--accent) 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .content-grid {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .section {
          opacity: 0;
          transform: translateY(10px);
          transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .section.visible {
          opacity: 1;
          transform: translateY(0);
        }

        .tag {
          font-family: var(--font-inter);
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 2px;
          color: var(--accent);
          margin-bottom: 0.5rem;
        }

        .insight-tag {
          color: var(--success);
        }

        p {
          font-size: 1.05rem;
          color: var(--foreground);
        }

        .highlighted {
          background: rgba(57, 255, 138, 0.03);
          padding: 1.5rem;
          border-left: 2px solid var(--success);
          margin: 0.5rem -1.5rem;
          border-radius: 0 8px 8px 0;
        }

        .insight-text {
          font-family: var(--font-crimson);
          font-size: 1.25rem;
          line-height: 1.4;
          font-style: italic;
        }

        .footer {
          margin-top: 1rem;
          opacity: 0;
          transition: opacity 0.6s ease;
        }

        .footer.visible {
          opacity: 1;
        }

        .confidence {
          margin-top: 1rem;
          font-family: var(--font-inter);
          font-size: 0.7rem;
          text-transform: uppercase;
          color: var(--text-muted);
          text-align: right;
        }

        .confidence span.high { color: var(--success); }
        .confidence span.medium { color: orange; }
        .confidence span.low { color: #ff4a4a; }
      `}</style>
    </div>
  );
}
