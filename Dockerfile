FROM python:3.11-slim

WORKDIR /app

# Install basic OS tools - Removed software-properties-common to fix build error
# This version removes the problematic package and is much faster!
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run defaults port to 8080
EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]