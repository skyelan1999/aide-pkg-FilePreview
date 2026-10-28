FROM python:3.12-slim-bookworm
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libreoffice-writer libreoffice-calc libreoffice-impress chromium fonts-noto-cjk fonts-liberation && rm -rf /var/lib/apt/lists/*
COPY engine/requirements.txt /opt/file-preview/requirements.txt
RUN pip install --no-cache-dir -r /opt/file-preview/requirements.txt
RUN useradd --uid 10001 --create-home renderer
COPY engine/server.py engine/gateway.py /opt/file-preview/
USER renderer
ENV HOME=/tmp/home PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8765
ENTRYPOINT ["python3","/opt/file-preview/server.py"]
