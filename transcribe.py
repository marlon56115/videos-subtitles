# transcribe.py
import sys, os
from datetime import timedelta
from faster_whisper import WhisperModel
from tqdm import tqdm

def format_ts(t: float) -> str:
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def main():
    if len(sys.argv) < 2:
        print("Uso: python transcribe.py <video.(mp4|mov|mkv|...)> [modelo]")
        sys.exit(1)

    video_path = os.path.abspath(sys.argv[1])
    model_name = sys.argv[2] if len(sys.argv) > 2 else "large-v3"

    print(f"[Transcribir] Archivo: {video_path} | Modelo: {model_name}")
    # Fuerza float32 para evitar warning de compute type
    model = WhisperModel(model_name, device="auto", compute_type="float32")

    # Obtenemos un iterador de segmentos y metadata con duración
    segments, info = model.transcribe(
        video_path,
        beam_size=5,
        vad_filter=True,
        language="en",
    )
    total_sec = float(getattr(info, "duration", 0.0) or 0.0)

    base = os.path.splitext(os.path.basename(video_path))[0]
    srt_path = f"{base}.srt"

    idx = 1
    progressed = 0.0
    bar_desc = "Transcribiendo"
    # Barra: si no conocemos duración, muestra en modo indeterminado con total=None
    pbar_total = int(total_sec) if total_sec > 0 else None
    pbar = tqdm(total=pbar_total, unit="s", dynamic_ncols=True, leave=True, desc=bar_desc)

    with open(srt_path, "w", encoding="utf-8") as f:
        for seg in segments:
            # actualiza progreso por la marca de fin del segmento
            if total_sec > 0:
                delta = max(0.0, seg.end - progressed)
                pbar.update(int(delta))
                progressed = max(progressed, seg.end)
            # escribe SRT
            start = format_ts(seg.start); end = format_ts(seg.end)
            text = (seg.text or "").strip()
            if not text:
                continue
            f.write(f"{idx}\n{start} --> {end}\n{text}\n\n")
            idx += 1

    # si no teníamos duración, al menos cierra al 100%
    if total_sec == 0:
        pbar.close()
    else:
        # ajusta por si quedó algún remanente
        if pbar.n < pbar.total:
            pbar.update(pbar.total - pbar.n)
        pbar.close()

    print(f"[OK] SRT generado: {srt_path}")

if __name__ == "__main__":
    main()
