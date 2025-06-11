# Guia de Instalação e Configuração do SalasTech

## Requisitos

- Python 3.10 ou superior
- Pip (gerenciador de pacotes Python)
- Banco de dados SQLite (padrão) ou MySQL/PostgreSQL (opcional)
- Git (para clonar o repositório)

## Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/jpedrops092/SalasTech-backend.git
cd SalasTech-backend
```

### 2. Crie um Ambiente Virtual

```bash
# Linux/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as Dependências

```bash
pip install -e .
```

Este comando instalará o pacote em modo de desenvolvimento, permitindo que você faça alterações no código sem precisar reinstalar.

### 4. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto baseado no arquivo `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```
# Configurações do Banco de Dados
DATABASE_URL=sqlite:///./db.sqlite

# Configurações de Segurança
SECRET_KEY=sua_chave_secreta_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Configurações do Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Configurações de Email (opcional)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=seu_email@example.com
MAIL_PASSWORD=sua_senha
MAIL_FROM=seu_email@example.com
MAIL_TLS=True
MAIL_SSL=False
```

### 5. Inicialize o Banco de Dados

```bash
cd src/SalasTech/app
python db_init.py
```

Ou use o script de migração:

```bash
cd src/SalasTech/app
bash migration_manager.sh upgrade head
```

### 6. Popule o Banco de Dados com Dados Iniciais (Opcional)

```bash
cd scripts
python populate_database.py
```

## Execução

### Iniciar o Servidor de Desenvolvimento

```bash
cd src/SalasTech/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Ou use o script de desenvolvimento:

```bash
cd scripts
bash dev.sh
```

### Acessar a Aplicação

- Interface Web: http://localhost:8000
- Documentação da API: http://localhost:8000/api/docs
- Documentação ReDoc: http://localhost:8000/api/redoc

## Utilização da CLI

A CLI do SalasTech está disponível após a instalação:

```bash
# Ver comandos disponíveis
SalasTech --help

# Exemplos de uso
SalasTech user list
SalasTech room create
SalasTech reservation list
```

## Configuração para Produção

### 1. Configurações Recomendadas

Edite o arquivo `.env` para o ambiente de produção:

```
# Configurações do Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost/salastech

# Configurações de Segurança
SECRET_KEY=chave_secreta_longa_e_aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=False

# Configurações do Servidor
HOST=0.0.0.0
PORT=8000
```

### 2. Servidor WSGI

Para produção, recomenda-se usar o Gunicorn como servidor WSGI:

```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.SalasTech.app.main:app
```

### 3. Proxy Reverso

Configure um proxy reverso (Nginx ou Apache) para servir a aplicação:

Exemplo de configuração Nginx:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /caminho/para/SalsTech-backend/src/SalasTech/app/static;
        expires 1d;
    }
}
```

### 4. Configuração de Backup

Configure backups automáticos do banco de dados:

```bash
cd scripts
bash setup_backup_cron.sh
```

## Solução de Problemas

### Erro de Conexão com o Banco de Dados

Verifique se:

- A URL do banco de dados está correta no arquivo `.env`
- O banco de dados está em execução
- O usuário tem permissões adequadas

### Erro ao Iniciar o Servidor

Verifique se:

- Todas as dependências foram instaladas
- O ambiente virtual está ativado
- As variáveis de ambiente estão configuradas corretamente

### Erro de Permissão

Em sistemas Linux/macOS, pode ser necessário ajustar as permissões:

```bash
chmod +x scripts/*.sh
chmod +x src/SalasTech/app/migration_manager.sh
```

## Atualização

Para atualizar o sistema:

```bash
git pull
pip install -e .
cd src/SalasTech/app
bash migration_manager.sh upgrade head
```
