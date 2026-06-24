# Excel Column Mapping Configuration
# Maps Excel column headers (Vietnamese) to database fields

# ==============================================================================
# TRAVEL (Du lịch) - Travel.xlsx
# ==============================================================================
TRAVEL_MAPPING = {
    # Excel Column → Database Field
    'Ngày': 'upload_date',  # Metadata
    'STT': 'row_number',  # Metadata
    
    # Insured Person Info
    'Họ Và Tên': 'name',
    'Ngày sinh': 'dob',
    'CCCD/CMND/Paspost ID': 'license',
    
    # Journey Info
    'Ngày thanh toán': 'payment_date',
    'Ngày đi': 'startDateJourney',
    'Ngày về': 'endDateJourney',
    'Số ngày': 'journey_days',
    'Nơi đến': 'destination_text',  # Need mapping to destination enum
    'Phạm vi': 'domesticOrInternational_text',
    
    # Program Info
    'Gói tham gia': 'packageName',
    'Plan tham gia': 'programName',
    'Phí bảo hiểm': 'feeInsurance',
    
    # Payer Info
    'Họ tên người mua': 'payerName',
    'Ngày sinh.1': 'payerDob',
    'CCCD/CMND/Paspost ID người mua': 'payerLicense',
    'Số Điện thoại NMBH': 'payerPhone',
    
    # Contract Info
    'Số hợp đồng': 'contractId',
    'Tên sale': 'saleId',
    'Đối tác nhà BH': 'companyProviderName',
    'Channel': 'channelId',
    'Hình thức thanh toán': 'termsFeePaymentMethod',
    'Sản phẩm': 'majorName',  # Loại BH
}

# ==============================================================================
# VEHICLE (Ô tô) - Vehicle.xlsx
# ==============================================================================
VEHICLE_MAPPING = {
    ' ': 'modifiedAt',  # First column (blank header)
    'STT': 'row_number',
    
    # Owner Info
    'Tên khách hàng': 'peopleName',
    'Số điện thoại': 'peoplePhone',
    'email': 'peopleEmail',
    'địa chỉ': 'peopleAddress',
    
    # Vehicle Info
    'Biển số': 'licensePlate',
    'Số Khung': 'chassisNumber',
    'Số Máy': 'engineNumber',
    'Trọng tải đối với xe tải': 'weight',
    'Số chỗ ngồi': 'seatNumber',
    'Loại xe': 'vehicleType',
    'Hiệu xe': 'brand',
    'Giá trị xe': 'vehicleValue',
    'Mục đích sử dụng': 'usagePurpose',
    'Năm SX': 'manufactureYear',
    
    # Contract Info
    'Ngày thanh toán': 'payment_date',
    'Giờ bắt đầu': 'start_time',
    'Ngày bắt đầu hiệu lực': 'contractObjectStartDate',
    'Giờ kết thúc': 'end_time',
    'Ngày kết thúc hiệu lực': 'contractObjectEndDate',
    'Số ngày bảo hiểm': 'insurance_days',
    'Số GCN': 'contractId',  # Số giấy chứng nhận = Mã hợp đồng
    'Số tiền': 'feeInsurance',
    
    # Program Info
    'Code sale': 'saleId',
    'Chương trình': 'programName',
    'Hình thức thanh toán': 'termsFeePaymentMethod',
    'Đối tác nhà bảo hiểm': 'companyProviderName',
    'Sản phẩm': 'majorName',  # NOTE: có 2 columns "Sản phẩm" và "Sản Phẩm"
    'Sản Phẩm': 'productName_2',
    'Channel': 'channelId',
    'Note': 'note',
}

# ==============================================================================
# MOTO (Xe máy) - Moto.xlsx
# ==============================================================================
MOTO_MAPPING = {
    'Ngày update': 'modifiedAt',
    'STT': 'row_number',
    
    # Vehicle Info
    'BIỂN SỐ XE': 'licensePlates',
    'SỐ KHUNG': 'chassisNumber',
    'SỐ MÁY': 'engineNumber',
    'LOẠI XE': 'type',
    'NHÃN HIỆU XE': 'maker',
    
    # Owner Info
    'TÊN KHÁCH HÀNG': 'name',
    'SỐ ĐIẸN THOẠI': 'phone',
    'Email': 'email',
    
    # Fee Info
    'PHÍ BẢO HIỂM TNDS BẮT BUỘC': 'feeMainBenefit',
    'PHÍ BẢO HIỂM TAI NẠN NNTX': 'feeSideBenefit',
    'TỔNG PHÍ BẢO HIỂM': 'feeInsurance',
    'SỐ NĂM': 'contractPeriodValue',
    
    # Contract Info
    'NGÀY CẤP ĐƠN': 'issue_date',
    'NGÀY BẮT ĐẦU': 'contractObjectStartDate',
    'NGÀY KẾT THÚC': 'contractObjectEndDate',
    'Số hợp đồng': 'contractId',
    
    # Program Info
    'Chương trình': 'programName',
    'Code sale': 'saleId',
    'Hình thức thanh toán': 'termsFeePaymentMethod',
    'Đối tác nhà bảo hiểm': 'companyProviderName',
    'Sản phẩm': 'majorName',
    'Channel': 'channelId',
}

# ==============================================================================
# MEDICAL & SOCIAL (BHYT & BHXH) - Medical-Social.xlsx
# ==============================================================================
MEDICAL_SOCIAL_MAPPING = {
    'Ngày update': 'modifiedAt',
    'STT': 'row_number',
    
    # Insured Person Info
    'Họ tên NĐBH': 'peopleName',
    'Ngày sinh': 'peopleDob',
    'Giới tính': 'peopleGender',
    'CCCD': 'peopleLicense',
    'Địa chỉ': 'peopleAddress',
    'SĐT': 'peoplePhone',
    'Email': 'peopleEmail',
    
    # Payer Info (Bên mua BH)
    'Họ tên BMBH': 'payerName',
    'Ngày sinh.1': 'payerDob',
    'CCCD.1': 'payerLicense',
    'Mối quan hệ với NĐBH': 'peopleRelationship',
    'Địa chỉ.1': 'payerAddress',
    'SĐT ': 'payerPhone',  # Note: có space sau SĐT
    'Email.1': 'payerEmail',
    
    # Insurance Info
    'Mã tờ khai': 'contractId',  # Mã tờ khai = Mã hợp đồng
    'Mã BHXH': 'socialId',
    'Loại sản phẩm': 'insuranceType_text',  # IMPORTANT: Phân biệt SOCIAL vs MEDICAL
    'Phương án KH': 'packageName',
    'Phí Bảo hiểm': 'feeInsurance',
    
    # Contract Info
    'Ngày thanh toán': 'payment_date',
    # 'Thời hạn BH': 'contractPeriod',  # Skip - text format "12 tháng", schema needs INT
    'Ngày bắt đầu': 'contractObjectStartDate',
    'Ngày kết thúc': 'contractObjectEndDate',
    'Ngày duyệt': 'approval_date',
    'Ngày hoàn phí': 'refund_date',
    'Trạng thái': 'contractStatus_text',
    
    # Program Info
    'Code sales': 'saleId',
    'Phone Khách hàng': 'customerPhone',
    'Tên liên hệ': 'contactName',
    # 'Hình thức thanh toán': 'paymentMethod',  # Skip - text "OCB", schema needs INT
    'Đối tác NBH': 'companyProviderName',
    'Sản phẩm (cũ_có ràng dữ liệu)': 'productName_old',
    'Sản phẩm': 'majorName',
    'Channel': 'channelId',
    'Phương án thù lao': 'remunerationType_text',
}

# ==============================================================================
# HEALTH (Sức khỏe) - Health.xlsx
# ==============================================================================
HEALTH_MAPPING = {
    'Ngày cập nhật': 'modifiedAt',
    'STT': 'row_number',
    
    # Insured Person Info
    'Thông tin \nNgười được bảo hiểm': 'peopleName',
    'Ngày tháng\nnăm sinh': 'peopleDob',
    'Giới tính': 'peopleGender',
    'Email': 'peopleEmail',
    'Passport': 'passport',
    'CCCD': 'peopleLicense',
    'Địa chỉ liên hệ': 'peopleAddress',
    
    # Payer Info (Bên mua BH)
    'Thông tin \nBên mua bảo hiểm': 'payerName',
    'Mối quan hệ\nđối với NĐBH': 'peopleRelationship',
    'Ngày tháng\nnăm sinh.1': 'payerDob',
    'CCCD/Passport': 'payerLicense',
    'Số điện thoại': 'payerPhone',
    'Địa chỉ liên hệ.1': 'payerAddress',
    'Email.1': 'payerEmail',
    
    # Program Info
    'Chương trình\nbảo hiểm': 'programName',
    'Ngoại trú': 'outpatient_benefit',
    'Nha khoa': 'dental_benefit',
    'Thai sản': 'maternity_benefit',
    'Top-up': 'topup_benefit',
    'Phí bảo hiểm': 'feeInsurance',
    'Phí điều chỉnh': 'feeAdjustment',
    'Số tiền\nthanh toán': 'amountPay',
    
    # Contract Info
    'Ngày thanh toán': 'payment_date',
    'Ngày hiệu lực': 'contractStartDate',
    'Ngày kết thúc': 'contractEndDate',
    'Số GCNBH': 'certificateNumberProvider',
    'Số hợp đồng': 'contractId',
    
    # Invoice Info
    'Thông tin xuất hóa đơn': 'invoiceInfo',
    
    # Contact Info
    'Phone trên lead': 'leadPhone',
    'Code sale': 'saleId',
    'Phone\nKhách hàng': 'customerPhone',
    'Tên liên hệ': 'contactName',
    'NOTE': 'note',
    
    # Program Info
    'Hình thức \nthanh toán': 'termsFeePaymentMethod',
    'Nhà bảo hiểm': 'companyProviderName',
    'Sản phẩm': 'majorName',
    'Channel': 'channelId',
}



# ==============================================================================
# INSURANCE TYPE AUTO-DETECTION
# ==============================================================================
INSURANCE_TYPE_BY_FILENAME = {
    'travel': 'TRAVEL',
    'vehicle': 'VEHICLE',
    'moto': 'MOTO',
    'medical-social': None,  # Need to detect from column value
    'health': 'HEALTH',
    # NOTE: HOUSE là online CDC, không có Excel file
}

# Insurance types list for validation
INSURANCE_TYPES = [
    'TRAVEL',    # Du lịch - Offline Excel
    'VEHICLE',   # Ô tô - Offline Excel
    'MOTO',      # Xe máy - Offline Excel
    'SOCIAL',    # BHXH - Offline Excel
    'MEDICAL',   # BHYT - Offline Excel
    'HEALTH',    # Sức khỏe - Offline Excel
    'HOUSE',     # Nhà ở - Online CDC (không có Excel)
]

# For Medical-Social file, detect from "Loại sản phẩm" column
INSURANCE_TYPE_KEYWORDS = {
    'SOCIAL': ['bhxh', 'bảo hiểm xã hội', 'xã hội'],
    'MEDICAL': ['bhyt', 'bảo hiểm y tế', 'y tế'],
}

# ==============================================================================
# BUSINESS KEY FIELDS (for deduplication & required validation)
# Business key = 7 fields dùng để:
#   1. Kiểm soát required fields (validation)
#   2. Kiểm soát duplicate (deduplication)
# Aligned with Portal: contractId + name + majorName + companyProviderName
#                      + startDate + endDate + feeInsurance
# ==============================================================================
# ==============================================================================
BUSINESS_KEY_FIELDS = {
    # Offline Excel insurance types
    'TRAVEL': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
               'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    'VEHICLE': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
                'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    'MOTO': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
             'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    'SOCIAL': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
               'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    'MEDICAL': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
                'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    'BHYT/BHXH': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
                  'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    'HEALTH': ['contractId', 'peopleName', 'majorName', 'companyProviderName',
               'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
    # Online CDC insurance types
    'HOUSE': ['contractObjectId', 'peopleName', 'majorName', 'companyProviderName',
              'contractObjectStartDate', 'contractObjectEndDate', 'feeInsurance'],
}

# ==============================================================================
# REQUIRED FIELDS FOR VALIDATION
# Required fields = first 4 business key fields (backwards compatible)
# ==============================================================================
REQUIRED_FIELDS = {
    k: v[:4] for k, v in BUSINESS_KEY_FIELDS.items()
}

# ==============================================================================
# TABLE MAPPING (Staging table names)
# ==============================================================================
STAGING_TABLE_MAPPING = {
    # Offline Excel -> stgInsuranceContractObjectOffline (wide table)
    'TRAVEL': 'stgInsuranceContractObjectOffline',
    'VEHICLE': 'stgInsuranceContractObjectOffline',
    'MOTO': 'stgInsuranceContractObjectOffline',
    'SOCIAL': 'stgInsuranceContractObjectOffline',
    'MEDICAL': 'stgInsuranceContractObjectOffline',
    'HEALTH': 'stgInsuranceContractObjectOffline',
    # House Online CDC -> dedicated staging table (CDC consumer uses this)
    'HOUSE': 'stgInsuranceContractObjectHouse',
}

# ==============================================================================
# PRIMARY KEY FIELD MAPPING
# ==============================================================================
PRIMARY_KEY_FIELD = {
    # Offline types use contractId as PK (no contractObjectId in Excel)
    'TRAVEL': 'contractObjectId',  # Generated UUID
    'VEHICLE': 'contractObjectId',  # Generated UUID
    'MOTO': 'contractObjectId',  # Generated UUID
    'SOCIAL': 'contractObjectId',  # Generated UUID
    'MEDICAL': 'contractObjectId',  # Generated UUID
    'HEALTH': 'contractObjectId',  # Generated UUID
    
    # Hazard uses contractId as PK (from Excel)
    # House uses contractObjectId as PK (from CDC source id)
    'HOUSE': 'contractObjectId',
}

# ==============================================================================
# NOTE: Business keys = 7 fields (aligned with Portal)
# Required fields = first 4 business key fields (backwards compatible)
# ==============================================================================

