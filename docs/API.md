# Documentação da API SalasTech

## Visão Geral

A API SalasTech fornece endpoints para gerenciamento completo do sistema de reservas de salas, incluindo:

- Autenticação e gerenciamento de usuários
- Gerenciamento de departamentos
- Gerenciamento de salas e recursos
- Reservas de salas com regras de negócio
- Relatórios e estatísticas

## Base URL

```
http://localhost:8000/api
```

## Autenticação

A API utiliza autenticação baseada em tokens JWT.

### Login

```
POST /auth/login
```

**Corpo da requisição:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Nome",
    "surname": "Sobrenome",
    "email": "usuario@exemplo.com",
    "role": "user"
  }
}
```

### Autenticação em Requisições

Inclua o token JWT no cabeçalho de autorização:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### Usuários

#### Listar Usuários

```
GET /users?limit=10&offset=0
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de usuários a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)

**Resposta:**
```json
[
  {
    "id": 1,
    "name": "Nome",
    "surname": "Sobrenome",
    "email": "usuario@exemplo.com",
    "role": "user",
    "department_id": 1,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

#### Obter Usuário por ID

```
GET /users/{id}
```

**Resposta:**
```json
{
  "id": 1,
  "name": "Nome",
  "surname": "Sobrenome",
  "email": "usuario@exemplo.com",
  "role": "user",
  "department_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

#### Criar Usuário

```
POST /users
```

**Corpo da requisição:**
```json
{
  "name": "Nome",
  "surname": "Sobrenome",
  "email": "usuario@exemplo.com",
  "password": "Senha123!",
  "department_id": 1,
  "role": "user"
}
```

**Resposta:**
```json
{
  "id": 1,
  "name": "Nome",
  "surname": "Sobrenome",
  "email": "usuario@exemplo.com",
  "role": "user",
  "department_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

#### Atualizar Nome do Usuário

```
PUT /users/{id}/name
```

**Corpo da requisição:**
```json
{
  "name": "Novo Nome",
  "surname": "Novo Sobrenome"
}
```

#### Atualizar Senha do Usuário

```
PUT /users/{id}/password
```

**Corpo da requisição:**
```json
{
  "old_password": "SenhaAntiga123!",
  "new_password": "SenhaNova456!"
}
```

#### Excluir Usuário

```
DELETE /users/{id}
```

### Departamentos

#### Listar Departamentos

```
GET /departments?limit=10&offset=0
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de departamentos a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)

**Resposta:**
```json
[
  {
    "id": 1,
    "name": "Departamento de TI",
    "code": "TI",
    "description": "Departamento de Tecnologia da Informação",
    "manager_id": 1,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

#### Obter Departamento por ID

```
GET /departments/{id}
```

**Resposta:**
```json
{
  "id": 1,
  "name": "Departamento de TI",
  "code": "TI",
  "description": "Departamento de Tecnologia da Informação",
  "manager_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

#### Obter Departamento por Código

```
GET /departments/code/{code}
```

#### Criar Departamento

```
POST /departments
```

**Corpo da requisição:**
```json
{
  "name": "Departamento de TI",
  "code": "TI",
  "description": "Departamento de Tecnologia da Informação",
  "manager_id": 1
}
```

#### Atualizar Departamento

```
PUT /departments/{id}
```

**Corpo da requisição:**
```json
{
  "name": "Novo Nome do Departamento",
  "code": "NOVO",
  "description": "Nova descrição",
  "manager_id": 2
}
```

#### Excluir Departamento

```
DELETE /departments/{id}
```

#### Atribuir Gerente ao Departamento

```
PUT /departments/{id}/manager/{manager_id}
```

#### Obter Estatísticas do Departamento

```
GET /departments/{id}/stats
```

**Resposta:**
```json
{
  "department_id": 1,
  "department_name": "Departamento de TI",
  "total_rooms": 5,
  "total_users": 10
}
```

### Salas

#### Listar Salas

```
GET /rooms?limit=10&offset=0&status=ATIVA&department_id=1
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de salas a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)
- `status` (opcional): Filtrar por status (ATIVA, INATIVA, MANUTENCAO)
- `department_id` (opcional): Filtrar por departamento

**Resposta:**
```json
[
  {
    "id": 1,
    "code": "SALA001",
    "name": "Sala de Reuniões 1",
    "capacity": 10,
    "building": "Prédio A",
    "floor": "1",
    "department_id": 1,
    "status": "ATIVA",
    "responsible": "João Silva",
    "description": "Sala de reuniões com projetor",
    "resources": [
      {
        "id": 1,
        "room_id": 1,
        "resource_name": "Projetor",
        "quantity": 1,
        "description": "Projetor HDMI",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
      }
    ],
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

#### Obter Sala por ID

```
GET /rooms/{id}
```

#### Obter Sala por Código

```
GET /rooms/code/{code}
```

#### Criar Sala

```
POST /rooms
```

**Corpo da requisição:**
```json
{
  "code": "SALA001",
  "name": "Sala de Reuniões 1",
  "capacity": 10,
  "building": "Prédio A",
  "floor": "1",
  "department_id": 1,
  "status": "ATIVA",
  "responsible": "João Silva",
  "description": "Sala de reuniões com projetor",
  "resources": [
    {
      "resource_name": "Projetor",
      "quantity": 1,
      "description": "Projetor HDMI"
    },
    {
      "resource_name": "Quadro Branco",
      "quantity": 1,
      "description": "Quadro branco 2m x 1m"
    }
  ]
}
```

#### Atualizar Sala

```
PUT /rooms/{id}
```

**Corpo da requisição:**
```json
{
  "name": "Novo Nome da Sala",
  "capacity": 15,
  "status": "MANUTENCAO",
  "resources": [
    {
      "resource_name": "Projetor",
      "quantity": 1,
      "description": "Projetor HDMI atualizado"
    }
  ]
}
```

#### Excluir Sala

```
DELETE /rooms/{id}
```

#### Buscar Salas

```
GET /rooms/search?query=reunião
```

**Parâmetros de consulta:**
- `query`: Termo de busca (mínimo 2 caracteres)
- `limit` (opcional): Número máximo de resultados (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)

#### Obter Salas Disponíveis

```
GET /rooms/available?start_datetime=2023-01-01T10:00:00&end_datetime=2023-01-01T12:00:00&department_id=1&capacity=10
```

**Parâmetros de consulta:**
- `start_datetime`: Data/hora de início (formato ISO)
- `end_datetime`: Data/hora de término (formato ISO)
- `department_id` (opcional): Filtrar por departamento
- `capacity` (opcional): Capacidade mínima necessária

#### Verificar Disponibilidade de Sala

```
GET /rooms/{id}/availability?start_datetime=2023-01-01T10:00:00&end_datetime=2023-01-01T12:00:00
```

**Parâmetros de consulta:**
- `start_datetime`: Data/hora de início (formato ISO)
- `end_datetime`: Data/hora de término (formato ISO)

**Resposta:**
```json
{
  "available": true,
  "room_id": 1,
  "start_datetime": "2023-01-01T10:00:00",
  "end_datetime": "2023-01-01T12:00:00"
}
```

#### Agendar Manutenção

```
POST /rooms/{id}/maintenance
```

**Parâmetros de consulta:**
- `start_datetime`: Data/hora de início (formato ISO)
- `end_datetime`: Data/hora de término (formato ISO)
- `description`: Descrição da manutenção

#### Obter Estatísticas de Utilização

```
GET /rooms/{id}/utilization?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)

**Resposta:**
```json
{
  "room_id": 1,
  "room_code": "SALA001",
  "room_name": "Sala de Reuniões 1",
  "total_reservations": 15,
  "total_hours": 30.5,
  "occupancy_rate": 25.4
}
```

### Reservas

#### Listar Reservas

```
GET /reservations?limit=10&offset=0&status=CONFIRMADA&room_id=1&user_id=1&start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de reservas a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)
- `status` (opcional): Filtrar por status (PENDENTE, CONFIRMADA, CANCELADA, FINALIZADA, EM_ANDAMENTO)
- `room_id` (opcional): Filtrar por sala
- `user_id` (opcional): Filtrar por usuário
- `start_date` (opcional): Data de início (formato ISO)
- `end_date` (opcional): Data de término (formato ISO)

**Resposta:**
```json
[
  {
    "id": 1,
    "room_id": 1,
    "user_id": 1,
    "title": "Reunião de Projeto",
    "description": "Discussão sobre o novo projeto",
    "start_datetime": "2023-01-01T10:00:00",
    "end_datetime": "2023-01-01T12:00:00",
    "status": "CONFIRMADA",
    "approved_by": 2,
    "approved_at": "2022-12-30T15:00:00",
    "cancellation_reason": null,
    "created_at": "2022-12-30T14:00:00",
    "updated_at": "2022-12-30T15:00:00"
  }
]
```

#### Listar Minhas Reservas

```
GET /reservations/my?limit=10&offset=0&status=CONFIRMADA
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de reservas a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)
- `status` (opcional): Filtrar por status

#### Obter Reserva por ID

```
GET /reservations/{id}
```

#### Criar Reserva

```
POST /reservations
```

**Corpo da requisição:**
```json
{
  "room_id": 1,
  "title": "Reunião de Projeto",
  "description": "Discussão sobre o novo projeto",
  "start_datetime": "2023-01-01T10:00:00",
  "end_datetime": "2023-01-01T12:00:00"
}
```

#### Atualizar Reserva

```
PUT /reservations/{id}
```

**Corpo da requisição:**
```json
{
  "title": "Novo Título da Reunião",
  "description": "Nova descrição",
  "start_datetime": "2023-01-01T11:00:00",
  "end_datetime": "2023-01-01T13:00:00"
}
```

#### Cancelar Reserva

```
DELETE /reservations/{id}?reason=Motivo do cancelamento
```

**Parâmetros de consulta:**
- `reason` (opcional): Motivo do cancelamento

#### Listar Reservas por Sala

```
GET /reservations/room/{room_id}?limit=10&offset=0&status=CONFIRMADA
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de reservas a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)
- `status` (opcional): Filtrar por status

#### Listar Reservas por Usuário

```
GET /reservations/user/{user_id}?limit=10&offset=0&status=CONFIRMADA
```

**Parâmetros de consulta:**
- `limit` (opcional): Número máximo de reservas a retornar (padrão: 1000)
- `offset` (opcional): Offset para paginação (padrão: 0)
- `status` (opcional): Filtrar por status

### Relatórios

#### Relatório de Uso

```
GET /reports/usage?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59&department_id=1
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)
- `department_id` (opcional): Filtrar por departamento

#### Relatório de Ocupação

```
GET /reports/occupancy?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)

#### Relatório de Uso por Departamento

```
GET /reports/department-usage?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)

#### Relatório de Atividade de Usuários

```
GET /reports/user-activity?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59&department_id=1
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)
- `department_id` (opcional): Filtrar por departamento

#### Relatório de Manutenções

```
GET /reports/maintenance?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)

#### Estatísticas Gerais

```
GET /reports/statistics?start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59
```

**Parâmetros de consulta:**
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)

#### Exportar Relatório

```
GET /reports/export?report_type=usage&start_date=2023-01-01T00:00:00&end_date=2023-01-31T23:59:59&format=json&department_id=1
```

**Parâmetros de consulta:**
- `report_type`: Tipo de relatório (usage, occupancy, department, user, maintenance, statistics)
- `start_date`: Data de início (formato ISO)
- `end_date`: Data de término (formato ISO)
- `format`: Formato de exportação (json, csv, pdf)
- `department_id` (opcional): Filtrar por departamento

## Códigos de Status

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `204 No Content`: Requisição bem-sucedida sem conteúdo de resposta
- `400 Bad Request`: Erro na requisição
- `401 Unauthorized`: Autenticação necessária
- `403 Forbidden`: Sem permissão para acessar o recurso
- `404 Not Found`: Recurso não encontrado
- `422 Unprocessable Entity`: Erro de validação
- `500 Internal Server Error`: Erro interno do servidor