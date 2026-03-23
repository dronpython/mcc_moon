from pydantic import BaseModel, field_validator
from typing import List, Optional, Union


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int
    children: List['Activity'] = []

    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    building_id: int
    phone_numbers: List[str] = []

    @field_validator('phone_numbers', mode='before')
    @classmethod
    def parse_phones(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return v.split(',') if v else []
        return v


class OrganizationCreate(OrganizationBase):
    activity_ids: List[int] = []


class Organization(OrganizationBase):
    id: int
    building: Building
    activities: List[Activity] = []

    class Config:
        from_attributes = True


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    building_id: Optional[int] = None
    phone_numbers: Optional[List[str]] = None
    activity_ids: Optional[List[int]] = None


Activity.model_rebuild()
