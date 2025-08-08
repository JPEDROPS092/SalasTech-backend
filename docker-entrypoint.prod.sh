#!/bin/bash

# =============================================================================
# SCRIPT DE INICIALIZAÇÃO PARA PRODUÇÃO - SALASTECH
# =============================================================================

set -e  # Sair se algum comando falhar

echo "🚀 Iniciando SalasTech em modo PRODUÇÃO..."

# Verificar variáveis de ambiente obrigatórias
if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERRO: SECRET_KEY não definida!"
    exit 1
fi

# Aguardar um pouco para garantir que o sistema está pronto
sleep 3

# Verificar se o banco de dados existe e executar migrações se necessário
echo "📊 Verificando banco de dados..."

if [ ! -f "db.sqlite" ]; then
    echo "🔧 Banco de dados não encontrado. Executando migrações..."
    python -m migrations.migrate
else
    echo "✅ Banco de dados encontrado."
fi

# Verificar migrações pendentes
echo "🔄 Verificando migrações pendentes..."
python -m migrations.check_migrations

# Criar backup do banco antes de iniciar (se existe)
if [ -f "db.sqlite" ]; then
    echo "💾 Criando backup do banco de dados..."
    python scripts/backup_database.py
fi

# Log de inicialização
echo "🎯 Iniciando servidor SalasTech em PRODUÇÃO..."
echo "📍 API disponível na porta 8000"
echo "📊 Logs salvos em: /app/logs/"

# Iniciar a aplicação com configurações de produção
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --access-log \
    --log-level info \
    --no-server-header
