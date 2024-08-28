FROM python:slim
WORKDIR /app

COPY . /app

RUN pip install requests
RUN pip install beautifulsoup4

CMD ["sh", "-c", "python3 /app/main.py"]