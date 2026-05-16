"use client";

import React from "react";

interface SourceBadgeProps {
  sources: string[];
}

export default function SourceBadge({ sources }: SourceBadgeProps) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-container">
      <span className="label">Sources retrieved:</span>
      <div className="badges">
        {sources.map((source, i) => (
          <div key={i} className="badge">
            {source}
          </div>
        ))}
      </div>

      <style jsx>{`
        .sources-container {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid var(--card-border);
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .label {
          font-family: var(--font-inter);
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: var(--text-muted);
        }

        .badges {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .badge {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--card-border);
          padding: 0.25rem 0.75rem;
          border-radius: 100px;
          font-size: 0.75rem;
          color: var(--accent);
          font-family: var(--font-inter);
        }
      `}</style>
    </div>
  );
}
