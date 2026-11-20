FROM python:3.12-slim
WORKDIR /app
COPY packages packages
COPY services services
COPY apps/api apps/api
ENV PYTHONUNBUFFERED=1 HIRT_DATA_DIR=/var/data
CMD ["python", "apps/api/server.py"]
