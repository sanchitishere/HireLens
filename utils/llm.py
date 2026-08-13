import requests
import streamlit as st

OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_LLAMA_MODEL = "llama3.2"

def call_llama(messages, model=None, temperature=0.3, top_p=0.9, timeout=120):
    model = model or st.session_state.get("llama_model", DEFAULT_LLAMA_MODEL)
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": model, "messages": messages, "stream": False, "options": {"temperature": temperature, "top_p": top_p}},
            timeout=timeout,
        )
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "").strip()
        if not content:
            return None, "Ollama returned an empty response."
        return content, None
    except requests.exceptions.ConnectionError:
        return None, f"Couldn't reach Ollama at {OLLAMA_HOST}. Make sure `ollama serve` is running."
    except Exception as e:
        return None, f"Llama call failed: {e}"
