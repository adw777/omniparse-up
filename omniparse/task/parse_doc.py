import os
import tempfile
import subprocess
import httpx
import logging 
import time
import io
from omniparse.image import parse_image
import pdf2image
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

MAX_SIZE_MB = 8
MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

# MAX_SIZE_KB = 200
# MAX_SIZE_BYTES = MAX_SIZE_KB * 1024

@celery_app.task(name="omniparse.task.parse_doc.process_and_callback_task")
def process_and_callback_task(file_data_list, callback_url,task_id):
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
    
    
    # =====================================================================================================================================================
    # model_state = get_shared_state()
    # results = []
    # logging.info(f"🚀 Starting Celery task for {len(file_data_list)} files.")
    # total_files = len(file_data_list)
    # for idx, (filename, file_bytes, file_ext) in enumerate(file_data_list, start=1):    
    #     logging.info(f"📄 Processing file {idx}/{total_files}: {filename} ({file_ext})")
    #     start_time = time.time()

    #     if file_bytes > MAX_SIZE_BYTES:
    #         logging.info(f"📷 Redirecting to parse_image for large file: {filename} ({file_bytes} bytes)")
    #         # Here you can call another function, enqueue a task, or return a different response
    #         # Example: call parse_image(file)
    #         images = pdf2image.convert_from_bytes(file_bytes, dpi=300, fmt="png")
    #         print(f"Converted to {len(images)} images")
    #         image_data_list = []
    #         for i, img in enumerate(images):
    #             img_bytes = io.BytesIO()
    #             img.save(img_bytes, format='PNG')
    #             img_bytes.seek(0)
                
    #             image_data_list.append({
    #                 "page_number": i + 1,
    #                 "image_bytes": img_bytes,  # Still in BytesIO format
    #                 "filename": f"{filename}_page_{i + 1}.png"
    #             })

    #             print("✅ Image data list prepared")
    #             parsed_result: responseDocument = parse_image(file_bytes, model_state)
    #             parsed_data_dict = parsed_result.model_dump(mode="json")  # ✅ Dump nested models
    #             results.append({
    #                 "status": "success",
    #                 "parsed_data": parsed_data_dict
    #             })
    #             # return image_data_list
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
    #         tmp_file.write(file_bytes)
    #         tmp_file.flush()
    #         input_path = tmp_file.name

    #     # Convert to PDF if needed
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
    #         })
    #         logging.info(f"✅ Completed {idx}/{total_files}: {filename} in {duration:.2f}s")
    #     finally:
    #         if os.path.exists(input_path):
    #             os.remove(input_path)

    # # 🔁 Send final results once — after loop ends
    # try:
    #     with httpx.Client() as client:
    #         response = client.post(callback_url, json={"results": results})
    #         response.raise_for_status()
    #         logging.info(f"📬 Sent callback to {callback_url} with {len(results)} results. Status: {response.status_code}")
    # except Exception as e:
    #     logging.error(f"❌ Failed to send callback to {callback_url}: {str(e)}")
    
    
    
    model_state = get_shared_state()
    results = []
    logging.info(f"🚀 Starting task for {len(file_data_list)} files.")

    total_files = len(file_data_list)

    for idx, (filename, file_bytes, file_ext) in enumerate(file_data_list, start=1):    
        logging.info(f"📄 Processing file {idx}/{total_files}: {filename} ({file_ext})")
        start_time = time.time()

        if len(file_bytes) > MAX_SIZE_BYTES:
            logging.info(f"📷 File > 20MB, converting to images: {filename} ({len(file_bytes)} bytes)")
            images = pdf2image.convert_from_bytes(file_bytes, dpi=300, fmt="png")
            logging.info(f"Converted {filename} to {len(images)} images.")

            markdown_pages = []
            for i, img in enumerate(images):
                page_number = i + 1
                logging.info(f"🖼️ Extracting from image page {page_number} of total {len(images)} images of {filename}...")

                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PNG")   
                img_bytes.seek(0)

                parsed_result: responseDocument = parse_image(img_bytes.getvalue(), model_state)
                parsed_data_dict = parsed_result.model_dump(mode="json")
                # print(parsed_data_dict,"............................")
                markdown = parsed_data_dict.get("text", "")  # ✅ extract only markdown string
                markdown_pages.append(markdown)

                logging.info(f"✅ Completed extraction from page {page_number} of {filename}")

            combined_markdown = "\n\n".join(markdown_pages)
            duration = time.time() - start_time
            results.append({
                "filename": filename,
                "text": combined_markdown,
                "metadata": {"source": "image-parsed"},
                "duration_sec": round(duration, 2),
            })
            logging.info(f"✅ Completed large-file image-parsing for {filename} in {duration:.2f}s")
            continue  # Skip normal flow

        # Handle regular files
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file.flush()
            input_path = tmp_file.name

        try:
            # Convert Office files to PDF
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

            full_text, images, out_meta = convert_single_pdf(input_path, model_state.model_list)
            duration = time.time() - start_time
            results.append({
                "filename": filename,
                "text": full_text,
                "metadata": out_meta,
                "duration_sec": round(duration, 2),
            })
            logging.info(f"✅ Completed {idx}/{total_files}: {filename} in {duration:.2f}s")

        except Exception as e:
            logging.error(f"❌ Error processing {filename}: {e}")
            results.append({
                "filename": filename,
                "error": str(e)
            })

        finally:    
            if os.path.exists(input_path):
                os.remove(input_path)

    # 🔁 Send results after processing all files
    try:
        with httpx.Client() as client:
            response = client.post(callback_url, json={"task_id": task_id,"results": results})
            response.raise_for_status()
            logging.info(f"📬 Callback sent to {callback_url} with {len(results)} results. Status: {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Callback failed to {callback_url}: {str(e)}")
