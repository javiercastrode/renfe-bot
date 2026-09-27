FROM python:3.12.7-slim

WORKDIR /app

LABEL org.opencontainers.image.source=https://github.com/javiercastrode/renfe-bot

# Copiamos e instalamos dependencias
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

# Copiamos el código fuente
COPY src /app/src
COPY assets /app/assets
ENV PYTHONPATH="/app/src"

# Pre-compilamos la caché y aplicamos los permisos estrictos (555)
RUN python -m compileall /app/src && \
    chmod -R 555 /app

CMD ["python", "-u", "src/bot.py"]
