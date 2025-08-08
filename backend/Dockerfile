FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       netcat-openbsd \
       python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY django_requirements.txt .
RUN pip install --no-cache-dir -r django_requirements.txt

COPY . .

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]