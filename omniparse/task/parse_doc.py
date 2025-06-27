import os
import tempfile
import subprocess
import httpx
import logging 
from marker.convert import convert_single_pdf
from omniparse.task.celery_app import celery_app
from omniparse.models import responseDocument
from omniparse import get_shared_state
from fastapi import APIRouter, File, UploadFile, HTTPException, Form

document_router = APIRouter()
model_state = get_shared_state()

@celery_app.task(name="omniparse.task.parse_doc.process_and_callback_task")
def process_and_callback_task(file_bytes: bytes, file_ext: str, callback_url: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_file.flush()
        input_path = tmp_file.name
    
    try:
        if file_ext.lower() in {".ppt", ".pptx", ".doc", ".docx"}:
            output_dir = tempfile.mkdtemp()
            command = [
                "libreoffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                output_dir,
                input_path,
            ]
            subprocess.run(command, check=True)
            input_path = os.path.join(
                output_dir,
                os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            logging.info("------v---")
            print(model_state,"...........................")
        # PDF processing
        full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)
        result = responseDocument(text=full_text, metadata=out_meta)
        encode_images(images, result)

        # Callback
        with httpx.Client() as client:
            client.post(callback_url, json=result.model_dump())

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
