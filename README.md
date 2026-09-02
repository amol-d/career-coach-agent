# 🎯 Career Coach Agent — Day 08 of 14 AI Agents in 14 Days

Compare a resume against a job description and get a gap analysis with concrete improvements.

Day **08** of a "14 AI Agents in 14 Days" build.

- **Live demo:** _(added once deployed — see the portfolio card)_
- **Stack:** Python · OpenAI (`gpt-5.6`) · Gradio · FastAPI · Cloud Run
- **Security:** see [SECURITY.md](SECURITY.md)

## Run locally

```bash
git clone https://github.com/amol-d/career-coach-agent.git
cd career-coach-agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then edit .env and set OPENAI_API_KEY
python app.py               # serves on http://localhost:8080
```

The OpenAI key is read from the environment by the SDK — never committed, logged,
or sent to the browser.

## Deploy to Google Cloud Run

```bash
gcloud run deploy career-coach-agent \
  --source . --region asia-south1 --allow-unauthenticated \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --set-env-vars "^@^ALLOWED_EMBED_ORIGINS=https://amoldesai.in,https://www.amoldesai.in,https://amoldesai-portfolio.web.app"
```

## License

[MIT](LICENSE)
