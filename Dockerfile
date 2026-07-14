FROM python:3.12-slim

WORKDIR /app

COPY main.py console_demo.py ./
COPY data/ ./data/

CMD ["python", "console_demo.py", "data/sample.json"]