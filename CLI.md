# SalsTech CLI

O SalsTech CLI é uma interface de linha de comando para gerenciamento do sistema de reservas de salas.

## Instalação

Para instalar o CLI, execute:

pip install -e .

## Uso

O CLI está disponível através do comando `salstech`. Você pode ver todas as opções disponíveis usando:

```bash
salstech --help
```

### Subcomandos Disponíveis

- `user` - Gerenciamento de usuários
- `dept` - Gerenciamento de departamentos
- `room` - Gerenciamento de salas
- `reservation` - Gerenciamento de reservas

### Exemplos de Uso

#### Usuários

```bash
# Listar usuários
salstech user list

# Criar novo usuário
salstech user create

# Criar usuário administrador
salstech user create --admin

# Ver detalhes de um usuário
salstech user get 1

# Atualizar nome de usuário
salstech user update-name 1

# Resetar senha
salstech user reset-password user@example.com
```

#### Departamentos

```bash
# Listar departamentos
salstech dept list

# Criar novo departamento
salstech dept create

# Ver detalhes de um departamento
salstech dept get 1

# Atualizar departamento
salstech dept update 1
```

#### Salas

```bash
# Listar salas
salstech room list

# Criar nova sala
salstech room create

# Ver detalhes de uma sala
salstech room get 1

# Atualizar status da sala
salstech room update-status 1 MAINTENANCE
```

#### Reservas

```bash
# Listar reservas
salstech reservation list

# Listar reservas por status
salstech reservation list --status PENDING

# Criar nova reserva
salstech reservation create --room-id 1 --user-id 1

# Ver detalhes de uma reserva
salstech reservation get 1

# Aprovar reserva
salstech reservation approve 1 --admin-id 2

# Rejeitar reserva
salstech reservation reject 1 --reason "Sala indisponível"

# Cancelar reserva
salstech reservation cancel 1 --reason "Evento cancelado"
```

## Funcionalidades

- Interface interativa com prompts e confirmações
- Formatação rica e colorida no terminal
- Suporte a paginação para listagens grandes
- Validações de entrada
- Mensagens de erro claras e informativas
- Auto-completação de comandos
- Ajuda detalhada para cada comando
