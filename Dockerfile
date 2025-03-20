FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Use entrypoint.sh instead of direct command
ENTRYPOINT ["/app/entrypoint.sh"]
