
## Sistema de Gerenciamento de Salas - Regras de Negócio (Versão Simplificada)

### 1. Entidades Principais

* **Sala** : Espaço físico com código, nome, capacidade e status (disponível, em manutenção, indisponível).
* **Usuário** : Pessoa autorizada a interagir com o sistema.
* **Tipos de Usuário** :
  *  **Administrador** : Controle total do sistema (cadastrar salas, gerenciar usuários, etc.).
  *  **Usuário Comum** : Pode visualizar salas e fazer/cancelar suas próprias reservas.
* **Reserva** : Agendamento de uma sala por um usuário para um período específico.

### 2. Cadastro e Gerenciamento de Salas

* **2.1 Informações da Sala** :
* Obrigatório: Código único, nome/identificação, capacidade máxima (número de pessoas).
* Status inicial: Disponível.
* **2.2 Ações do Administrador** :
* Administradores podem cadastrar novas salas.
* Administradores podem editar informações de salas existentes.
* Administradores podem alterar o status de uma sala (ex: para "Em Manutenção", tornando-a temporariamente indisponível para novas reservas).
* **2.3 Validações** :
* O código da sala deve ser único.
* A capacidade deve ser um número positivo maior que zero.

### 3. Cadastro e Gerenciamento de Usuários

* **3.1 Informações do Usuário** :
* Obrigatório: Nome, email (usado como login e deve ser único), senha, tipo de usuário (Administrador ou Usuário Comum).
* **3.2 Ações do Administrador** :
* Administradores podem cadastrar novos usuários.
* Administradores podem editar informações de usuários existentes (exceto senha de outros).
* Administradores podem ativar/desativar contas de usuários. Usuários desativados não podem logar ou fazer reservas.

### 4. Regras de Reserva de Salas

* **4.1 Criação de Reserva** :
* Para criar uma reserva, o usuário deve informar: sala desejada, data, horário de início e horário de fim.
* Um breve motivo ou descrição da reserva é recomendado.
* **4.2 Disponibilidade e Conflitos** :
* Uma sala não pode ser reservada se já houver outra reserva confirmada para o mesmo horário (conflito).
* O sistema deve verificar a disponibilidade em tempo real antes de confirmar uma reserva.
* Uma sala com status "Em Manutenção" ou "Indisponível" não pode ser reservada.
* **4.3 Validações Temporais** :
* A data/hora de início da reserva não pode ser no passado.
* O horário de fim deve ser posterior ao horário de início.
* Deve haver uma duração mínima para a reserva (ex: 30 minutos).
* Pode haver uma antecedência máxima para agendamento (ex: reservar com até 30 dias de antecedência).
* **4.4 Confirmação e Status da Reserva** :
* Se todas as condições forem atendidas (sala disponível, usuário ativo, regras temporais respeitadas), a reserva é **Confirmada** automaticamente.
* Outros status possíveis:  **Cancelada** .

### 5. Cancelamento de Reservas

* **5.1 Cancelamento pelo Usuário Comum** :
* O usuário que fez a reserva pode cancelá-la.
* O cancelamento pelo usuário só é permitido até um certo tempo antes do início da reserva (ex: até 1 hora antes).
* **5.2 Cancelamento pelo Administrador** :
* O Administrador pode cancelar qualquer reserva, a qualquer momento, preferencialmente com uma justificativa.

### 6. Horário de Funcionamento (Opcional, mas Comum)

* **6.1 Restrição de Horário** :
* As reservas só podem ser feitas dentro de um horário de funcionamento padrão definido pelo sistema (ex: Segunda a Sexta, das 08:00 às 22:00).
* O Administrador pode, em casos excepcionais, realizar agendamentos fora desses horários.

### 7. Notificações Essenciais (Simplificado)

* **7.1 Eventos de Notificação** :
* Quando uma reserva é  **Confirmada** , o usuário responsável recebe uma notificação (ex: por email).
* Quando uma reserva é **Cancelada** (pelo usuário ou administrador), o usuário responsável recebe uma notificação.
