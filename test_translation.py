
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "kinleyrabgay/nllb-200-600M-dzo-eng-300k"

torch.set_num_threads(2)

print("Loading Dzongkha translation model...")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    src_lang="eng_Latn",
    tgt_lang="dzo_Tibt"
)

model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model.eval()

def translate_to_dzongkha(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    with torch.no_grad():
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids("dzo_Tibt"),
            max_length=256,
            num_beams=2
        )

    return tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )[0]


english_text = "What is artificial intelligence?"

print("\nEnglish:", english_text)

print("\nTranslating...")
result = translate_to_dzongkha(english_text)

print("\nDzongkha:", result)
