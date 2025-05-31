from sqlalchemy import Integer, Float, String, Enum, DateTime, ForeignKey, Text, Boolean, Index
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship

from app.models import enums


Base = declarative_base()

class DepartmentDb(Base):
    __tablename__ = 'departments'
    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name = mapped_column("name", String, nullable=False)
    code = mapped_column("code", String, nullable=False, unique=True, index=True)
    description = mapped_column("description", Text, nullable=True)
    manager_id = mapped_column("manager_id", Integer, ForeignKey('users.id'), nullable=True, index=True)
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    
    # Indexes
    __table_args__ = (
        Index('ix_departments_name', 'name'),
    )
    
    # Relationships
    users = relationship("UserDb", back_populates="department", foreign_keys="UserDb.department_id")
    manager = relationship("UserDb", foreign_keys=[manager_id])
    rooms = relationship("RoomDb", back_populates="department")

class UserDb(Base):
    __tablename__ = 'users'
    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    name = mapped_column("name", String, nullable=False)
    surname = mapped_column("surname", String, nullable=False)
    role = mapped_column("role", Enum(enums.UserRole), default=enums.UserRole.USER, index=True)
    email = mapped_column("email", String, unique=True, index=True, nullable=False)
    password = mapped_column("password", String, nullable=False)
    department_id = mapped_column("department_id", Integer, ForeignKey('departments.id'), nullable=True, index=True)
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    
    # Indexes
    __table_args__ = (
        Index('ix_users_name_surname', 'name', 'surname'),
    )
    
    # Relationships
    department = relationship("DepartmentDb", back_populates="users", foreign_keys=[department_id])
    reservations = relationship("ReservationDb", back_populates="user", foreign_keys="ReservationDb.user_id")
    approved_reservations = relationship("ReservationDb", back_populates="approved_by_user", foreign_keys="ReservationDb.approved_by")

# one to one relationship
class TaxAccountDb(Base):
    __tablename__ = 'tax_accounts'
    id = mapped_column("id", Integer, ForeignKey("users.id"), index=True, primary_key=True)
    rate = mapped_column("rate", Float(precision=2), nullable=False)
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())

# one to many relationship
class SalaryDb(Base):
    __tablename__ = 'salaries'
    id = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    user_id = mapped_column("user_id", Integer(), ForeignKey('users.id'), nullable=False, index=True)
    amount = mapped_column("amount", Float(precision=2), nullable=False)
    amount_hours = mapped_column("amount_hours", Float(precision=1), nullable=False)
    salary_date = mapped_column("salary_date", DateTime(), nullable=False, index=True)
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())

class RoomDb(Base):
    __tablename__ = 'rooms'
    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    code = mapped_column("code", String, unique=True, nullable=False, index=True)
    name = mapped_column("name", String, nullable=False, index=True)
    capacity = mapped_column("capacity", Integer, nullable=False, index=True)
    building = mapped_column("building", String, nullable=False, index=True)
    floor = mapped_column("floor", String, nullable=False, index=True)
    department_id = mapped_column("department_id", Integer, ForeignKey('departments.id'), nullable=False, index=True)
    status = mapped_column("status", Enum(enums.RoomStatus), default=enums.RoomStatus.ATIVA, nullable=False, index=True)
    responsible = mapped_column("responsible", String, nullable=True)
    description = mapped_column("description", Text, nullable=True)
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    
    # Indexes for combined queries
    __table_args__ = (
        Index('ix_rooms_building_floor', 'building', 'floor'),
        Index('ix_rooms_capacity_status', 'capacity', 'status'),
    )
    
    # Relationships
    department = relationship("DepartmentDb", back_populates="rooms")
    resources = relationship("RoomResourceDb", back_populates="room", cascade="all, delete-orphan")
    reservations = relationship("ReservationDb", back_populates="room", cascade="all, delete-orphan")

class RoomResourceDb(Base):
    __tablename__ = 'room_resources'
    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    room_id = mapped_column("room_id", Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    resource_name = mapped_column("resource_name", String, nullable=False, index=True)
    quantity = mapped_column("quantity", Integer, default=1, nullable=False)
    description = mapped_column("description", Text, nullable=True)
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    
    # Relationships
    room = relationship("RoomDb", back_populates="resources")

class ReservationDb(Base):
    __tablename__ = 'reservations'
    id = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    room_id = mapped_column("room_id", Integer, ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = mapped_column("user_id", Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = mapped_column("title", String, nullable=False)
    description = mapped_column("description", Text, nullable=True)
    start_datetime = mapped_column("start_datetime", DateTime(), nullable=False, index=True)
    end_datetime = mapped_column("end_datetime", DateTime(), nullable=False, index=True)
    status = mapped_column("status", Enum(enums.ReservationStatus), default=enums.ReservationStatus.PENDENTE, nullable=False, index=True)
    approved_by = mapped_column("approved_by", Integer, ForeignKey('users.id'), nullable=True, index=True)
    approved_at = mapped_column("approved_at", DateTime(), nullable=True)
    cancellation_reason = mapped_column("cancellation_reason", Text, nullable=True)
    created_at = mapped_column("created_at", DateTime(), server_default=current_timestamp())
    updated_at = mapped_column("updated_at", DateTime(), server_default=current_timestamp(), server_onupdate=current_timestamp())
    
    # Indexes for combined queries
    __table_args__ = (
        # Index for date range queries
        Index('ix_reservations_datetime_range', 'start_datetime', 'end_datetime'),
        # Index for room availability queries
        Index('ix_reservations_room_datetime', 'room_id', 'start_datetime', 'end_datetime', 'status'),
        # Index for user reservation queries
        Index('ix_reservations_user_status', 'user_id', 'status'),
    )
    
    # Relationships
    room = relationship("RoomDb", back_populates="reservations")
    user = relationship("UserDb", back_populates="reservations", foreign_keys=[user_id])
    approved_by_user = relationship("UserDb", back_populates="approved_reservations", foreign_keys=[approved_by])