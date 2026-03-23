from sqlalchemy.orm import Session
from typing import List
from app import models


# Building CRUD
def get_building(db: Session, building_id: int):
    return db.query(models.Building).filter(models.Building.id == building_id).first()


def get_buildings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Building).offset(skip).limit(limit).all()


# Activity CRUD
def get_activity(db: Session, activity_id: int):
    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()


def get_activity_with_children_ids(db: Session, activity_id: int) -> List[int]:
    """Получить ID активности и всех её потомков"""
    activity_ids = [activity_id]
    children = db.query(models.Activity).filter(models.Activity.parent_id == activity_id).all()

    for child in children:
        activity_ids.extend(get_activity_with_children_ids(db, child.id))

    return activity_ids


# Organization CRUD
def get_organization(db: Session, organization_id: int):
    return db.query(models.Organization).filter(models.Organization.id == organization_id).first()


def get_organizations_by_building(db: Session, building_id: int):
    return db.query(models.Organization).filter(models.Organization.building_id == building_id).all()


def get_organizations_by_radius(db: Session, latitude: float, longitude: float, radius_km: float):
    """Поиск организаций в радиусе (приблизительный расчет)"""
    # Приблизительное преобразование км в градусы
    lat_km = 111.0
    lon_km = 111.0 * latitude
    lat_delta = radius_km / lat_km
    lon_delta = radius_km / lon_km

    buildings = db.query(models.Building).filter(
        models.Building.latitude.between(latitude - lat_delta, latitude + lat_delta),
        models.Building.longitude.between(longitude - lon_delta, longitude + lon_delta)
    ).all()

    building_ids = [b.id for b in buildings]
    return db.query(models.Organization).filter(
        models.Organization.building_id.in_(building_ids)
    ).all()


def get_organizations_by_activity_hierarchy(db: Session, activity_id: int):
    """Организации по виду деятельности с учетом всех дочерних (макс 3 уровня)"""
    activity_ids = [activity_id]

    # 1 уровень
    children = db.query(models.Activity).filter(models.Activity.parent_id == activity_id).all()
    activity_ids.extend([c.id for c in children])

    # 2 уровень
    for child in children:
        grandchildren = db.query(models.Activity).filter(models.Activity.parent_id == child.id).all()
        activity_ids.extend([g.id for g in grandchildren])

        # 3 уровень
        for grand in grandchildren:
            great_grand = db.query(models.Activity).filter(models.Activity.parent_id == grand.id).all()
            activity_ids.extend([gg.id for gg in great_grand])

    activity_ids = list(set(activity_ids))

    return db.query(models.Organization).join(
        models.organization_activity
    ).filter(
        models.organization_activity.c.activity_id.in_(activity_ids)
    ).distinct().all()


def get_organizations_by_bbox(db: Session, min_lat: float, max_lat: float, min_lon: float, max_lon: float):
    buildings = db.query(models.Building).filter(
        models.Building.latitude.between(min_lat, max_lat),
        models.Building.longitude.between(min_lon, max_lon)
    ).all()
    building_ids = [b.id for b in buildings]
    return db.query(models.Organization).filter(
        models.Organization.building_id.in_(building_ids)
    ).all()


def search_organizations_by_name(db: Session, name: str):
    return db.query(models.Organization).filter(
        models.Organization.name.ilike(f"%{name}%")
    ).all()