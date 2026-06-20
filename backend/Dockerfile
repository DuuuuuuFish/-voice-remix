FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/.cache/huggingface
ENV MODELSCOPE_CACHE=/app/.cache/modelscope

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    git-lfs \
    unzip \
    wget \
    sox \
    libsox-dev \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/* \
    && git lfs install

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git /opt/CosyVoice
RUN pip install --no-cache-dir -e /opt/CosyVoice

COPY . .

RUN mkdir -p /app/storage /app/pretrained_models /app/.cache/huggingface /app/.cache/modelscope

CMD ["bash", "-lc", "python scripts/download_models.py --source ${MODEL_SOURCE:-modelscope} --model-id ${COSYVOICE_MODEL_ID:-iic/CosyVoice2-0.5B} --hf-model-id ${HF_COSYVOICE_MODEL_ID:-FunAudioLLM/CosyVoice2-0.5B} --target-dir ${COSYVOICE_MODEL_DIR:-/app/pretrained_models/CosyVoice2-0.5B} && uvicorn main:app --host 0.0.0.0 --port 8000"]
