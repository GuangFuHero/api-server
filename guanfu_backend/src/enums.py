# Enums for models - separated to avoid circular imports
import enum


class GeneralStatusEnum(str, enum.Enum):
    """General status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AccommodationVacancyEnum(str, enum.Enum):
    """Accommodation vacancy status enumeration"""

    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class SupplyItemTypeEnum(str, enum.Enum):
    """Supply item type enumeration"""

    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    CLOTHING = "clothing"
    SHELTER = "shelter"
    OTHER = "other"


class ReportTypeEnum(str, enum.Enum):
    """Report type enumeration"""

    EMERGENCY = "emergency"
    DAMAGE = "damage"
    RESOURCE = "resource"
    STATUS = "status"
    OTHER = "other"


class ReportStatusEnum(str, enum.Enum):
    """Report status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ShelterStatusEnum(str, enum.Enum):
    """Shelter status enumeration"""

    OPEN = "open"
    CLOSED = "closed"
    FULL = "full"
    MAINTENANCE = "maintenance"


class SupplyItemTypeEnum(str, enum.Enum):
    """Supply item type enumeration"""

    FOOD = "food"
    WATER = "water"
    MEDICAL = "medical"
    CLOTHING = "clothing"
    SHELTER = "shelter"
    OTHER = "other"


class ShowerFacilityTypeEnum(str, enum.Enum):
    """Shower facility type enumeration"""

    PUBLIC = "public"
    PRIVATE = "private"
    MOBILE = "mobile"
    TEMPORARY = "temporary"


class WaterTypeEnum(str, enum.Enum):
    """Water type enumeration"""

    DRINKING = "drinking"
    NON_DRINKING = "non_drinking"
    BOTH = "both"


class MedicalStationTypeEnum(str, enum.Enum):
    """Medical station type enumeration"""

    HOSPITAL = "hospital"
    CLINIC = "clinic"
    MOBILE = "mobile"
    FIRST_AID = "first_aid"


class RestroomFacilityTypeEnum(str, enum.Enum):
    """Restroom facility type enumeration"""

    PUBLIC = "public"
    PRIVATE = "private"
    MOBILE = "mobile"
    TEMPORARY = "temporary"


class HumanResourceTypeEnum(str, enum.Enum):
    """Human resource type enumeration"""

    VOLUNTEER = "volunteer"
    PROFESSIONAL = "professional"
    COORDINATOR = "coordinator"
    ADMINISTRATOR = "administrator"


class MentalHealthServiceTypeEnum(str, enum.Enum):
    """Mental health service type enumeration"""

    COUNSELING = "counseling"
    THERAPY = "therapy"
    SUPPORT_GROUP = "support_group"
    CRISIS_INTERVENTION = "crisis_intervention"


class HumanResourceExperienceLevelEnum(str, enum.Enum):
    """Human resource experience level enumeration"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class HumanResourceRoleStatusEnum(str, enum.Enum):
    """Human resource role status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class HumanResourceRoleTypeEnum(str, enum.Enum):
    """Human resource role type enumeration"""

    VOLUNTEER = "volunteer"
    COORDINATOR = "coordinator"
    SUPERVISOR = "supervisor"
    ADMINISTRATOR = "administrator"


class ShelterStatusEnum(enum.Enum):
    open = "open"
    full = "full"
    closed = "closed"
    temporary_closed = "temporary_closed"


class MedicalStationTypeEnum(enum.Enum):
    self_organized = "self_organized"
    fixed_point = "fixed_point"
    shelter_medical = "shelter_medical"


class GeneralStatusEnum(enum.Enum):
    active = "active"
    paused = "paused"
    ended = "ended"
    temporarily_closed = "temporarily_closed"
    temporarily_unavailable = "temporarily_unavailable"
    maintenance = "maintenance"
    out_of_service = "out_of_service"
    completed = "completed"
    cancelled = "cancelled"


class MentalHealthDurationEnum(enum.Enum):
    temporary = "temporary"
    long_term = "long_term"
    both = "both"


class MentalHealthFormatEnum(enum.Enum):
    onsite = "onsite"
    phone = "phone"
    online = "online"
    hybrid = "hybrid"


class AccommodationVacancyEnum(enum.Enum):
    available = "available"
    full = "full"
    unknown = "unknown"
    need_confirm = "need_confirm"


class ShowerFacilityTypeEnum(enum.Enum):
    mobile_shower = "mobile_shower"
    coin_operated = "coin_operated"
    regular_bathroom = "regular_bathroom"


class WaterTypeEnum(enum.Enum):
    drinking_water = "drinking_water"
    bottled_water = "bottled_water"
    filtered_water = "filtered_water"


class RestroomFacilityTypeEnum(enum.Enum):
    mobile_toilet = "mobile_toilet"
    permanent_toilet = "permanent_toilet"
    public_restroom = "public_restroom"


class HumanResourceRoleTypeEnum(enum.Enum):
    general_volunteer = "general_volunteer"
    medical_staff = "medical_staff"
    logistics = "logistics"
    cleaning = "cleaning"
    admin_support = "admin_support"
    driver = "driver"
    security = "security"
    professional = "professional"
    other = "other"


class HumanResourceRoleStatusEnum(enum.Enum):
    completed = "completed"
    pending = "pending"
    partial = "partial"


class HumanResourceExperienceLevelEnum(enum.Enum):
    level_1 = "level_1"
    level_2 = "level_2"
    level_3 = "level_3"


class SupplyItemTypeEnum(enum.Enum):
    food = "food"
    medical_supplies = "medical_supplies"
    groceries = "groceries"
    machinery = "machinery"
    equipment = "equipment"
    plumber = "plumber"
    other = "other"
