import xml.etree.ElementTree as ET
import os
from pathlib import Path

XML_PATH = "/Users/navyakalyani/Desktop/receipt-analyzer/data/annotations.xml"
IMG_DIR = "/Users/navyakalyani/Desktop/receipt-analyzer/data/images"
YOLO_DIR = "/Users/navyakalyani/Desktop/receipt-analyzer/data/yolo_labels"

os.makedirs(YOLO_DIR, exist_ok=True)

# Class mapping (YOLO starts from 0)
classes = {"STORE": 0, "DATE": 1, "DATE_TIME": 1, "ITEM": 2, "TOTAL": 3}
class_names = ["STORE", "DATE_TIME", "ITEM", "TOTAL"]

tree = ET.parse(XML_PATH)
root = tree.getroot()

for image_elem in root.findall("image"):
    img_name = os.path.basename(image_elem.get("name"))
    width = float(image_elem.get("width"))
    height = float(image_elem.get("height"))

    label_path = os.path.join(YOLO_DIR, img_name.replace(".jpg", ".txt").replace(".JPG", ".txt"))

    with open(label_path, "w") as f:
        for box in image_elem.findall("box"):
            label = box.get("label").upper()
            if label == "SHOP":
                label = "STORE"
            if label == "DATE_TIME":
                label = "DATE"

            if label not in classes:
                continue

            class_id = classes[label]

            xtl = float(box.get("xtl"))
            ytl = float(box.get("ytl"))
            xbr = float(box.get("xbr"))
            ybr = float(box.get("ybr"))

            # YOLO format: center_x, center_y, width, height (normalized)
            center_x = (xtl + xbr) / 2 / width
            center_y = (ytl + ybr) / 2 / height
            w = (xbr - xtl) / width
            h = (ybr - ytl) / height

            f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {w:.6f} {h:.6f}\n")

print("YOLO labels created in data/yolo_labels/")