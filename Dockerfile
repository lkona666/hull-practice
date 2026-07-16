FROM python:3.12-slim

WORKDIR /app

COPY algorithms.py geometry.py main.py console_demo.py ./
COPY data/ ./data/
COPY tests/ ./tests/

RUN pip install --no-cache-dir pytest

CMD ["python", "console_demo.py", "data/sample.json"]
