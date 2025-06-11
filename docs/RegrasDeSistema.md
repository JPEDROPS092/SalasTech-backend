# Regras do Sistema SalasTech

Este documento detalha as regras de sistema implementadas no SalasTech, complementando as regras de negócio já estabelecidas.

## 1. Regras de Autenticação e Autorização

### 1.1 Autenticação

- Usuários devem se autenticar com email e senha
- Tokens JWT são utilizados para manter a sessão
- Tokens expiram após o tempo configurado (padrão: 24 horas)
- Após 5 tentativas falhas de login, a conta é bloqueada por 15 minutos

### 1.2 Autorização

- **Administrador**: Acesso total ao sistema
- **Gestor**: Gerencia departamentos específicos, aprova reservas
- **Usuário Avançado**: Pode reservar salas de qualquer departamento
- **Usuário Comum**: Pode reservar apenas salas do próprio departamento

### 1.3 Permissões por Recurso

| Recurso | Administrador | Gestor | Usuário Avançado | Usuário Comum |
|---------|---------------|--------|------------------|---------------|
| Usuários | CRUD | Visualizar | Visualizar | Visualizar próprio |
| Departamentos | CRUD | Visualizar, Editar próprio | Visualizar | Visualizar |
| Salas | CRUD | CRUD (próprio depto) | Visualizar | Visualizar |
| Reservas | CRUD | CRUD, Aprovar | CRUD | CRUD (próprio depto) |
| Relatórios | Todos | Departamentais | Limitados | Nenhum |

## 2. Regras de Reserva

### 2.1 Criação de Reservas

- Horário mínimo de antecedência: 2 horas
- Horário máximo de antecedência: 30 dias
- Duração mínima: 30 minutos
- Duração máxima: 8 horas
- Não é permitido reservar salas em manutenção ou inativas
- Não é permitido criar reservas com conflito de horário

### 2.2 Aprovação de Reservas

- Reservas de administradores e usuários avançados são aprovadas automaticamente
- Reservas com duração de até 2 horas são aprovadas automaticamente
- Reservas com duração superior a 4 horas sempre requerem aprovação
- Reservas pendentes há mais de 24 horas são aprovadas automaticamente
- Apenas gestores e administradores podem aprovar reservas

### 2.3 Cancelamento de Reservas

- Usuários podem cancelar suas próprias reservas até 2 horas antes do início
- Após esse prazo, apenas com justificativa
- Gestores e administradores podem cancelar qualquer reserva
- Ao cancelar, é necessário informar o motivo
- Usuários são notificados sobre o cancelamento

### 2.4 Horários de Funcionamento

- Segunda a Sexta: 07:00 às 22:00
- Sábado: 08:00 às 18:00
- Domingo: Fechado
- Feriados: Seguem regras específicas configuradas no sistema

## 3. Regras de Salas

### 3.1 Status de Salas

- **Ativa**: Disponível para reservas
- **Inativa**: Temporariamente indisponível
- **Manutenção**: Em manutenção programada

### 3.2 Manutenção de Salas

- Apenas administradores podem agendar manutenções
- Reservas existentes no período de manutenção são canceladas
- Usuários afetados são notificados
- Após o período de manutenção, a sala volta automaticamente ao status "Ativa"

### 3.3 Recursos de Salas

- Cada sala pode ter múltiplos recursos associados
- Recursos têm quantidade e descrição
- Recursos são considerados na busca de salas

## 4. Regras de Departamentos

### 4.1 Gerenciamento de Departamentos

- Cada departamento deve ter um código único
- Departamentos podem ter um gerente associado
- Apenas usuários com papel de gestor ou administrador podem ser gerentes
- Salas são associadas a departamentos

### 4.2 Acesso por Departamento

- Usuários comuns só podem reservar salas do próprio departamento
- Gestores podem gerenciar salas e reservas do próprio departamento
- Usuários avançados podem reservar salas de qualquer departamento
- Administradores têm acesso a todos os departamentos

## 5. Regras de Notificação

### 5.1 Eventos de Notificação

- Confirmação de reserva
- Lembrete 24 horas antes da reserva
- Cancelamento de reserva
- Aprovação ou rejeição de reserva
- Manutenção programada que afete reservas existentes

### 5.2 Canais de Notificação

- Email (principal)
- Notificações no sistema
- Exportação para calendário (iCal)

## 6. Regras de Relatórios

### 6.1 Tipos de Relatórios

- Ocupação de salas
- Reservas por departamento
- Atividade de usuários
- Manutenções realizadas
- Estatísticas gerais

### 6.2 Acesso a Relatórios

- Administradores têm acesso a todos os relatórios
- Gestores têm acesso a relatórios do próprio departamento
- Usuários avançados têm acesso a relatórios limitados
- Usuários comuns não têm acesso a relatórios

### 6.3 Exportação de Relatórios

- Formatos disponíveis: JSON, CSV, PDF
- Relatórios podem ser filtrados por período e departamento

## 7. Regras de Auditoria

### 7.1 Eventos Auditados

- Login e logout
- Criação, modificação e cancelamento de reservas
- Aprovação e rejeição de reservas
- Alterações em salas e departamentos
- Alterações em usuários e permissões

### 7.2 Dados de Auditoria

- Data e hora do evento
- Usuário responsável
- Tipo de evento
- Detalhes da operação
- Endereço IP

## 8. Regras de Validação de Dados

### 8.1 Validação de Usuários

- Email deve ser único e válido
- Senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas, números e caracteres especiais
- Nome e sobrenome devem ter entre 2 e 100 caracteres

### 8.2 Validação de Salas

- Código deve ser único
- Capacidade deve ser maior que zero
- Nome deve ter entre 2 e 100 caracteres

### 8.3 Validação de Reservas

- Data/hora de início deve ser posterior à atual
- Data/hora de término deve ser posterior à de início
- Título deve ter entre 3 e 100 caracteres

## 9. Regras de Cache e Performance

### 9.1 Cache de Dados

- Lista de salas é cacheada por 5 minutos
- Disponibilidade de salas é cacheada por 1 minuto
- Dados de usuário são cacheados durante a sessão

### 9.2 Limites de Requisição

- Máximo de 100 requisições por minuto por usuário
- Máximo de 10 reservas simultâneas por usuário
- Máximo de 1000 registros por página em listagens

## 10. Regras de Backup e Recuperação

### 10.1 Backup de Dados

- Backup completo diário às 03:00
- Backup incremental a cada 6 horas
- Retenção de backups por 30 dias

### 10.2 Recuperação de Dados

- Ponto de restauração disponível para os últimos 7 dias
- Logs de transações mantidos por 30 dias