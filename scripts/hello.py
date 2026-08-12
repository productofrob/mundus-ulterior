"""Part 1 milestone: prove the plumbing.

Sends "hello" through the LiteLLM gateway to one chat model and one embedding
model and prints both responses. If this works, the env skeleton is sound.

Run with the proxy up (litellm --config gateway/config.yaml --port 4000) and the
venv active:  python scripts/hello.py
"""
import os
from openai import OpenAI  # LiteLLM proxy is OpenAI-compatible

client = OpenAI(
    base_url="http://localhost:4000",
    api_key=os.environ.get("LITELLM_MASTER_KEY", "sk-local-dev"),
)

# 1) chat model through the gateway
chat = client.chat.completions.create(
    model="chat-default",
    messages=[{"role": "user", "content": "hello"}],
)
print("CHAT:", chat.choices[0].message.content)

# 2) embedding model through the gateway
emb = client.embeddings.create(model="embed-default", input="hello")
vec = emb.data[0].embedding
print("EMBED: dims =", len(vec), "| first 3 =", vec[:3])
