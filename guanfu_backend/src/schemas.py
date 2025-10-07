import datetime
from typing import Annotated, Any, List, Optional

from pydantic import BaseModel, Field, NonNegativeInt, constr

from .enum_serializer import *


def generate_uuid_str():
    """Generates a string representation of a UUID4."""
    return str(uuid.uuid4())


def current_timestamp_int():
    """Returns the current Unix timestamp as an integer."""
    return int(time.time())


# ===================================================================
# 通用基礎模型 (Common Base Models)
# ===================================================================
class BaseColumn(BaseModel):
    id: str


class BaseSchema(BaseModel):
    """Base schema model for all schemas"""

    pass


class Coordinates(BaseSchema):
    lat: float
    lng: float


class CollectionBase(BaseSchema):
    totalItems: int
    limit: int
    offset: int
    member: List[Any]


# ===================================================================
# 志工團體 (Volunteer Organizations)
# ===================================================================


# Import the SQLModel classes from models
from .models.volunteer_organizations import (
    VolunteerOrganization,
    VolunteerOrganizationBase,
)

# Use the SQLModel classes directly as schemas
VolunteerOrgBase = VolunteerOrganizationBase
VolunteerOrgCreate = VolunteerOrganizationBase
VolunteerOrganization = VolunteerOrganization


# Create proper PATCH schema with all fields optional
class VolunteerOrgPatch(BaseSchema):
    registration_status: Optional[str] = None
    organization_nature: Optional[str] = None
    organization_name: Optional[str] = None
    coordinator: Optional[str] = None
    contact_info: Optional[str] = None
    registration_method: Optional[str] = None
    service_content: Optional[str] = None
    meeting_info: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None  # Todo:需要協助補上驗證規則


class VolunteerOrgCollection(CollectionBase):
    member: List[VolunteerOrganization]


# ===================================================================
# 庇護所 (Shelters)
# ===================================================================


# Import the SQLModel classes from models
from .models.shelters import Shelter, ShelterBase

# Use the SQLModel classes directly as schemas
ShelterCreate = ShelterBase


# Create proper PATCH schema with all fields optional
class ShelterPatch(BaseSchema):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    link: Optional[str] = None
    status: Optional[ShelterStatusEnum] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    available_spaces: Optional[int] = None
    facilities: Optional[List[str]] = None
    contact_person: Optional[str] = None
    notes: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    opening_hours: Optional[str] = None  # The full model with timestamps


class ShelterCollection(CollectionBase):
    member: List[Shelter]


# ===================================================================
# 醫療站 (Medical Stations)
# ===================================================================


# Import the SQLModel classes from models
from .models.medical_stations import MedicalStation, MedicalStationBase

# Use the SQLModel classes directly as schemas
MedicalStationCreate = MedicalStationBase
MedicalStation = MedicalStation


# Create proper PATCH schema with all fields optional
class MedicalStationPatch(BaseSchema):
    station_type: Optional[MedicalStationTypeEnum] = None
    name: Optional[str] = None
    status: Optional[MedicalStationStatusEnum] = None
    location: Optional[str] = None
    detailed_address: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    services: Optional[List[str]] = None
    operating_hours: Optional[str] = None
    equipment: Optional[List[str]] = None
    medical_staff: Optional[int] = None
    daily_capacity: Optional[int] = None
    coordinates: Optional[Coordinates] = None
    affiliated_organization: Optional[str] = None
    notes: Optional[str] = None
    link: Optional[str] = None


class MedicalStationCollection(CollectionBase):
    member: List[MedicalStation]


# ===================================================================
# 心理健康資源 (Mental Health Resources)
# ===================================================================


# Import the SQLModel classes from models
from .models.mental_health_resources import (
    MentalHealthResource,
    MentalHealthResourceBase,
)

# Use the SQLModel classes directly as schemas
MentalHealthResourceCreate = MentalHealthResourceBase
MentalHealthResource = MentalHealthResource


# Create proper PATCH schema with all fields optional
class MentalHealthResourcePatch(BaseSchema):
    duration_type: Optional[MentalHealthDurationEnum] = None
    name: Optional[str] = None
    service_format: Optional[MentalHealthFormatEnum] = None
    service_hours: Optional[str] = None
    contact_info: Optional[str] = None
    is_free: Optional[bool] = None
    status: Optional[MentalHealthResourceStatusEnum] = None
    emergency_support: Optional[bool] = None
    website_url: Optional[str] = None
    target_audience: Optional[List[str]] = None
    specialties: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    location: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    capacity: Optional[int] = None
    waiting_time: Optional[str] = None
    notes: Optional[str] = None


class MentalHealthResourceCollection(CollectionBase):
    member: List[MentalHealthResource]


# ===================================================================
# 住宿資源 (Accommodations)
# ===================================================================


# Import the SQLModel classes from models
from .models.accommodations import Accommodation, AccommodationBase

# Use the SQLModel classes directly as schemas
AccommodationCreate = AccommodationBase
Accommodation = Accommodation


# Create proper PATCH schema with all fields optional
class AccommodationPatch(BaseSchema):
    township: Optional[str] = None
    name: Optional[str] = None
    has_vacancy: Optional[AccommodationVacancyEnum] = None
    available_period: Optional[str] = None
    contact_info: Optional[str] = None
    address: Optional[str] = None
    pricing: Optional[str] = None
    status: AccommodationStatusEnum
    restrictions: Optional[str] = None
    room_info: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    info_source: Optional[str] = None
    notes: Optional[str] = None
    capacity: Optional[int] = None
    registration_method: Optional[str] = None
    facilities: Optional[List[str]] = None
    distance_to_disaster_area: Optional[str] = None


class AccommodationCollection(CollectionBase):
    member: List[Accommodation]


# ===================================================================
# 洗澡點 (Shower Stations)
# ===================================================================


# Import the SQLModel classes from models
from .models.shower_stations import ShowerStation, ShowerStationBase

# Use the SQLModel classes directly as schemas
ShowerStationCreate = ShowerStationBase
ShowerStation = ShowerStation


# Create proper PATCH schema with all fields optional
class ShowerStationPatch(BaseSchema):
    name: Optional[str] = None
    address: Optional[str] = None
    facility_type: Optional[ShowerFacilityTypeEnum] = None
    time_slots: Optional[str] = None
    available_period: Optional[str] = None
    is_free: Optional[bool] = None
    status: Optional[ShowerStationStatusEnum] = None
    requires_appointment: Optional[bool] = None
    coordinates: Optional[Coordinates] = None
    phone: Optional[str] = None
    gender_schedule: Optional[Dict[str, Any]] = None
    capacity: Optional[int] = None
    pricing: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None
    facilities: Optional[List[str]] = None
    distance_to_guangfu: Optional[str] = None
    contact_method: Optional[str] = None


class ShowerStationCollection(CollectionBase):
    member: List[ShowerStation]


# ===================================================================
# 飲用水補給站 (Water Refill Stations)
# ===================================================================


# Import the SQLModel classes from models
from .models.water_refill_stations import WaterRefillStation, WaterRefillStationBase

# Use the SQLModel classes directly as schemas
WaterRefillStationCreate = WaterRefillStationBase
WaterRefillStation = WaterRefillStation


# Create proper PATCH schema with all fields optional
class WaterRefillStationPatch(BaseSchema):
    name: Optional[str] = None
    address: Optional[str] = None
    water_type: Optional[WaterTypeEnum] = None
    opening_hours: Optional[str] = None
    is_free: Optional[bool] = None
    status: Optional[WaterRefillStationStatusEnum] = None
    accessibility: Optional[bool] = None
    coordinates: Optional[Coordinates] = None
    phone: Optional[str] = None
    container_required: Optional[str] = None
    daily_capacity: Optional[int] = None
    water_quality: Optional[str] = None
    facilities: Optional[List[str]] = None
    distance_to_disaster_area: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None


class WaterRefillStationCollection(CollectionBase):
    member: List[WaterRefillStation]


# ===================================================================
# 廁所 (Restrooms)
# ===================================================================


# Import the SQLModel classes from models
from .models.restrooms import Restroom, RestroomBase

# Use the SQLModel classes directly as schemas
RestroomCreate = RestroomBase
Restroom = Restroom


# Create proper PATCH schema with all fields optional
class RestroomPatch(BaseSchema):
    name: Optional[str] = None
    address: Optional[str] = None
    facility_type: Optional[RestroomFacilityTypeEnum] = None
    opening_hours: Optional[str] = None
    is_free: Optional[bool] = None
    has_water: Optional[bool] = None
    has_lighting: Optional[bool] = None
    status: Optional[RestroomStatusEnum] = None
    coordinates: Optional[Coordinates] = None
    phone: Optional[str] = None
    male_units: Optional[int] = None
    female_units: Optional[int] = None
    unisex_units: Optional[int] = None
    accessible_units: Optional[int] = None
    cleanliness: Optional[str] = None
    last_cleaned: Optional[int] = None
    facilities: Optional[List[str]] = None
    distance_to_disaster_area: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None


class RestroomCollection(CollectionBase):
    member: List[Restroom]


# ===================================================================
# 人力資源 (Human Resources)
# ===================================================================


# Import the SQLModel classes from models
from .models.human_resources import HumanResource, HumanResourceBase

# Use the SQLModel classes directly as schemas
HumanResourceCreate = HumanResourceBase
HumanResource = HumanResource
HumanResourceWithPin = HumanResource  # Add PIN field as needed


# Create proper PATCH schema with all fields optional
class HumanResourcePatch(BaseSchema):
    org: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[HumanResourceStatusEnum] = None
    is_completed: Optional[bool] = None
    role_name: Optional[str] = None
    role_type: Optional[HumanResourceRoleTypeEnum] = None
    headcount_need: Optional[NonNegativeInt] = None
    headcount_got: Optional[NonNegativeInt] = None
    role_status: Optional[HumanResourceRoleStatusEnum] = None
    pii_date: Optional[int] = None
    has_medical: Optional[bool] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    experience_level: Optional[HumanResourceExperienceLevelEnum] = None
    language_requirements: Optional[List[str]] = None
    headcount_unit: Optional[str] = None
    shift_start_ts: Optional[int] = None
    shift_end_ts: Optional[int] = None
    shift_notes: Optional[str] = None
    assignment_timestamp: Optional[int] = None
    assignment_count: Optional[int] = None
    assignment_notes: Optional[str] = None
    valid_pin: Optional[str] = None


class HumanResourceCollection(CollectionBase):
    member: List[HumanResource]


# ===================================================================
# 物資項目 (Supply Items) & 物資單 (Supplies)
# ===================================================================


# Import the SQLModel classes from models
from .models.supplies import Supply, SupplyBase, SupplyItem, SupplyItemBase

# Use the SQLModel classes directly as schemas
SupplyItemCreate = SupplyItemBase
SupplyItemCreateWithPin = SupplyItemBase  # Add PIN field as needed
SupplyItem = SupplyItem

SupplyCreate = SupplyBase  # Add supplies field as needed
Supply = Supply
SupplyWithPin = Supply  # Add PIN field as needed


# Create proper PATCH schemas with all fields optional
class SupplyItemPatch(BaseSchema):
    total_number: Optional[int] = None
    tag: Optional[SupplyItemTypeEnum] = None
    name: Optional[str] = None
    received_count: Optional[NonNegativeInt] = None
    unit: Optional[str] = None
    valid_pin: Optional[str] = None


class SupplyItemCollection(CollectionBase):
    member: List[SupplyItem]


class SupplyCollection(CollectionBase):
    member: List[Supply]


class SupplyPatch(BaseSchema):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    valid_pin: Optional[str] = None


SixDigitPin = Annotated[str, constr(pattern=r"^\d{6}$")]


class SupplyItemDistribution(BaseSchema):
    id: str
    valid_pin: SixDigitPin


# ===================================================================
# 回報事件 (Reports)
# ===================================================================


# Import the SQLModel classes from models
from .models.reports import Report, ReportBase

# Use the SQLModel classes directly as schemas
ReportCreate = ReportBase
Report = Report


# Create proper PATCH schema with all fields optional
class ReportPatch(BaseSchema):
    location_id: Optional[str] = None
    name: Optional[str] = None
    location_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[bool] = None


class ReportCollection(CollectionBase):
    member: List[Report]
