from SalasTech.app.models.db import DepartamentoDb
from SalasTech.app.core.db_context import session_maker


def add(department: DepartamentoDb) -> DepartamentoDb:
    with session_maker.begin() as session:
        session.add(department)
        return department

def update(department: DepartamentoDb) -> None:
    with session_maker.begin() as session:
        session.query(DepartamentoDb).filter(DepartamentoDb.id == department.id).update({
            DepartamentoDb.name: department.name,
            DepartamentoDb.code: department.code,
            DepartamentoDb.description: department.description,
            DepartamentoDb.manager_id: department.manager_id
        })

def delete(id: int) -> None:
    with session_maker.begin() as session:
        session.query(DepartamentoDb).filter(DepartamentoDb.id == id).delete()

def get(limit: int = 1000, offset: int = 0) -> list[DepartamentoDb]:
    with session_maker() as session:
        return session.query(DepartamentoDb).limit(limit).offset(offset).all()

def get_by_id(id: int) -> DepartamentoDb | None:
    with session_maker() as session:
        return session.query(DepartamentoDb).where(
            DepartamentoDb.id == id
        ).first()

def get_by_code(code: str) -> DepartamentoDb | None:
    with session_maker() as session:
        return session.query(DepartamentoDb).where(
            DepartamentoDb.code == code
        ).first()
