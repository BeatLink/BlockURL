FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
ENV DATABASE_PATH=/app/database/blockurl.db
ENV BLOCKURL_HOST=0.0.0.0
ENV BLOCKURL_PORT=8000
EXPOSE 8000
CMD ["blockurl-server"]