"""
Upload routes - handles HTTP endpoints for file upload
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
import os
import shutil
from typing import Dict, Any

from services.excel_service import ExcelService
from services.duplicate_service import DuplicateService
from repositories.contract_repository import ContractRepository
from models.contract_model import ContractRecord
from configs.database.db_config import db_config
from configs.app.settings import app_settings


router = APIRouter(prefix="/api/upload", tags=["upload"])


class UploadController:
    """Controller for upload operations"""
    
    def __init__(self):
        """Initialize controller with services"""
        self.excel_service = ExcelService()
        self.repository = ContractRepository(db_config)
        self.duplicate_service = DuplicateService(self.repository)
        
        # Ensure upload folder exists
        os.makedirs(app_settings.upload_folder, exist_ok=True)
    
    @staticmethod
    def _safe_str(val) -> str:
        """Convert any value to a JSON-safe string"""
        if val is None:
            return ""
        return str(val)

    def _record_to_preview(self, record: ContractRecord, row_num: int = None) -> dict:
        """Convert a ContractRecord to a preview dict for frontend display"""
        data = record.to_dict()
        # Use actual Excel row number stored during validation, fallback to provided row_num
        excel_row = data.get("_excel_row", row_num)
        preview = {
            "row": excel_row,
            "contractId": self._safe_str(data.get("contractId")),
            "peopleName": self._safe_str(data.get("peopleName")),
            "majorName": self._safe_str(data.get("majorName")),
            "companyProviderName": self._safe_str(data.get("companyProviderName")),
        }
        return preview
    
    async def upload_excel(self, file: UploadFile, insurance_type: str = None) -> Dict[str, Any]:
        """
        Handle Excel file upload with duplicate checking
        
        Args:
            file: Uploaded Excel file
            insurance_type: Insurance type from frontend (optional)
            
        Returns:
            Dictionary with upload results
        """
        try:
            # Validate file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in app_settings.allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed: {', '.join(app_settings.allowed_extensions)}"
                )
            
            # Save uploaded file
            file_path = os.path.join(app_settings.upload_folder, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Use provided insurance_type or detect from filename
            if not insurance_type:
                try:
                    insurance_type = self.excel_service.detect_insurance_type(file.filename)
                except ValueError as e:
                    os.remove(file_path)
                    raise HTTPException(status_code=400, detail=str(e))
            
            print(f"\n{'='*80}")
            print(f"Processing file: {file.filename}")
            print(f"Insurance type: {insurance_type}")
            print(f"{'='*80}\n")
            
            # Parse Excel file - returns (valid_records, validation_errors)
            records, parse_errors = self.excel_service.process_excel_file(
                file_path, insurance_type
            )
            
            # Get processor for validation summary
            processor = self.excel_service.get_processor(insurance_type)
            total_rows = len(records) + len(parse_errors)
            
            # PARTIAL SUCCESS APPROACH:
            # - Insert valid records into database
            # - Report errors for invalid records
            
            inserted_records = []
            inserted_count = 0
            duplicate_count = 0
            new_records = []
            duplicate_records = []
            insert_failed = []  # (record, error_msg) for records that passed dedup but failed INSERT

            # STRICT VALIDATION MODE:
            # If any row is invalid, reject the whole file and do not insert anything.
            if parse_errors:
                validation_summary = processor.get_validation_summary(
                    total_records=total_rows,
                    valid_count=len(records),
                    errors=parse_errors
                )
                valid_previews = [self._record_to_preview(r) for r in records] if records else []
                os.remove(file_path)
                return {
                    "success": False,
                    "status": "validation_error",
                    "message": f"File '{file.filename}' có {len(parse_errors)} dòng lỗi. Toàn bộ file chưa được import; vui lòng sửa hết lỗi rồi upload lại.",
                    "filename": file.filename,
                    "insurance_type": insurance_type,
                    "records_processed": 0,
                    "records_inserted": 0,
                    "duplicates_found": 0,
                    "valid_records_preview": valid_previews,
                    "validation_summary": validation_summary,
                    "error_details": {
                        "total_rows": total_rows,
                        "valid_rows": len(records),
                        "invalid_rows": len(parse_errors),
                        "success_rate": "0%",
                        "error_by_field": validation_summary['error_summary_by_field'],
                        "sample_errors": validation_summary['first_10_errors'],
                        "all_errors": validation_summary['all_errors'],
                        "has_more_errors": validation_summary['has_more_errors'],
                    },
                    "suggestion": "Phải sửa toàn bộ dòng lỗi trong file Excel trước khi import. Hiện tại hệ thống không import một phần dữ liệu.",
                    "upload_id": None
                }
            
            # Process valid records (even if there are some errors)
            if records:
                # Check for duplicates among valid records
                new_records, duplicate_records = self.duplicate_service.filter_duplicates(records)
                duplicate_count = len(duplicate_records)
                
                # Insert non-duplicate records
                if new_records:
                    inserted_records, insert_failed = self.repository.insert_records_batch(new_records)
                    inserted_count = len(inserted_records)
                    
                    # Add insert failures to parse_errors so they show up in Invalid tab
                    for failed_record, error_msg in insert_failed:
                        data = failed_record.to_dict()
                        row_num = data.get("_excel_row", "?")
                        parse_errors.append({
                            'row': row_num,
                            'excel_row': row_num,
                            'error_count': 1,
                            'field_errors': [{
                                'field': 'db_insert',
                                'excel_column': 'N/A',
                                'error_type': 'INSERT_FAILED',
                                'message': f'Lỗi khi ghi vào DB: {error_msg}',
                                'current_value': None
                            }],
                            'record_preview': {
                                'contractId': self._safe_str(data.get('contractId')),
                                'peopleName': self._safe_str(data.get('peopleName')),
                                'majorName': self._safe_str(data.get('majorName')),
                                'companyProviderName': self._safe_str(data.get('companyProviderName')),
                            }
                        })
            
            # Generate duplicate summary
            duplicate_summary = self.duplicate_service.get_duplicate_summary(
                total_count=len(records),
                new_count=len(new_records),
                duplicate_count=duplicate_count
            )
            
            # Clean up uploaded file
            os.remove(file_path)
            
            # Determine response status
            if parse_errors and len(records) == 0:
                # ALL records failed validation
                validation_summary = processor.get_validation_summary(
                    total_records=total_rows,
                    valid_count=0,
                    errors=parse_errors
                )
                return {
                    "success": False,
                    "status": "validation_error",
                    "message": f"File '{file.filename}' có {len(parse_errors)} dòng lỗi, không có dữ liệu hợp lệ để import",
                    "filename": file.filename,
                    "insurance_type": insurance_type,
                    "records_processed": 0,
                    "records_inserted": 0,
                    "duplicates_found": 0,
                    "validation_summary": validation_summary,
                    "error_details": {
                        "total_rows": total_rows,
                        "valid_rows": 0,
                        "invalid_rows": len(parse_errors),
                        "success_rate": "0%",
                        "error_by_field": validation_summary['error_summary_by_field'],
                        "sample_errors": validation_summary['first_10_errors'],
                        "all_errors": validation_summary['all_errors'],
                        "has_more_errors": validation_summary['has_more_errors'],
                    },
                    "suggestion": "Vui lòng kiểm tra và sửa các dòng lỗi trong file Excel, sau đó upload lại.",
                    "upload_id": None
                }
            
            elif parse_errors and len(records) > 0:
                # PARTIAL SUCCESS: Some records valid, some failed
                failed_insert_rows = {
                    (r.to_dict().get("_excel_row") if hasattr(r, "to_dict") else None)
                    for r, _ in insert_failed
                }
                filtered_valid_records = [
                    r for r in records
                    if r.to_dict().get("_excel_row") not in failed_insert_rows
                ]

                validation_summary = processor.get_validation_summary(
                    total_records=total_rows,
                    valid_count=len(filtered_valid_records),
                    errors=parse_errors
                )
                
                # Calculate ACTUAL success rate based on inserted + duplicates
                # (duplicates are valid records, just skipped)
                actual_success_count = inserted_count + duplicate_count
                actual_success_rate = f"{round(actual_success_count / total_rows * 100, 1)}%" if total_rows > 0 else "0%"
                
                # Build record previews for frontend tabs
                inserted_previews = [self._record_to_preview(r) for r in inserted_records] if inserted_records else []
                duplicate_previews = [self._record_to_preview(r) for r in duplicate_records] if duplicate_records else []
                valid_previews = [self._record_to_preview(r) for r in filtered_valid_records] if filtered_valid_records else []
                
                return {
                    "success": True,
                    "status": "partial_success",
                    "message": f"Đã import {inserted_count}/{total_rows} dòng. Có {len(parse_errors)} dòng lỗi không được import.",
                    "filename": file.filename,
                    "insurance_type": insurance_type,
                    # Summary counts
                    "records_processed": len(records),
                    "records_inserted": inserted_count,
                    "duplicates_found": duplicate_count,
                    "invalid_rows": len(parse_errors),
                    # Detailed fields
                    "total_records": total_rows,
                    "new_records": len(new_records),
                    "duplicate_records": duplicate_count,
                    "inserted_count": inserted_count,
                    "duplicate_summary": duplicate_summary,
                    # Record previews for frontend tabs
                    "inserted_records_preview": inserted_previews,
                    "duplicate_records_preview": duplicate_previews,
                    "valid_records_preview": valid_previews,
                    # Error details for invalid rows
                    "validation_summary": validation_summary,
                    "error_details": {
                        "total_rows": total_rows,
                        "valid_rows": len(filtered_valid_records),
                        "invalid_rows": len(parse_errors),
                        "success_rate": actual_success_rate,  # Use actual success rate
                        "error_by_field": validation_summary['error_summary_by_field'],
                        "sample_errors": validation_summary['first_10_errors'],
                        "all_errors": validation_summary['all_errors'],
                        "has_more_errors": validation_summary['has_more_errors'],
                    },
                    "suggestion": "Các dòng hợp lệ đã được import. Vui lòng sửa các dòng lỗi và upload lại nếu cần.",
                    "upload_id": f"upload_{insurance_type}_{inserted_count}"
                }
            
            else:
                # ALL records valid - full success
                # Update message based on whether there are duplicates
                if duplicate_count > 0 and inserted_count == 0:
                    message = f"Tất cả {duplicate_count} dòng đã tồn tại trong hệ thống (duplicates). Không có dòng mới được thêm."
                elif duplicate_count > 0:
                    message = f"Đã import {inserted_count}/{total_rows} dòng. Có {duplicate_count} dòng trùng lặp đã bỏ qua."
                else:
                    message = f"Đã xử lý thành công {inserted_count}/{total_rows} dòng từ file {file.filename}"
                
                # Build record previews for frontend tabs
                inserted_previews = [self._record_to_preview(r) for r in inserted_records] if inserted_records else []
                duplicate_previews = [self._record_to_preview(r) for r in duplicate_records] if duplicate_records else []
                valid_previews = [self._record_to_preview(r) for r in records] if records else []
                
                return {
                    "success": True,
                    "status": "success",
                    "message": message,
                    "filename": file.filename,
                    "insurance_type": insurance_type,
                    # Fields for frontend compatibility
                    "records_processed": len(records),
                    "records_inserted": inserted_count,
                    "duplicates_found": duplicate_count,
                    # Detailed fields
                    "total_records": total_rows,
                    "new_records": len(new_records),
                    "duplicate_records": duplicate_count,
                    "inserted_count": inserted_count,
                    "duplicate_summary": duplicate_summary,
                    "has_duplicates": duplicate_count > 0,
                    # Record previews for frontend tabs
                    "inserted_records_preview": inserted_previews,
                    "duplicate_records_preview": duplicate_previews,
                    "valid_records_preview": valid_previews,
                    "errors": [],
                    "upload_id": f"upload_{insurance_type}_{inserted_count}"
                }
            
        except HTTPException:
            raise
        except Exception as e:
            # Clean up file if it exists
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
            
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )


# Initialize controller
upload_controller = UploadController()


@router.post("/excel")
async def upload_excel_file(
    file: UploadFile = File(...),
    insurance_type: Optional[str] = Form(None)
):
    """
    Upload and process Excel file
    
    Args:
        file: Excel file to upload
        insurance_type: Insurance type from frontend (optional, auto-detect if not provided)
        
    Returns:
        JSON response with processing results
    """
    result = await upload_controller.upload_excel(file, insurance_type)
    # Ensure datetime and other non-primitive objects are safely serialized.
    return JSONResponse(content=jsonable_encoder(result))


@router.get("/status")
async def get_upload_status():
    """
    Get upload service status
    
    Returns:
        Status information
    """
    return {
        "status": "online",
        "service": "Excel Upload Service",
        "allowed_extensions": app_settings.allowed_extensions,
        "max_file_size_mb": app_settings.max_file_size / (1024 * 1024)
    }

