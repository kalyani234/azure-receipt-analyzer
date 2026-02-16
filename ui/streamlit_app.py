# ui/streamlit_app.py

import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import time
import json

st.set_page_config(
    page_title="Receipt Analyzer",
    page_icon="🧾",
    layout="wide"
)

st.title("Receipt Analyzer")

# Upload & Analyze
uploaded_file = st.file_uploader(
    "Upload receipt photo",
    type=["jpg", "jpeg", "png"],
    help="jpg / jpeg / png • clear photo recommended"
)

if uploaded_file is not None:
    col1, col2 = st.columns([5, 1])
    with col1:
        if st.button("Analyze Receipt", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()

            for percent in range(0, 101, 10):
                time.sleep(0.12)
                progress_bar.progress(percent)
                status_text.text(f"Processing: {percent}%")

            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                response = requests.post("http://host.docker.internal:8000/analyze", files=files, timeout=30)
                response.raise_for_status()
                result = response.json()

                original_image = Image.open(io.BytesIO(uploaded_file.getvalue()))
                draw_image = original_image.convert("RGB")
                draw = ImageDraw.Draw(draw_image, "RGBA")

                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                    small_font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                    small_font = ImageFont.load_default()

                detections = result.get("detections", [])
                filtered = [d for d in detections if d.get("confidence", 0) >= 0.0]  # show all for now

                color_map = {
                    "STORE": (0, 0, 255, 160),
                    "DATE": (0, 255, 0, 140),
                    "DATE_TIME": (0, 255, 0, 140),
                    "ITEM": (255, 165, 0, 120),
                    "TOTAL": (255, 0, 0, 160)
                }

                for det in filtered:
                    label = det["label"]
                    box = det["box"]
                    conf = det.get("confidence", 0.95)
                    text = det.get("text", "")

                    color = color_map.get(label, (128, 0, 128, 140))

                    x1, y1, x2, y2 = box

                    draw.rectangle([x1, y1, x2, y2], outline=color, width=5, fill=color[:3] + (60,))
                    label_text = f"{label} {conf:.0%}"
                    draw.text((x1, y1 - 38), label_text, fill=color[:3] + (255,), font=font)

                    if text:
                        draw.text((x1 + 8, y1 + 8), text[:35] + ("..." if len(text) > 35 else ""), fill=(255,255,255,220), font=small_font)

                # Tabs for polished view
                tab1, tab2, tab3 = st.tabs(["📷 Images", "📊 Summary", "🔍 Raw JSON"])

                with tab1:
                    col_img1, col_img2 = st.columns(2)
                    with col_img1:
                        st.subheader("Original")
                        st.image(original_image, width=450)
                    with col_img2:
                        st.subheader("Detected Regions")
                        st.image(draw_image, width=450)

                with tab2:
                    st.markdown("### Analysis Results")

                    store = next((d["text"] for d in detections if d["label"] == "STORE"), "—")
                    date = next((d["text"] for d in detections if d["label"] in ["DATE", "DATE_TIME"]), "—")
                    total = next((d["text"] for d in detections if d["label"] == "TOTAL"), "—")

                    kcol1, kcol2, kcol3 = st.columns(3)
                    kcol1.metric("Store", store)
                    kcol2.metric("Date / Time", date)
                    kcol3.metric("Total", total)

                    items = [d for d in detections if d["label"] == "ITEM"]
                    if items:
                        st.subheader("Detected Items")
                        table_data = [
                            {"#": i+1, "Description": d["text"], "Confidence": f"{d['confidence']:.0%}"}
                            for i, d in enumerate(items)
                        ]
                        st.dataframe(table_data, hide_index=True, use_container_width=True)
                    else:
                        st.info("No items detected")

                with tab3:
                    st.subheader("Raw JSON from Backend")
                    st.json(result)

                st.success("Analysis complete!")

                img_bytes = io.BytesIO()
                draw_image.save(img_bytes, format="PNG")
                st.download_button(
                    label="Download Detected Image (PNG)",
                    data=img_bytes.getvalue(),
                    file_name=f"analyzed_{uploaded_file.name}",
                    mime="image/png"
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.button("Clear Upload"):
        st.rerun()

else:
    st.info("Upload a receipt photo to start.")