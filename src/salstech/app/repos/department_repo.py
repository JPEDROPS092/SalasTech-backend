from salstech.app.models.db import DepartmentDb
from salstech.app.core.db_context import session_maker


def add(department: DepartmentDb) -> DepartmentDb:
    with session_maker.begin() as session:
        session.add(department)
        return department

def update(department: DepartmentDb) -> None:
    with session_maker.begin() as session:
        session.query(DepartmentDb).filter(DepartmentDb.id == department.id).update({
            DepartmentDb.name: department.name,
            DepartmentDb.code: department.code,
            DepartmentDb.description: department.description,
            DepartmentDb.manager_id: department.manager_id
        })

def delete(id: int) -> None:
    with session_maker.begin() as session:
        session.query(DepartmentDb).filter(DepartmentDb.id == id).delete()

def get(limit: int = 1000, offset: int = 0) -> list[DepartmentDb]:
    with session_maker() as session:
        return session.query(DepartmentDb).limit(limit).offset(offset).all()

def get_by_id(id: int) -> DepartmentDb | None:
    with session_maker() as session:
        return session.query(DepartmentDb).where(
            DepartmentDb.id == id
        ).first()

def get_by_code(code: str) -> DepartmentDb | None:
    with session_maker() as session:
        return session.query(DepartmentDb).where(
            DepartmentDb.code == code
        ).first()
