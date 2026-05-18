# Prefrontal Frontend

This is the Next.js frontend application for Prefrontal, a RAG-powered evolutionary psychology explainer.

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 19
- **Styling**: Vanilla CSS with CSS Modules (No utility class overhead)
- **Deployment**: Configured for standalone Docker deployment

## Local Development

Ensure the backend is running first (on port 8000), as the frontend relies on the `/api/explain` SSE streaming endpoint.

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Components

The UI is built with a custom glassmorphic clinical aesthetic. Key components:
- `InputPanel` — Handles user queries and state tracking.
- `NeuralLoader` — A custom SVG/CSS animation representing a neural network firing during retrieval.
- `ExplanationCard` — Renders the structured JSON output from the backend into a readable, clinical report.

## Docker Deployment

To build and run the frontend in a containerized environment:

```bash
docker build -t prefrontal-frontend .
docker run -p 3000:3000 prefrontal-frontend
```

*(Note: Use `docker-compose up` from the project root to run both frontend and backend together).*
