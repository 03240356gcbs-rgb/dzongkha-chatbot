import torch
import ollama

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# -------------------------------
# CONFIGURATION
# -------------------------------
MODEL_NAME = "kinleyrabgay/nllb-200-600M-dzo-eng-300k"

# Limit CPU thread usage to keep laptop performance smooth
torch.set_num_threads(2)

app = FastAPI(title="English-to-Dzongkha AI Chatbot")

# Serve frontend static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Lazy loading variables for translation model
tokenizer = None
translation_model = None


# -------------------------------
# REQUEST AND RESPONSE SCHEMAS
# -------------------------------
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)

class ChatResponse(BaseModel):
    response: str
    english_response: str


# -------------------------------
# LOAD TRANSLATION MODEL
# -------------------------------
def load_translation_model():
    global tokenizer, translation_model
    if tokenizer is None or translation_model is None:
        print("Loading Dzongkha NLLB translation model (this may take a moment on first run)...")
        
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            src_lang="eng_Latn",
            tgt_lang="dzo_Tibt"
        )
        
        translation_model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME
        )
        
        translation_model.eval()
        print("Dzongkha Translation model loaded successfully!")


# -------------------------------
# TRANSLATION FUNCTION
# -------------------------------
def translate_to_dzongkha(text: str) -> str:
    load_translation_model()

    # Truncate text to avoid memory spikes on long answers
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    with torch.inference_mode():
        translated_tokens = translation_model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids("dzo_Tibt"),
            max_length=256,
            num_beams=2
        )

    result = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )

    return result[0]


# -------------------------------
# ROUTING & ENDPOINTS
# -------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a message."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Answer questions accurately and clearly in English. "
                "Use the previous conversation for context. "
                "Keep answers reasonably concise so they can be translated well."
            )
        }
    ]

    # Include recent conversation context (up to 10 turns)
    for item in request.history[-10:]:
        role = item.get("role")
        content = item.get("content")
        if role in ["user", "assistant"] and isinstance(content, str):
            if content.strip():
                messages.append({
                    "role": role,
                    "content": content.strip()
                })

    messages.append({
        "role": "user",
        "content": question
    })

    try:
        # 1. Generate factual answer using local Ollama model (gemma2)
        print(f"Generating answer via Ollama for: '{question}'...")
        ai_result = ollama.chat(
            model="gemma2",
            messages=messages,
            keep_alive=0
        )
        english_answer = ai_result["message"]["content"].strip()

        # 2. Translate English answer into authentic Dzongkha using NLLB
        print("Translating answer into Dzongkha script via NLLB...")
        dzongkha_answer = translate_to_dzongkha(english_answer)

        print("Translation completed successfully!")

        return ChatResponse(
            response=dzongkha_answer,
            english_response=english_answer
        )

    except Exception as error:
        print("Chatbot error details:", str(error))
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(error)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)