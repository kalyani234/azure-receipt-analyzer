# Final reliable Dockerfile - python:3.11 (non-slim) + explicit deps for OpenCV/YOLO
FROM python:3.11

# Install minimal runtime deps for OpenCV (fixes libxcb, libGL, etc. on Debian trixie/bookworm)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Run both services (backend & frontend)
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port 8000 & streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]