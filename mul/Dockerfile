FROM python:3.12-slim
WORKDIR /app

COPY . /app

RUN pip install requests

CMD ["sh", "-c", "python3 /app/mul.py"]