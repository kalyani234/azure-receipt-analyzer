# Receipt Analyzer

**Azure Receipt Text Detection & Extraction System**  
A full-stack web application that automatically detects key text regions on grocery receipt images (store name, date/time, items, total) and extracts structured information using Azure AI, custom annotations, and YOLOv8 fallback.

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

## Demo Screenshots

(Add your screenshots here later – e.g. upload to repo and link)

![Screenshot 1](screenshots/screenshot1.png)  
![Screenshot 2](screenshots/screenshot2.png)

## Architecture Diagram

```mermaid
graph TD
    User[User / Browser] -->|1. Upload receipt image| Streamlit[Streamlit Frontend<br>ui/streamlit_app.py<br>port 8501]

    Streamlit -->|2. POST /analyze<br>multipart file| FastAPI[FastAPI Backend<br>api/main.py<br>port 8000]

    subgraph "Backend Processing"
        FastAPI --> AzureAI[Azure AI Document Intelligence<br>prebuilt-receipt model]

        AzureAI -->|Primary: Real OCR + structured fields<br>MerchantName, TransactionDate, Total, Items table| Merge[Merge Results<br>detections + azure_fields + azure_items]

        FastAPI --> XMLCheck{filename in XML?}
        XMLCheck -->|Yes| XML[XML Annotations<br>data/annotations.xml<br>Exact boxes + labeled text]
        XML --> Merge

        XMLCheck -->|No| YOLOCheck{YOLO loaded?}
        YOLOCheck -->|Yes| YOLO[YOLOv8 Model<br>PyTorch-based<br>runs/detect/train3/weights/best.pt<br>Boxes + real confidence]
        YOLO --> Merge

        Merge -->|3. Return JSON| FastAPI
    end

    FastAPI -->|4. JSON response| Streamlit

    Streamlit -->|5. Render:<br>• Side-by-side images with boxes<br>• Summary cards (Store, Date, Total)<br>• Items table<br>• Download annotated PNG| User

    classDef azure fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef pytorch fill:#ee4c2c,stroke:#b33a1f,stroke-width:2px,color:#fff
    classDef streamlit fill:#ff4b4b,stroke:#d43f3f
    classDef fastapi fill:#00bfff,stroke:#009acd

    class AzureAI azure
    class YOLO pytorch
    class Streamlit streamlit
    class FastAPI fastapi
```
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
