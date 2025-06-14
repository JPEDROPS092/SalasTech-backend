from SalasTech.app.models.db import UsuarioDb
from SalasTech.app.core.db_context import session_maker


def add(user: UsuarioDb)-> UsuarioDb:
    with session_maker.begin() as session:
        session.add(user)
        return user

def update(user: UsuarioDb) -> None:
    with session_maker.begin() as session:
        session.query(UsuarioDb).filter(UsuarioDb.id == user.id).update({
            UsuarioDb.name: user.name,
            UsuarioDb.surname: user.surname,
            UsuarioDb.role: user.role,
            UsuarioDb.email: user.email,
            UsuarioDb.password: user.password
        })

def delete(id: int) -> None:
    with session_maker.begin() as session:
        session.query(UsuarioDb).filter(UsuarioDb.id == id).delete()

def get(limit:int = 1000, offset: int = 0) -> list[UsuarioDb]:
    with session_maker() as session:
        return session.query(UsuarioDb).limit(limit).offset(offset).all()

def get_by_id(id: int) -> UsuarioDb | None:
    with session_maker() as session:
        return session.query(UsuarioDb).where(
            UsuarioDb.id == id
        ).first()

def get_by_email(email: str) -> UsuarioDb | None:
    with session_maker.begin() as session:
        return session.query(UsuarioDb).where(
            UsuarioDb.email == email
        ).first()
