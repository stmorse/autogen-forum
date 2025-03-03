FROM python:3.10-slim

WORKDIR /app

# Install dependencies from a non-overridden directory
COPY requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir -r /build/requirements.txt

# for interactive
CMD ["python", "bootstrap.py"]