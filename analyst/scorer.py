import json, os
from openai import OpenAI
from dotenv import load_dotenv
from analyst.prompts import SYSTEM_PROMPT, build_user_prompt
from analyst.rag_retriever import retrieve_context

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyse_essay(essay: str, level: str, discipline: str,
                  rubric: str, use_rag: bool, max_refs: int = 7) -> dict:

    rag_context, sources = "", []
    if use_rag:
        rag_context, sources = retrieve_context(essay[:2000], k=max_refs)

    user_prompt = build_user_prompt(essay, level, discipline, rubric, rag_context)

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
    )

    result = json.loads(response.choices[0].message.content)
    result["rag_sources"] = sources
    return result
