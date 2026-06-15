FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências de runtime do WeasyPrint.
# psycopg2-binary já embute o libpq, então NÃO precisamos de libpq-dev nem gcc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Coleta arquivos estáticos em build time.
# Usa chave dummy só pra carregar o settings — não é usada em runtime.
RUN DJANGO_SECRET_KEY=build-time-collect \
    DJANGO_DEBUG=False \
    python manage.py collectstatic --noinput

# Documental apenas; o Render roteia via $PORT de qualquer forma.
EXPOSE 8000

# Shell form para que $PORT seja expandido.
# ${PORT:-8000} => usa a porta do Render em produção e 8000 no local.
# migrate fica no Pre-Deploy Command do Render, NÃO aqui.
CMD gunicorn ecodash.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -