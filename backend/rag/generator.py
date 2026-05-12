# backend/rag/generator.py
from groq import Groq
from backend.config import settings

SYSTEM_PROMPT = """Eres Molly, la asistente virtual amigable del Colegio Gemelli (Colombia).
Respondes ÚNICAMENTE con información de los documentos oficiales del colegio.
Si no tienes información suficiente, dilo con amabilidad y sugiere contactar secretaría (secretaria@colgemelli.edu.co o llamar al número en la web).
Responde siempre en español, de forma clara y concisa.
No inventes información. Si la pregunta no tiene que ver con el colegio, redirige amablemente."""

def build_prompt(question: str, chunks: list[dict], history: list[dict]) -> str:
    context = "\n\n".join([f"[Fuente: {c['source']}]\n{c['text']}" for c in chunks])
    return f"Contexto del colegio:\n{context}\n\nPregunta del padre: {question}"

def generate_answer(question: str, chunks: list[dict], history: list[dict]) -> str:
    client = Groq(api_key=settings.groq_api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": build_prompt(question, chunks, history)})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.3,
    )
    return response.choices[0].message.content

def retrieve_and_generate(question: str, history: list[dict]) -> dict:
    from backend.rag.retriever import retrieve_chunks
    chunks = retrieve_chunks(question)
    answer = generate_answer(question, chunks, history)
    sources = list({c["source"] for c in chunks if c["source"]})
    return {"answer": answer, "sources": sources}
