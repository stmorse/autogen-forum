FROM python:3.11-slim

# set working directory
WORKDIR /app

# Install dependencies from a non-overridden directory
COPY requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir -r /build/requirements.txt

# for interactive
CMD ["python", "bootstrap.py"]