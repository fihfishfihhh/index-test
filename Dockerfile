# Sample Dockerfile for deploying Flask app
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app_prod.py
EXPOSE 5000
CMD ["gunicorn","-b","0.0.0.0:5000","app_prod:app","--workers","2","--threads","4"]
