from datetime import timezone, datetime, timedelta
from typing import List, Optional, Annotated, Union, Literal, Tuple

from pydantic import BaseModel, constr, field_validator, NonNegativeInt, Field, conint

from .enum_serializer import *


# ===================================================================
# 通用基礎模型 (Common Base Models)
# ===================================================================
class BaseColumn(BaseModel):
    id: str
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _coerce_epoch(cls, v):
        if isinstance(v, int):
            return v
        if isinstance(v, datetime):
            # naive: UTC+8
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone(timedelta(hours=8)))
            return int(v.timestamp())
        return int(v.timestamp())


class Coordinates(BaseModel):
    lat: float
    lng: float


class CollectionBase(BaseModel):
    totalItems: int
    limit: int
    offset: int
    next: Optional[str] = None
    member: List[Any]


# ===================================================================
# 志工團體 (Volunteer Organizations)
# ===================================================================


class VolunteerOrgBase(BaseModel):
    organization_name: str
    registration_status: Optional[str] = None
    organization_nature: Optional[str] = None
    coordinator: Optional[str] = None
    contact_info: Optional[str] = None
    registration_method: Optional[str] = None
    service_content: Optional[str] = None
    meeting_info: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None  # Todo:需要協助補上驗證規則


class VolunteerOrgCreate(VolunteerOrgBase):
    pass


class VolunteerOrgPatch(BaseModel):
    organization_name: Optional[str] = None
    registration_status: Optional[str] = None
    organization_nature: Optional[str] = None
    coordinator: Optional[str] = None
    contact_info: Optional[str] = None
    registration_method: Optional[str] = None
    service_content: Optional[str] = None
    meeting_info: Optional[str] = None
    notes: Optional[str] = None
    image_url: Optional[str] = None  # Todo:需要協助補上驗證規則


class VolunteerOrganization(VolunteerOrgBase, BaseColumn):
    id: str
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class VolunteerOrgCollection(CollectionBase):
    member: List[VolunteerOrganization]


# ===================================================================
# 庇護所 (Shelters)
# ===================================================================


class ShelterBase(BaseModel):
    name: str
    location: str
    phone: str
    status: str
    link: Optional[str] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    available_spaces: Optional[int] = None
    facilities: Optional[List[str]] = []
    contact_person: Optional[str] = None
    notes: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    opening_hours: Optional[str] = None


# Todo:需要協助補上驗證規則 like link
class ShelterCreate(ShelterBase):
    status: ShelterStatusEnum


class ShelterPatch(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    status: ShelterStatusEnum
    link: Optional[str] = None
    capacity: Optional[int] = None
    current_occupancy: Optional[int] = None
    available_spaces: Optional[int] = None
    facilities: Optional[List[str]] = None
    contact_person: Optional[str] = None
    notes: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    opening_hours: Optional[str] = None


class Shelter(ShelterBase, BaseColumn):
    class Config:
        from_attributes = True


class ShelterCollection(CollectionBase):
    member: List[Shelter]


# ===================================================================
# 醫療站 (Medical Stations)
# ===================================================================


class MedicalStationBase(BaseModel):
    station_type: MedicalStationTypeEnum
    name: str
    status: str
    location: Optional[str] = None
    detailed_address: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    services: Optional[List[str]] = Field(default_factory=list)
    operating_hours: Optional[str] = None
    equipment: Optional[Any] = Field(default_factory=list)
    medical_staff: Optional[int] = None
    daily_capacity: Optional[int] = None
    coordinates: Optional[Coordinates] = None
    affiliated_organization: Optional[str] = None
    notes: Optional[str] = None
    link: Optional[str] = None


# Todo:需要協助補上驗證規則 like phone and link
class MedicalStationCreate(MedicalStationBase):
    status: MedicalStationStatusEnum


class MedicalStationPatch(BaseModel):
    station_type: Optional[MedicalStationTypeEnum] = None
    name: Optional[str] = None
    status: Optional[MedicalStationStatusEnum] = None
    location: Optional[str] = None
    detailed_address: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    services: Optional[List[str]] = None
    operating_hours: Optional[str] = None
    equipment: Optional[Any] = None
    medical_staff: Optional[int] = None
    daily_capacity: Optional[int] = None
    coordinates: Optional[Coordinates] = None
    affiliated_organization: Optional[str] = None
    notes: Optional[str] = None
    link: Optional[str] = None


class MedicalStation(MedicalStationBase, BaseColumn):
    class Config:
        from_attributes = True


class MedicalStationCollection(CollectionBase):
    member: List[MedicalStation]


# ===================================================================
# 心理健康資源 (Mental Health Resources)
# ===================================================================


class MentalHealthResourceBase(BaseModel):
    duration_type: str
    name: str
    service_format: str
    service_hours: str
    contact_info: str
    is_free: bool
    status: str
    emergency_support: bool
    website_url: Optional[str] = None
    target_audience: Optional[List[str]] = []
    specialties: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    location: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    capacity: Optional[int] = None
    waiting_time: Optional[str] = None
    notes: Optional[str] = None


class MentalHealthResourceCreate(MentalHealthResourceBase):
    duration_type: MentalHealthDurationEnum
    service_format: MentalHealthFormatEnum
    status: MentalHealthResourceStatusEnum
    is_free: Optional[bool] = False
    emergency_support: Optional[bool] = False


class MentalHealthResourcePatch(BaseModel):
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


class MentalHealthResource(MentalHealthResourceBase, BaseColumn):
    class Config:
        from_attributes = True


class MentalHealthResourceCollection(CollectionBase):
    member: List[MentalHealthResource]


# ===================================================================
# 住宿資源 (Accommodations)
# ===================================================================


class AccommodationBase(BaseModel):
    township: str
    name: str
    has_vacancy: str
    available_period: str
    contact_info: str
    address: str
    pricing: str
    status: str
    restrictions: Optional[str] = None
    room_info: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    info_source: Optional[str] = None
    notes: Optional[str] = None
    capacity: Optional[int] = None
    registration_method: Optional[str] = None
    facilities: Optional[List[str]] = []
    distance_to_disaster_area: Optional[str] = None


class AccommodationCreate(AccommodationBase):
    status: AccommodationStatusEnum
    has_vacancy: AccommodationVacancyEnum
    available_period: Optional[str] = None
    pricing: Optional[str] = None


class AccommodationPatch(BaseModel):
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


class Accommodation(AccommodationBase, BaseColumn):
    class Config:
        from_attributes = True


class AccommodationCollection(CollectionBase):
    member: List[Accommodation]


# ===================================================================
# 洗澡點 (Shower Stations)
# ===================================================================


class GenderSchedule(BaseModel):
    male: Optional[List[str]] = []
    female: Optional[List[str]] = []


# Todo:需要協助補上驗證規則 like phone
class ShowerStationBase(BaseModel):
    name: str
    address: str
    facility_type: str
    time_slots: str
    available_period: str
    is_free: bool
    status: str
    requires_appointment: bool
    coordinates: Optional[Coordinates] = None
    phone: Optional[str] = None
    gender_schedule: Optional[GenderSchedule] = None
    capacity: Optional[int] = None
    pricing: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None
    facilities: Optional[List[str]] = []
    distance_to_guangfu: Optional[str] = None
    contact_method: Optional[str] = None


class ShowerStationCreate(ShowerStationBase):
    facility_type: ShowerFacilityTypeEnum
    status: ShowerStationStatusEnum


class ShowerStationPatch(BaseModel):
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
    gender_schedule: Optional[GenderSchedule] = None
    capacity: Optional[int] = None
    pricing: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None
    facilities: Optional[List[str]] = None
    distance_to_guangfu: Optional[str] = None
    contact_method: Optional[str] = None


class ShowerStation(ShowerStationBase, BaseColumn):
    class Config:
        from_attributes = True


class ShowerStationCollection(CollectionBase):
    member: List[ShowerStation]


# ===================================================================
# 飲用水補給站 (Water Refill Stations)
# ===================================================================


class WaterRefillStationBase(BaseModel):
    name: str
    address: str
    water_type: WaterTypeEnum
    opening_hours: str
    is_free: bool
    status: WaterRefillStationStatusEnum
    accessibility: bool
    coordinates: Optional[Coordinates] = None
    phone: Optional[str] = None
    container_required: Optional[str] = None
    daily_capacity: Optional[int] = None
    water_quality: Optional[str] = None
    facilities: Optional[List[str]] = []
    distance_to_disaster_area: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None


# Todo:需要協助補上驗證規則 like phone
class WaterRefillStationCreate(WaterRefillStationBase):
    water_type: WaterTypeEnum
    status: WaterRefillStationStatusEnum


class WaterRefillStationPatch(BaseModel):
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


class WaterRefillStation(WaterRefillStationBase, BaseColumn):
    class Config:
        from_attributes = True


class WaterRefillStationCollection(CollectionBase):
    member: List[WaterRefillStation]


# ===================================================================
# 廁所 (Restrooms)
# ===================================================================


class RestroomBase(BaseModel):
    name: str
    address: str
    facility_type: str
    opening_hours: str
    is_free: bool
    has_water: bool
    has_lighting: bool
    status: str
    coordinates: Optional[Coordinates] = None
    phone: Optional[str] = None
    male_units: Optional[int] = None
    female_units: Optional[int] = None
    unisex_units: Optional[int] = None
    accessible_units: Optional[int] = None
    cleanliness: Optional[str] = None
    last_cleaned: Optional[datetime] = None
    facilities: Optional[List[str]] = []
    distance_to_disaster_area: Optional[str] = None
    notes: Optional[str] = None
    info_source: Optional[str] = None


# Todo:需要協助補上驗證規則 like phone and cleanliness
class RestroomCreate(RestroomBase):
    facility_type: RestroomFacilityTypeEnum
    status: RestroomStatusEnum


class RestroomPatch(BaseModel):
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


class Restroom(RestroomBase, BaseColumn):
    class Config:
        from_attributes = True


class RestroomCollection(CollectionBase):
    member: List[Restroom]


# ===================================================================
# 人力資源 (Human Resources) (NOTE: This is obsolated by "Requirements HR")
# ===================================================================


class HumanResourceBase(BaseModel):
    org: str
    address: str
    phone: str
    status: str
    is_completed: bool
    role_name: str
    role_type: str
    headcount_need: NonNegativeInt
    headcount_got: NonNegativeInt
    role_status: str
    has_medical: Optional[bool] = None
    skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    experience_level: Optional[str] = None
    language_requirements: Optional[List[str]] = []
    headcount_unit: Optional[str] = None
    shift_start_ts: Optional[datetime] = None
    shift_end_ts: Optional[datetime] = None
    shift_notes: Optional[str] = None
    assignment_timestamp: Optional[datetime] = None
    assignment_count: Optional[int] = None
    assignment_notes: Optional[str] = None


# Todo:需要協助補上驗證規則 like phone
class HumanResourceCreate(HumanResourceBase):
    status: HumanResourceStatusEnum
    role_type: HumanResourceRoleTypeEnum
    role_status: HumanResourceRoleStatusEnum
    experience_level: Optional[HumanResourceExperienceLevelEnum] = None
    is_completed: Optional[bool] = False
    headcount_got: Optional[int] = 0


class HumanResourcePatch(BaseModel):
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


class HumanResource(HumanResourceBase, BaseColumn):
    total_roles_in_request: Optional[int] = None
    completed_roles_in_request: Optional[int] = None
    pending_roles_in_request: Optional[int] = None
    total_requests: Optional[int] = None
    active_requests: Optional[int] = None
    completed_requests: Optional[int] = None
    cancelled_requests: Optional[int] = None
    total_roles: Optional[int] = None
    completed_roles: Optional[int] = None
    pending_roles: Optional[int] = None
    urgent_requests: Optional[int] = None
    medical_requests: Optional[int] = None

    class Config:
        from_attributes = True


class HumanResourceWithPin(HumanResource):
    valid_pin: Optional[str] = None


class HumanResourceCollection(CollectionBase):
    member: List[HumanResource]


# ===================================================================
# 物資項目 (Supply Items) & 物資單 (Supplies)
# ===================================================================


class SupplyItemBase(BaseModel):
    total_number: NonNegativeInt
    tag: Optional[str] = None
    name: Optional[str] = None
    received_count: Optional[NonNegativeInt] = 0
    unit: Optional[str] = None


class SupplyItemCreateWithPin(SupplyItemBase):
    supply_id: str
    valid_pin: str


class SupplyItemCreate(SupplyItemBase):
    supply_id: str


class SupplyItemPatch(BaseModel):
    total_number: Optional[NonNegativeInt] = None
    tag: Optional[str] = None
    name: Optional[str] = None
    received_count: Optional[NonNegativeInt] = None
    unit: Optional[str] = None
    valid_pin: Optional[str] = None


class SupplyItem(SupplyItemBase, BaseColumn):
    supply_id: str

    class Config:
        from_attributes = True


class SupplyItemCollection(CollectionBase):
    member: List[SupplyItem]


class SupplyBase(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class SupplyCreate(SupplyBase):
    supplies: Dict[str, Any]


class SupplyPatch(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    valid_pin: Optional[str] = None
    spam_warn: Optional[bool] = None


class Supply(SupplyBase, BaseColumn):
    supplies: List[SupplyItem] = []
    spam_warn: Optional[bool] = None

    class Config:
        from_attributes = True


class SupplyWithPin(Supply):
    valid_pin: Optional[str] = None


class SupplyCollection(CollectionBase):
    member: List[Supply]


SixDigitPin = Annotated[str, constr(pattern=r"^\d{6}$")]


class SupplyItemDistribution(BaseModel):
    id: str
    valid_pin: SixDigitPin


class SupplyItemUpdate(BaseModel):
    id: str = Field(..., description="supply_item_id")
    count: conint(strict=True, gt=0) = Field(
        ..., description="要累加的數量，必須為正整數"
    )


# ===================================================================
# 物資供應提供者 (Supply Providers)
# ===================================================================


class SupplyProviderBase(BaseModel):
    name: str
    phone: str
    supply_item_id: str
    address: str
    notes: Optional[str] = None
    provide_count: NonNegativeInt
    provide_unit: Optional[str] = None


class SupplyProviderCreate(SupplyProviderBase):
    pass


class SupplyProviderPatch(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    supply_item_id: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    provide_count: Optional[NonNegativeInt] = None
    provide_unit: Optional[str] = None


class SupplyProvider(SupplyProviderBase, BaseColumn):
    class Config:
        from_attributes = True


class SupplyProviderCollection(CollectionBase):
    member: List[SupplyProvider]


# ===================================================================
# 回報事件 (Reports)
# ===================================================================


class ReportBase(BaseModel):
    name: str
    location_type: str
    location_id: str
    reason: str
    status: str
    notes: Optional[str] = None


class ReportCreate(ReportBase):
    pass


class ReportPatch(BaseModel):
    name: Optional[str] = None
    location_type: Optional[str] = None
    location_id: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Report(ReportBase, BaseColumn):
    class Config:
        from_attributes = True


class ReportCollection(CollectionBase):
    member: List[Report]


# ===================================================================
# LINE OAuth2 認證 (LINE OAuth2 Authentication)
# ===================================================================


class LineTokenResponse(BaseModel):
    """LINE OAuth2 token 交換成功的回應"""

    access_token: str = Field(..., description="存取權杖")
    refresh_token: Optional[str] = Field(None, description="刷新權杖")
    id_token: Optional[str] = Field(..., description="ID 權杖 (OpenID Connect)")
    token_type: str = Field(default="Bearer", description="權杖類型")
    expires_in: int = Field(..., description="權杖有效期限（秒）")
    line_user_id: Optional[str] = Field(..., description="LINE 使用者 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "RPWOpZNN0itB...",
                "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "Bearer",
                "expires_in": 2592000,
                "line_user_id": "U1497c257fa61519387b5c6666067fcfe",
            }
        }


class LineUserInfoResponse(BaseModel):
    """LINE 使用者資訊回應"""

    sub: str = Field(..., description="LINE 使用者 ID (subject)")
    name: Optional[str] = Field(None, description="使用者顯示名稱")
    picture: Optional[str] = Field(None, description="使用者頭像 URL")
    email: Optional[str] = Field(None, description="使用者電子郵件")
    email_granted: bool = Field(default=False, description="是否授予電子郵件權限")
    scope: str = Field(..., description="授權範圍")

    class Config:
        json_schema_extra = {
            "example": {
                "sub": "U1497c257fa61519...",
                "name": "TEST",
                "picture": "https://profile.line-scdn.net/0hcW0mc133PHgdFC1txHVC...",
                "email": None,
                "email_granted": False,
                "scope": "profile openid",
            }
        }


# ===================================================================
# 場所 (Places)
# ===================================================================


class PointCoordinates(BaseModel):
    """Point 類型座標 - 單一明確位置點"""

    type: Literal["Point"] = Field(
        "Point", description="座標類型: Point (明確的服務位置點)"
    )
    coordinates: Tuple[float, float] = Field(
        ..., description="座標 [經度, 緯度]，例如：[121.123, 24.456]"
    )

    @field_validator("coordinates")
    @classmethod
    def validate_point_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError("Point 座標必須包含兩個值 [經度, 緯度]")
        lng, lat = v
        if not (-180 <= lng <= 180):
            raise ValueError(f"經度必須在 -180 到 180 之間，當前值: {lng}")
        if not (-90 <= lat <= 90):
            raise ValueError(f"緯度必須在 -90 到 90 之間，當前值: {lat}")
        return v

    class Config:
        json_schema_extra = {
            "example": {"type": "Point", "coordinates": [121.3897, 23.9870]}
        }


class PolygonCoordinates(BaseModel):
    """Polygon 類型座標 - 表示覆蓋範圍（多邊形區域）"""

    type: Literal["Polygon"] = Field(
        "Polygon", description="座標類型: Polygon (表示覆蓋範圍)"
    )
    coordinates: List[Tuple[float, float]] = Field(
        ...,
        description="座標陣列 [[經度, 緯度], [經度, 緯度], ...]，例如：[[121.1, 24.1], [121.2, 24.1], [121.2, 24.2]]",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_polygon_coordinates(cls, v):
        if len(v) < 3:
            raise ValueError("Polygon 至少需要 3 個座標點")
        for i, coord in enumerate(v):
            if len(coord) != 2:
                raise ValueError(f"座標點 {i} 必須包含兩個值 [經度, 緯度]")
            lng, lat = coord
            if not (-180 <= lng <= 180):
                raise ValueError(f"座標點 {i} 經度必須在 -180 到 180 之間，當前值: {lng}")
            if not (-90 <= lat <= 90):
                raise ValueError(f"座標點 {i} 緯度必須在 -90 到 90 之間，當前值: {lat}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "type": "Polygon",
                "coordinates": [
                    [121.38, 23.98],
                    [121.39, 23.98],
                    [121.39, 23.99],
                    [121.38, 23.99],
                ],
            }
        }


class LineStringCoordinates(BaseModel):
    """LineString 類型座標 - 路徑規劃（線段）"""

    type: Literal["LineString"] = Field(
        "LineString", description="座標類型: LineString (路徑規劃)"
    )
    coordinates: List[Tuple[float, float]] = Field(
        ...,
        description="座標陣列 [[經度, 緯度], [經度, 緯度], ...]，例如：[[121.1, 24.1], [121.2, 24.2]]",
    )

    @field_validator("coordinates")
    @classmethod
    def validate_linestring_coordinates(cls, v):
        if len(v) < 2:
            raise ValueError("LineString 至少需要 2 個座標點")
        for i, coord in enumerate(v):
            if len(coord) != 2:
                raise ValueError(f"座標點 {i} 必須包含兩個值 [經度, 緯度]")
            lng, lat = coord
            if not (-180 <= lng <= 180):
                raise ValueError(f"座標點 {i} 經度必須在 -180 到 180 之間，當前值: {lng}")
            if not (-90 <= lat <= 90):
                raise ValueError(f"座標點 {i} 緯度必須在 -90 到 90 之間，當前值: {lat}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "type": "LineString",
                "coordinates": [[121.38, 23.98], [121.39, 23.99], [121.40, 23.99]],
            }
        }


# 使用 Union 來支援三種不同的座標類型
PlaceCoordinates = Union[PointCoordinates, PolygonCoordinates, LineStringCoordinates]


class PlaceResource(BaseModel):
    """站點資源資料"""

    name: str = Field(..., description="資源名稱，例如：女廁")
    amount: int = Field(..., description="數量，例如：10")
    unit: str = Field(..., description="單位，例如：座")

    class Config:
        json_schema_extra = {
            "example": {"name": "測試資源名稱", "amount": 10, "unit": "個"}
        }


class PlaceBase(BaseModel):
    name: str
    address: str = Field(
        ..., description="地址格式規定：不能有空格、數字或英文一律半型、盡量是完整地址"
    )
    address_description: Optional[str] = Field(
        None, description="針對地址的進一步說明（如果地方不好找的話）"
    )
    coordinates: Optional[PlaceCoordinates] = Field(
        None, description="GeoJSON 格式的經緯度座標"
    )
    type: str = Field(
        ...,
        description="站點類型，例如：醫療、加水、廁所、洗澡、避難、住宿、物資、心理援助",
    )
    sub_type: Optional[str] = Field(
        None, description="站點服務類別，例如：流動廁所/車站/學校、民宿/飯店/民眾提供"
    )
    info_sources: Optional[List[str]] = Field(
        default_factory=list, description="資料來源連結"
    )
    verified_at: Optional[int] = Field(
        None, description="資料最後被核實的時間（Unix timestamp）"
    )
    website_url: Optional[str] = Field(
        None, description="若這個地方是某單位提供，可附上該單位官方連結"
    )
    status: str = Field(..., description="嚴格規定僅限於：開放、暫停、關閉")
    resources: Optional[List[PlaceResource]] = Field(None, description="站點資源列表")
    open_date: Optional[str] = Field(None, description="站點開放日期，格式：2025/09/30")
    end_date: Optional[str] = Field(
        None, description="站點預計關閉日期，格式：2025/10/12"
    )
    open_time: Optional[str] = Field(
        None,
        description="站點每天開放時間（24小時格式），例如：08:00，若為24小時開放則留 null",
    )
    end_time: Optional[str] = Field(
        None,
        description="站點每天關閉時間（24小時格式），例如：20:00，若為24小時開放則留 null",
    )
    contact_name: str = Field(..., description="聯絡人姓名，例如：張先生")
    contact_phone: str = Field(..., description="聯絡人手機號碼")
    notes: Optional[str] = Field(None, description="其他備註，例如：本站點的量能")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        # allowed_statuses = ["開放", "暫停", "關閉"]
        allowed_statuses = [e.value for e in PlaceStatusEnum]
        if v not in allowed_statuses:
            raise ValueError(f"status 必須是 {', '.join(allowed_statuses)} 其中之一")
        return v


class PlaceCreate(PlaceBase):
    type: PlaceTypeEnum

    class Config:
        json_schema_extra = {
            "example": {
                "name": "測試站點A",
                "address": "976台灣花蓮縣光復鄉測試路100號",
                "address_description": "測試路與範例街路口",
                "coordinates": {"type": "Point", "coordinates": [121.3897, 23.9870]},
                "type": "醫療",
                "sub_type": "測試醫療站",
                "info_sources": [
                    "https://example.com/test-source1",
                    "https://example.com/test-source2",
                ],
                "verified_at": 1727654400,
                "website_url": "https://example.com/test-hospital",
                "status": "開放",
                "resources": [
                    {"name": "測試資源A", "amount": 5, "unit": "個"},
                    {"name": "測試資源B", "amount": 10, "unit": "件"},
                ],
                "open_date": "2025/09/30",
                "end_date": "2025/10/12",
                "open_time": "08:00",
                "end_time": "20:00",
                "contact_name": "測試聯絡人",
                "contact_phone": "0912345678",
                "notes": "測試備註內容",
            }
        }


class PlacePatch(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    address_description: Optional[str] = None
    coordinates: Optional[PlaceCoordinates] = None
    type: Optional[PlaceTypeEnum] = None
    sub_type: Optional[str] = None
    info_sources: Optional[List[str]] = None
    verified_at: Optional[int] = None
    website_url: Optional[str] = None
    status: Optional[PlaceStatusEnum] = None
    resources: Optional[List[PlaceResource]] = None
    open_date: Optional[str] = None
    end_date: Optional[str] = None
    open_time: Optional[str] = None
    end_time: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class Place(PlaceBase, BaseColumn):
    class Config:
        from_attributes = True


class PlaceCollection(CollectionBase):
    member: List[Place]


# ===================================================================
# 人力需求 (Requirements HR) (NOTE: This obsolates "Human Resources")
# ===================================================================


class RequirementsHrBase(BaseModel):
    place_id: str
    required_type: str
    name: str
    unit: str
    require_count: NonNegativeInt
    received_count: NonNegativeInt


class RequirementsHrCreate(RequirementsHrBase):
    required_type: RequirementsHrTypeEnum
    received_count: Optional[NonNegativeInt] = 0


class RequirementsHrPatch(BaseModel):
    place_id: Optional[str] = None
    required_type: Optional[RequirementsHrTypeEnum] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    require_count: Optional[NonNegativeInt] = None
    received_count: Optional[NonNegativeInt] = None


class RequirementsHr(RequirementsHrBase, BaseColumn):
    class Config:
        from_attributes = True


class RequirementsHrCollection(CollectionBase):
    member: List[RequirementsHr]


# ===================================================================
# 物資需求 (Requirements Supplies) (NOTE: This obsolates "Supplies")
# ===================================================================


class RequirementsSuppliesBase(BaseModel):
    place_id: str
    required_type: str
    name: str
    unit: str
    require_count: NonNegativeInt
    received_count: NonNegativeInt


class RequirementsSuppliesCreate(RequirementsSuppliesBase):
    required_type: RequirementsSuppliesTypeEnum
    received_count: Optional[NonNegativeInt] = 0


class RequirementsSuppliesPatch(BaseModel):
    place_id: Optional[str] = None
    required_type: Optional[RequirementsSuppliesTypeEnum] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    require_count: Optional[NonNegativeInt] = None
    received_count: Optional[NonNegativeInt] = None


class RequirementsSupplies(RequirementsSuppliesBase, BaseColumn):
    class Config:
        from_attributes = True


class RequirementsSuppliesCollection(CollectionBase):
    member: List[RequirementsSupplies]

