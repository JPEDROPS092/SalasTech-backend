# Arquitetura do Sistema SalasTech

## Visão Geral

O SalasTech é um sistema de gerenciamento de salas desenvolvido com arquitetura MVC (Model-View-Controller) utilizando o framework FastAPI. O sistema permite o gerenciamento completo de salas, reservas, usuários e departamentos, seguindo as regras de negócio estabelecidas.

## Estrutura do Projeto

```
SalasTech-backend/
├── docs/                   # Documentação do sistema
├── scripts/                # Scripts de utilidade
├── src/
│   └── SalasTech/
│       ├── app/            # Aplicação principal
│       │   ├── controllers/  # Controladores (API e páginas)
│       │   ├── core/         # Configurações e dependências
│       │   ├── exceptions/   # Tratamento de exceções
│       │   ├── mappers/      # Mapeadores de objetos
│       │   ├── migrations/   # Migrações do banco de dados
│       │   ├── models/       # Modelos de dados
│       │   ├── repos/        # Repositórios de acesso a dados
│       │   ├── schedulers/   # Tarefas agendadas
│       │   ├── services/     # Serviços de negócio
│       │   ├── static/       # Arquivos estáticos
│       │   ├── utils/        # Utilitários
│       │   └── views/        # Views para renderização
│       └── cli/            # Interface de linha de comando
└── tests/                  # Testes automatizados
```

## Camadas da Arquitetura

### 1. Models (Modelos)

Os modelos representam as entidades do sistema e são divididos em:

- **Modelos de Banco de Dados (db.py)**: Classes SQLAlchemy que definem o esquema do banco de dados.
- **DTOs (dto.py)**: Objetos de transferência de dados usando Pydantic para validação e serialização.
- **Enums (enums.py)**: Enumerações para valores constantes.

### 2. Repositories (Repositórios)

Os repositórios são responsáveis pelo acesso direto ao banco de dados:

- Implementam operações CRUD básicas
- Encapsulam consultas SQL complexas
- Fornecem métodos específicos para cada entidade

### 3. Services (Serviços)

Os serviços implementam a lógica de negócio:

- Validam regras de negócio
- Orquestram operações entre diferentes repositórios
- Aplicam transformações de dados
- Tratam exceções de negócio

### 4. Controllers (Controladores)

Os controladores gerenciam as requisições HTTP:

- **API Controllers**: Endpoints REST para comunicação via JSON
- **Page Controllers**: Controladores para renderização de páginas web

### 5. Views (Visões)

As views são responsáveis pela renderização de páginas:

- Formatam dados para apresentação
- Renderizam templates Jinja2
- Implementam lógica de apresentação

## Fluxo de Dados

1. O cliente faz uma requisição HTTP
2. O controlador recebe a requisição
3. O controlador chama o serviço apropriado
4. O serviço aplica a lógica de negócio
5. O serviço utiliza repositórios para acessar dados
6. O repositório interage com o banco de dados
7. Os dados retornam pelo caminho inverso
8. O controlador retorna a resposta ao cliente

## Componentes Principais

### Entidades

1. **Usuário (User)**
   - Representa os usuários do sistema
   - Possui diferentes níveis de acesso (admin, gestor, usuário comum)
   - Associado a um departamento

2. **Departamento (Department)**
   - Agrupa usuários e salas
   - Possui um gerente responsável

3. **Sala (Room)**
   - Representa os espaços físicos
   - Possui recursos associados
   - Pertence a um departamento

4. **Recurso de Sala (RoomResource)**
   - Equipamentos ou características da sala
   - Associado a uma sala específica

5. **Reserva (Reservation)**
   - Agendamento de uma sala
   - Possui status (pendente, confirmada, cancelada, etc.)
   - Associada a um usuário e uma sala

### Serviços Principais

1. **UserService**
   - Gerenciamento de usuários
   - Autenticação e autorização

2. **DepartmentService**
   - Gerenciamento de departamentos
   - Estatísticas por departamento

3. **RoomService**
   - Gerenciamento de salas e recursos
   - Verificação de disponibilidade

4. **ReservationService**
   - Criação e gerenciamento de reservas
   - Aplicação de regras de negócio
   - Aprovação e cancelamento

5. **NotificationService**
   - Envio de notificações
   - Lembretes de reservas

6. **ReportService**
   - Geração de relatórios
   - Estatísticas de uso

## Segurança

- Autenticação via JWT (JSON Web Tokens)
- Controle de acesso baseado em papéis (RBAC)
- Proteção contra CSRF
- Limitação de taxa de requisições
- Validação de entrada de dados

## Tarefas Agendadas

O sistema possui tarefas agendadas para:

- Atualização automática de status de reservas
- Envio de lembretes
- Aprovação automática de reservas
- Limpeza de dados antigos

## Interface de Linha de Comando (CLI)

O sistema inclui uma CLI para:

- Gerenciamento de usuários
- Gerenciamento de departamentos
- Gerenciamento de salas
- Gerenciamento de reservas

## Tecnologias Utilizadas

- **FastAPI**: Framework web de alta performance
- **SQLAlchemy**: ORM para acesso ao banco de dados
- **Pydantic**: Validação de dados e serialização
- **Alembic**: Migrações de banco de dados
- **Jinja2**: Engine de templates
- **Typer**: Framework para CLI
- **Rich**: Formatação rica para CLI
- **JWT**: Autenticação baseada em tokens
- **Pytest**: Framework de testes