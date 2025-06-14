"""
Contexto de banco de dados para a aplicação SalasTech.

Este módulo é responsável por configurar e gerenciar as conexões com o banco de dados,
criando engines (motores de banco de dados), factories de sessões (sessionmakers) e
fornecendo utilitários para a inicialização e manutenção das tabelas do banco de dados.

Características principais:
- Suporte flexível para SQLite e MySQL através de configurações.
- Configuração automática do engine baseada no tipo de banco de dados especificado.
- Utilização de um pool de conexões otimizado para melhor desempenho e resiliência.
- Capacidade de criar o banco de dados automaticamente se ele não existir (especialmente para MySQL).
- Ativação do suporte a chaves estrangeiras para bancos de dados SQLite para garantir a integridade.
- Funções utilitárias para o gerenciamento do esquema das tabelas (criação, exclusão, recriação).

Autor: Equipe de Desenvolvimento SalasTech
Data: 2025
"""

from typing import Optional
from sqlalchemy import create_engine, event, text # 'text' pode ser usado para comandos SQL brutos
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from SalasTech.app.models.db import Base # Importa a Base declarativa de onde todos os modelos herdam
from SalasTech.app.core.config import CONFIG # Importa as configurações da aplicação

# Dicionário para armazenar argumentos específicos para a criação do engine.
# Isso permite flexibilidade na configuração dependendo do tipo de banco de dados.
args_engine = {
    "echo": False,  # Define se os comandos SQL executados pelo SQLAlchemy serão exibidos no console.
                    # 'True' é útil para depuração, 'False' para produção.
    "pool_pre_ping": True,  # Habilita o "pre-ping" do pool de conexões. Isso garante que as conexões
                             # no pool são testadas antes de serem usadas, detectando e descartando
                             # conexões "mortas" (por exemplo, após um timeout do servidor de banco de dados).
}
# Cria o engine (motor de banco de dados) do SQLAlchemy.
# A string de conexão é lida das configurações da aplicação.
engine = create_engine(CONFIG.DB_CONNECTION_STRING, **args_engine)

# Para SQLite, é necessário ativar explicitamente o suporte a chaves estrangeiras por conexão.
# Este listener garante que o comando PRAGMA foreign_keys=ON seja executado para cada nova conexão.
if CONFIG.DB_TYPE == "sqlite":
    @event.listens_for(Engine, "connect")
    def habilitar_pragma_sqlite(dbapi_connection, connection_record):
        """
        Listener para conexões SQLite que executa 'PRAGMA foreign_keys=ON'.
        Isso garante que as chaves estrangeiras sejam aplicadas e respeitadas
        pelo SQLite, que as desabilita por padrão para compatibilidade.
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Cria uma fábrica de sessões.
# `sessionmaker` é uma classe configurável que retorna uma nova instância de `Session`
# cada vez que é chamada.
# `bind=engine`: vincula a sessão ao engine criado.
# `expire_on_commit=False`: impede que os objetos anexados à sessão expirem após um commit,
# permitindo que seus atributos sejam acessados mesmo após a transação.
session_maker = sessionmaker(bind=engine, expire_on_commit=False)

def criar_tabelas() -> None:
    """
    Cria todas as tabelas do banco de dados conforme definidas nos modelos
    que herdam da `Base` declarativa.
    """
    Base.metadata.create_all(engine)

def excluir_tabelas() -> None:
    """
    Exclui todas as tabelas do banco de dados.
    Use com cautela, pois isso resultará na perda de todos os dados.
    """
    Base.metadata.drop_all(engine)

def recriar_tabelas() -> None:
    """
    Recria todas as tabelas do banco de dados, excluindo-as primeiro
    e depois criando-as novamente. Isso é útil para testes ou para
    redefinir o esquema do banco de dados.
    """
    excluir_tabelas() # Primeiro, remove todas as tabelas existentes
    criar_tabelas()   # Em seguida, cria as tabelas novamente

def auto_criar_banco_dados():
    """
    Tenta conectar ao banco de dados e criar suas tabelas.
    Para MySQL, se o banco de dados especificado na string de conexão
    não existir, ele tenta criá-lo automaticamente antes de criar as tabelas.
    Para SQLite, o arquivo do banco de dados é criado automaticamente
    quando as tabelas são geradas.
    """
    try:
        # Tenta estabelecer uma conexão para verificar se o banco de dados e as tabelas existem.
        # Se a conexão falhar, especialmente em MySQL, pode ser que o DB não exista.
        with engine.connect() as conexao:
            criar_tabelas() # Se a conexão for bem-sucedida, tenta criar as tabelas (elas serão criadas se não existirem)
            conexao.close() # Garante que a conexão seja fechada.

    except Exception as e:
        # Se ocorrer uma exceção na conexão inicial
        if CONFIG.DB_TYPE == "mysql":
            # Para MySQL, a exceção pode indicar que o banco de dados não existe.
            # Tentamos criar o banco de dados programaticamente.
            try:
                # Extrai a parte da string de conexão que não inclui o nome do banco de dados.
                # Ex: "mysql://user:pass@host:port/dbname" -> "mysql://user:pass@host:port" e "dbname"
                string_conexao_sem_db, nome_db = CONFIG.DB_CONNECTION_STRING.rsplit("/", 1)
                
                # Cria um engine temporário para conectar ao servidor MySQL (sem um DB específico).
                engine_temporario = create_engine(string_conexao_sem_db)
                
                # Usa uma sessão para executar um comando SQL direto para criar o banco de dados.
                with engine_temporario.begin() as sessao_temporaria:
                    # Executa o comando SQL para criar o banco de dados. O nome é escapado com backticks
                    # para evitar problemas com nomes que são palavras reservadas ou contêm caracteres especiais.
                    sessao_temporaria.exec_driver_sql(f"CREATE DATABASE `{nome_db}`")
                
                # Após o banco de dados ser criado, tenta criar as tabelas novamente.
                # Agora o engine principal deve conseguir conectar-se ao DB recém-criado.
                criar_tabelas()
                print(f"Banco de dados '{nome_db}' criado e tabelas inicializadas com sucesso.")
            except Exception as erro_mysql:
                # Captura erros que podem ocorrer durante a criação do banco de dados MySQL.
                print(f"Erro ao criar o banco de dados MySQL: {erro_mysql}")
                raise # Re-lança a exceção original para que seja tratada em um nível superior.
        elif CONFIG.DB_TYPE == "sqlite":
            # Para SQLite, o arquivo de banco de dados é criado automaticamente
            # quando Base.metadata.create_all() é chamado.
            # Se uma exceção ocorreu, pode ser um problema de permissão ou caminho inválido.
            criar_tabelas() # Tenta criar as tabelas novamente; o arquivo será gerado.
            print(f"Banco de dados SQLite criado/inicializado com sucesso.")
        else:
            # Para outros tipos de banco de dados não explicitamente tratados,
            # re-lança a exceção original.
            print(f"Erro inesperado ao conectar ou criar banco de dados: {e}")
            raise # Re-lança a exceção.