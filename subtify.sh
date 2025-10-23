#!/usr/bin/env bash
set -Eeuo pipefail

# =========================
# Config: ruta FIJA del venv
# =========================
PYTHON_BIN="$HOME/.pyenv/versions/whisper-env/bin/python"
DEFAULT_MODEL="large-v3"

die() { echo "❌ $*" >&2; exit 1; }
usage() {
  cat <<USAGE
Uso:
  $(basename "$0") "/ruta/al/video.ext" [modelo]

Ejemplos:
  $(basename "$0") "/Users/marlon/Downloads/Timeline.mov"
  $(basename "$0") "/Users/marlon/Downloads/Timeline.mov" medium
USAGE
}

# =========================
# Validaciones iniciales
# =========================
if [ $# -lt 1 ]; then usage; exit 1; fi
VIDEO="$1"
MODEL="${2:-$DEFAULT_MODEL}"
[ -f "$VIDEO" ] || die "No existe el archivo de video: $VIDEO"

[ -x "$PYTHON_BIN" ] || die "No se encontró el intérprete del venv en: $PYTHON_BIN
- Asegúrate de haber creado el entorno:
    pyenv virtualenv 3.12.x whisper-env
- O ajusta la variable PYTHON_BIN al intérprete correcto."

if ! command -v ffmpeg >/dev/null 2>&1; then
  die "ffmpeg no está instalado. Instálalo con: brew install ffmpeg"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VIDEO_DIR="$(cd "$(dirname "$VIDEO")" && pwd)"
VIDEO_BASE="$(basename "$VIDEO")"
NAME="${VIDEO_BASE%.*}"
OUT_DIR="${VIDEO_DIR}/${NAME}"
mkdir -p "$OUT_DIR"

echo "[debug] PYTHON_BIN: $PYTHON_BIN"
"$PYTHON_BIN" -V || die "No se pudo ejecutar $PYTHON_BIN"

echo "[i] Verificando dependencias Python en el venv…"
"$PYTHON_BIN" - <<'PY' || { echo "❌ Dependencias Python faltantes en el venv."; exit 1; }
missing = []
for mod in ["srt", "faster_whisper", "transformers", "sentencepiece"]:
    try:
        __import__(mod)
    except Exception:
        missing.append(mod)
if missing:
    raise SystemExit(f"Faltan módulos en el entorno: {missing}\n"
                     f"Instala con: pip install {' '.join(missing)}")
print("Dependencias OK")
PY

echo "[i] Video: $VIDEO"
echo "[i] Carpeta de salida: $OUT_DIR"
echo "[i] Modelo de transcripción: $MODEL"

# =========================
# 1) Transcripción → SRT (EN)
# =========================
echo "[1/3] Transcribiendo → ${OUT_DIR}/${NAME}.srt"
pushd "$OUT_DIR" >/dev/null
"$PYTHON_BIN" "$SCRIPT_DIR/transcribe.py" "$VIDEO" "$MODEL"

# =========================
# 2) Traducción → SRT bilingüe
# =========================
echo "[2/3] Traduciendo y creando SRT bilingüe → ${OUT_DIR}/${NAME}_bilingual.srt"
"$PYTHON_BIN" "$SCRIPT_DIR/translate_bilingual.py" "${NAME}.srt"

# =========================
# 3) Quemar subtítulos → MP4
# =========================
echo "[3/3] Quemando subtítulos → ${OUT_DIR}/${NAME}_bilingual.mp4"
ffmpeg -y -hide_banner -loglevel error -i "${NAME}_bilingual.srt" "${NAME}_bilingual.ass"
ffmpeg -y -hide_banner -loglevel error -i "$VIDEO" -vf "ass=${NAME}_bilingual.ass" -c:a copy "${NAME}_bilingual.mp4"

popd >/dev/null

echo
echo "✅ Listo. Archivos en: ${OUT_DIR}"
echo " - ${NAME}.srt                (Inglés)"
echo " - ${NAME}_bilingual.srt      (Inglés + Español)"
echo " - ${NAME}_bilingual.ass      (para quemar subtítulos)"
echo " - ${NAME}_bilingual.mp4      (video final con subtítulos)"
