# 🎬 videos-subtitles

Herramienta local para **transcribir (EN)**, **traducir (EN→ES)** y **quemar subtítulos** en tus videos, optimizada para macOS con Apple Silicon (M-series).  
Usa **faster-whisper** para transcripción y **MarianMT (transformers)** para traducción, con barras de progreso.

---

## ⚙️ 0) Requisitos (una sola vez)

```bash
brew install pyenv pyenv-virtualenv ffmpeg git
```

Asegura que `pyenv` y `pyenv-virtualenv` se carguen en tu shell (zsh por defecto):

```bash
# En ~/.zshrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"

eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Luego ejecuta:
```bash
source ~/.zshrc
```

---

## 🚀 1) Setup del proyecto

### 1.1 Clonar el repositorio

```bash
git clone https://github.com/<tuusuario>/videos-subtitles.git
cd videos-subtitles
```

### 1.2 Crear entorno Python

```bash
pyenv install 3.12.6
pyenv virtualenv 3.12.6 whisper-env
pyenv local whisper-env
python -V
```

### 1.3 Instalar dependencias

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

O si prefieres manualmente:

```bash
pip install faster-whisper torch torchvision torchaudio
pip install transformers sentencepiece
pip install srt tqdm sacremoses
```

---

## 🧩 2) Archivos del proyecto

Estos archivos deben estar en la raíz del repo:

```
videos-subtitles/
├── subtify.sh
├── transcribe.py
├── translate_bilingual.py
└── requirements.txt
```

Y da permisos al script principal:

```bash
chmod +x subtify.sh
```

---

## ▶️ 3) Uso básico

### 3.1 Transcribir, traducir y quemar subtítulos

```bash
./subtify.sh "/Users/marlon/Downloads/Timeline.mov"
```

Esto generará una carpeta junto al video con los archivos:

```
Timeline/
├── Timeline.srt
├── Timeline_bilingual.srt
├── Timeline_bilingual.ass
└── Timeline_bilingual.mp4
```

### 3.2 Elegir modelo

```bash
./subtify.sh "/Users/marlon/Downloads/Timeline.mov" medium
```

Modelos disponibles: `base`, `small`, `medium`, `large-v3`.

---

## ⚡ 4) Rendimiento y ajustes

- `large-v3` → máxima precisión, más lento.  
- `medium` → excelente balance velocidad/precisión.  
- `small` / `base` → pruebas rápidas.

### Ajustes recomendados en `transcribe.py`

```python
segments, info = model.transcribe(
    video_path,
    beam_size=3,      # 1–3 = más rápido, menos preciso
    vad_filter=False, # si el audio es limpio
    language="en",
)
```

### Tamaño de lote de traducción (`translate_bilingual.py`)

```python
batch_size = 40  # 32–48 es ideal para 48 GB de RAM
```

### Tip: extraer audio antes (para más velocidad)

```bash
ffmpeg -i video.mov -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
./subtify.sh "./audio.wav"
```

---

## 🧰 5) Solución de problemas

| Problema | Solución |
|-----------|-----------|
| ⚠️ *float16 → float32 warning* | Normal en Mac. Apple usa float32. |
| ❌ `ModuleNotFoundError: srt` | Instálalo en el venv correcto. |
| ⚠️ `pyenv activate whisper-env` falla | Revisa configuración en `~/.zshrc`. |
| 🐢 Transcribe muy lento | Usa modelo `medium`, `beam_size=3`, `vad_filter=False`, o WAV. |

---

## 📖 6) Ejemplos rápidos

```bash
./subtify.sh "/Users/marlon/Downloads/Timeline.mov"
./subtify.sh "/Users/marlon/Downloads/Timeline.mov" medium
ffmpeg -i "/Users/marlon/Downloads/Timeline.mov" -vn -acodec pcm_s16le -ar 16000 -ac 1 "/Users/marlon/Downloads/Timeline.wav"
./subtify.sh "/Users/marlon/Downloads/Timeline.wav" medium
```

---

## 🧡 Créditos

Proyecto mantenido por **Marlon Guerra (2025)**  
Uso personal y educativo — compatible con macOS (M-series) y Linux.

