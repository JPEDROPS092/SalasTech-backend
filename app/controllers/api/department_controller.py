from fastapi import APIRouter, HTTPException
from fastapi import Query
from fastapi import Path
from fastapi import Depends, status
from sqlalchemy.orm import Session

from app.models import dto
from app.models.db import DepartamentoDb, UsuarioDb
from app.core.db_context import get_db
from app.core.security.middleware import get_current_user, get_admin_user


router = APIRouter(
#    prefix="/departments",
    tags=["Departments"]
)

@router.get("", response_model=list[dto.DepartamentoRespostaDTO])
def get_all(
    limit: int = Query(1000, gt=0), 
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Retorna todos os departamentos
    """
    departamentos = db.query(DepartamentoDb).offset(offset).limit(limit).all()
    return [dto.DepartamentoRespostaDTO.from_orm(dept) for dept in departamentos]

@router.get("/{id}", response_model=dto.DepartamentoRespostaDTO)
def get_by_id(id: int = Path(ge=1), db: Session = Depends(get_db)):
    """
    Retorna um departamento pelo ID
    """
    departamento = db.query(DepartamentoDb).filter(DepartamentoDb.id == id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return dto.DepartamentoRespostaDTO.from_orm(departamento)

@router.get("/code/{code}", response_model=dto.DepartamentoRespostaDTO)
def get_by_code(code: str, db: Session = Depends(get_db)):
    """
    Retorna um departamento pelo código
    """
    departamento = db.query(DepartamentoDb).filter(DepartamentoDb.codigo == code).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return dto.DepartamentoRespostaDTO.from_orm(departamento)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=dto.DepartamentoRespostaDTO)
def create_department(
    department: dto.DepartamentoCriarDTO, 
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cria um novo departamento (apenas administradores)
    """
    # Verificar se código já existe
    existing = db.query(DepartamentoDb).filter(DepartamentoDb.codigo == department.codigo).first()
    if existing:
        raise HTTPException(status_code=409, detail="Código do departamento já existe")
    
    # Criar novo departamento
    dept_db = DepartamentoDb(**department.dict())
    db.add(dept_db)
    db.commit()
    db.refresh(dept_db)
    return dto.DepartamentoRespostaDTO.from_orm(dept_db)

@router.put("/{id}", response_model=dto.DepartamentoRespostaDTO)
def update_department(
    id: int, 
    department: dto.DepartamentoCriarDTO, 
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza um departamento existente (apenas administradores)
    """
    dept = db.query(DepartamentoDb).filter(DepartamentoDb.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    
    # Atualizar campos
    for field, value in department.dict(exclude_unset=True).items():
        setattr(dept, field, value)
    
    db.commit()
    db.refresh(dept)
    return dto.DepartamentoRespostaDTO.from_orm(dept)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    id: int, 
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Exclui um departamento (apenas administradores)
    """
    dept = db.query(DepartamentoDb).filter(DepartamentoDb.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    
    db.delete(dept)
    db.commit()

@router.put("/{id}/manager/{manager_id}", response_model=dto.DepartamentoRespostaDTO)
def assign_manager(
    id: int, 
    manager_id: int, 
    admin_user = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Atribui um gerente a um departamento (apenas administradores)
    """
    dept = db.query(DepartamentoDb).filter(DepartamentoDb.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    
    manager = db.query(UsuarioDb).filter(UsuarioDb.id == manager_id).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    dept.gerente_id = manager_id
    db.commit()
    db.refresh(dept)
    return dto.DepartamentoRespostaDTO.from_orm(dept)

@router.get("/{id}/stats", response_model=dict)
def get_department_stats(
    id: int, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas do departamento
    """
    dept = db.query(DepartamentoDb).filter(DepartamentoDb.id == id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    
    # TODO: Implementar estatísticas reais
    return {
        "department_id": id,
        "name": dept.nome,
        "code": dept.codigo,
        "total_users": db.query(UsuarioDb).filter(UsuarioDb.departamento_id == id).count(),
        "total_rooms": 0,  # TODO: Implementar quando tiver relação com salas
        "active_reservations": 0  # TODO: Implementar quando tiver reservas
    }
