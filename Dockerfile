FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "-m", "src"]
