"""Gradio demo UI for the Career Coach Agent, mounted on FastAPI."""

from __future__ import annotations

import gradio as gr

from career_coach_agent.agent import CareerCoachAgent
from career_coach_agent.config import CONFIG
from career_coach_agent.security import RateLimitError, ValidationError, sanitize_text, validate_upload
from career_coach_agent.web import LIMITER, caller_id, make_app, run

_agent: CareerCoachAgent | None = None
ALLOWED = {".pdf", ".txt", ".md", ".markdown"}


def _get_agent() -> CareerCoachAgent:
    global _agent
    if _agent is None:
        _agent = CareerCoachAgent()
    return _agent


def handle(resume_file, resume_text, jd_text, request: gr.Request):
    # Resume from an upload, or pasted text.
    resume = ""
    if resume_file is not None:
        path = resume_file if isinstance(resume_file, str) else getattr(resume_file, "name", None)
        try:
            validate_upload(path, ALLOWED)
            resume = _get_agent().extract_resume(path)
        except ValidationError as exc:
            yield f"⚠️ {exc}"
            return
        except Exception:  # noqa: BLE001
            yield "⚠️ Could not read the resume file."
            return
    elif resume_text and resume_text.strip():
        try:
            resume = sanitize_text(resume_text, field="resume text", min_chars=30)
        except ValidationError as exc:
            yield f"⚠️ {exc}"
            return
    else:
        yield "⚠️ Please upload or paste your resume."
        return

    try:
        jd = sanitize_text(jd_text, field="a job description", min_chars=30)
    except ValidationError as exc:
        yield f"⚠️ {exc}"
        return
    try:
        LIMITER.check(caller_id(request))
    except RateLimitError as exc:
        yield f"⏳ {exc}"
        return
    if not CONFIG.api_key_present:
        yield "⚠️ The demo is not configured (missing API key). See the GitHub repo to run it locally."
        return
    yield "🎯 Comparing your resume to the role…"
    try:
        yield _get_agent().analyze(resume, jd)
    except Exception:  # noqa: BLE001
        yield "⚠️ Something went wrong. Please try again in a moment."


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Career Coach Agent — Day 08", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "## 🎯 Career Coach Agent\n"
            "Compare your resume to a job description and get a **gap analysis** with "
            "concrete improvements.\n\n"
            "*Day 08 of 14 AI Agents in 14 Days — document analysis + semantic matching.*"
        )
        with gr.Row():
            with gr.Column():
                resume_file = gr.File(label="Resume (PDF / TXT / MD)", file_types=[".pdf", ".txt", ".md", ".markdown"], file_count="single")
                resume_text = gr.Textbox(label="…or paste your resume", lines=6)
            jd_text = gr.Textbox(label="Job description", lines=12, placeholder="Paste the target job description here…")
        run_btn = gr.Button("Analyze fit", variant="primary")
        out = gr.Markdown()
        run_btn.click(handle, inputs=[resume_file, resume_text, jd_text], outputs=out)
    demo.queue(default_concurrency_limit=2, max_size=20)
    return demo


app = make_app(build_demo(), title="Career Coach Agent")

if __name__ == "__main__":
    run(app)
