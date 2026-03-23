from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas, models
from app.database import get_db

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/search", response_model=List[schemas.Organization])
def search_organizations(
        name: Optional[str] = Query(None, min_length=1),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius_km: Optional[float] = Query(None, ge=0),
        min_lat: Optional[float] = Query(None, ge=-90, le=90),
        max_lat: Optional[float] = Query(None, ge=-90, le=90),
        min_lon: Optional[float] = Query(None, ge=-180, le=180),
        max_lon: Optional[float] = Query(None, ge=-180, le=180),
        db: Session = Depends(get_db)
):
    """Поиск организаций по названию, радиусу или прямоугольной области"""
    if name:
        return crud.search_organizations_by_name(db, name)

    if radius_km is not None and lat is not None and lon is not None:
        return crud.get_organizations_by_radius(db, lat, lon, radius_km)

    if all(x is not None for x in [min_lat, max_lat, min_lon, max_lon]):
        return crud.get_organizations_by_bbox(db, min_lat, max_lat, min_lon, max_lon)

    raise HTTPException(status_code=400, detail="Не указаны параметры поиска")


@router.get("/{organization_id}", response_model=schemas.Organization)
def get_organization(
        organization_id: int,
        db: Session = Depends(get_db)
):
    """Вывод информации об организации по её идентификатору"""
    organization = crud.get_organization(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get("/by-building/{building_id}", response_model=List[schemas.Organization])
def get_organizations_by_building(
        building_id: int,
        db: Session = Depends(get_db)
):
    """Список всех организаций находящихся в конкретном здании"""
    building = crud.get_building(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return crud.get_organizations_by_building(db, building_id)


@router.get("/by-activity/{activity_id}", response_model=List[schemas.Organization])
def get_organizations_by_activity(
        activity_id: int,
        db: Session = Depends(get_db)
):
    """Список организаций по виду деятельности (с учетом всех дочерних)"""
    activity = crud.get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return crud.get_organizations_by_activity_hierarchy(db, activity_id)


@router.get("/buildings", response_model=List[schemas.Building])
def get_buildings(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Список зданий"""
    return crud.get_buildings(db, skip=skip, limit=limit)