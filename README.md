# 🏫 SalsTech - Sistema de Gerenciamento de Salas IFAM (Backend)

<div align="center">

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI Version](https://img.shields.io/badge/fastapi-0.95%2B-teal)
![License](https://img.shields.io/badge/license-MIT-green)

*Sistema de gerenciamento de reservas de salas, agendamentos e recursos.*

<p align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" alt="fastapi" width="40" height="40"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/mysql/mysql-original-wordmark.svg" alt="mysql" width="40" height="40"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/bash/bash-original.svg" alt="shell" width="40" height="40"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/sqlite/sqlite-original-wordmark.svg" alt="shell" width="40" height="40" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/sqlalchemy/sqlalchemy-original-wordmark.svg" alt="alembic" width="40" height="40"/>

---

## 📋 Índice

- [Características](#-características)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [API Documentation](#-api-documentation)
- [Desenvolvimento](#-desenvolvimento)
- [Testes](#-testes)
- [CLI Admin](#-cli-admin)
- [Segurança](#-segurança)
- [Database](#-database)
- [Scripts de Manutenção](#-scripts-de-manutenção)
- [Licença](#-licença)

## ✨ Características

- **Autenticação Robusta**

  - Sistema completo de login/registro
  - JWT Tokens
  - Proteção CSRF
  - Rate Limiting
  - Refresh Tokens
- **Gerenciamento de Recursos**

  - Salas e Departamentos
  - Reservas e Agendamentos
  - Recursos por Sala
  - Status e Disponibilidade
- **Controle de Acesso**

  - Múltiplos níveis de usuário
  - Permissões por departamento
  - Aprovação de reservas
  - Auditoria de mudanças
- **Automações**

  - Aprovação automática
  - Notificações
  - Limpeza de dados
  - Backups automáticos

## 🚀 Pré-requisitos

- Python 3.9+
- Banco de dados:
  - SQLite (desenvolvimento)
  - MySQL 8.0+ (produção)
- Sistema de virtualenv

## 📥 Instalação

1. **Clone o repositório**

   ```bash
   git clone https://github.com/jpedrops092/SalasTech-backend.git
   cd SalasTech-backend
   ```
2. **Configure o ambiente virtual**

   ```bash
   # Criar e ativar ambiente virtual
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\\Scripts\\activate

   # Atualizar pip
   pip install --upgrade pip
   ```
3. **Instalar dependências**

   O projeto usa `pyproject.toml` para gerenciar dependências. Você tem várias opções de instalação:

   ```bash
   # Instalação básica (ambiente de produção)
   pip install -e .

   # Instalação com dependências de teste
   pip install -e ".[test]"
   ```

   Dependências incluídas:

   - **Core**: FastAPI, SQLAlchemy, Pydantic, etc.
   - **Segurança**: JWT, CSRF, bcrypt, passlib
   - **Database**: MySQL, PostgreSQL, SQLite
   - **CLI**: Typer, Rich
   - **Testes**: pytest, coverage, httpx
4. **Variáveis de ambiente**

   ```bash
   cp .env.example .env
   # Configure as variáveis no arquivo .env
   ```
5. **Inicialize o banco de dados**

   ```bash
   ./dev.sh setup
   ```
6. **Execute o servidor**

   ```bash
   ./dev.sh run
   # ou
   uvicorn src.SalasTech.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🏗 Estrutura do Projeto

```
src/SalasTech/
├── app/
│   ├── controllers/          # Endpoints e rotas
│   │   ├── api/             # API REST
│   │   └── pages/           # Renderização de páginas
│   ├── models/              # Modelos e schemas
│   ├── services/            # Lógica de negócios
│   ├── repos/               # Acesso a dados
│   ├── core/                # Configurações core
│   │   ├── security/        # Autenticação e proteção
│   │   └── middlewares/     # Middlewares
│   └── exceptions/          # Tratamento de erros
├── cli/                     # Interface de linha de comando
└── tests/                   # Testes automatizados
    ├── unit/           
    ├── integration/    
    └── e2e/            
```

## 📚 API Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI**: `/openapi.json`

### Principais Endpoints

- **Autenticação**

  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/logout`
  - `POST /api/auth/password/reset`
- **Salas**

  - `GET /api/rooms`
  - `POST /api/rooms`
  - `GET /api/rooms/{id}`
  - `GET /api/rooms/{id}/availability`
- **Reservas**

  - `GET /api/reservations`
  - `POST /api/reservations`
  - `GET /api/reservations/{id}`
  - `POST /api/reservations/{id}/approve`

## 🔧 Desenvolvimento

### Script dev.sh

O script `dev.sh` facilita tarefas comuns:

```bash
./dev.sh setup       # Configura o ambiente
./dev.sh run         # Inicia o servidor
./dev.sh populate    # Popula dados de teste
./dev.sh migrations  # Gerencia migrações
./dev.sh test        # Executa testes
./dev.sh clean       # Limpa temporários
```

## 🧪 Testes

O projeto utiliza pytest para testes:

```bash
# Executar todos os testes
pytest

# Testes específicos
pytest tests/unit
pytest tests/integration
pytest tests/e2e

# Com cobertura
pytest --cov=src
```

## 💻 CLI Admin

Interface de linha de comando para administração:

```bash
# Instalação
pip install -e .

# Uso
SalasTech --help
SalasTech user list
SalasTech room create
SalasTech reservation approve 1
```

## 🔒 Segurança

- JWT para autenticação
- CSRF Protection
- Rate Limiting
- Bcrypt para senhas
- CORS configurável
- Logs de segurança

## 🗄 Database

### Configuração

```env
# SQLite (Dev)
DB_TYPE=sqlite
SQLITE_PATH=db.sqlite

# MySQL (Prod)
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=SalasTech
```

### Migrações (Alembic)

```bash
./dev.sh migrations generate  # Nova migração
./dev.sh migrations apply    # Aplicar migrações
./dev.sh migrations revert   # Reverter última
```

## 🛠 Scripts de Manutenção

- `scripts/backup_database.py`: Backup automático
- `scripts/optimize_database.py`: Otimização
- `scripts/monitor_database.py`: Monitoramento
- `scripts/setup_backup_cron.sh`: Configuração de cron

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**Desenvolvido com ❤️ para o IFAM**

[Reportar Bug](https://github.com/jpedrops092/SalasTech-backend/issues) ·
[Solicitar Feature](https://github.com/jpedrops092/SalasTech-backend/issues)

</div>
