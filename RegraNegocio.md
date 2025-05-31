# Sistema de Gerenciamento de Salas - Regras de Negócio

## 1. Definições e Conceitos

### 1.1 Entidades Principais

* **Sala** : Espaço físico com capacidade e recursos específicos
* **Usuário** : Pessoa autorizada a fazer reservas (funcionários, professores, alunos)
* **Reserva** : Agendamento de uso de uma sala por período determinado
* **Recurso** : Equipamentos disponíveis nas salas (projetor, computador, etc.)
* **Departamento** : Unidade organizacional da instituição

### 1.2 Tipos de Usuários

* **Administrador** : Controle total do sistema
* **Gestor** : Gerencia salas de seu departamento
* **Usuário Comum** : Pode fazer reservas conforme permissões

## 2. Regras de Cadastro de Salas

### 2.1 Informações Obrigatórias

* Código único da sala
* Nome/identificação
* Capacidade máxima de pessoas
* Localização (prédio, andar)
* Departamento responsável
* Status (ativa, inativa, manutenção)

### 2.2 Informações Opcionais

* Recursos disponíveis
* Observações especiais
* Foto da sala
* Responsável pela sala

### 2.3 Validações

* Código da sala deve ser único no sistema
* Capacidade deve ser maior que zero
* Localização deve seguir padrão da instituição

## 3. Regras de Usuários e Permissões

### 3.1 Cadastro de Usuários

* Informações obrigatórias: nome, email, tipo de usuário, departamento
* Email deve ser único no sistema
* Usuários inativos não podem fazer reservas

### 3.2 Níveis de Permissão

* **Nível 1 - Usuário Básico** : Pode reservar salas do próprio departamento
* **Nível 2 - Usuário Avançado** : Pode reservar qualquer sala disponível
* **Nível 3 - Gestor** : Pode aprovar/cancelar reservas do departamento
* **Nível 4 - Administrador** : Controle total

### 3.3 Restrições por Departamento

* Usuários só podem reservar salas de seu departamento (exceto níveis 2+)
* Gestores podem definir regras específicas para suas salas
* Salas podem ter acesso restrito a determinados usuários

## 4. Regras de Reservas

### 4.1 Criação de Reservas

* Data e horário de início e fim obrigatórios
* Descrição/motivo da reserva obrigatório
* Usuário responsável pela reserva
* Sala deve estar disponível no período solicitado

### 4.2 Validações Temporais

* Reserva não pode ser feita para data/hora passada
* Horário de fim deve ser posterior ao de início
* Duração mínima: 30 minutos
* Duração máxima: 8 horas por reserva
* Antecedência mínima: 2 horas
* Antecedência máxima: 30 dias

### 4.3 Conflitos e Disponibilidade

* Não podem existir reservas sobrepostas para a mesma sala
* Sistema deve verificar disponibilidade em time real
* Reservas confirmadas têm prioridade sobre pendentes

### 4.4 Status das Reservas

* **Pendente** : Aguardando aprovação (se necessário)
* **Confirmada** : Aprovada e ativa
* **Cancelada** : Cancelada pelo usuário ou gestor
* **Finalizada** : Reserva já ocorreu
* **Em andamento** : Reserva acontecendo no momento

## 5. Regras de Aprovação

### 5.1 Aprovação Automática

* Reservas de usuários nível 2+ são aprovadas automaticamente
* Salas sem restrição especial são aprovadas automaticamente
* Reservas com até 2 horas de duração são aprovadas automaticamente

### 5.2 Aprovação Manual

* Reservas de usuários nível 1 podem requerer aprovação
* Salas com recursos especiais podem requerer aprovação
* Reservas fora do horário padrão podem requerer aprovação
* Reservas com mais de 4 horas requerem aprovação

### 5.3 Prazo para Aprovação

* Gestores têm 24 horas para aprovar/rejeitar
* Após 24 horas, reserva é aprovada automaticamente
* Reservas urgentes (menos de 4 horas) têm prazo de 2 horas

## 6. Regras de Cancelamento

### 6.1 Cancelamento pelo Usuário

* Pode cancelar até 2 horas antes do início
* Após início da reserva, só pode cancelar com justificativa
* Usuário que não comparece 3 vezes pode ter restrições

### 6.2 Cancelamento pelo Gestor

* Pode cancelar qualquer reserva com justificativa
* Deve notificar usuário com antecedência mínima de 2 horas
* Motivos válidos: manutenção, evento institucional, emergência

### 6.3 Cancelamento Automático

* Reservas não aprovadas em 24 horas são canceladas
* Sistema pode cancelar reservas de usuários inativos

## 7. Regras de Horário de Funcionamento

### 7.1 Horários Padrão

* Segunda a Sexta: 07:00 às 22:00
* Sábado: 08:00 às 18:00
* Domingo: Fechado (exceto eventos especiais)

### 7.2 Horários Especiais

* Cada sala pode ter horário específico
* Feriados seguem calendário institucional
* Períodos de férias podem ter horários reduzidos

### 7.3 Exceções

* Administradores podem autorizar uso fora do horário
* Eventos especiais podem estender horários
* Manutenção programada bloqueia horários

## 8. Regras de Relatórios e Monitoramento

### 8.1 Métricas de Uso

* Taxa de ocupação por sala
* Usuários com mais reservas
* Horários de pico
* Taxa de cancelamento
* Taxa de no-show

### 8.2 Relatórios Obrigatórios

* Relatório mensal de uso por departamento
* Relatório de manutenções realizadas
* Relatório de incidentes e problemas

### 8.3 Auditoria

* Log de todas as ações no sistema
* Histórico de alterações em reservas
* Rastreamento de acessos por usuário

## 9. Regras de Manutenção e Bloqueios

### 9.1 Manutenção Preventiva

* Salas devem ter manutenção programada mensalmente
* Durante manutenção, sala fica indisponível
* Usuários devem ser notificados com 48 horas de antecedência

### 9.2 Bloqueios Temporários

* Gestores podem bloquear salas por período determinado
* Bloqueios para eventos especiais têm prioridade
* Sistema deve notificar usuários afetados

### 9.3 Incidentes

* Problemas na sala devem ser reportados
* Sala pode ser bloqueada até resolução do problema
* Histórico de incidentes deve ser mantido

## 10. Regras de Notificações

### 10.1 Notificações Obrigatórias

* Confirmação de reserva
* Lembrete 1 hora antes da reserva
* Cancelamento de reserva
* Alterações em reservas existentes

### 10.2 Notificações Opcionais

* Resumo semanal de reservas
* Alertas de salas disponíveis
* Lembretes de manutenção

### 10.3 Canais de Notificação

* Email institucional
* Sistema interno de mensagens
* SMS (para casos urgentes)

## 11. Regras de Integração

### 11.1 Sistema Acadêmico

* Integração com calendário acadêmico
* Bloqueio automático durante provas
* Reservas automáticas para aulas regulares

### 11.2 Sistema de RH

* Sincronização de dados de funcionários
* Atualização automática de departamentos
* Controle de usuários ativos/inativos

### 11.3 Sistema de Patrimônio

* Controle de recursos e equipamentos
* Registro de manutenções
* Inventário de bens por sala

## 12. Regras de Backup e Segurança

### 12.1 Backup de Dados

* Backup diário de dados críticos
* Backup semanal completo
* Retenção de backups por 1 ano

### 12.2 Segurança de Acesso

* Autenticação obrigatória
* Senhas devem seguir política institucional
* Sessões expiram após inatividade

### 12.3 Controle de Dados

* Dados pessoais protegidos conforme LGPD
* Log de acesso a dados sensíveis
* Anonimização de dados para relatórios
