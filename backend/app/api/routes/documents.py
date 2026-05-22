from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from app.models.document import DocumentResponse
from app.services.docx_parser import save_upload_file, parse_docx
from app.services.ieee_formatter import generate_ieee_docx
from app.services.auth import get_current_user
import os

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # 1. Store upload locally and validate
    file_path = await save_upload_file(file)
    
    try:
        # 2. Extract text and structure using python-docx
        parsed_data = parse_docx(file_path)
        return DocumentResponse(**parsed_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/format")
async def format_document(file: UploadFile = File(...), template: str = Form(...), current_user: dict = Depends(get_current_user)):
    if template != "ieee":
        raise HTTPException(status_code=400, detail="Only the 'ieee' template is currently supported.")
        
    file_path = await save_upload_file(file)
    try:
        parsed_data = parse_docx(file_path)
        output_path = file_path.replace(".docx", "_formatted.docx")
        generate_ieee_docx(parsed_data, output_path)
        
        return FileResponse(
            path=output_path, 
            filename=f"formatted_{file.filename}",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
