# =============================================================================
# MAKEFILE PARA FACILITAR OPERAÇÕES DOCKER - SALASTECH
# =============================================================================

.PHONY: help dev prod build-dev build-prod up-dev up-prod down logs clean test

# Configuração padrão
COMPOSE_DEV = docker-compose -f docker-compose.dev.yml
COMPOSE_PROD = docker-compose -f docker-compose.prod.yml

help: ## Mostrar este help
	@echo "Comandos disponíveis para SalasTech:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Comandos de desenvolvimento
dev: ## Iniciar ambiente de desenvolvimento
	$(COMPOSE_DEV) up --build

dev-daemon: ## Iniciar ambiente de desenvolvimento em background
	$(COMPOSE_DEV) up --build -d

build-dev: ## Fazer build da imagem de desenvolvimento
	$(COMPOSE_DEV) build

# Comandos de produção
prod: ## Iniciar ambiente de produção
	$(COMPOSE_PROD) up --build

prod-daemon: ## Iniciar ambiente de produção em background
	$(COMPOSE_PROD) up --build -d

build-prod: ## Fazer build da imagem de produção
	$(COMPOSE_PROD) build

# Comandos de nginx (produção)
nginx: ## Iniciar com nginx reverse proxy
	$(COMPOSE_PROD) --profile with-nginx up --build -d

# Comandos gerais
down: ## Parar todos os serviços
	$(COMPOSE_DEV) down
	$(COMPOSE_PROD) down

down-dev: ## Parar serviços de desenvolvimento
	$(COMPOSE_DEV) down

down-prod: ## Parar serviços de produção
	$(COMPOSE_PROD) down

logs: ## Ver logs dos serviços
	$(COMPOSE_DEV) logs -f

logs-prod: ## Ver logs de produção
	$(COMPOSE_PROD) logs -f

# Comandos de teste
test: ## Executar testes
	$(COMPOSE_DEV) --profile testing up --build test

test-unit: ## Executar apenas testes unitários
	$(COMPOSE_DEV) run --rm salastech-test python -m pytest tests/unit/ -v

test-integration: ## Executar testes de integração
	$(COMPOSE_DEV) run --rm salastech-test python -m pytest tests/integration/ -v

test-e2e: ## Executar testes end-to-end
	$(COMPOSE_DEV) run --rm salastech-test python -m pytest tests/e2e/ -v

# Comandos de limpeza
clean: ## Limpar containers, volumes e imagens não utilizados
	docker system prune -f
	docker volume prune -f

clean-all: ## Limpeza completa (CUIDADO: remove tudo)
	docker system prune -af
	docker volume prune -f

# Comandos de backup
backup: ## Criar backup do banco de dados
	$(COMPOSE_PROD) exec salastech-api python scripts/backup_database.py

# Comandos de shell
shell-dev: ## Abrir shell no container de desenvolvimento
	$(COMPOSE_DEV) exec salastech-api-dev bash

shell-prod: ## Abrir shell no container de produção
	$(COMPOSE_PROD) exec salastech-api bash

# Comandos de monitoramento
status: ## Ver status dos containers
	docker ps

stats: ## Ver estatísticas dos containers
	docker stats

# Comandos de configuração
setup-env: ## Configurar arquivos de ambiente
	@echo "Configurando arquivos de ambiente..."
	@if [ ! -f .env.dev ]; then cp .env.dev.example .env.dev; fi
	@if [ ! -f .env.prod ]; then cp .env.prod.example .env.prod; fi
	@echo "Arquivos .env.dev e .env.prod criados. Configure-os conforme necessário."

# Comando para instalação inicial
install: setup-env build-dev ## Instalação inicial completa
	@echo "🎉 SalasTech configurado com sucesso!"
	@echo "Use 'make dev' para iniciar o ambiente de desenvolvimento"
