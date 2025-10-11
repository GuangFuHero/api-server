import uuid
import time
from sqlalchemy import (
    Column, String, DateTime, Integer, Boolean, Text, BigInteger, ForeignKey, text, ARRAY
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


def current_timestamp_int():
    """Returns the current Unix timestamp as an integer."""
    return time.time()


# ===================================================================
# 資料表模型定義
# ===================================================================

class VolunteerOrganization(Base):
    __tablename__ = "volunteer_organizations"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    registration_status = Column(String)
    organization_nature = Column(String)
    organization_name = Column(String, nullable=False)
    coordinator = Column(String)
    contact_info = Column(String)
    registration_method = Column(String)
    service_content = Column(Text)
    meeting_info = Column(Text)
    notes = Column(Text)
    image_url = Column(String)


class Shelter(Base):
    __tablename__ = "shelters"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    link = Column(String)
    status = Column(String, nullable=False)
    capacity = Column(Integer)
    current_occupancy = Column(Integer)
    available_spaces = Column(Integer)
    facilities = Column(ARRAY(Text), nullable=True)
    contact_person = Column(String)
    notes = Column(Text)
    coordinates = Column(JSONB)
    opening_hours = Column(String)


class MedicalStation(Base):
    __tablename__ = "medical_stations"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    station_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    location = Column(String)
    detailed_address = Column(String)
    phone = Column(String)
    contact_person = Column(String)
    services = Column(ARRAY(Text), nullable=True)
    operating_hours = Column(String)
    equipment = Column(ARRAY(Text), nullable=True)
    medical_staff = Column(Integer)
    daily_capacity = Column(Integer)
    coordinates = Column(JSONB)
    affiliated_organization = Column(String)
    notes = Column(Text)
    link = Column(String)


class MentalHealthResource(Base):
    __tablename__ = "mental_health_resources"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    duration_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    service_format = Column(String, nullable=False)
    service_hours = Column(String, nullable=False)
    contact_info = Column(String, nullable=False)
    is_free = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    emergency_support = Column(Boolean, nullable=False)
    website_url = Column(String)
    target_audience = Column(ARRAY(Text), nullable=True)
    specialties = Column(ARRAY(Text), nullable=True)
    languages = Column(ARRAY(Text), nullable=True)
    location = Column(String)
    coordinates = Column(JSONB)
    capacity = Column(Integer)
    waiting_time = Column(String)
    notes = Column(Text)


class Accommodation(Base):
    __tablename__ = "accommodations"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    township = Column(String, nullable=False)
    name = Column(String, nullable=False)
    has_vacancy = Column(String, nullable=False)
    available_period = Column(String, nullable=False)
    contact_info = Column(String, nullable=False)
    address = Column(String, nullable=False)
    pricing = Column(String, nullable=False)
    status = Column(String, nullable=False)
    restrictions = Column(String)
    room_info = Column(String)
    coordinates = Column(JSONB)
    info_source = Column(String)
    notes = Column(Text)
    capacity = Column(Integer)
    registration_method = Column(String)
    facilities = Column(ARRAY(Text), nullable=True)
    distance_to_disaster_area = Column(String)


class ShowerStation(Base):
    __tablename__ = "shower_stations"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    facility_type = Column(String, nullable=False)
    time_slots = Column(String, nullable=False)
    available_period = Column(String, nullable=False)
    is_free = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    requires_appointment = Column(Boolean, nullable=False)
    coordinates = Column(JSONB)
    phone = Column(String)
    gender_schedule = Column(JSONB)
    capacity = Column(Integer)
    pricing = Column(String)
    notes = Column(Text)
    info_source = Column(String)
    facilities = Column(ARRAY(Text), nullable=True)
    distance_to_guangfu = Column(String)
    contact_method = Column(String)


class WaterRefillStation(Base):
    __tablename__ = "water_refill_stations"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    water_type = Column(String, nullable=False)
    opening_hours = Column(String, nullable=False)
    is_free = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    accessibility = Column(Boolean, nullable=False)
    coordinates = Column(JSONB)
    phone = Column(String)
    container_required = Column(String)
    daily_capacity = Column(Integer)
    water_quality = Column(String)
    facilities = Column(ARRAY(Text), nullable=True)
    distance_to_disaster_area = Column(String)
    notes = Column(Text)
    info_source = Column(String)


class Restroom(Base):
    __tablename__ = "restrooms"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    facility_type = Column(String, nullable=False)
    opening_hours = Column(String, nullable=False)
    is_free = Column(Boolean, nullable=False)
    has_water = Column(Boolean, nullable=False)
    has_lighting = Column(Boolean, nullable=False)
    status = Column(String, nullable=False)
    coordinates = Column(JSONB)
    phone = Column(String)
    male_units = Column(DateTime(timezone=True), nullable=False)
    female_units = Column(DateTime(timezone=True), nullable=False)
    unisex_units = Column(DateTime(timezone=True), nullable=False)
    accessible_units = Column(DateTime(timezone=True), nullable=False)
    cleanliness = Column(String)
    last_cleaned = Column(DateTime(timezone=True), nullable=False)
    facilities = Column(ARRAY(Text), nullable=True)
    distance_to_disaster_area = Column(String)
    notes = Column(Text)
    info_source = Column(String)


class HumanResource(Base):
    __tablename__ = "human_resources"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    org = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    status = Column(String, nullable=False)
    is_completed = Column(Boolean, nullable=False)
    role_name = Column(String, nullable=False)
    role_type = Column(String, nullable=False)
    headcount_need = Column(Integer, nullable=False)
    headcount_got = Column(Integer, nullable=False)
    role_status = Column(String, nullable=False)
    has_medical = Column(Boolean)
    skills = Column(ARRAY(Text), nullable=True)
    certifications = Column(ARRAY(Text), nullable=True)
    experience_level = Column(String, nullable=False)
    language_requirements = Column(ARRAY(Text), nullable=True)
    headcount_unit = Column(String)
    shift_start_ts = Column(DateTime(timezone=True), nullable=False)
    shift_end_ts = Column(DateTime(timezone=True), nullable=False)
    shift_notes = Column(Text)
    assignment_timestamp = Column(BigInteger)
    assignment_count = Column(Integer)
    assignment_notes = Column(Text)
    pii_date = Column(BigInteger, nullable=False, default=current_timestamp_int)
    valid_pin = Column(String)


class Supply(Base):
    __tablename__ = "supplies"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    notes = Column(Text)
    supplies = relationship("SupplyItem", back_populates="supply", cascade="all, delete-orphan")
    pii_date = Column(BigInteger, nullable=False, default=current_timestamp_int)
    valid_pin = Column(String)
    spam_warn = Column(Boolean)


class SupplyItem(Base):
    __tablename__ = "supply_items"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    supply_id = Column(String, ForeignKey("supplies.id"), nullable=False)
    total_number = Column(Integer, nullable=False)
    tag = Column(String, nullable=False)
    name = Column(String)
    received_count = Column(Integer)
    unit = Column(String)
    supply = relationship("Supply", back_populates="supplies")


class Report(Base):
    __tablename__ = "reports"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    location_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    location_type = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    notes = Column(Text)
    status = Column(String, nullable=False)


class SupplyProvider(Base):
    __tablename__ = "supply_providers"
    id = Column(String, primary_key=True, default=generate_uuid_str)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    supply_item_id = Column(String, nullable=False)
    address = Column(String, nullable=False)
    notes = Column(Text)
    provide_count = Column(Integer)
    provide_unit = Column(String)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("NOW()"))
