# videos-subtitles — README

Herramientas locales para **transcribir (EN)**, **traducir (EN→ES)** y **quemar subtítulos** en tus videos, optimizado para macOS con Apple Silicon (M-series).  
Usa **faster-whisper** para transcripción y **MarianMT (transformers)** para traducción. Incluye barras de progreso.

---

## 0) Requisitos (una sola vez)

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

## 1) Setup del proyecto

```bash
mkdir -p ~/videos-subtitles && cd ~/videos-subtitles
pyenv install 3.12.6
pyenv virtualenv 3.12.6 whisper-env
pyenv local whisper-env
python -V
```

### 1.1 Instalar dependencias

```bash
pip install --upgrade pip setuptools wheel
pip install faster-whisper torch torchvision torchaudio
pip install transformers sentencepiece
pip install srt tqdm sacremoses
```

---

## 2) Archivos requeridos

Coloca en la carpeta `~/videos-subtitles/` los siguientes archivos:

- `subtify.sh`
- `transcribe.py`
- `translate_bilingual.py`

Y da permisos:
```bash
chmod +x subtify.sh
```

---

## 3) Uso

### 3.1 Ejemplo básico
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

---

## 4) Ajustes y rendimiento

- `large-v3` → mayor precisión, más lento.  
- `medium` → más rápido, buena precisión.  
- `small` / `base` → pruebas rápidas.

### Ajustes recomendados en `transcribe.py`
```python
segments, info = model.transcribe(
    video_path,
    beam_size=3,
    vad_filter=False,
    language="en",
)
```

### Tamaño de lote de traducción
En `translate_bilingual.py`:
```python
batch_size = 40
```

### Tip: extraer audio antes
```bash
ffmpeg -i video.mov -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
./subtify.sh "./audio.wav"
```

---

## 5) Solución de problemas

- **Warning float16 → float32:** No es error, Apple usa float32.
- **`ModuleNotFoundError: srt`:** Instálalo en el entorno correcto.
- **`pyenv activate whisper-env` falla:** revisa configuración de `~/.zshrc`.

---

## 6) Estructura del proyecto

```
videos-subtitles/
├── subtify.sh
├── transcribe.py
├── translate_bilingual.py
└── requirements.txt
```

---

## 7) Ejemplos finales

```bash
./subtify.sh "/Users/marlon/Downloads/Timeline.mov"
./subtify.sh "/Users/marlon/Downloads/Timeline.mov" medium
ffmpeg -i "/Users/marlon/Downloads/Timeline.mov" -vn -acodec pcm_s16le -ar 16000 -ac 1 "/Users/marlon/Downloads/Timeline.wav"
./subtify.sh "/Users/marlon/Downloads/Timeline.wav" medium
```

---

© 2025 Marlon Guerra — uso personal y educativo.
