"use client";

import React from "react";

export default function NeuralLoader() {
  return (
    <div className="neural-loader">
      <div className="nodes">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="node" style={{ 
            animationDelay: `${i * 0.2}s`,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`
          }} />
        ))}
      </div>
      <div className="scanning-text">Analyzing neural pathways...</div>
      
      <style jsx>{`
        .neural-loader {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 200px;
          gap: 1.5rem;
          margin: 2rem 0;
        }

        .nodes {
          position: relative;
          width: 80px;
          height: 80px;
        }

        .node {
          position: absolute;
          width: 8px;
          height: 8px;
          background: var(--accent);
          border-radius: 50%;
          box-shadow: 0 0 10px var(--accent);
          animation: pulse 1.5s infinite ease-in-out;
        }

        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 1; transform: scale(1.5); box-shadow: 0 0 20px var(--accent); }
        }

        .scanning-text {
          font-family: var(--font-inter);
          font-size: 0.9rem;
          letter-spacing: 2px;
          text-transform: uppercase;
          color: var(--text-muted);
          animation: breath 2s infinite ease-in-out;
        }

        @keyframes breath {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
