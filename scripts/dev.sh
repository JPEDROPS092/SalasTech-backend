#!/usr/bin/env bash

# Sistema de Gerenciamento de Salas IFAM
# Script de desenvolvimento

# Cores para melhor visualização
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para exibir mensagem de ajuda
help_message() {
    echo -e "${BLUE}Sistema de Gerenciamento de Salas IFAM${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${YELLOW}Script de Desenvolvimento${NC}"
    echo -e "${BLUE}-------------------------------------${NC}"
    echo -e "Uso: $0 <comando>"
    echo -e ""
    echo -e "Comandos:"
    echo -e "  ${GREEN}run${NC}         Inicia o servidor de desenvolvimento"
    echo -e "  ${GREEN}setup${NC}       Configura o ambiente (cria tabelas e popula o banco)"
    echo -e "  ${GREEN}populate${NC}    Popula o banco de dados com dados de teste"
    echo -e "  ${GREEN}reset${NC}       Recria as tabelas e popula o banco de dados"
    echo -e "  ${GREEN}migrations${NC}  Gerencia migrações do banco de dados"
    echo -e "  ${GREEN}test${NC}        Executa os testes"
    echo -e "  ${GREEN}clean${NC}       Limpa arquivos temporários e caches"
    echo -e "  ${GREEN}help${NC}        Exibe esta mensagem de ajuda"
}

# Função para iniciar o servidor de desenvolvimento
run_server() {
    echo -e "${BLUE}Iniciando servidor de desenvolvimento...${NC}"
    cd "$(dirname "$0")"
    python -m uvicorn src.SalasTech.app.main:app --reload --host 0.0.0.0 --port 8000
}

# Função para configurar o ambiente
setup_environment() {
    echo -e "${BLUE}Configurando ambiente de desenvolvimento...${NC}"
    cd "$(dirname "$0")"
    
    # Verificar se o ambiente virtual está ativo
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}Ambiente virtual não está ativo. Ativando...${NC}"
        if [ ! -d "venv" ]; then
            echo -e "${YELLOW}Criando ambiente virtual...${NC}"
            python -m venv venv
        fi
        source venv/bin/activate
    fi
    
    # Instalar o projeto em modo de desenvolvimento
    echo -e "${BLUE}Instalando dependências...${NC}"
    pip install -e ".[test]"
    
    # Verificar se o arquivo .env existe
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Arquivo .env não encontrado. Criando a partir do .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}Arquivo .env criado. Verifique as configurações antes de continuar.${NC}"
    fi
    
    # Criar tabelas no banco de dados
    echo -e "${BLUE}Criando tabelas no banco de dados...${NC}"
    python -c "from SalasTech.app.core.db_context import create_tables; create_tables()"
    
    # Popular o banco de dados
    echo -e "${BLUE}Populando o banco de dados...${NC}"
    python populate_database.py
    
    echo -e "${GREEN}Ambiente configurado com sucesso!${NC}"
    echo -e "${YELLOW}Criando tabelas no banco de dados...${NC}"
    python -m app.core.db_context
    
    # Popula o banco de dados
    echo -e "${YELLOW}Populando o banco de dados...${NC}"
    python populate_database.py
    
    echo -e "${GREEN}Ambiente configurado com sucesso!${NC}"
}

# Função para popular o banco de dados
populate_database() {
    echo -e "${BLUE}Populando banco de dados...${NC}"
    cd "$(dirname "$0")"
    python populate_database.py
}

# Função para resetar o banco de dados
reset_database() {
    echo -e "${BLUE}Recriando e populando banco de dados...${NC}"
    cd "$(dirname "$0")"
    python populate_database.py --force
}

# Função para gerenciar migrações
manage_migrations() {
    echo -e "${BLUE}Gerenciando migrações...${NC}"
    cd "$(dirname "$0")/app"
    
    if [ "$#" -eq 0 ]; then
        ./migration_manager.sh help
    else
        ./migration_manager.sh "$1"
    fi
}

# Função para executar testes
run_tests() {
    echo -e "${BLUE}Executando testes...${NC}"
    cd "$(dirname "$0")"
    python -m pytest tests/
}

# Função para limpar arquivos temporários
clean_project() {
    echo -e "${BLUE}Limpando arquivos temporários...${NC}"
    cd "$(dirname "$0")"
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    echo -e "${GREEN}Limpeza concluída!${NC}"
}

# Verificar se foi passado um comando
if [ "$#" -eq 0 ]; then
    help_message
    exit 1
fi

# Executar o comando apropriado
case "$1" in
    run)
        run_server
        ;;
    setup)
        setup_environment
        ;;
    populate)
        populate_database
        ;;
    reset)
        reset_database
        ;;
    migrations)
        if [ "$#" -eq 2 ]; then
            manage_migrations "$2"
        else
            manage_migrations
        fi
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_project
        ;;
    help)
        help_message
        ;;
    *)
        echo -e "${RED}Comando inválido: $1${NC}"
        help_message
        exit 1
        ;;
esac
