FROM python:3.11-slim

RUN pip install --no-cache-dir uwsgi

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

ENV DATABASE_PATH=/app/database/blockurl.db
ENV BLOCKURL_HOST=0.0.0.0
ENV BLOCKURL_PORT=8000

EXPOSE 8000

CMD ["uwsgi", "--ini", "uwsgi.ini"]