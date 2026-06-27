"""
Base mapping class - Abstract base for insurance type mappings
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseInsuranceMapping(ABC):
    """
    Abstract base class for insurance type column mappings
    Defines common fields and structure that all insurance types must have

    Design Pattern: Template Method Pattern
    - Define skeleton of algorithm in base class
    - Let subclasses override specific steps
    """

    # Valid Channel values (programCodeMiningChannel)
    VALID_CHANNELS = {
        'DSA',
        'DSA/Renew',
        'DSA_NEO',
        'DSA_NEO/Renew',
        'TSA',
        'Renew',
        'CTV_TSA (TSA 2)',
        'CTV_TSA (TSA 2)/Renew',
        'HO',
        'Digital',
        'Referral'
    }

    # Valid payment method values (termsFeePaymentMethod) - NOT NULL & enum
    VALID_PAYMENT_METHODS = {
        'OCB', 'Payoo', 'Bảo Kim', 'VietcomBank', 'Nhà bảo hiểm', 'InsuStream'
    }

    # Valid company providers per insurance type (companyProviderName)
    # Subclasses override INSURANCE_TYPE_KEY to select the right set
    VALID_COMPANY_PROVIDERS: Dict[str, set] = {
        'TRAVEL': {
            'AAA', 'AAA Thủ Đức', 'Bảo Minh', 'Bảo Minh Bến Thành',
            'Bảo Việt', 'BHV', 'VBI', 'LIBERTY',
        },
        'VEHICLE': {
            'AAA', 'AAA Thủ Đức', 'Bảo Minh', 'Bảo Minh Bến Nghé',
            'Bảo Minh Bến Thành', 'Bảo Việt', 'BSH', 'DBV Nghệ An',
            'LIBERTY', 'MIC', 'PJICO', 'PTI', 'PVI Digital',
            'PVI Đồng Khởi', 'PVI Gia Định', 'Tasco', 'VNI',
        },

        'HEALTH': {
            'AAA', 'Bảo Minh', 'Bảo Minh Bến Nghé', 'Bảo Minh Bến Thành',
            'Bảo Việt', 'BHV', 'BSH', 'GIC', 'LIBERTY', 'MIC', 'OPES',
            'Pacific Cross', 'PCV', 'PTI', 'PVI', 'PVI Đồng Khởi',
            'PVI Gia Định', 'TCGI', 'VBI',
        },
        'MOTO': {
            'AAA', 'DBV Nghệ An', 'BSH', 'PVI Digital',
        },
        'MEDICAL_SOCIAL': {
            'PVI Digital',
        },
    }

    # Valid program names per insurance type (programName)
    # Subclasses override INSURANCE_TYPE_KEY to select the right set
    VALID_PROGRAM_NAMES: Dict[str, set] = {
        'TRAVEL': {
            'Bảo hiểm du lịch Trong nước',
            'Bảo hiểm người Việt Nam du lịch nước ngoài',
            'Bảo hiểm người nước ngoài du lịch Việt Nam',
            'Bảo hiểm du lịch Bảo Minh', 'Bảo hiểm du lịch Bảo Việt',
            'Bảo hiểm du lịch VBI', 'Bảo hiểm du lịch BHV',
            'Bảo hiểm du lịch Liberty', 'Bảo hiểm du lịch AAATD',
            'Bảo hiểm du lịch Nước ngoài',
        },
        'VEHICLE': {
            'BHVCOTO_AAATD',
            'Bảo hiểm Lái phụ xe và người ngồi trên xe ô tô, TNDS tự nguyện',
            'Bảo hiểm Trách nhiệm Dân sự ô tô', 'BHVCOTO_PVI',
            'BHVCOTO_PVI_GĐ', 'BHVCOTO_DBV Nghệ An_Xe taxi',
            'BHVCOTO_Bảo Minh', 'BHVCOTO_Bảo Minh Bến Nghé',
            'BHVCOTO_Bảo Việt', 'Bảo hiểm vật chất xe Ô tô',
            'BHVCOTO_BSH', 'Bảo hiểm Vật chất xe ô tô',
            'BHVCOTO_PJICO', 'BHVCOTO_PJICO dưới 600',
            'BHVCOTO_PJICO trên 800', 'BHVCOTO_PJICO từ 600 đến dưới 800',
            'BHVCOTO_PTI', 'BHVCOTO_PVI_Digital',
            'BHVCOTO_PVI_ĐK dưới 500', 'BHVCOTO_PVI_ĐK trên 1000',
            'BHVCOTO_PVI_ĐK từ 500 đến dưới 700',
            'BHVCOTO_PVI_ĐK từ 700 đến dưới 1000',
            'BHVCOTO_Bảo Minh Bến Thành', 'BHVCOTO_VNI',
            'Bảo hiểm Lái phụ xe và người ngồi trên xe ô tô, TNDS tự nguyện_Xe còn lại',
            'Bảo hiểm Lái phụ xe và người ngồi trên xe ô tô, TNDS tự nguyện_Ô tô dưới 16 chỗ, xe tải dưới 3 tấn',
            'Bảo hiểm Trách nhiệm Dân sự ô tô_Xe còn lại',
            'Bảo hiểm Trách nhiệm Dân sự ô tô_Ô tô dưới 16 chỗ, xe tải dưới 3 tấn',
            'BHVCOTO_PTI >= 500', 'BHVCOTO_PTI dưới 500',
            'BHVCOTO_Liberty', 'BHVCOTO_Liberty_new', 'BHVCOTO_Liberty_renew',
            'BHVCOTO_MIC', 'BHVCOTO_Tasco', 'BHVCOTO_DBV Nghệ An_Xe cơ giới khác',
        },

        'HEALTH': {
            'SKTA_renew', 'An Sinh Thịnh Vượng', 'BV_Cl10',
            'Bảo hiểm Tai nạn', 'Bảo hiểm sức khỏe doanh nghiệp',
            'B-One', 'B-One_new', 'B-One_renew',
            'Bestlife', 'Bestlife_new', 'Bestlife_renew',
            'SKNC_new', 'SKNC_renew', 'Tai nạn cá nhân GIC',
            'Foundation (Toàn Mỹ)_new', 'Foundation (Toàn Mỹ)_renew',
            'Health first_new', 'Health first_renew',
            'Health up_new', 'Health up_renew',
            'Master M1+', 'Master M2', 'Master M3',
            'An Gia Phát', 'Bảo hiểm An Gia Phát',
            'Bảo hiểm tai nạn cá nhân', 'Sức khỏe toàn diện cá nhân',
            'InsuStream_care_renew', 'InsuStream 100', 'Bảo hiểm y tế vượt trội',
            'Tận Tâm', 'Y Tế Vượt Trội',
            'Bảo hiểm du lịch Pacific Cross',
            'Master_new', 'Master_renew',
            'VBI Care nhỏ hơn 7 tuổi', 'VBI Care nhỏ từ 7 đến 50', 'VBI Care trên 50',
            'Bảo hiểm 37 bệnh/Tình trạng hiểm nghèo',
            'Chăm Sóc Học Sinh', 'Chăm Sóc Sinh Viên', 'Chăm Sóc Sinh Viên Sinh Viên',
            'BVAG', 'BVTB_new', 'BVTB_renew', 'BV_Intercare',
            'Bệnh hiểm nghèo', 'Medical Care',
            'Bảo Hiểm Ung Thư', 'Bảo hiểm bệnh hiểm nghèo',
            'Bảo hiểm tai nạn nhóm', 'Sức Khoẻ Toàn Diện',
            'SKTA', 'SKTA_new', 'Tai nạn 24/7',
            'MIC Care', 'InsuStream_care', 'InsuStream_care_new', 'Phúc An Sinh',
        },
        'MOTO': {
            'Bảo hiểm Lái xe, người ngồi trên xe máy',
            'Bảo hiểm Trách nhiệm Dân sự xe máy',
        },
        'MEDICAL_SOCIAL': {
            'BHXH 1 THÁNG_NEW', 'BHXH 1 THÁNG_RENEW',
            'BHXH 3 THÁNG_NEW', 'BHXH 3 THÁNG_RENEW',
            'BHXH 6 THÁNG_NEW', 'BHXH 6 THÁNG_RENEW',
            'BHXH 12 THÁNG_NEW', 'BHXH 12 THÁNG_RENEW',
            'BHYTHGD 3 THÁNG_NEW', 'BHYTHGD 3 THÁNG_RENEW',
            'BHYTHGD 6 THÁNG_NEW', 'BHYTHGD 6 THÁNG_RENEW',
            'BHYTHGD 12 THÁNG_NEW', 'BHYTHGD 12 THÁNG_RENEW',
        },
    }

    # ==================== COMMON FIELDS (All insurance types have these) ====================
    COMMON_DB_FIELDS = {
        # Contract info - REQUIRED for all types
        'contractId': str,           # Số hợp đồng / Số GCN / Mã tờ khai
        'majorName': str,            # Sản phẩm (loại BH)
        'companyProviderName': str,  # Đối tác nhà BH

        # Program & Sale
        'programName': str,          # Chương trình
        'saleId': str,               # Code sale / Tên sale
        'programCodeMiningChannel': str,  # Channel (programCodeMiningChannel in database)
        'termsFeePaymentMethod': str, # Hình thức thanh toán (text field)

        # Financial
        'feeInsurance': float,       # Phí bảo hiểm / Tổng phí

        # Metadata
        'modifiedAt': str,           # Ngày update / cập nhật
    }
    
    # Business keys for duplicate checking (4-key combination)
    # These are ALSO the required fields for validation
    BUSINESS_KEYS = ['contractId', 'peopleName', 'majorName', 'companyProviderName']
    
    # Required fields = Business Keys (same 4 fields)
    BASE_REQUIRED_FIELDS = ['contractId', 'peopleName', 'majorName', 'companyProviderName']
    
    def __init__(self):
        """Initialize mapping configuration"""
        self._column_mapping: Optional[Dict[str, str]] = None
        self._insurance_type: Optional[str] = None
    
    @property
    def column_mapping(self) -> Dict[str, str]:
        """Lazy load column mapping"""
        if self._column_mapping is None:
            self._column_mapping = self._build_column_mapping()
        return self._column_mapping
    
    @property
    def insurance_type(self) -> str:
        """Get insurance type identifier"""
        if self._insurance_type is None:
            self._insurance_type = self.get_insurance_type()
        return self._insurance_type
    
    def _build_column_mapping(self) -> Dict[str, str]:
        """
        Build complete column mapping by merging common and specific mappings
        
        Returns:
            Complete Excel column to database field mapping
        """
        mapping = {}
        mapping.update(self.get_common_column_mapping())
        mapping.update(self.get_specific_column_mapping())
        return mapping
    
    # ==================== ABSTRACT METHODS (Must be implemented) ====================
    
    @abstractmethod
    def get_insurance_type(self) -> str:
        """
        Get the insurance type identifier
        
        Returns:
            Insurance type string (TRAVEL, VEHICLE, MOTO, MEDICAL_SOCIAL, HEALTH)
        """
        pass
    
    @abstractmethod
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """
        Get Excel column to DB field mapping specific to this insurance type
        
        Returns:
            Dictionary mapping Excel columns (Vietnamese) to database fields
        """
        pass
    
    @abstractmethod
    def get_specific_fields(self) -> List[str]:
        """
        Get database fields specific to this insurance type
        
        Returns:
            List of field names specific to this type
        """
        pass
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """
        Get required fields for this insurance type
        
        Returns:
            List of required field names
        """
        pass
    
    # ==================== COMMON METHODS (Can be overridden) ====================
    
    def get_common_column_mapping(self) -> Dict[str, str]:
        """
        Get common column mappings shared by all insurance types
        Override this if your type has different Vietnamese headers for common fields

        Returns:
            Dictionary mapping common Excel columns to database fields
        """
        return {
            'Sản phẩm': 'programName',
            'Channel': 'programCodeMiningChannel',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
        }
    
    def get_name_field(self) -> str:
        """
        Get the field name used for the primary name source in Excel mapping.
        For VEHICLE/MOTO: returns 'payerName' (buyer = insured, will be
        mirrored to peopleName in transform_records for business key).
        For HEALTH/MEDICAL_SOCIAL/TRAVEL: can be overridden to 'peopleName'
        if peopleName is mapped directly from Excel.
        
        Returns:
            Field name for the primary name source
        """
        return 'payerName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        """
        Get filename keywords that identify this insurance type
        Used for auto-detection from filename
        
        Returns:
            List of keywords to match in filename (case-insensitive)
        """
        return []
    
    # ==================== UTILITY METHODS ====================
    
    def get_all_db_fields(self) -> List[str]:
        """
        Get all database fields for this insurance type
        
        Returns:
            List of all field names (common + specific)
        """
        common = list(self.COMMON_DB_FIELDS.keys())
        specific = self.get_specific_fields()
        return list(set(common + specific))
    
    def get_business_key_values(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract business key values from record for duplicate checking
        
        Args:
            record: Dictionary with database field names
            
        Returns:
            Dictionary with business key fields
        """
        return {
            'contractId': record.get('contractId'),
            'peopleName': record.get('peopleName'),
            'majorName': record.get('majorName'),
            'companyProviderName': record.get('companyProviderName')
        }
    
    def validate_required_fields(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that all required fields (4 business keys) are present and not empty

        Required fields (Business Keys):
        1. contractId
        2. name (or peopleName depending on insurance type)
        3. majorName
        4. companyProviderName

        Args:
            record: Dictionary with database field names

        Returns:
            Tuple of (is_valid, list_of_error_details)
            Each error detail is a dict with: field, excel_column, error_type, message
        """
        errors = []

        # Check non-name business key fields
        for field in ['contractId', 'majorName', 'companyProviderName']:
            value = record.get(field)
            excel_col = self._get_excel_column_for_field(field)

            if value is None:
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'MISSING',
                    'message': f"Thiếu dữ liệu tại cột '{excel_col}' (field: {field})",
                    'current_value': None
                })
            elif isinstance(value, str) and not value.strip():
                errors.append({
                    'field': field,
                    'excel_column': excel_col,
                    'error_type': 'EMPTY',
                    'message': f"Dữ liệu trống tại cột '{excel_col}' (field: {field})",
                    'current_value': value
                })

        # Check peopleName (business key - insured person name)
        people_name_value = record.get('peopleName')
        excel_col = self._get_excel_column_for_field('peopleName') or self._get_excel_column_for_field(self.get_name_field())

        if not people_name_value:
            errors.append({
                'field': 'peopleName',
                'excel_column': excel_col,
                'error_type': 'MISSING',
                'message': f"Thiếu tên người được bảo hiểm tại cột '{excel_col}'",
                'current_value': None
            })
        elif isinstance(people_name_value, str) and not people_name_value.strip():
            errors.append({
                'field': 'peopleName',
                'excel_column': excel_col,
                'error_type': 'EMPTY',
                'message': f"Tên người được bảo hiểm trống tại cột '{excel_col}'",
                'current_value': people_name_value
            })

        # NOTE: Only 4 business keys are required
        # Type-specific fields (dates, fees) are NOT required - they can be NULL

        return (len(errors) == 0, errors)

    def validate_channel_value(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that Channel (programCodeMiningChannel) value is valid

        Valid values: DSA, DSA/Renew, DSA_NEO, TSA, Renew, CTV_TSA (TSA 2),
                      CTV_TSA (TSA 2)/Renew, HO, Digital, Referral

        Args:
            record: Dictionary with database field names

        Returns:
            Tuple of (is_valid, list_of_error_details)
        """
        errors = []
        channel_value = record.get('programCodeMiningChannel')

        if channel_value is not None and channel_value.strip():
            # Channel has value, check if valid
            if channel_value not in self.VALID_CHANNELS:
                excel_col = self._get_excel_column_for_field('programCodeMiningChannel')
                valid_values_str = ', '.join(sorted(self.VALID_CHANNELS))
                errors.append({
                    'field': 'programCodeMiningChannel',
                    'excel_column': excel_col,
                    'error_type': 'INVALID_VALUE',
                    'message': f"Giá trị Channel không hợp lệ: '{channel_value}'. "
                               f"Các giá trị hợp lệ: {valid_values_str}",
                    'current_value': channel_value
                })

        return (len(errors) == 0, errors)

    def validate_payment_method(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that termsFeePaymentMethod is NOT NULL and belongs to the allowed enum.

        Valid values: OCB, Payoo, Bảo Kim, VietcomBank, Nhà bảo hiểm, Affina

        Args:
            record: Dictionary with database field names

        Returns:
            Tuple of (is_valid, list_of_error_details)
        """
        errors = []
        field = 'termsFeePaymentMethod'
        value = record.get(field)
        excel_col = self._get_excel_column_for_field(field)
        valid_values_str = ', '.join(sorted(self.VALID_PAYMENT_METHODS))

        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append({
                'field': field,
                'excel_column': excel_col,
                'error_type': 'MISSING',
                'message': f"Thiếu 'Hình thức thanh toán' (bắt buộc - NOT NULL). "
                           f"Các giá trị hợp lệ: {valid_values_str}",
                'current_value': value,
            })
        elif value not in self.VALID_PAYMENT_METHODS:
            errors.append({
                'field': field,
                'excel_column': excel_col,
                'error_type': 'INVALID_VALUE',
                'message': f"Hình thức thanh toán không hợp lệ: '{value}'. "
                           f"Các giá trị hợp lệ: {valid_values_str}",
                'current_value': value,
            })

        return (len(errors) == 0, errors)

    def validate_company_provider(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that companyProviderName belongs to the allowed enum for this insurance type.

        Args:
            record: Dictionary with database field names

        Returns:
            Tuple of (is_valid, list_of_error_details)
        """
        errors = []
        field = 'companyProviderName'
        value = record.get(field)
        excel_col = self._get_excel_column_for_field(field)
        valid_set = self.VALID_COMPANY_PROVIDERS.get(self.insurance_type, set())

        if not valid_set:
            # No enum defined for this type → skip
            return (True, [])

        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append({
                'field': field,
                'excel_column': excel_col,
                'error_type': 'MISSING',
                'message': f"Thiếu 'Nhà cung cấp bảo hiểm' (bắt buộc - NOT NULL).",
                'current_value': value,
            })
        elif value not in valid_set:
            valid_values_str = ', '.join(sorted(valid_set))
            errors.append({
                'field': field,
                'excel_column': excel_col,
                'error_type': 'INVALID_VALUE',
                'message': f"Nhà cung cấp bảo hiểm không hợp lệ: '{value}'. "
                           f"Các giá trị hợp lệ: {valid_values_str}",
                'current_value': value,
            })

        return (len(errors) == 0, errors)

    def validate_program_name(self, record: Dict[str, Any]) -> tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that programName belongs to the allowed enum for this insurance type.

        Args:
            record: Dictionary with database field names

        Returns:
            Tuple of (is_valid, list_of_error_details)
        """
        errors = []
        field = 'programName'
        value = record.get(field)
        excel_col = self._get_excel_column_for_field(field)
        valid_set = self.VALID_PROGRAM_NAMES.get(self.insurance_type, set())

        if not valid_set:
            # No enum defined for this type → skip
            return (True, [])

        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append({
                'field': field,
                'excel_column': excel_col,
                'error_type': 'MISSING',
                'message': f"Thiếu 'Sản phẩm' (bắt buộc - NOT NULL).",
                'current_value': value,
            })
        elif value not in valid_set:
            valid_values_str = ', '.join(sorted(valid_set))
            errors.append({
                'field': field,
                'excel_column': excel_col,
                'error_type': 'INVALID_VALUE',
                'message': f"Sản phẩm không hợp lệ: '{value}'. "
                           f"Các giá trị hợp lệ: {valid_values_str}",
                'current_value': value,
            })

        return (len(errors) == 0, errors)
    
    def _get_excel_column_for_field(self, db_field: str) -> str:
        """
        Reverse lookup: get Excel column name from database field name
        
        Args:
            db_field: Database field name
            
        Returns:
            Excel column name or db_field if not found
        """
        for excel_col, field in self.column_mapping.items():
            if field == db_field:
                return excel_col.replace('\n', ' ')  # Clean multiline headers
        return db_field
    
    def get_field_display_name(self, db_field: str) -> str:
        """
        Get human-readable display name for a database field (Vietnamese)
        
        Args:
            db_field: Database field name
            
        Returns:
            Vietnamese display name
        """
        display_names = {
            'contractId': 'Số hợp đồng/Số GCN/Mã tờ khai',
            'name': 'Họ và tên người được BH',
            'peopleName': 'Tên khách hàng/Họ tên NĐBH',
            'majorName': 'Sản phẩm (Loại BH)',
            'companyProviderName': 'Đối tác nhà bảo hiểm',
            'startDateJourney': 'Ngày đi',
            'endDateJourney': 'Ngày về',
            'contractObjectStartDate': 'Ngày bắt đầu hiệu lực',
            'contractObjectEndDate': 'Ngày kết thúc hiệu lực',
            'contractStartDate': 'Ngày hiệu lực',
            'contractEndDate': 'Ngày kết thúc',
            'feeInsurance': 'Phí bảo hiểm',
            'feeMainBenefit': 'Phí bảo hiểm chính',
        }
        return display_names.get(db_field, db_field)
    
    def map_excel_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a single Excel row to database fields
        
        Args:
            row: Dictionary with Excel column names as keys
            
        Returns:
            Dictionary with database field names as keys
        """
        mapped_row = {}
        
        for excel_col, db_field in self.column_mapping.items():
            if excel_col in row:
                value = row[excel_col]
                # Clean string values
                if isinstance(value, str):
                    value = value.strip() if value else None
                mapped_row[db_field] = value
        
        # Add insurance type
        mapped_row['insuranceType'] = self.insurance_type
        
        # Ensure 'name' field exists
        if 'name' not in mapped_row or not mapped_row.get('name'):
            name_field = self.get_name_field()
            if name_field in mapped_row:
                mapped_row['name'] = mapped_row[name_field]
        
        return mapped_row
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.insurance_type})"

