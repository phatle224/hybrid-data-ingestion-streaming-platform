#!/usr/bin/env python3
"""
Profiling Streaming Consumer - CDC Stream → profiling_analysis on PostgreSQL
=============================================================================
Build profiling_analysis table from staging CDC events (real-time).

Architecture:
    Debezium → Kafka → This Consumer → PostgreSQL profiling_analysis

Replaces trigger-based approach with streaming consumer.

Inherits BaseKafkaConsumer for standardized lifecycle.
Uses shared DebeziumTransformer for message parsing.
"""
import os
import sys
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal

from shared.logger import create_logger, configure_shared_loggers
from shared.configs import PostgreSQLConfig, KafkaConfig
from shared.connections import PostgreSQLConnectionManager
from shared.debezium import DebeziumTransformer
from shared.query_builder import SQLQueryBuilder
from shared.base_consumer import BaseKafkaConsumer


# =============================================================================
# Domain Constants (profiling-specific business rules)
# =============================================================================

CITY_CODE_MAP = {
    1: 'Thành phố Hà Nội', 2: 'Tỉnh Hà Giang', 4: 'Tỉnh Cao Bằng',
    6: 'Tỉnh Bắc Kạn', 8: 'Tỉnh Tuyên Quang', 10: 'Tỉnh Lào Cai',
    11: 'Tỉnh Điện Biên', 12: 'Tỉnh Lai Châu', 14: 'Tỉnh Sơn La',
    15: 'Tỉnh Yên Bái', 17: 'Tỉnh Hoà Bình', 19: 'Tỉnh Thái Nguyên',
    20: 'Tỉnh Lạng Sơn', 22: 'Tỉnh Quảng Ninh', 24: 'Tỉnh Bắc Giang',
    25: 'Tỉnh Phú Thọ', 26: 'Tỉnh Vĩnh Phúc', 27: 'Tỉnh Bắc Ninh',
    30: 'Tỉnh Hải Dương', 31: 'Thành phố Hải Phòng', 33: 'Tỉnh Hưng Yên',
    34: 'Tỉnh Thái Bình', 35: 'Tỉnh Hà Nam', 36: 'Tỉnh Nam Định',
    37: 'Tỉnh Ninh Bình', 38: 'Tỉnh Thanh Hoá', 40: 'Tỉnh Nghệ An',
    42: 'Tỉnh Hà Tĩnh', 44: 'Tỉnh Quảng Bình', 45: 'Tỉnh Quảng Trị',
    46: 'Tỉnh Thừa Thiên Huế', 48: 'Thành phố Đà Nẵng', 49: 'Tỉnh Quảng Nam',
    51: 'Tỉnh Quảng Ngãi', 52: 'Tỉnh Bình Định', 54: 'Tỉnh Phú Yên',
    56: 'Tỉnh Khánh Hoà', 58: 'Tỉnh Ninh Thuận', 60: 'Tỉnh Bình Thuận',
    62: 'Tỉnh Kon Tum', 64: 'Tỉnh Gia Lai', 66: 'Tỉnh Đắk Lắk',
    67: 'Tỉnh Đắk Nông', 68: 'Tỉnh Lâm Đồng', 70: 'Tỉnh Bình Phước',
    72: 'Tỉnh Tây Ninh', 74: 'Tỉnh Bình Dương', 75: 'Tỉnh Đồng Nai',
    77: 'Tỉnh Bà Rịa - Vũng Tàu', 79: 'Thành phố Hồ Chí Minh',
    80: 'Tỉnh Long An', 82: 'Tỉnh Tiền Giang', 83: 'Tỉnh Bến Tre',
    84: 'Tỉnh Trà Vinh', 86: 'Tỉnh Vĩnh Long', 87: 'Tỉnh Đồng Tháp',
    89: 'Tỉnh An Giang', 91: 'Tỉnh Kiên Giang', 92: 'Thành phố Cần Thơ',
    93: 'Tỉnh Hậu Giang', 94: 'Tỉnh Sóc Trăng', 95: 'Tỉnh Bạc Liêu',
    96: 'Tỉnh Cà Mau',
}

RELATIONSHIP_MAP = {
    0: 'Bản thân', 1: 'Bố/Mẹ đẻ', 2: 'Vợ/Chồng',
    3: 'Anh/Chị/Em ruột', 4: 'Con đẻ/nuôi hợp pháp',
    5: 'Khác', 6: 'Bố/Mẹ của vợ/chồng',
}


# =============================================================================
# Diagnostic Classifier (domain-specific business logic)
# =============================================================================

class DiagnosticClassifier:
    """Classifies medical diagnostic text into predefined categories."""

    CATEGORIES = [
        ('Thai sản', ['thai', 'sản khoa', 'chửa ngoài tử cung']),
        ('Nha khoa', ['răng', 'nướu', 'nha chu', 'lợi', 'chỉnh nha']),
        ('Mắt', ['mắt', 'kết mạc', 'thủy tinh thể', 'thị lực', 'cận thị',
                  'loạn thị', 'viễn thị', 'quáng gà', 'lé']),
        ('Tai Mũi Họng', ['tai', 'họng', 'mũi', 'xoang', 'amydan',
                          'thanh quản', 'lẹo', 'chắp']),
        ('Thận/Tiết niệu', ['thận', 'tiết niệu', 'bàng quang']),
        ('Chấn thương/Tai nạn', ['chấn thương', 'tai nạn', 'vết thương', 'gãy',
                                  'bong gân', 'trật khớp', 'chật khớp', 'rách',
                                  'bỏng', 'ngộ độc', 'đả thương', 'cắn', 'đốt',
                                  'tổn thương']),
        ('Nội tiết/Chuyển hóa', ['tiểu đường', 'đái tháo đường', 'huyết áp',
                                  'chuyển hoá', 'lipid', 'axit uric', 'gout',
                                  'tuyến giáp']),
        ('Tim mạch', ['tim', 'mạch vành', 'đau thắt ngực', 'xơ vữa',
                       'nhồi máu não']),
        ('Hô hấp', ['phổi', 'phế quản', 'hen', 'suyễn', 'cảm', 'ho', 'covid']),
        ('Tiêu hóa', ['dạ dày', 'tiêu hóa', 'ruột', 'mật', 'gan', 'tụy',
                       'đại tràng', 'polyp', 'táo bón', 'tiêu chảy', 'trĩ',
                       'trào ngược']),
        ('Cơ xương khớp', ['xương', 'khớp', 'lưng', 'cột sống', 'gút',
                            'vai gáy', 'cơ', 'dây chằng']),
        ('Da liễu', ['da', 'mày đay', 'dị ứng', 'mụn', 'chàm', 'lang ben',
                      'nang lông', 'vảy nến', 'zona']),
        ('Nhiễm trùng', ['nhiễm', 'sốt', 'lao', 'cúm', 'sởi', 'thủy đậu',
                          'quai bị', 'virus', 'vi khuẩn', 'ký sinh trùng', 'nấm']),
        ('Thần kinh', ['thần kinh', 'đau đầu', 'mất ngủ', 'lo âu', 'trầm cảm',
                        'đột quỵ', 'tiền đình', 'nội sọ', 'động kinh',
                        'parkinson', 'alzheimer']),
        ('Khám tổng quát', ['tổng quát', 'kiểm tra', 'tầm soát']),
    ]

    @classmethod
    def classify(cls, diagnostic: str) -> str:
        """Classify diagnostic text into category."""
        if not diagnostic:
            return 'Khác'
        text = diagnostic.lower()
        for category, keywords in cls.CATEGORIES:
            if any(kw in text for kw in keywords):
                return category
        return 'Khác'


# =============================================================================
# Age Group Calculator
# =============================================================================

class AgeGroupCalculator:
    """Calculate age and age group from date of birth."""

    GROUPS = [
        (0, 6, '0-6'),
        (7, 17, '7-17'),
        (18, 35, '18-35'),
        (36, 55, '36-55'),
        (56, 999, '56+'),
    ]

    @classmethod
    def get_age(cls, dob: date) -> Optional[int]:
        if not dob:
            return None
        return (datetime.now().date() - dob).days // 365

    @classmethod
    def get_group(cls, dob: date) -> str:
        age = cls.get_age(dob)
        if age is None:
            return 'Unknown'
        for low, high, label in cls.GROUPS:
            if low <= age <= high:
                return label
        return 'Unknown'


# =============================================================================
# Profiling Record Builder (encapsulates record-building logic)
# =============================================================================

class ProfilingRecordBuilder:
    """Builds profiling_analysis records from claim + contract + contract_object data."""

    @classmethod
    def build(
        cls,
        claim_data: Dict[str, Any],
        contract_info: Dict[str, Any],
        contract_object_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a complete profiling_analysis record."""
        people_dob = DebeziumTransformer.to_date(contract_object_info.get('peopleDob'))
        contract_start_date = DebeziumTransformer.to_date(contract_info.get('contractStartDate'))

        created_at = DebeziumTransformer.to_datetime(claim_data.get('createdAt'))
        claim_start_date = created_at.date() if created_at else None

        hospitalized_date = DebeziumTransformer.to_date(claim_data.get('hospitalizedDate'))
        hospital_discharge_date = DebeziumTransformer.to_date(
            claim_data.get('hospitalDischargeDate')
        )

        age = AgeGroupCalculator.get_age(people_dob)
        age_group = AgeGroupCalculator.get_group(people_dob)

        days_from_contract_to_claim = None
        if contract_start_date and claim_start_date:
            days_from_contract_to_claim = (claim_start_date - contract_start_date).days

        amount_claim = cls._to_float(claim_data.get('amountClaim', 0))
        compensation_amount = cls._to_float(claim_data.get('compensationAmount', 0))
        compensation_rate = (
            (compensation_amount / amount_claim * 100) if amount_claim > 0 else 0
        )

        relationship_name = RELATIONSHIP_MAP.get(
            contract_object_info.get('peopleRelationship'), 'Khác'
        )
        city = CITY_CODE_MAP.get(
            contract_object_info.get('peopleCityCode'), 'Khác'
        )

        diagnostic = claim_data.get('diagnostic', '')
        common_diagnostic_category = DiagnosticClassifier.classify(diagnostic)

        return {
            'id': claim_data.get('id'),
            'contractId': claim_data.get('contractId'),
            'contractObjectId': claim_data.get('contractObjectId'),
            'amountClaim': amount_claim,
            'compensationAmount': compensation_amount,
            'compensationRate': compensation_rate,
            'hospitalizedDate': hospitalized_date,
            'clinics': claim_data.get('placeOfTreatment'),
            'contractStartDate': contract_start_date,
            'claimStartDate': claim_start_date,
            'claimMonth': claim_start_date.month if claim_start_date else None,
            'claimYear': claim_start_date.year if claim_start_date else None,
            'age_group': age_group,
            'relationshipName': relationship_name,
            'age': age,
            'gender': contract_object_info.get('peopleGender'),
            'city': city,
            'treatmentType': claim_data.get('treatmentType'),
            'diagnostic': diagnostic,
            'common_diagnostic_category': common_diagnostic_category,
            'days_from_contract_to_claim': days_from_contract_to_claim,
            'hospitalDischargeDate': hospital_discharge_date,
            'customerType': contract_info.get('customerType'),
            'tpaId': claim_data.get('tpaId'),
            'name': contract_object_info.get('peopleName'),
            'phone': contract_object_info.get('peoplePhone'),
            'email': contract_object_info.get('peopleEmail'),
            'address': contract_object_info.get('peopleAddress'),
            'comp_prog_id': contract_object_info.get('programId'),
            'comp_prog_name': contract_object_info.get('programName'),
        }

    @classmethod
    def _to_float(cls, value) -> float:
        try:
            return float(value) if value else 0
        except (ValueError, TypeError):
            return 0


# =============================================================================
# Profiling Consumer
# =============================================================================

class ProfilingConsumer(BaseKafkaConsumer):
    """
    Streaming Consumer for profiling_analysis on PostgreSQL.

    Processes CDC events from stgInsuranceClaim, stgInsuranceContract, stgInsuranceContractObject*
    to build and maintain the profiling_analysis table in real-time.

    Replaces database triggers with event-driven processing.
    """

    def __init__(self):
        # ── Configuration ────────────────────────────────────
        topic_prefix = os.getenv('TOPIC_PREFIX', 'staging')

        self._topics = [
            f'{topic_prefix}.stgInsuranceClaim',
            f'{topic_prefix}.stgInsuranceContract',
            f'{topic_prefix}.stgInsuranceContractObject',
            f'{topic_prefix}.stgInsuranceContractObjectVehicle',
            f'{topic_prefix}.stgInsuranceContractObjectMoto',
            f'{topic_prefix}.stgInsuranceContractObjectTravel',
            f'{topic_prefix}.stgInsuranceContractObjectSocialInsurance',
            f'{topic_prefix}.stgInsuranceContractObjectMedicalInsurance',
            f'{topic_prefix}.stgInsuranceContractObjectHouse',
        ]

        self._staging_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()
        self._reporting_config = PostgreSQLConfig(database_env='DB_DATABASE').get_config()

        self._kafka_config = KafkaConfig(
            group_id=os.getenv('CONSUMER_GROUP', 'profiling-consumer-v1'),
        ).get_config()

        # Logger
        log_file = '/app/logs/profiling_consumer.log' if os.path.exists('/app') else './profiling_consumer.log'
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        _logger = create_logger('ProfilingConsumer', log_file)
        configure_shared_loggers(log_file)
        super().__init__('Profiling Consumer', _logger)

        # ── Connections ──────────────────────────────────────
        self._staging_db = PostgreSQLConnectionManager(self._staging_config, 'staging')
        self._reporting_db = PostgreSQLConnectionManager(self._reporting_config, 'reporting')

    # ─── BaseKafkaConsumer Implementation ────────────────────

    def _get_topics(self) -> List[str]:
        return self._topics

    def _get_kafka_config(self) -> Dict[str, Any]:
        return self._kafka_config

    def _setup_connections(self) -> bool:
        if not self._staging_db.connect():
            return False
        if not self._reporting_db.connect():
            return False
        return True

    def _cleanup_connections(self):
        self._staging_db.close()
        self._reporting_db.close()

    def _init_stats(self):
        stats = super()._init_stats()
        stats.update({
            'claim_events': 0,
            'contract_events': 0,
            'contract_object_events': 0,
            'inserts': 0,
            'updates': 0,
            'deletes': 0,
            'skipped': 0,
        })
        return stats

    def _print_custom_stats(self):
        self.logger.info("Claim events: %d", self._stats['claim_events'])
        self.logger.info("Contract events: %d", self._stats['contract_events'])
        self.logger.info("Contract Object events: %d", self._stats['contract_object_events'])
        self.logger.info("Inserts: %d", self._stats['inserts'])
        self.logger.info("Updates: %d", self._stats['updates'])
        self.logger.info("Deletes: %d", self._stats['deletes'])
        self.logger.info("Skipped: %d", self._stats['skipped'])

    # ─── Message Routing ─────────────────────────────────────

    def process_message(self, topic: str, message_value: Dict[str, Any]):
        """Route message to appropriate handler based on topic."""
        op, data = DebeziumTransformer.extract_operation_and_data(message_value)
        if not op or not data:
            self.logger.warning("Invalid message from %s", topic)
            self._stats['skipped'] += 1
            return

        if 'stgInsuranceClaim' in topic:
            self._process_claim_event(op, data)
        elif 'stgInsuranceContract' in topic and 'stgInsuranceContractObject' not in topic:
            self._process_contract_event(op, data)
        elif 'stgInsuranceContractObject' in topic:
            self._process_contract_object_event(op, data)
        else:
            self.logger.warning("Unknown topic: %s", topic)
            self._stats['skipped'] += 1

    # ─── Claim Event Handler ─────────────────────────────────

    def _process_claim_event(self, op: str, data: Dict[str, Any]):
        """Process stgInsuranceClaim CDC event (replaces trigger logic)."""
        claim_id = data.get('id')
        contract_id = data.get('contractId')
        contract_object_id = data.get('contractObjectId')

        if not all([claim_id, contract_id, contract_object_id]):
            self.logger.warning(
                "Missing required fields in claim: id=%s, contractId=%s, coId=%s",
                claim_id, contract_id, contract_object_id
            )
            self._stats['skipped'] += 1
            return

        if op == 'd':
            self._delete_profiling_record(claim_id)
            self._stats['deletes'] += 1
            self.logger.info("[CLAIM] Deleted profiling for claim %s", claim_id)
            return

        contract_info = self._get_contract_info(contract_id)
        contract_object_info = self._get_contract_object_info(contract_object_id)

        if not contract_info:
            self.logger.warning("[CLAIM] Missing contract for claim %s", claim_id)
            self._stats['skipped'] += 1
            return
        if not contract_object_info:
            self.logger.warning("[CLAIM] Missing contract_object for claim %s", claim_id)
            self._stats['skipped'] += 1
            return

        record = ProfilingRecordBuilder.build(data, contract_info, contract_object_info)

        if self._upsert_profiling_record(record):
            if op in ['c', 'r']:
                self._stats['inserts'] += 1
            else:
                self._stats['updates'] += 1
            self.logger.info("[CLAIM] Profiled claim %s (%s)", claim_id, op)
        else:
            self._stats['errors'] = self._stats.get('errors', 0) + 1
            self.logger.error("[CLAIM] Failed to profile claim %s", claim_id)

        self._stats['claim_events'] += 1

    # ─── Contract Event Handler ──────────────────────────────

    def _process_contract_event(self, op: str, data: Dict[str, Any]):
        """Process stgInsuranceContract CDC event. Refreshes related profiling records."""
        contract_id = data.get('contractId')
        if not contract_id:
            return

        if op in ('u', 'c', 'r'):
            self._refresh_profiling_for_contract(contract_id)

        self._stats['contract_events'] += 1

    def _process_contract_object_event(self, op: str, data: Dict[str, Any]):
        """Process stgInsuranceContractObject* CDC event. Refreshes related profiling records."""
        contract_object_id = data.get('contractObjectId') or data.get('id')
        if not contract_object_id:
            return

        if op in ('u', 'c', 'r'):
            self._refresh_profiling_for_contract_object(contract_object_id)

        self._stats['contract_object_events'] += 1

    # ─── Staging Lookups ─────────────────────────────────────

    def _get_contract_info(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Lookup contract master info from staging DB."""
        return self._staging_db.fetch_one(
            'SELECT "contractStartDate", "customerType" FROM "stgInsuranceContract" WHERE "contractId" = %s LIMIT 1',
            [contract_id]
        )

    def _get_contract_object_info(self, contract_object_id: str) -> Optional[Dict[str, Any]]:
        """
        Lookup contract object info from staging DB.
        """
        _UNION_QUERY = """
            SELECT "peopleDob", "peopleRelationship", "peopleGender", "peopleCityCode",
                   "peopleName", "peoplePhone", "peopleEmail", "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObject" WHERE "contractObjectId" = %s
          UNION ALL
            SELECT "peopleDob", "peopleRelationship", "peopleGender", "peopleCityCode",
                   "peopleName", "peoplePhone", "peopleEmail", "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObjectVehicle" WHERE "contractObjectId" = %s
          UNION ALL
            SELECT "peopleDob", "peopleRelationship", "peopleGender", "peopleCityCode",
                   "peopleName", "peoplePhone", "peopleEmail", "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObjectSocialInsurance" WHERE "contractObjectId" = %s
          UNION ALL
            SELECT "peopleDob", "peopleRelationship", "peopleGender", "peopleCityCode",
                   "peopleName", "peoplePhone", "peopleEmail", "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObjectMedicalInsurance" WHERE "contractObjectId" = %s
          UNION ALL
            SELECT "dob"       AS "peopleDob",
                   NULL        AS "peopleRelationship",
                   "gender"    AS "peopleGender",
                   "cityCode"  AS "peopleCityCode",
                   "name"      AS "peopleName",
                   "phone"     AS "peoplePhone",
                   "email"     AS "peopleEmail",
                   "address"   AS "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObjectMoto" WHERE "id" = %s
          UNION ALL
            SELECT "dob"       AS "peopleDob",
                   NULL        AS "peopleRelationship",
                   "gender"    AS "peopleGender",
                   "cityCode"  AS "peopleCityCode",
                   "name"      AS "peopleName",
                   "phone"     AS "peoplePhone",
                   "email"     AS "peopleEmail",
                   "address"   AS "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObjectTravel" WHERE "id" = %s
          UNION ALL
            SELECT "dob"       AS "peopleDob",
                   NULL        AS "peopleRelationship",
                   "gender"    AS "peopleGender",
                   "cityCode"  AS "peopleCityCode",
                   "name"      AS "peopleName",
                   "phone"     AS "peoplePhone",
                   "email"     AS "peopleEmail",
                   "address"   AS "peopleAddress",
                   "programId", "programName"
            FROM "stgInsuranceContractObjectHouse" WHERE "id" = %s
          LIMIT 1
        """
        return self._staging_db.fetch_one(
            _UNION_QUERY,
            [contract_object_id] * 7
        )

    # ─── Profiling DB Operations ─────────────────────────────

    def _upsert_profiling_record(self, record: Dict[str, Any]) -> bool:
        """Insert or update profiling_analysis record."""
        query, values = SQLQueryBuilder.build_reporting_upsert(
            table='reporting.profiling_analysis',
            data=record,
            key_fields=['id'],
            exclude_fields=[],
        )
        if not query or not values:
            return False
        try:
            self._reporting_db.execute(query, values)
            return True
        except Exception:
            return False

    def _delete_profiling_record(self, claim_id: str) -> bool:
        """Delete profiling_analysis record by claim id."""
        try:
            self._reporting_db.execute(
                'DELETE FROM "reporting"."profiling_analysis" WHERE "id" = %s',
                [claim_id]
            )
            return True
        except Exception:
            return False

    # ─── Refresh Operations (cascade from parent changes) ────

    def _refresh_profiling_for_contract(self, contract_id: str):
        """
        Refresh all profiling records related to a contract.
        """
        claims = self._staging_db.fetch_all(
            'SELECT * FROM "stgInsuranceClaim" WHERE "contractId" = %s',
            [contract_id]
        )
        if not claims:
            return

        contract_info = self._get_contract_info(contract_id)
        if not contract_info:
            self.logger.warning(
                "[REFRESH] Missing contract %s — skipping %d claims",
                contract_id, len(claims)
            )
            return

        co_ids = list({c.get('contractObjectId') for c in claims if c.get('contractObjectId')})
        co_info_map: Dict[str, Dict] = {}
        for co_id in co_ids:
            info = self._get_contract_object_info(co_id)
            if info:
                co_info_map[co_id] = info

        for claim in claims:
            co_id = claim.get('contractObjectId')
            co_info = co_info_map.get(co_id)
            if not co_info:
                continue
            record = ProfilingRecordBuilder.build(claim, contract_info, co_info)
            if self._upsert_profiling_record(record):
                self._stats['updates'] += 1
            else:
                self._stats['errors'] = self._stats.get('errors', 0) + 1

        self.logger.debug(
            "Refreshed %d profiling records for contract %s",
            len(claims), contract_id
        )

    def _refresh_profiling_for_contract_object(self, contract_object_id: str):
        """
        Refresh all profiling records related to a contract object.
        """
        claims = self._staging_db.fetch_all(
            'SELECT * FROM "stgInsuranceClaim" WHERE "contractObjectId" = %s',
            [contract_object_id]
        )
        if not claims:
            return

        co_info = self._get_contract_object_info(contract_object_id)
        if not co_info:
            return

        contract_info_cache: Dict[str, Optional[Dict]] = {}
        for claim in claims:
            cid = claim.get('contractId')
            if cid not in contract_info_cache:
                contract_info_cache[cid] = self._get_contract_info(cid)
            contract_info = contract_info_cache[cid]
            if not contract_info:
                continue
            record = ProfilingRecordBuilder.build(claim, contract_info, co_info)
            if self._upsert_profiling_record(record):
                self._stats['updates'] += 1
            else:
                self._stats['errors'] = self._stats.get('errors', 0) + 1

        self.logger.debug(
            "Refreshed %d profiling records for contract_object %s",
            len(claims), contract_object_id
        )

    # ─── Override run() for architecture info ────────────────

    def run(self):
        self.logger.info("Architecture: Debezium → Kafka → This Consumer → profiling_analysis")
        self.logger.info("Mode: Real-time streaming (replaces DB triggers)")
        super().run()


def main():
    """Main entry point."""
    consumer = ProfilingConsumer()
    consumer.run()


if __name__ == '__main__':
    main()
