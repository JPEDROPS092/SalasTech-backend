from SalasTech.app.models import db
from SalasTech.app.models import dto
from SalasTech.app.models import enums
from SalasTech.app.repos import department_repo
from SalasTech.app.repos import user_repo

from SalasTech.app.utils import formatting
from SalasTech.app.exceptions.scheme import AppException


def get_all(limit: int = 1000, offset: int = 0) -> list[dto.DepartamentoRespostaDTO]:
    """
    Retorna todos os departamentos
    """
    departments = department_repo.get(limit, offset)
    return [_db_to_response(dept) for dept in departments]


def get_by_id(id: int) -> dto.DepartamentoRespostaDTO:
    """
    Busca um departamento pelo ID
    """
    department = department_repo.get_by_id(id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=404)
    
    return _db_to_response(department)


def get_by_code(code: str) -> dto.DepartamentoRespostaDTO:
    """
    Busca um departamento pelo código
    """
    code_formatted = formatting.format_string(code)
    department = department_repo.get_by_code(code_formatted)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=404)
    
    return _db_to_response(department)


def create_department(obj: dto.DepartamentoCriarDTO) -> dto.DepartamentoRespostaDTO:
    """
    Cria um novo departamento
    """
    # Formatar e validar dados
    name_formatted = formatting.format_string(obj.nome)
    code_formatted = formatting.format_string(obj.codigo)
    
    if name_formatted == "":
        raise AppException(message="Nome é obrigatório", status_code=422)
    
    if code_formatted == "":
        raise AppException(message="Código é obrigatório", status_code=422)
    
    # Verificar se já existe departamento com o mesmo código
    existing_department = department_repo.get_by_code(code_formatted)
    if existing_department is not None:
        raise AppException(message="Já existe um departamento com este código", status_code=422)
    
    # Verificar se o gerente existe, se informado
    if obj.gerente_id:
        manager = user_repo.get_by_id(obj.gerente_id)
        if manager is None:
            raise AppException(message="Gerente não encontrado", status_code=422)
    
    # Criar o departamento
    department = db.DepartamentoDb()
    department.name = name_formatted
    department.code = code_formatted
    department.description = obj.descricao
    department.manager_id = obj.gerente_id
    
    created_department = department_repo.add(department)
    return _db_to_response(created_department)


def update_department(id: int, obj: dto.DepartamentoCriarDTO) -> dto.DepartamentoRespostaDTO:
    """
    Atualiza um departamento existente
    """
    # Verificar se o departamento existe
    department = department_repo.get_by_id(id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=404)
    
    # Formatar e validar dados
    name_formatted = formatting.format_string(obj.nome)
    code_formatted = formatting.format_string(obj.codigo)
    
    if name_formatted == "":
        raise AppException(message="Nome é obrigatório", status_code=422)
    
    if code_formatted == "":
        raise AppException(message="Código é obrigatório", status_code=422)
    
    # Verificar se já existe outro departamento com o mesmo código
    existing_department = department_repo.get_by_code(code_formatted)
    if existing_department is not None and existing_department.id != id:
        raise AppException(message="Já existe um departamento com este código", status_code=422)
    
    # Verificar se o gerente existe, se informado
    if obj.gerente_id:
        manager = user_repo.get_by_id(obj.gerente_id)
        if manager is None:
            raise AppException(message="Gerente não encontrado", status_code=422)
    
    # Atualizar o departamento
    department.name = name_formatted
    department.code = code_formatted
    department.description = obj.descricao
    department.manager_id = obj.gerente_id
    
    department_repo.update(department)
    return _db_to_response(department)


def delete_department(id: int) -> None:
    """
    Exclui um departamento
    """
    # Verificar se o departamento existe
    department = department_repo.get_by_id(id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=404)
    
    # Verificar se existem usuários ou salas vinculados ao departamento
    # Esta verificação seria melhor feita no nível do banco de dados com constraints
    # Mas para fins de demonstração, fazemos aqui
    
    # Excluir o departamento
    try:
        department_repo.delete(id)
    except Exception as e:
        raise AppException(message="Não é possível excluir o departamento. Existem usuários ou salas vinculados a ele.", status_code=422)


def assign_manager(department_id: int, manager_id: int) -> dto.DepartamentoRespostaDTO:
    """
    Atribui um gerente a um departamento
    """
    # Verificar se o departamento existe
    department = department_repo.get_by_id(department_id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=404)
    
    # Verificar se o usuário existe
    manager = user_repo.get_by_id(manager_id)
    if manager is None:
        raise AppException(message="Usuário não encontrado", status_code=404)
    
    # Verificar se o usuário tem permissão para ser gerente
    if manager.role not in [enums.UserRole.ADMIN, enums.UserRole.GESTOR, enums.UserRole.ADMINISTRADOR]:
        raise AppException(message="Usuário não tem permissão para ser gerente", status_code=422)
    
    # Atribuir o gerente
    department.manager_id = manager_id
    department_repo.update(department)
    
    return _db_to_response(department)


def get_department_stats(department_id: int) -> dict:
    """
    Retorna estatísticas do departamento
    """
    # Esta função seria implementada com consultas específicas
    # para obter estatísticas como número de salas, reservas, etc.
    # Por ora, retornamos um placeholder
    
    department = department_repo.get_by_id(department_id)
    if department is None:
        raise AppException(message="Departamento não encontrado", status_code=404)
    
    return {
        "department_id": department_id,
        "department_name": department.name,
        "total_rooms": len(department.rooms) if hasattr(department, 'rooms') else 0,
        "total_users": len(department.users) if hasattr(department, 'users') else 0,
        # Outras estatísticas seriam calculadas com base em consultas específicas
    }


def _db_to_response(department: db.DepartamentoDb) -> dto.DepartamentoRespostaDTO:
    """
    Converte um objeto DepartmentDb para DepartamentoRespostaDTO
    """
    return dto.DepartamentoRespostaDTO(
        id=department.id,
        nome=department.name,
        codigo=department.code,
        descricao=department.description,
        gerente_id=department.manager_id,
        criado_em=department.created_at,
        atualizado_em=department.updated_at
    )
