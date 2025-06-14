from SalasTech.app.models import db
from SalasTech.app.models import dto


def db_to_get_dto(user_db: db.UsuarioDb) -> dto.UsuarioDTO:
    """Convert a User DB object to a GetUser DTO"""
    return dto.UsuarioDTO(
        id=user_db.id,
        nome=user_db.nome,
        sobrenome=user_db.sobrenome,
        papel=user_db.papel,
        email=user_db.email,
        atualizado_em=user_db.atualizado_em,
        criado_em=user_db.criado_em
    )