# SalasTech CLI

O SalasTech CLI é uma interface de linha de comando para gerenciamento do sistema de reservas de salas.

## Instalação

Para instalar o CLI, execute:

pip install -e .

## Uso

O CLI está disponível através do comando `SalasTech`. Você pode ver todas as opções disponíveis usando:

```bash
SalasTech --help
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
SalasTech user list

# Criar novo usuário
SalasTech user create

# Criar usuário administrador
SalasTech user create --admin

# Ver detalhes de um usuário
SalasTech user get 1

# Atualizar nome de usuário
SalasTech user update-name 1

# Resetar senha
SalasTech user reset-password user@example.com
```

#### Departamentos

```bash
# Listar departamentos
SalasTech dept list

# Criar novo departamento
SalasTech dept create

# Ver detalhes de um departamento
SalasTech dept get 1

# Atualizar departamento
SalasTech dept update 1
```

#### Salas

```bash
# Listar salas
SalasTech room list

# Criar nova sala
SalasTech room create

# Ver detalhes de uma sala
SalasTech room get 1

# Atualizar status da sala
SalasTech room update-status 1 MAINTENANCE
```

#### Reservas

```bash
# Listar reservas
SalasTech reservation list

# Listar reservas por status
SalasTech reservation list --status PENDING

# Criar nova reserva
SalasTech reservation create --room-id 1 --user-id 1

# Ver detalhes de uma reserva
SalasTech reservation get 1

# Aprovar reserva
SalasTech reservation approve 1 --admin-id 2

# Rejeitar reserva
SalasTech reservation reject 1 --reason "Sala indisponível"

# Cancelar reserva
SalasTech reservation cancel 1 --reason "Evento cancelado"
```

## Funcionalidades

- Interface interativa com prompts e confirmações
- Formatação rica e colorida no terminal
- Suporte a paginação para listagens grandes
- Validações de entrada
- Mensagens de erro claras e informativas
- Auto-completação de comandos
- Ajuda detalhada para cada comando
