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
from fastapi.responses import JSONResponse
from omniparse.image import parse_image, process_image
# from omniparse import load_omnimodel

from omniparse.utils import encode_images

document_router = APIRouter()
model_state = get_shared_state()

@celery_app.task(name="omniparse.task.parse_img.process_and_callback_img_task")
# def process_and_callback__img_task(file_bytes_list, callback_url):
#     model_state = get_shared_state()
#     results = []

#     logging.info(f"🚀 Starting image parsing task for {len(file_bytes_list)} image(s).")

#     for index ,file_bytes in enumerate(file_bytes_list):
#         try:
#             logging.info(f"🖼️ Processing image {index + 1}/{len(file_bytes_list)}...") 
#             parsed_result:responseDocument = parse_image(file_bytes, model_state)
            
#             results.append({
#                 "status": "success",
#                 "index": index,
#                 "parsed_data": parsed_result
#             })
#             logging.info(f"✅ Successfully processed image {index + 1}.")
#         except Exception as e:
#             error_msg = f"❌ Failed to process image {index + 1}: {e}"
#             logging.error(error_msg)
#             results.append({
#                 "status": "error",
#                 "index": index,
#                 "error": str(e)
#             })

#     # ✅ Send final results to callback
#     try:
#         logging.info(f"📬 Sending callback to {callback_url} with {len(results)} result(s).")
#         with httpx.Client() as client:
#             response = client.post(callback_url, json={"results": results})
#             response.raise_for_status()
#             logging.info(f"✅ Callback sent successfully. Status code: {response.status_code}")
#     except Exception as e:
#         logging.error(f"❌ Failed to send callback to {callback_url}: {str(e)}")
def process_and_callback__img_task(file_bytes_list, callback_url):
    model_state = get_shared_state()
    results = []

    logging.info(f"🚀 Starting image parsing task for {len(file_bytes_list)} image(s).")

    for index, file_bytes in enumerate(file_bytes_list):
        try:
            logging.info(f"🖼️ Processing image {index + 1}/{len(file_bytes_list)}...") 

            parsed_result: responseDocument = parse_image(file_bytes, model_state)
            parsed_data_dict = parsed_result.model_dump(mode="json")  # ✅ Dump nested models
            results.append({
                "status": "success",
                "index": index,
                "parsed_data": parsed_data_dict
            })

            logging.info(f"✅ Successfully processed image {index + 1}.")

        except Exception as e:
            error_msg = f"❌ Failed to process image {index + 1}: {e}"
            logging.error(error_msg)

            results.append({
                "status": "error",
                "index": index,
                "error": str(e)
            })

    # ✅ Send final results to callback
    try:
        logging.info(f"📬 Sending callback to {callback_url} with {len(results)} result(s).")

        with httpx.Client() as client:
            response = client.post(callback_url, json={"results": results})
            response.raise_for_status()
            logging.info(f"✅ Callback sent successfully. Status code: {response.status_code}")

    except Exception as e:
        logging.error(f"❌ Failed to send callback to {callback_url}: {str(e)}")
