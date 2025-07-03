from typing import List
from fastapi import UploadFile, File, HTTPException, APIRouter, Form
from fastapi.responses import JSONResponse
from omniparse import get_shared_state
from omniparse.image import parse_image, process_image
from omniparse.models import responseDocument
from omniparse.task.parse_img import process_and_callback__img_task
from fastapi import status


image_router = APIRouter()
model_state = get_shared_state()


# @image_router.post("/image")
# async def parse_image_endpoint(file: UploadFile = File(...),callback_url: str = Form(...)):
#     try:
#         file_bytes = await file.read()
#         await process_and_callback__img_task(file_bytes ,callback_url)
#         # result: responseDocument = parse_image(file_bytes, model_state)
#         # return JSONResponse(content=result.model_dump())
#         return JSONResponse(content={"message": "Processing started."}, status_code=status.HTTP_202_ACCEPTED)


#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@image_router.post("/image")
async def parse_image_endpoint(
    files: List[UploadFile] = File(...),
    callback_url: str = Form(...)
):
    try:
        file_bytes_list = [await file.read() for file in files]
        # Send task to Celery
        process_and_callback__img_task.delay(file_bytes_list, callback_url)

        return JSONResponse(
            content={"message": f"Started processing {len(files)} image(s)."},
            status_code=status.HTTP_202_ACCEPTED
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@image_router.post("/process_image")
async def process_image_route(image: UploadFile = File(...), task: str = Form(...)):
    try:
        file_bytes = await image.read()
        # await process_and_callback__img_task(file_bytes,task ,callback_url)
        result: responseDocument = process_image(file_bytes, task)
        return JSONResponse(content=result.model_dump())


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
