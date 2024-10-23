FROM tiangolo/uwsgi-nginx-flask:python3.11
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./app /app
ENV STATIC_PATH /app/blockurl/static
ENV DATABASE_PATH=/app/database/blockurl.db