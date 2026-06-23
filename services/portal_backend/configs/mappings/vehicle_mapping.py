"""
Vehicle insurance mapping configuration
Inherits from BaseInsuranceMapping
"""
from typing import Dict, List
from configs.mappings.base_mapping import BaseInsuranceMapping


class VehicleMapping(BaseInsuranceMapping):
    """
    Vehicle Insurance (Ô tô) - Vehicle.xlsx
    
    Specific characteristics:
    - Has vehicle information (license plate, chassis, engine numbers)
    - Uses 'peopleName' instead of 'name'
    - Has contract object dates
    """
    
    def get_insurance_type(self) -> str:
        return "VEHICLE"
    
    def get_common_column_mapping(self) -> Dict[str, str]:
        """Override common mapping for Vehicle-specific Vietnamese headers"""
        return {
            ' ': 'modifiedAt',  # First column (blank header)
            'Sản phẩm': 'programName',
            'Sản Phẩm': 'productName_2',  # Note: có 2 columns
            'Số GCN': 'contractId',
            'Đối tác nhà bảo hiểm': 'companyProviderName',
            'Code sale': 'saleId',
            'Chương trình': 'programName',
            'Channel': 'programCodeMiningChannel',
            'Hình thức thanh toán': 'termsFeePaymentMethod',
            'Số tiền': 'feeInsurance',
        }
    
    def get_specific_column_mapping(self) -> Dict[str, str]:
        """Vehicle-specific Excel column mapping"""
        return {
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
            
            # Note
            'Note': 'note',
        }
    
    def get_specific_fields(self) -> List[str]:
        """Fields specific to vehicle insurance"""
        return [
            'peopleName', 'peoplePhone', 'peopleEmail', 'peopleAddress',
            'licensePlate', 'chassisNumber', 'engineNumber',
            'weight', 'seatNumber', 'vehicleType', 'brand',
            'vehicleValue', 'usagePurpose', 'manufactureYear',
            'contractObjectStartDate', 'contractObjectEndDate',
            'start_time', 'end_time', 'insurance_days',
            'payment_date', 'note', 'productName_2',
        ]
    
    def get_required_fields(self) -> List[str]:
        """Required fields for vehicle insurance validation
        
        NOTE: Only 4 business keys are truly required:
        - contractId, name (peopleName), majorName, companyProviderName
        Other fields like dates, fees are optional (can be NULL)
        """
        return []  # All required validation is done via business keys
    
    def get_name_field(self) -> str:
        """Vehicle uses 'peopleName' for owner"""
        return 'peopleName'
    
    @classmethod
    def get_file_keywords(cls) -> List[str]:
        return ["vehicle", "oto", "xe oto", "o to", "xe_oto"]
