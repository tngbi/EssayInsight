import json
import os
from openai import OpenAI
from dotenv import load_dotenv

from analyst.prompts import SYSTEM_PROMPT, build_user_prompt
from analyst.rag_retriever import retrieve_context
from analyst.feedback_parser import parse_feedback
from analyst.utils import ensure_api_key

load_dotenv()

# ensure API key exists
ensure_api_key()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyse_essay(
    essay: str,
    level: str,
    discipline: str,
    rubric: str,
    use_rag: bool,
    max_refs: int = 7
) -> dict:

    rag_context, sources = "", []

    if use_rag:
        try:
            rag_context, sources = retrieve_context(essay[:2000], k=max_refs)
        except Exception:
            # do not crash if RAG fails
            rag_context, sources = "", []

    user_prompt = build_user_prompt(
        essay,
        level,
        discipline,
        rubric,
        rag_context
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

    except Exception as exc:
        return {
            "overall_score": None,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "error": "failed to contact LLM service",
            "details": str(exc),
            "rag_sources": sources
        }

    raw = response.choices[0].message.content

    try:
        result = parse_feedback(raw)

        # ensure result is dict
        if not isinstance(result, dict):
            raise ValueError("Parsed output is not dict")

    except Exception:
        result = {
            "overall_score": None,
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "error": "invalid LLM response format",
            "raw_output": raw
        }

    result["rag_sources"] = sources

    return result
