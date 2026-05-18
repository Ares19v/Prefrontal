# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | ✅ Yes             |

## Reporting a Vulnerability

If you discover a security vulnerability in Prefrontal, **please do not open a public GitHub issue**.

Instead, report it privately by emailing the repository owner via the GitHub profile at [@Ares19v](https://github.com/Ares19v).

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix (optional)

You can expect an acknowledgement within 48 hours and a resolution or mitigation plan within 7 days.

## Security Notes for Self-Hosting

- **Never commit your `.env` file.** Your `GROQ_API_KEY` and `PINECONE_API_KEY` must be kept secret at all times.
- **Use environment variables** when deploying via Docker. See `backend/.env.example` for the required variables.
- The `backend/.env` file is explicitly excluded in `.gitignore` — do not remove this exclusion.
- The CORS policy in `main.py` restricts origins to `localhost` by default. Update this for production deployments.
