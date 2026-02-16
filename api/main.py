# api/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import os
from typing import Dict, List
from ultralytics import YOLO
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import AnalyzeResult

app = FastAPI(title="Receipt Analyzer Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────
# Azure Document Intelligence (C)
# ────────────────────────────────────────────────

AZURE_ENDPOINT = "https://xxx.cognitiveservices.azure.com/"  # ← YOUR ENDPOINT
AZURE_KEY = "1P2o6oRva"  # ← YOUR KEY 1

azure_client = DocumentIntelligenceClient(
    endpoint=AZURE_ENDPOINT,
    credential=AzureKeyCredential(AZURE_KEY)
)

# ────────────────────────────────────────────────
# Load XML annotations (fallback)
# ────────────────────────────────────────────────

ANNOTATIONS_PATH = "/app/data/annotations.xml"  # path inside container
annotations: Dict[str, List[Dict]] = {}

if os.path.exists(ANNOTATIONS_PATH):
    try:
        tree = ET.parse(ANNOTATIONS_PATH)
        root = tree.getroot()

        for image_elem in root.findall("image"):
            img_name = os.path.basename(image_elem.get("name", ""))
            if not img_name:
                continue

            detections = []

            for box in image_elem.findall("box"):
                label = box.get("label", "").strip().upper()
                if label == "SHOP":
                    label = "STORE"
                if label == "DATE_TIME":
                    label = "DATE"

                try:
                    xtl = float(box.get("xtl", 0))
                    ytl = float(box.get("ytl", 0))
                    xbr = float(box.get("xbr", 0))
                    ybr = float(box.get("ybr", 0))
                except:
                    continue

                text_elem = box.find(".//attribute[@name='text']")
                text = text_elem.text.strip() if text_elem is not None and text_elem.text else ""

                detections.append({
                    "label": label,
                    "box": [xtl, ytl, xbr, ybr],
                    "text": text,
                    "confidence": 0.95
                })

            if detections:
                annotations[img_name] = detections

        print(f"Loaded {len(annotations)} images from XML")
        print("Loaded filenames:", sorted(annotations.keys()))

    except Exception as e:
        print(f"XML load error: {str(e)}")
        annotations = {}
else:
    print(f"XML not found at {ANNOTATIONS_PATH} — skipping XML")

# ────────────────────────────────────────────────
# Load YOLOv8 model (fallback)
# ────────────────────────────────────────────────

YOLO_MODEL_PATH = "/app/runs/detect/train3/weights/best.pt"  # path inside container

yolo_model = None
if os.path.exists(YOLO_MODEL_PATH):
    try:
        yolo_model = YOLO(YOLO_MODEL_PATH)
        print(f"✅ YOLOv8 model loaded from: {YOLO_MODEL_PATH}")
    except Exception as e:
        print(f"❌ YOLO load failed: {str(e)}")
else:
    print(f"YOLO model not found at {YOLO_MODEL_PATH} — fallback disabled")

# ────────────────────────────────────────────────
# Analyze endpoint
# ────────────────────────────────────────────────

@app.post("/analyze")
async def analyze_receipt(file: UploadFile = File(...)):
    filename = file.filename.strip()
    contents = await file.read()

    detections = []
    azure_fields = {}
    azure_items = []

    # Primary: Azure Document Intelligence (prebuilt-receipt)
    try:
        poller = azure_client.begin_analyze_document(
            "prebuilt-receipt",
            analyze_request=contents,  # ← FIXED: required argument
            content_type="application/octet-stream"
        )
        azure_result = poller.result()

        # Extract key fields
        if azure_result.documents:
            doc = azure_result.documents[0]
            for field in doc.fields.values():
                if field.value_string:
                    azure_fields[field.name] = field.value_string

        # Extract items table
        if "Items" in doc.fields:
            items_field = doc.fields["Items"]
            if items_field.value_array:
                for item in items_field.value_array:
                    item_dict = {}
                    if item.value_object:
                        for item_field in item.value_object.values():
                            if item_field.value_string:
                                item_dict[item_field.name] = item_field.value_string
                    azure_items.append(item_dict)

        print(f"Azure extracted fields: {azure_fields}")
        print(f"Azure items: {len(azure_items)}")

    except Exception as e:
        print(f"Azure error: {str(e)} – falling back to XML/YOLO")

    # Fallback 1: XML for boxes + text
    if filename in annotations:
        detections = annotations[filename]
        # Merge Azure text
        for det in detections:
            if det["label"] == "TOTAL" and "Total" in azure_fields:
                det["text"] = azure_fields["Total"]
            if det["label"] == "DATE" and "TransactionDate" in azure_fields:
                det["text"] = azure_fields["TransactionDate"]
            if det["label"] == "STORE" and "MerchantName" in azure_fields:
                det["text"] = azure_fields["MerchantName"]
        print(f"XML match for {filename}")

    # Fallback 2: YOLO for boxes/confidence
    if not detections and yolo_model:
        results = yolo_model(contents)[0]
        for box in results.boxes:
            cls = int(box.cls)
            conf = float(box.conf)
            xyxy = box.xyxy[0].tolist()
            label = yolo_model.names[cls]

            detections.append({
                "label": label,
                "box": xyxy,
                "text": "",
                "confidence": conf
            })
        print(f"YOLO fallback for {filename} — {len(detections)} detections")

    if not detections:
        raise HTTPException(
            status_code=404,
            detail=f"No detections found for '{filename}'. Loaded XML keys: {sorted(annotations.keys())}"
        )

    return {
        "status": "success",
        "detections": detections,
        "azure_fields": azure_fields,
        "azure_items": azure_items
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
