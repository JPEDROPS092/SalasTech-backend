#!/bin/bash

# Script de inicialização do Docker para SalasTech

echo "🚀 Iniciando SalasTech..."

# Aguardar um pouco para garantir que o sistema está pronto
sleep 2

# Verificar se o banco de dados existe e executar migrações se necessário
echo "📊 Verificando banco de dados..."

if [ ! -f "db.sqlite" ]; then
    echo "🔧 Banco de dados não encontrado. Executando migrações..."
    python -m migrations.migrate
else
    echo "✅ Banco de dados encontrado."
fi

# Verificar se há migrações pendentes
echo "🔄 Verificando migrações pendentes..."
python -m migrations.check_migrations

echo "🎯 Iniciando servidor SalasTech..."
echo "📍 API disponível em: http://localhost:8000"
echo "📖 Documentação disponível em: http://localhost:8000/docs"
echo "🔧 Painel Admin disponível em: http://localhost:8000/admin"

# Iniciar a aplicação
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
