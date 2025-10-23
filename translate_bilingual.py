# translate_bilingual.py
import sys, os, srt
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from tqdm import tqdm

MODEL_NAME = "Helsinki-NLP/opus-mt-en-es"

def batch_iter(seq, size):
    for i in range(0, len(seq), size):
        yield i, seq[i:i+size]

def main():
    if len(sys.argv) < 2:
        print("Uso: python translate_bilingual.py <archivo.srt> [salida_bilingue.srt]")
        sys.exit(1)

    srt_in = sys.argv[1]
    base = os.path.splitext(os.path.basename(srt_in))[0]
    srt_out = sys.argv[2] if len(sys.argv) > 2 else f"{base}_bilingual.srt"

    print(f"[Traducir] Cargando modelo {MODEL_NAME} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    # GPU/Metal no aplica para HF en MPS fácilmente; usa CPU con threads
    if torch.get_num_threads() < 4:
        torch.set_num_threads(4)

    print(f"[Leer] {srt_in}")
    with open(srt_in, "r", encoding="utf-8") as f:
        subs = list(srt.parse(f.read()))

    english_texts = [sub.content for sub in subs]
    total = len(english_texts)
    print(f"[Traducir] {total} líneas ...")

    spanish_texts = [None] * total
    batch_size = 40  # ajusta según RAM

    pbar = tqdm(total=total, desc="Traduciendo", unit="línea", dynamic_ncols=True, leave=True)
    for start_idx, batch in batch_iter(english_texts, batch_size):
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512)
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        spanish_texts[start_idx:start_idx+len(decoded)] = decoded
        pbar.update(len(decoded))
    pbar.close()

    # compón SRT bilingüe: EN + ES
    bilingual_subs = []
    for i, sub in enumerate(subs):
        es_line = (spanish_texts[i] or "").strip()
        content = f"{sub.content}\n{es_line}".strip()
        bilingual_subs.append(srt.Subtitle(index=sub.index, start=sub.start, end=sub.end, content=content))

    with open(srt_out, "w", encoding="utf-8") as f:
        f.write(srt.compose(bilingual_subs))

    print(f"[OK] SRT bilingüe: {srt_out}")

if __name__ == "__main__":
    main()
