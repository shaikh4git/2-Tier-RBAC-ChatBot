FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/appuser/.cache/huggingface

WORKDIR /app

# Runtime library required by NumPy / SciPy / scikit-learn
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first.
# This avoids pulling CUDA-enabled PyTorch and NVIDIA libraries.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu \
        "torch==2.15.0" && \
    pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home --uid 10001 appuser && \
    mkdir -p /home/appuser/.cache/huggingface && \
    chown -R appuser:appuser /app /home/appuser

USER 10001

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
