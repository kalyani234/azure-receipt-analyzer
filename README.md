# 🧾 Azure-YOLO Receipt Parser
### *Advanced AI-Powered OCR & Object Detection for Grocery Analytics*

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Azure](https://img.shields.io/badge/AI-Azure%20Document%20Intelligence-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)

---

## 📖 Project Description
The **Azure-YOLO Receipt Parser** is a full-stack engineering solution designed to bridge the gap between raw grocery receipt images and structured digital data. While standard OCR tools often lose context, this system utilizes a **Tri-Tier Hybrid Extraction Engine** to maintain spatial relationships between merchant names, line items, and totals.

By cascading from **Enterprise Cloud AI** (Azure) to **Custom Edge AI** (YOLOv8), the application ensures high-reliability extraction even when receipts are blurred, poorly lit, or follow non-standard layouts.

---
```
## Project Structure
receipt-analyzer/
├── api/                    # FastAPI backend
│   └── main.py             # API logic + /analyze endpoint
├── ui/                     # Streamlit frontend
│   └── streamlit_app.py    # UI: upload, analyze, display results
├── data/                   # Dataset
│   ├── images/             # 0.jpg ... 19.jpg (receipt photos)
│   └── annotations.xml     # Bounding boxes + text labels
├── runs/                   # YOLO training outputs
│   └── detect/trainX/      # weights/best.pt
├── scripts/                # Helpers
│   └── convert_to_yolo.py  # XML → YOLO converter
├── Dockerfile              # Docker build
├── requirements.txt        # Dependencies
├── .dockerignore           # Exclude large files
├── .gitignore              # Ignore venv, cache, runs/
└── README.md               # This file
```
---

## 📐 System Architecture
The system is built on a microservices architecture, dockerized for seamless deployment.

<p align="center">
  <img width="100%" alt="Azure-YOLO System Architecture" src="https://github.com/user-attachments/assets/c8c05658-cd4e-4726-980b-aa920358f088" />
</p>

### **The Hybrid Logic Flow:**
1.  **Primary Engine:** **Azure AI Document Intelligence** performs real-time OCR and structured field mapping.
2.  **Deterministic Fallback:** If the receipt is from the core dataset, the system uses **Pre-annotated XML Mapping** for 100% coordinate accuracy.
3.  **Heuristic Fallback:** For unseen formats, a custom-trained **YOLOv8 (PyTorch)** model detects key regions (Header, Items, Footer) and applies confidence scoring to filter noise.
---

### Demo
[Recording](https://github.com/user-attachments/assets/bb44fd9f-dd4d-4337-b451-9dd4d4a9673a)

---

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

### **Local Run (Docker)**

1.  **Build the Project Image:**
    ```bash
    docker build -t receipt-analyzer:latest .
    ```

2.  **Deploy the Backend (FastAPI):**
    ```bash
    docker run -d -p 8000:8000 --name receipt-backend receipt-analyzer:latest uvicorn api.main:app --host 0.0.0.0 --port 8000
    ```

3.  **Deploy the Frontend (Streamlit):**
    ```bash
    docker run -d -p 8501:8501 --name receipt-frontend receipt-analyzer:latest streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
    ```

### **How to Use**
1.  Navigate to `http://localhost:8501`.
2.  Upload a receipt image (`.jpg`, `.jpeg`, or `.png`).
3.  Adjust the **Confidence Threshold** slider to filter detections.
4.  Review the extracted table and download the annotated image for your records.

---

## 📊 Dataset Reference
This project utilizes the **OCR Receipts from Grocery Stores** dataset:
* **Source:** [Kaggle - TrainingDataPro](https://www.kaggle.com/datasets/trainingdatapro/ocr-receipts-text-detection)
* **Scope:** 20 high-quality grocery receipts with full XML annotations for `store`, `item`, `date_time`, and `total`.

---

## 📜 License
Distributed under the **MIT License**.

**Built with ❤️ — 2026**
