"use client";

import React, { useState } from "react";

interface InputPanelProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export default function InputPanel({ onSubmit, isLoading }: InputPanelProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleSubmit(e);
    }
  };

  return (
    <form className="input-container fade-in" onSubmit={handleSubmit}>
      <div className="input-card">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type here..."
          disabled={isLoading}
          className={isLoading ? "disabled" : ""}
        />
        
        <div className="input-toolbar">
          <div className="toolbar-left">
            <button type="button" className="icon-btn" disabled>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
              Attach
            </button>
            <button type="button" className="icon-btn" disabled>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
              Context
            </button>
          </div>
          
          <div className="toolbar-right">
            <button type="button" className="icon-btn" disabled>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              Public
            </button>
            
            <button type="submit" className="submit-btn" disabled={isLoading || !query.trim()}>
              {isLoading ? (
                <div className="spinner"></div>
              ) : (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 19V5"/><path d="m5 12 7-7 7 7"/></svg>
              )}
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .input-container {
          width: 100%;
        }

        .input-card {
          background: rgba(25, 25, 35, 0.6);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 16px;
          padding: 0.5rem;
          display: flex;
          flex-direction: column;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
          transition: border-color 0.3s ease;
        }

        .input-card:focus-within {
          border-color: rgba(255, 255, 255, 0.2);
        }

        textarea {
          width: 100%;
          min-height: 80px;
          background: transparent;
          border: none;
          padding: 1rem;
          color: white;
          font-family: var(--font-inter);
          font-size: 1.1rem;
          resize: none;
          outline: none;
        }

        textarea.disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .input-toolbar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.5rem;
          border-top: 1px solid rgba(255, 255, 255, 0.05);
          margin-top: 0.5rem;
        }

        .toolbar-left, .toolbar-right {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .icon-btn {
          display: flex;
          align-items: center;
          gap: 0.4rem;
          background: transparent;
          border: none;
          color: #888899;
          font-family: var(--font-inter);
          font-size: 0.8rem;
          padding: 0.4rem 0.8rem;
          border-radius: 100px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .icon-btn:hover:not(:disabled) {
          background: rgba(255, 255, 255, 0.05);
          color: #e0e0e6;
        }
        
        .icon-btn:disabled {
          cursor: default;
        }

        .submit-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 36px;
          height: 36px;
          background: #ffffff;
          color: #050508;
          border: none;
          border-radius: 50%;
          cursor: pointer;
          transition: all 0.2s ease;
          margin-left: 0.5rem;
        }

        .submit-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
        }

        .submit-btn:disabled {
          background: rgba(255, 255, 255, 0.2);
          color: rgba(0, 0, 0, 0.5);
          cursor: not-allowed;
          box-shadow: none;
        }

        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(0, 0, 0, 0.2);
          border-top-color: #050508;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </form>
  );
}
