# Receipt Analyzer

**Azure Receipt Text Detection & Extraction System**  
A full-stack web application that automatically detects key text regions on grocery receipt images (store name, date/time, items, total) and extracts structured information using Azure AI, custom annotations, and YOLOv8 fallback.

### Demo
[Recording](https://github.com/kalyani234/azure-receipt-analyzer/issues/1#issue-3945287063)

## Features

- Upload receipt photo (jpg/jpeg/png)
- Side-by-side view: Original vs Detected Regions (with bounding boxes)
- Extracted information: Store, Date/Time, Total, Items list with confidence
- Confidence filter slider
- Download annotated image (PNG)
- Backend powered by **FastAPI** + **Azure AI Document Intelligence** (primary OCR)
- Fallback to XML annotations from a 20-image dataset
- Fallback to custom-trained **YOLOv8** model (PyTorch) for unseen receipts
- Dockerized (separate backend & frontend containers)

## Architectural Diagram
<img width="1536" height="1024" alt="imag2" src="https://github.com/user-attachments/assets/c8c05658-cd4e-4726-980b-aa920358f088" />


## 🚀 Technologies Used

| Category | Technology / Tool | Purpose / Role |
|----------|------------------|----------------|
| **Frontend (UI)** | Streamlit | Interactive web interface for image upload, visualization, and result download |
| **Backend (API)** | FastAPI | High-performance REST API with `/analyze` endpoint |
| **Web Server** | Uvicorn | ASGI server to run FastAPI |
| **Containerization** | Docker | Package backend & frontend into isolated containers |
| **Object Detection** | YOLOv8 (Ultralytics) | Region detection fallback with real confidence scores |
| **OCR & Structured Extraction** | Azure AI Document Intelligence | Primary real-time OCR for merchant, date/time, total, subtotal, tax, and item table extraction |
| **Image Processing** | Pillow (PIL) | Draw bounding boxes, labels, and text overlays on images |
| **XML Parsing** | xml.etree.ElementTree | Parse `annotations.xml` for bounding boxes and text |
| **HTTP Requests** | requests | Streamlit frontend communicates with FastAPI backend |
| **Utilities** | tqdm | Progress tracking (optional, for model training or batch processing) |

---
### Prerequisites

* Python 3.11+
* Docker Desktop (recommended)
* Azure AI Document Intelligence resource (free F0 tier) – Endpoint & Key

### Local Run (Docker)

1. Build the image

```docker build -t receipt-analyzer:latest . ```

2. Run backend (FastAPI)

```docker run -d -p 8000:8000 --name receipt-backend receipt-analyzer:latest uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload ```

3. Run frontend (Streamlit) in another terminal

```docker run -d -p 8501:8501 --name receipt-frontend receipt-analyzer:latest streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0```

4. Open in browser:
* UI: http://localhost:8501
* Backend docs: http://localhost:8000/docs

5. Stop Containers
```docker stop receipt-backend receipt-frontend```
```docker rm receipt-backend receipt-frontend```

### License
MIT License – free to use, modify, and share!
Built with ❤️ – 2026
