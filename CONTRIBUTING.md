# Contributing to Prefrontal

Thank you for your interest in contributing! Prefrontal is a RAG-powered evolutionary psychology explainer and welcomes contributions of all kinds.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Follow the [Installation Guide](README.md#installation) to get the project running.
3. Create a new branch for your changes: `git checkout -b feat/your-feature-name`

## Types of Contributions Welcome

- **New seed entries** — Add new behaviors to `knowledge_base/curated/seed.json`. Each entry must follow the existing schema (see [Seed Schema](#seed-schema) below).
- **Bug fixes** — Open an issue first describing the bug, then submit a PR with the fix.
- **Performance improvements** — RAG retrieval, embedding, or UI rendering improvements.
- **UI/UX improvements** — Component-level changes to the Next.js frontend.
- **Documentation** — Improvements to the README, inline comments, or docstrings.

## Seed Schema

Every entry in `seed.json` must contain the following fields:

```json
{
  "id": "snake_case_unique_id",
  "behavior": "A clear description of the behavior or fear",
  "modern_trigger": "What triggers this in the modern world",
  "ancestral_mechanism": "The survival reason this existed for our ancestors",
  "brain_region": "Which brain regions are involved",
  "brain_chemistry": "Which neurochemicals are involved and how",
  "the_insight": "The reframe — help the person understand this reaction",
  "tags": ["tag1", "tag2"],
  "sources": ["Source Name — Author"]
}
```

Run `test.bat` after adding entries to validate the schema automatically.

## Pull Request Process

1. Ensure your changes pass the test suite: `test.bat` (or `python scripts/test_all.py` directly).
2. Update `README.md` if you're changing any user-facing behavior.
3. Keep PRs focused — one feature or fix per PR.
4. Write a clear PR title and description.

## Code Style

- **Python**: Follow PEP 8. Use type hints where possible.
- **TypeScript/React**: Follow the existing component patterns. No utility class frameworks (Tailwind, etc.).
- **No secrets**: Never commit `.env` files or API keys.

## Questions?

Open a [GitHub Issue](https://github.com/Ares19v/Prefrontal/issues) — happy to help.
