FROM python:3.9-slim

# set work dir
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# start training
CMD ["python", "main_cloud.py"]