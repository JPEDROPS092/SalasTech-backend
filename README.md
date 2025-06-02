<div align="center">

# 🏫 Sistema de Gerenciamento de Salas IFAM

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI Version](https://img.shields.io/badge/fastapi-0.95%2B-teal)
![License](https://img.shields.io/badge/license-MIT-green)

*Uma solução completa para gerenciamento de reservas de salas, agendamentos e alocação de recursos.*

<p align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" alt="fastapi" width="40" height="40"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/mysql/mysql-original-wordmark.svg" alt="mysql" width="40" height="40"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/bootstrap/bootstrap-plain-wordmark.svg" alt="bootstrap" width="40" height="40"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="javascript" width="40" height="40"/>
</p>

</div>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher (optional, SQLite is also supported)
- Node.js and npm (for frontend assets)
- Docker and Docker Compose (for containerized deployment)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/seuusuario/gerenciamento-salas-ifam.git
cd gerenciamento-salas-ifam
```

2. **Set up the environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env file with your database settings
```

4. **Initialize the database**

```bash
./dev.sh setup    # Sets up the database and populates it with initial data
```

5. **Run the application**

```bash
./dev.sh run      # Starts the development server
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the application**

Visit `http://localhost:8000` in your browser.

---

## 📚 Documentation

- **API Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc).
- **Setup Guide**: Refer to the [Pipeline de Desenvolvimento](#pipeline-de-desenvolvimento) section for detailed setup instructions.

---

## 🛠️ Pipeline de Desenvolvimento

### Arquitetura do Projeto

O projeto segue uma arquitetura em camadas:

- **Controllers**: Gerenciam as requisições HTTP e respostas
  - `controllers/api`: Endpoints da API REST
  - `controllers/pages`: Rotas para renderização de páginas
- **Models**: Definições de modelos de dados e esquemas
- **Repositories**: Camada de acesso a dados
- **Services**: Lógica de negócios
- **Core**: Configurações, middlewares e utilitários

### Fluxo de Desenvolvimento

1. **Configuração do Ambiente**

   ```bash
   # Clone o repositório
   git clone https://github.com/seuusuario/gerenciamento-salas-ifam.git](https://github.com/JPEDROPS092/gerenciamento-salas
   cd gerenciamento-salas

   # Crie e ative o ambiente virtual
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate

   # Instale as dependências
   pip install -r requirements.txt

   # Configure as variáveis de ambiente
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```
2. **Inicialização do Banco de Dados**

   ```bash
   # Configure e popule o banco de dados
   ./dev.sh setup
   ```
3. **Desenvolvimento**

   ```bash
   # Inicie o servidor de desenvolvimento
   ./dev.sh run
   ```
4. **Testes**

   ```bash
   # Execute os testes
   ./dev.sh test
   ```

### Usando o Script `dev.sh`

O script `dev.sh` simplifica tarefas comuns de desenvolvimento:

```bash
./dev.sh setup       # Configura o ambiente (cria tabelas e popula o banco)
./dev.sh run         # Inicia o servidor de desenvolvimento
./dev.sh populate    # Popula o banco de dados com dados de teste
./dev.sh reset       # Recria as tabelas e popula o banco de dados
./dev.sh migrations  # Gerencia migrações do banco de dados
./dev.sh test        # Executa os testes
./dev.sh clean       # Limpa arquivos temporários e caches
```

---

## 📂 Sistema de Migração do Banco de Dados

O projeto utiliza o Alembic para gerenciar migrações de banco de dados, permitindo controle de versão do esquema do banco de dados.

### Configuração do Banco de Dados

O sistema suporta dois tipos de bancos de dados:

1. **SQLite** (padrão para desenvolvimento)

   ```env
   DB_TYPE=sqlite
   SQLITE_PATH=db.sqlite
   ```
2. **MySQL** (recomendado para produção)

   ```env
   DB_TYPE=mysql
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=sua_senha
   DB_NAME=room_management
   ```

### Gerenciamento de Migrações

O projeto utiliza Alembic para gerenciar migrações de banco de dados. O script `migration_manager.sh` facilita o uso do Alembic:

```bash
# Gerar uma nova migração baseada nas alterações nos modelos
./dev.sh migrations generate

# Aplicar migrações pendentes
./dev.sh migrations apply

# Reverter a última migração
./dev.sh migrations revert

# Gerar e aplicar migrações em um único comando
./dev.sh migrations all
```

### Fluxo de Trabalho com Migrações

1. **Modificar Modelos**: Atualize os modelos em `app/models/`
2. **Gerar Migração**: Execute `./dev.sh migrations generate`
3. **Revisar Migração**: Verifique o arquivo gerado em `app/migrations/versions/`
4. **Aplicar Migração**: Execute `./dev.sh migrations apply`

### Inicialização Automática do Banco de Dados

O sistema pode criar automaticamente o banco de dados e tabelas na primeira execução:

```python
# Em app/db_init.py
from app.core.db_context import auto_create_db
auto_create_db()
```

---

## 🤝 Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Developed with ❤️ for IFAM**

[Report a Bug](https://github.com/seuusuario/gerenciamento-salas-ifam/issues) · [Request a Feature](https://github.com/seuusuario/gerenciamento-salas-ifam/issues)

</div>
