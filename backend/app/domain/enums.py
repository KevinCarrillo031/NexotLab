from enum import StrEnum


class ProfileType(StrEnum):
    ENTREPRENEUR = "entrepreneur"
    COMPANY = "company"
    RESEARCHER = "researcher"
    CITIZEN = "citizen"


class ProposalStatus(StrEnum):
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs-improvement"
    EVALUATING = "evaluating"


class ProposalCategory(StrEnum):
    DIGITAL_TRANSFORMATION = "digital-transformation"
    DIGITAL_ECONOMY = "digital-economy"
    SUSTAINABILITY = "sustainability"
    HEALTH_TECH = "health-tech"
    EDUCATION_TECH = "edtech"
    AGRITECH = "agritech"
    SMART_CITIES = "smart-cities"
    FINTECH = "fintech"
    CIRCULAR_ECONOMY = "circular-economy"
    OPEN_DATA = "open-data"


class NotificationType(StrEnum):
    POSITIVE = "positive"
    IMPROVEMENT = "improvement"
    SOCIAL = "social"


class CollaboratorStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"


class Sector(StrEnum):
    AGRO = "agro"
    HEALTH = "health"
    EDUCATION = "education"
    ENERGY = "energy"
    MOBILITY = "mobility"
    FINTECH = "fintech"
    GOVERNMENT = "government"
    ENVIRONMENT = "environment"
