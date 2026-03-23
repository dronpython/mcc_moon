from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Связующая таблица для many-to-many
organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id', ondelete='CASCADE')),
    Column('activity_id', Integer, ForeignKey('activities.id', ondelete='CASCADE')),
    Index('idx_org_activity', 'organization_id', 'activity_id')
)


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(500), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organizations = relationship("Organization", back_populates="building", cascade="all, delete-orphan")

    # Составной индекс для геопоиска
    __table_args__ = (
        Index('idx_buildings_location', 'latitude', 'longitude'),
    )


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('activities.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Activity", remote_side=[id], backref="children")
    organizations = relationship("Organization", secondary=organization_activity, back_populates="activities")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    building_id = Column(Integer, ForeignKey('buildings.id', ondelete='CASCADE'), nullable=False)
    phone_numbers = Column(String(1000))  # Храним номера через запятую
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=organization_activity, back_populates="organizations")