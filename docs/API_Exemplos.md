# Exemplos de Uso da API SalasTech

Este documento apresenta exemplos práticos de uso da API SalasTech, demonstrando os principais fluxos de trabalho e operações.

## Autenticação

### Login

**Requisição:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@exemplo.com",
    "password": "Senha123!"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Admin",
    "surname": "Sistema",
    "email": "admin@exemplo.com",
    "role": "admin"
  }
}
```

## Fluxo de Gerenciamento de Salas

### 1. Listar Departamentos

**Requisição:**
```bash
curl -X GET http://localhost:8000/api/departments \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

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
  },
  {
    "id": 2,
    "name": "Departamento de RH",
    "code": "RH",
    "description": "Recursos Humanos",
    "manager_id": 2,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

### 2. Criar uma Nova Sala

**Requisição:**
```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SALA101",
    "name": "Sala de Reuniões 101",
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
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "code": "SALA101",
  "name": "Sala de Reuniões 101",
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
    },
    {
      "id": 2,
      "room_id": 1,
      "resource_name": "Quadro Branco",
      "quantity": 1,
      "description": "Quadro branco 2m x 1m",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    }
  ],
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 3. Listar Salas

**Requisição:**
```bash
curl -X GET http://localhost:8000/api/rooms \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
[
  {
    "id": 1,
    "code": "SALA101",
    "name": "Sala de Reuniões 101",
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
      },
      {
        "id": 2,
        "room_id": 1,
        "resource_name": "Quadro Branco",
        "quantity": 1,
        "description": "Quadro branco 2m x 1m",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:00:00"
      }
    ],
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

### 4. Atualizar uma Sala

**Requisição:**
```bash
curl -X PUT http://localhost:8000/api/rooms/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sala de Reuniões 101 - Atualizada",
    "capacity": 12,
    "resources": [
      {
        "resource_name": "Projetor",
        "quantity": 1,
        "description": "Projetor HDMI atualizado"
      },
      {
        "resource_name": "Quadro Branco",
        "quantity": 1,
        "description": "Quadro branco 2m x 1m"
      },
      {
        "resource_name": "TV",
        "quantity": 1,
        "description": "Smart TV 55 polegadas"
      }
    ]
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "code": "SALA101",
  "name": "Sala de Reuniões 101 - Atualizada",
  "capacity": 12,
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
      "description": "Projetor HDMI atualizado",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    },
    {
      "id": 2,
      "room_id": 1,
      "resource_name": "Quadro Branco",
      "quantity": 1,
      "description": "Quadro branco 2m x 1m",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    },
    {
      "id": 3,
      "room_id": 1,
      "resource_name": "TV",
      "quantity": 1,
      "description": "Smart TV 55 polegadas",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    }
  ],
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

## Fluxo de Reservas

### 1. Verificar Disponibilidade de Sala

**Requisição:**
```bash
curl -X GET "http://localhost:8000/api/rooms/1/availability?start_datetime=2023-06-01T10:00:00&end_datetime=2023-06-01T12:00:00" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
{
  "available": true,
  "room_id": 1,
  "start_datetime": "2023-06-01T10:00:00",
  "end_datetime": "2023-06-01T12:00:00"
}
```

### 2. Criar uma Reserva

**Requisição:**
```bash
curl -X POST http://localhost:8000/api/reservations \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": 1,
    "title": "Reunião de Planejamento",
    "description": "Planejamento do próximo trimestre",
    "start_datetime": "2023-06-01T10:00:00",
    "end_datetime": "2023-06-01T12:00:00"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "room_id": 1,
  "user_id": 1,
  "title": "Reunião de Planejamento",
  "description": "Planejamento do próximo trimestre",
  "start_datetime": "2023-06-01T10:00:00",
  "end_datetime": "2023-06-01T12:00:00",
  "status": "CONFIRMADA",
  "approved_by": 1,
  "approved_at": "2023-01-01T00:00:00",
  "cancellation_reason": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 3. Listar Minhas Reservas

**Requisição:**
```bash
curl -X GET http://localhost:8000/api/reservations/my \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
[
  {
    "id": 1,
    "room_id": 1,
    "user_id": 1,
    "title": "Reunião de Planejamento",
    "description": "Planejamento do próximo trimestre",
    "start_datetime": "2023-06-01T10:00:00",
    "end_datetime": "2023-06-01T12:00:00",
    "status": "CONFIRMADA",
    "approved_by": 1,
    "approved_at": "2023-01-01T00:00:00",
    "cancellation_reason": null,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

### 4. Atualizar uma Reserva

**Requisição:**
```bash
curl -X PUT http://localhost:8000/api/reservations/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Reunião de Planejamento Estratégico",
    "description": "Planejamento do próximo trimestre com diretoria",
    "start_datetime": "2023-06-01T10:30:00",
    "end_datetime": "2023-06-01T12:30:00"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "room_id": 1,
  "user_id": 1,
  "title": "Reunião de Planejamento Estratégico",
  "description": "Planejamento do próximo trimestre com diretoria",
  "start_datetime": "2023-06-01T10:30:00",
  "end_datetime": "2023-06-01T12:30:00",
  "status": "PENDENTE",
  "approved_by": null,
  "approved_at": null,
  "cancellation_reason": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 5. Aprovar uma Reserva (Gestor/Admin)

**Requisição:**
```bash
curl -X POST http://localhost:8000/api/reservations/1/approve \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
{
  "id": 1,
  "room_id": 1,
  "user_id": 1,
  "title": "Reunião de Planejamento Estratégico",
  "description": "Planejamento do próximo trimestre com diretoria",
  "start_datetime": "2023-06-01T10:30:00",
  "end_datetime": "2023-06-01T12:30:00",
  "status": "CONFIRMADA",
  "approved_by": 2,
  "approved_at": "2023-01-01T00:00:00",
  "cancellation_reason": null,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 6. Cancelar uma Reserva

**Requisição:**
```bash
curl -X DELETE "http://localhost:8000/api/reservations/1?reason=Reunião cancelada pela diretoria" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```
204 No Content
```

## Fluxo de Relatórios

### 1. Gerar Relatório de Ocupação

**Requisição:**
```bash
curl -X GET "http://localhost:8000/api/reports/occupancy?start_date=2023-06-01T00:00:00&end_date=2023-06-30T23:59:59" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
[
  {
    "room_id": 1,
    "room_code": "SALA101",
    "room_name": "Sala de Reuniões 101 - Atualizada",
    "total_reservations": 5,
    "total_hours": 10.5,
    "occupancy_rate": 15.2
  },
  {
    "room_id": 2,
    "room_code": "SALA102",
    "room_name": "Sala de Reuniões 102",
    "total_reservations": 8,
    "total_hours": 16.0,
    "occupancy_rate": 23.1
  }
]
```

### 2. Gerar Relatório de Uso por Departamento

**Requisição:**
```bash
curl -X GET "http://localhost:8000/api/reports/department-usage?start_date=2023-06-01T00:00:00&end_date=2023-06-30T23:59:59" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
[
  {
    "department_id": 1,
    "department_name": "Departamento de TI",
    "total_rooms": 3,
    "total_reservations": 15,
    "rooms_usage": [
      {
        "room_id": 1,
        "room_code": "SALA101",
        "room_name": "Sala de Reuniões 101 - Atualizada",
        "total_reservations": 5,
        "total_hours": 10.5,
        "occupancy_rate": 15.2
      },
      {
        "room_id": 2,
        "room_code": "SALA102",
        "room_name": "Sala de Reuniões 102",
        "total_reservations": 8,
        "total_hours": 16.0,
        "occupancy_rate": 23.1
      },
      {
        "room_id": 3,
        "room_code": "SALA103",
        "room_name": "Sala de Reuniões 103",
        "total_reservations": 2,
        "total_hours": 4.0,
        "occupancy_rate": 5.8
      }
    ]
  },
  {
    "department_id": 2,
    "department_name": "Departamento de RH",
    "total_rooms": 2,
    "total_reservations": 10,
    "rooms_usage": [
      {
        "room_id": 4,
        "room_code": "SALA201",
        "room_name": "Sala de Reuniões 201",
        "total_reservations": 6,
        "total_hours": 12.0,
        "occupancy_rate": 17.3
      },
      {
        "room_id": 5,
        "room_code": "SALA202",
        "room_name": "Sala de Reuniões 202",
        "total_reservations": 4,
        "total_hours": 8.0,
        "occupancy_rate": 11.5
      }
    ]
  }
]
```

### 3. Exportar Relatório

**Requisição:**
```bash
curl -X GET "http://localhost:8000/api/reports/export?report_type=usage&start_date=2023-06-01T00:00:00&end_date=2023-06-30T23:59:59&format=json&department_id=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
{
  "report_type": "usage",
  "format": "json",
  "period": {
    "start_date": "2023-06-01T00:00:00",
    "end_date": "2023-06-30T23:59:59"
  },
  "department_id": 1,
  "data": [
    {
      "room_id": 1,
      "room_code": "SALA101",
      "room_name": "Sala de Reuniões 101 - Atualizada",
      "building": "Prédio A",
      "floor": "1",
      "department_id": 1,
      "capacity": 12,
      "total_reservations": 5,
      "total_hours": 10.5,
      "occupancy_rate": 15.2
    },
    {
      "room_id": 2,
      "room_code": "SALA102",
      "room_name": "Sala de Reuniões 102",
      "building": "Prédio A",
      "floor": "1",
      "department_id": 1,
      "capacity": 8,
      "total_reservations": 8,
      "total_hours": 16.0,
      "occupancy_rate": 23.1
    },
    {
      "room_id": 3,
      "room_code": "SALA103",
      "room_name": "Sala de Reuniões 103",
      "building": "Prédio A",
      "floor": "1",
      "department_id": 1,
      "capacity": 6,
      "total_reservations": 2,
      "total_hours": 4.0,
      "occupancy_rate": 5.8
    }
  ]
}
```

## Fluxo de Gerenciamento de Usuários

### 1. Criar um Novo Usuário

**Requisição:**
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria",
    "surname": "Silva",
    "email": "maria.silva@exemplo.com",
    "password": "Senha123!",
    "department_id": 1,
    "role": "user"
  }'
```

**Resposta:**
```json
{
  "id": 3,
  "name": "Maria",
  "surname": "Silva",
  "email": "maria.silva@exemplo.com",
  "role": "user",
  "department_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

### 2. Listar Usuários

**Requisição:**
```bash
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
[
  {
    "id": 1,
    "name": "Admin",
    "surname": "Sistema",
    "email": "admin@exemplo.com",
    "role": "admin",
    "department_id": null,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  },
  {
    "id": 2,
    "name": "João",
    "surname": "Silva",
    "email": "joao.silva@exemplo.com",
    "role": "gestor",
    "department_id": 1,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  },
  {
    "id": 3,
    "name": "Maria",
    "surname": "Silva",
    "email": "maria.silva@exemplo.com",
    "role": "user",
    "department_id": 1,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00"
  }
]
```

### 3. Atualizar Nome do Usuário

**Requisição:**
```bash
curl -X PUT http://localhost:8000/api/users/3/name \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria",
    "surname": "Oliveira"
  }'
```

**Resposta:**
```json
{
  "id": 3,
  "name": "Maria",
  "surname": "Oliveira",
  "email": "maria.silva@exemplo.com",
  "role": "user",
  "department_id": 1,
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

## Fluxo de Manutenção de Salas

### 1. Agendar Manutenção

**Requisição:**
```bash
curl -X POST "http://localhost:8000/api/rooms/1/maintenance?start_datetime=2023-07-01T08:00:00&end_datetime=2023-07-01T18:00:00&description=Manutenção do ar condicionado" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```
204 No Content
```

### 2. Verificar Status da Sala

**Requisição:**
```bash
curl -X GET http://localhost:8000/api/rooms/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Resposta:**
```json
{
  "id": 1,
  "code": "SALA101",
  "name": "Sala de Reuniões 101 - Atualizada",
  "capacity": 12,
  "building": "Prédio A",
  "floor": "1",
  "department_id": 1,
  "status": "MANUTENCAO",
  "responsible": "João Silva",
  "description": "Sala de reuniões com projetor",
  "resources": [
    {
      "id": 1,
      "room_id": 1,
      "resource_name": "Projetor",
      "quantity": 1,
      "description": "Projetor HDMI atualizado",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    },
    {
      "id": 2,
      "room_id": 1,
      "resource_name": "Quadro Branco",
      "quantity": 1,
      "description": "Quadro branco 2m x 1m",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    },
    {
      "id": 3,
      "room_id": 1,
      "resource_name": "TV",
      "quantity": 1,
      "description": "Smart TV 55 polegadas",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    }
  ],
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```