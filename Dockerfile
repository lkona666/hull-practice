<<<<<<< HEAD
FROM python:3.12-slim

WORKDIR /app

COPY main.py console_demo.py ./
COPY data/ ./data/

=======
FROM python:3.12-slim

WORKDIR /app

COPY main.py console_demo.py ./
COPY data/ ./data/

>>>>>>> 5fd4d7eea2ac6baab0f6de9122979f5c776c18e3
CMD ["python", "console_demo.py", "data/sample.json"]