# SalasTech Docker Configuration

Este diretório contém toda a configuração Docker para o projeto SalasTech, com setups otimizados para desenvolvimento e produção.

## 📁 Estrutura de Arquivos

```
├── Dockerfile              # Dockerfile original (mantido para compatibilidade)
├── Dockerfile.dev          # Dockerfile otimizado para desenvolvimento
├── Dockerfile.prod         # Dockerfile otimizado para produção
├── docker-compose.yml      # Docker Compose original
├── docker-compose.dev.yml  # Docker Compose para desenvolvimento
├── docker-compose.prod.yml # Docker Compose para produção
├── docker-entrypoint.sh    # Script original
├── docker-entrypoint.dev.sh  # Script para desenvolvimento
├── docker-entrypoint.prod.sh # Script para produção
├── .env.dev.example        # Exemplo de variáveis para desenvolvimento
├── .env.prod.example       # Exemplo de variáveis para produção
├── nginx/                  # Configuração do Nginx para produção
│   └── nginx.conf
└── Makefile               # Comandos facilitadores
```

## 🚀 Início Rápido

### Desenvolvimento

```bash
# Configurar ambiente
make install

# Iniciar desenvolvimento
make dev

# Ou com docker-compose diretamente
docker-compose -f docker-compose.dev.yml up --build
```

### Produção

```bash
# Configurar variáveis de ambiente
cp .env.prod.example .env.prod
# Edite .env.prod com suas configurações

# Iniciar produção
make prod

# Com nginx reverse proxy
make nginx
```

## 🛠️ Comandos Disponíveis (Makefile)

| Comando | Descrição |
|---------|-----------|
| `make help` | Mostra todos os comandos disponíveis |
| `make dev` | Inicia ambiente de desenvolvimento |
| `make prod` | Inicia ambiente de produção |
| `make test` | Executa todos os testes |
| `make logs` | Visualiza logs dos containers |
| `make clean` | Limpa containers e volumes não utilizados |
| `make backup` | Cria backup do banco de dados |

## 🔧 Configuração de Desenvolvimento

### Características:
- ✅ Hot reload automático
- ✅ Ferramentas de desenvolvimento (black, flake8, mypy)
- ✅ Debug habilitado
- ✅ Volumes para código fonte
- ✅ Logs detalhados

### Portas:
- **8000**: API principal

### Volumes:
- `./app:/app/app:ro` - Código fonte (read-only para hot reload)
- `salastech_dev_db` - Banco de dados
- `salastech_dev_logs` - Logs
- `salastech_dev_backups` - Backups

## 🏭 Configuração de Produção

### Características:
- ✅ Multi-stage build (imagem otimizada)
- ✅ Usuário não-root
- ✅ Health checks
- ✅ Limites de recursos
- ✅ Nginx reverse proxy (opcional)
- ✅ Backup automático (opcional)

### Variáveis de Ambiente Obrigatórias:
- `SECRET_KEY`: Chave secreta para produção
- `ALLOWED_HOSTS`: Hosts permitidos

### Profiles Disponíveis:
- `with-nginx`: Inclui Nginx reverse proxy
- `with-backup`: Inclui serviço de backup automático

## 🔒 Segurança

### Produção:
- ✅ Usuário não-root
- ✅ Multi-stage build
- ✅ Secrets via variáveis de ambiente
- ✅ Nginx com headers de segurança
- ✅ Limites de recursos

### Desenvolvimento:
- ⚠️ Debug habilitado
- ⚠️ Chaves de desenvolvimento

## 📊 Monitoramento

### Health Checks:
- **Desenvolvimento**: A cada 60s
- **Produção**: A cada 30s

### Logs:
- **Desenvolvimento**: Debug level
- **Produção**: Info level
- Volumes persistentes para logs

## 🔄 CI/CD

Para integração contínua, use:

```bash
# Testes
docker-compose -f docker-compose.dev.yml --profile testing up --build test

# Build de produção
docker build -f Dockerfile.prod -t salastech:latest .
```

## 📝 Variáveis de Ambiente

### Desenvolvimento (.env.dev)
```env
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=salastech-dev-secret-key
```

### Produção (.env.prod)
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=your-domain.com
```

## 🚨 Troubleshooting

### Container não inicia:
```bash
# Ver logs
make logs

# Verificar status
make status
```

### Problemas de permissão:
```bash
# Limpar e reconstruir
make clean
make build-dev
```

### Banco de dados corrompido:
```bash
# Restaurar backup
make backup
```

## 📈 Performance

### Desenvolvimento:
- Reload automático otimizado
- Cache de dependências

### Produção:
- 4 workers uvicorn
- Nginx com cache
- Compressão gzip
- Limites de memória/CPU
