from fastapi import APIRouter
from fastapi import Query
from fastapi import Path
from fastapi import Depends

from app.models import dto
from app.services import department_service
from app.core import dependencies


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)

@router.get("", response_model=list[dto.DepartmentResponse])
def get_all(limit: int = Query(1000, gt=0), offset: int = Query(0, ge=0)):
    """
    Retorna todos os departamentos
    """
    return department_service.get_all(limit, offset)

@router.get("/{id}", response_model=dto.DepartmentResponse)
def get_by_id(id: int = Path(ge=1)):
    """
    Retorna um departamento pelo ID
    """
    return department_service.get_by_id(id)

@router.get("/code/{code}", response_model=dto.DepartmentResponse)
def get_by_code(code: str):
    """
    Retorna um departamento pelo código
    """
    return department_service.get_by_code(code)

@router.post("", status_code=201, response_model=dto.DepartmentResponse)
def create_department(department: dto.DepartmentCreate, user: dependencies.admin_dependency):
    """
    Cria um novo departamento (apenas administradores)
    """
    return department_service.create_department(department)

@router.put("/{id}", response_model=dto.DepartmentResponse)
def update_department(id: int, department: dto.DepartmentCreate, user: dependencies.admin_dependency):
    """
    Atualiza um departamento existente (apenas administradores)
    """
    return department_service.update_department(id, department)

@router.delete("/{id}", status_code=204)
def delete_department(id: int, user: dependencies.admin_dependency):
    """
    Exclui um departamento (apenas administradores)
    """
    department_service.delete_department(id)

@router.put("/{id}/manager/{manager_id}", response_model=dto.DepartmentResponse)
def assign_manager(id: int, manager_id: int, user: dependencies.admin_dependency):
    """
    Atribui um gerente a um departamento (apenas administradores)
    """
    return department_service.assign_manager(id, manager_id)

@router.get("/{id}/stats", response_model=dict)
def get_department_stats(id: int, user: dependencies.user_dependency):
    """
    Retorna estatísticas do departamento
    """
    return department_service.get_department_stats(id)
