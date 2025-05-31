# Prompt: Sistema de Gerenciamento de Salas - FastAPI MVC

Implemente um sistema completo de gerenciamento de salas para uma instituição seguindo a arquitetura MVC do projeto FastAPI existente. O sistema deve aplicar todas as regras de negócio especificadas no documento de regras de negócio.

## Estrutura de Arquivos e Responsabilidades

### 1. Models (app/models/)

#### app/models/db.py
**Adicionar as seguintes entidades SQLAlchemy:**

**Room (Sala)**
- Campos: id, code (código único), name, capacity, building, floor, department, status, responsible, description, created_at, updated_at
- Relacionamentos: recursos da sala, reservas
- Validações: código único, capacidade maior que zero

**RoomResource (Recursos da Sala)**
- Campos: id, room_id, resource_name, quantity, description
- Relacionamento: pertence a uma sala

**Reservation (Reserva)**
- Campos: id, room_id, user_id, title, description, start_datetime, end_datetime, status, approved_by, approved_at, cancellation_reason, created_at, updated_at
- Relacionamentos: sala, usuário, aprovador
- Validações: datas, horários, conflitos

**Department (Departamento)**
- Campos: id, name, code, description, manager_id, created_at
- Relacionamento: gerente do departamento

**Atualizar User (Usuário existente)**
- Adicionar campos: department_id, role
- Relacionamentos: departamento, reservas

#### app/models/enums.py
**Adicionar enums:**
- RoomStatus: ATIVA, INATIVA, MANUTENCAO
- ReservationStatus: PENDENTE, CONFIRMADA, CANCELADA, FINALIZADA, EM_ANDAMENTO
- UserRole: ADMINISTRADOR, GESTOR, USUARIO_AVANCADO, USUARIO

#### app/models/dto.py
**Criar DTOs Pydantic:**
- RoomResourceBase, RoomResourceCreate, RoomResourceResponse
- RoomBase, RoomCreate, RoomUpdate, RoomResponse
- ReservationBase, ReservationCreate, ReservationUpdate, ReservationResponse
- DepartmentBase, DepartmentCreate, DepartmentResponse
- Validadores para regras de negócio (datas, horários, antecedência)

### 2. Repositories (app/repos/)

#### app/repos/room_repo.py
**RoomRepository - Operações de dados para salas:**
- get_all(): listar salas com filtros (status, departamento)
- get_by_id(): buscar sala por ID
- get_by_code(): buscar sala por código
- create(): criar nova sala com recursos
- update(): atualizar sala e recursos
- delete(): excluir sala (verificar dependências)
- check_availability(): verificar disponibilidade por período
- get_by_department(): salas por departamento
- search(): busca por nome/código

#### app/repos/reservation_repo.py
**ReservationRepository - Operações de dados para reservas:**
- get_all(): listar reservas com filtros múltiplos
- get_by_id(): buscar reserva por ID
- get_by_user(): reservas de um usuário
- get_by_room(): reservas de uma sala
- get_by_date_range(): reservas em período
- create(): criar nova reserva
- update(): atualizar reserva
- cancel(): cancelar reserva
- approve(): aprovar reserva
- get_pending_approvals(): reservas pendentes
- get_conflicts(): verificar conflitos
- get_upcoming(): próximas reservas

#### app/repos/department_repo.py
**DepartmentRepository - Operações de dados para departamentos:**
- get_all(): listar departamentos
- get_by_id(): buscar por ID
- get_by_code(): buscar por código
- create(): criar departamento
- update(): atualizar departamento
- delete(): excluir departamento

### 3. Services (app/services/)

#### app/services/room_service.py
**RoomService - Lógica de negócio para salas:**
- create_room(): aplicar validações e criar sala
- update_room(): validar alterações e atualizar
- delete_room(): verificar dependências antes de excluir
- get_available_rooms(): salas disponíveis por período
- check_room_permissions(): verificar permissões de acesso
- schedule_maintenance(): agendar manutenção
- get_room_utilization(): estatísticas de uso
- validate_room_data(): validações de negócio

#### app/services/reservation_service.py
**ReservationService - Lógica de negócio para reservas:**
- create_reservation(): validar e criar reserva (aplicar todas as regras)
- update_reservation(): validar alterações
- cancel_reservation(): cancelar com validações de prazo
- approve_reservation(): aprovar reserva (gestores)
- reject_reservation(): rejeitar com motivo
- check_availability(): verificar disponibilidade completa
- validate_reservation_rules(): aplicar regras de antecedência, duração, conflitos
- auto_approve(): lógica de aprovação automática
- send_notifications(): integrar com sistema de notificações
- check_user_permissions(): validar permissões por departamento
- get_reservation_conflicts(): detectar conflitos
- handle_no_show(): tratar ausências

#### app/services/department_service.py
**DepartmentService - Lógica de negócio para departamentos:**
- create_department(): criar com validações
- assign_manager(): atribuir gerente
- get_department_stats(): estatísticas do departamento
- manage_permissions(): gerenciar permissões de acesso

#### app/services/notification_service.py
**NotificationService - Sistema de notificações:**
- send_reservation_confirmation(): confirmar reserva
- send_reminder(): lembrete antes da reserva
- send_cancellation_notice(): aviso de cancelamento
- send_approval_request(): solicitar aprovação
- send_maintenance_notice(): aviso de manutenção

#### app/services/report_service.py
**ReportService - Geração de relatórios:**
- generate_usage_report(): relatório de uso
- generate_occupancy_report(): taxa de ocupação
- generate_user_activity(): atividade dos usuários
- generate_maintenance_report(): relatório de manutenções
- get_statistics(): estatísticas gerais

### 4. Controllers (app/controllers/)

#### app/controllers/api/room_controller.py
**Endpoints REST para salas:**
- GET /rooms: listar salas com filtros
- GET /rooms/{id}: detalhes da sala
- POST /rooms: criar sala
- PUT /rooms/{id}: atualizar sala
- DELETE /rooms/{id}: excluir sala
- GET /rooms/{id}/availability: verificar disponibilidade
- GET /rooms/search: buscar salas
- Aplicar autenticação e autorização

#### app/controllers/api/reservation_controller.py
**Endpoints REST para reservas:**
- GET /reservations: listar reservas
- GET /reservations/{id}: detalhes da reserva
- POST /reservations: criar reserva
- PUT /reservations/{id}: atualizar reserva
- DELETE /reservations/{id}: cancelar reserva
- POST /reservations/{id}/approve: aprovar reserva
- POST /reservations/{id}/reject: rejeitar reserva
- GET /reservations/my: minhas reservas
- GET /reservations/pending: pendentes de aprovação

#### app/controllers/api/department_controller.py
**Endpoints REST para departamentos:**
- GET /departments: listar departamentos
- GET /departments/{id}: detalhes do departamento
- POST /departments: criar departamento
- PUT /departments/{id}: atualizar departamento
- GET /departments/{id}/stats: estatísticas

#### app/controllers/api/report_controller.py
**Endpoints para relatórios:**
- GET /reports/usage: relatório de uso
- GET /reports/occupancy: taxa de ocupação
- GET /reports/statistics: estatísticas gerais
- GET /reports/export: exportar relatórios

#### app/controllers/pages/room_page_controller.py
**Controladores para páginas web:**
- room_list_page(): página de listagem
- room_detail_page(): página de detalhes
- room_form_page(): formulário de sala
- reservation_calendar_page(): calendário de reservas

### 5. Views (app/views/)

#### app/views/room_view.py
**Views para renderização de páginas de salas:**
- render_room_list(): lista de salas
- render_room_form(): formulário de sala
- render_room_calendar(): calendário da sala

#### app/views/reservation_view.py
**Views para renderização de páginas de reservas:**
- render_reservation_list(): lista de reservas
- render_reservation_form(): formulário de reserva
- render_dashboard(): dashboard principal

### 6. Templates (app/templates/)
**Adicionar templates Jinja2:**
- rooms/: templates de salas
  - list.jinja: listagem de salas
  - detail.jinja: detalhes da sala
  - form.jinja: formulário de sala
- reservations/: templates de reservas
  - list.jinja: listagem de reservas
  - form.jinja: formulário de reserva
  - calendar.jinja: calendário de reservas
- dashboard.jinja: dashboard principal
- reports/: templates de relatórios

### 7. Migrations (app/migrations/versions/)
**Criar migrações Alembic:**
- Criação das tabelas: rooms, room_resources, reservations, departments
- Alteração da tabela users: adicionar department_id, role
- Índices para performance
- Dados iniciais (seed data)

### 8. Schedulers (app/schedulers/)

#### app/schedulers/reservation_scheduler.py
**Tarefas agendadas para reservas:**
- auto_approve_reservations(): aprovação automática após 24h
- send_reminders(): enviar lembretes
- update_reservation_status(): atualizar status (em andamento, finalizada)
- cleanup_old_reservations(): limpeza de dados antigos
- check_no_shows(): verificar ausências

#### app/schedulers/maintenance_scheduler.py
**Tarefas de manutenção:**
- schedule_preventive_maintenance(): manutenção preventiva
- send_maintenance_alerts(): alertas de manutenção
- update_room_status(): atualizar status das salas

### 9. Utils (app/utils/)

#### app/utils/reservation_utils.py
**Utilitários para reservas:**
- validate_business_hours(): validar horários de funcionamento
- calculate_duration(): calcular duração
- check_holiday(): verificar feriados
- format_datetime(): formatação de datas

#### app/utils/notification_utils.py
**Utilitários para notificações:**
- send_email(): enviar emails
- format_notification(): formatar mensagens
- get_notification_templates(): templates de notificação

### 10. Middlewares (app/core/middlewares/)

#### app/core/middlewares/permission_middleware.py
**Middleware de permissões:**
- Verificar permissões por departamento
- Controlar acesso a salas específicas
- Validar níveis de usuário

### 11. Exceptions (app/exceptions/)

#### app/exceptions/room_exceptions.py
**Exceções específicas do domínio:**
- RoomNotAvailableException
- ReservationConflictException
- InvalidReservationTimeException
- PermissionDeniedException
- RoomMaintenanceException

### 12. Configurações

#### app/core/config.py
**Adicionar configurações:**
- Horários de funcionamento
- Limites de reserva
- Configurações de notificação
- Integração com sistemas externos

## Funcionalidades Implementadas

### Gestão de Salas
- CRUD completo com validações
- Controle de recursos por sala
- Gestão de status (ativa, inativa, manutenção)
- Verificação de disponibilidade
- Controle de acesso por departamento

### Gestão de Reservas
- Criação com validação de regras de negócio
- Sistema de aprovação automática/manual
- Verificação de conflitos em tempo real
- Cancelamento com regras de prazo
- Controle de permissões por usuário

### Sistema de Notificações
- Confirmações de reserva
- Lembretes automáticos
- Avisos de cancelamento
- Solicitações de aprovação

### Relatórios e Estatísticas
- Taxa de ocupação por sala
- Uso por departamento
- Relatórios de manutenção
- Estatísticas de usuários

### Autenticação e Autorização
- Diferentes níveis de usuário
- Controle de acesso por departamento
- Permissões específicas por funcionalidade

### Tarefas Automatizadas
- Aprovação automática de reservas
- Envio de lembretes
- Atualização de status
- Limpeza de dados antigos

## Integração com Sistema Existente
- Utilizar sistema de autenticação existente
- Integrar com tabela de usuários atual
- Manter padrões de middleware e exceções
- Seguir estrutura MVC estabelecida
- Utilizar configurações e dependências existentes