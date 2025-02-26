from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import shutil
import uvicorn

app = FastAPI()

UPLOAD_DIR = "uploads"
DATA_CACHE = []

# Hàm đọc và xử lý từng tệp Excel
def process_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        df = df.dropna(how='all')
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi khi xử lý tệp: {str(e)}")

# Endpoint tải lên tệp
@app.post("/upload")
def upload_files(files: list[UploadFile] = File(...)):
    global DATA_CACHE
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    DATA_CACHE.clear()

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df = process_excel_file(file_path)
        if df is not None:
            DATA_CACHE.append(df)

    if not DATA_CACHE:
        raise HTTPException(status_code=400, detail="Không có dữ liệu hợp lệ.")
    return {"message": "Tệp đã được tải lên và xử lý thành công."}

# Endpoint trả về dữ liệu JSON với cấu trúc tùy thuộc vào tệp Excel
@app.get("/get-json")
def get_json():
    global DATA_CACHE
    if not DATA_CACHE:
        raise HTTPException(status_code=404, detail="Không có dữ liệu nào được lưu trữ.")

    combined_df = pd.concat(DATA_CACHE, ignore_index=True, sort=False)
    response_data = combined_df.to_dict(orient='records')
    return JSONResponse(content=response_data)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)