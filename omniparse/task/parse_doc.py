import os
import tempfile
import subprocess
import httpx
import logging 
import time
from marker.convert import convert_single_pdf
from omniparse.task.celery_app import celery_app
from omniparse.models import responseDocument
from omniparse import get_shared_state
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
# from omniparse import load_omnimodel

from omniparse.utils import encode_images

document_router = APIRouter()
model_state = get_shared_state()

# print(model_state,"...........................")

# load_omnimodel(load_documents=True, load_media= False, load_web=False)

# @celery_app.task(name="omniparse.task.parse_doc.process_and_callback_task")
# def process_and_callback_task(file_bytes: bytes, file_ext: str, callback_url: str):
    # with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
    #     tmp_file.write(file_bytes)
    #     tmp_file.flush()
    #     input_path = tmp_file.name
    
    # try:
    #     if file_ext.lower() in {".ppt", ".pptx", ".doc", ".docx"}:
    #         output_dir = tempfile.mkdtemp()
    #         command = [
    #             "libreoffice",
    #             "--headless",
    #             "--convert-to",
    #             "pdf",
    #             "--outdir",
    #             output_dir,
    #             input_path,
    #         ]
    #         subprocess.run(command, check=True)
    #         input_path = os.path.join(
    #             output_dir,
    #             os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    #         )
    #         logging.info("------v---")
    #     # PDF processing
    #     full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)
    #     result = responseDocument(text=full_text, metadata=out_meta)
    #     encode_images(images, result)

    #     # Callback
    #     with httpx.Client() as client:
    #         client.post(callback_url, json=result.model_dump())

    # finally:
    #     if os.path.exists(input_path):
    #         os.remove(input_path)


@celery_app.task(name="omniparse.task.parse_doc.process_and_callback_task")
def process_and_callback_task(file_data_list, callback_url):
    # model_state = get_shared_state()
    # # load_omnimodel(load_documents=True, load_media=False, load_web=False)
    # results = []
    # logging.info(f"🚀 Starting Celery task for {len(file_data_list)} files.")
    # for filename, file_bytes, file_ext in file_data_list:
    #     logging.info(f"📄 Processing: {filename} ({file_ext})")
    #     start_time = time.time()
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
    #         tmp_file.write(file_bytes)
    #         tmp_file.flush()
    #         input_path = tmp_file.name

    #     # DOCX to PDF conversion if needed
    #     if file_ext in {".doc", ".docx", ".ppt", ".pptx"}:
    #         output_dir = tempfile.mkdtemp()
    #         subprocess.run([
    #             "libreoffice", "--headless", "--convert-to", "pdf",
    #             "--outdir", output_dir, input_path
    #         ], check=True)
    #         input_path = os.path.join(
    #             output_dir,
    #             os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    #         )
    #         logging.info(f"🔄 Converted {filename} to PDF.")

    #     try:
    #         full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)
    #         duration = time.time() - start_time
    #         results.append({
    #             "filename": filename,
    #             "text": full_text,
    #             "metadata": out_meta,
    #             "duration_sec": round(duration, 2),
    #             # "num_images": len(images),
    #         })
    #         logging.info(f"✅ Finished processing {filename} in {duration:.2f}s")
    #     finally:
    #         if os.path.exists(input_path):
    #             os.remove(input_path)

    # # 🔁 Send all results together
    # with httpx.Client() as client:
    #     client.post(callback_url, json={"results": results})
    #     logging.info(f"📬 Sent callback to {callback_url} with {len(results)} results.")
    model_state = get_shared_state()
    results = []
    logging.info(f"🚀 Starting Celery task for {len(file_data_list)} files.")
    total_files = len(file_data_list)
    for idx, (filename, file_bytes, file_ext) in enumerate(file_data_list, start=1):    
        logging.info(f"📄 Processing file {idx}/{total_files}: {filename} ({file_ext})")
        start_time = time.time()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()
            input_path = tmp_file.name

        # Convert to PDF if needed
        if file_ext in {".doc", ".docx", ".ppt", ".pptx"}:
            output_dir = tempfile.mkdtemp()
            subprocess.run([
                "libreoffice", "--headless", "--convert-to", "pdf",
                "--outdir", output_dir, input_path
            ], check=True)
            input_path = os.path.join(
                output_dir,
                os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            )
            logging.info(f"🔄 Converted {filename} to PDF.")

        try:
            full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)
            duration = time.time() - start_time
            results.append({
                "filename": filename,
                "text": full_text,
                "metadata": out_meta,
                "duration_sec": round(duration, 2),
            })
            logging.info(f"✅ Completed {idx}/{total_files}: {filename} in {duration:.2f}s")
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

    # 🔁 Send final results once — after loop ends
    try:
        with httpx.Client() as client:
            response = client.post(callback_url, json={"results": results})
            response.raise_for_status()
            logging.info(f"📬 Sent callback to {callback_url} with {len(results)} results. Status: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Failed to send callback to {callback_url}: {str(e)}")