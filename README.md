# SalasTech - Sistema de Gerenciamento de Salas

SalasTech é um sistema completo para gerenciamento de salas e reservas, desenvolvido com FastAPI e seguindo a arquitetura MVC.

## Funcionalidades

- Gerenciamento de usuários com diferentes níveis de acesso
- Gerenciamento de departamentos
- Cadastro e manutenção de salas e recursos
- Sistema de reservas com regras de negócio
- Aprovação automática ou manual de reservas
- Relatórios e estatísticas de uso
- Interface web e API REST
- CLI para administração

## Tecnologias

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Banco de Dados**: SQLite (desenvolvimento), PostgreSQL (produção)
- **Autenticação**: JWT
- **CLI**: Typer, Rich
- **Testes**: Pytest

## Documentação

A documentação completa está disponível no diretório `docs/`:

- [API](docs/API.md): Documentação da API REST
- [Arquitetura](docs/Arquitetura.md): Visão geral da arquitetura do sistema
- [CLI](docs/CLI.md): Documentação da interface de linha de comando
- [Instalação](docs/Instalacao.md): Guia de instalação e configuração
- [Manual do Usuário](docs/ManualUsuario.md): Manual para usuários finais
- [Regras de Negócio](docs/RegraNegocio.md): Regras de negócio implementadas
- [Regras do Sistema](docs/RegrasDeSistema.md): Regras técnicas do sistema
- [Plano de Testes](docs/plano_de_testes.md): Estratégia e casos de teste
- [Contribuição](docs/Contribuicao.md): Guia para contribuidores
- [API Exemplos](docs/API_Exemplos.md): Exemplos práticos de uso da API

## Instalação Rápida

1. Clone o repositório:

   ```bash
   git clone https://github.com/jpedrops092/SalsTech-backend.git
   cd SalsTech-backend
   ```
2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:

   ```bash
   pip install -e .
   ```
4. Configure o ambiente:

   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```
5. Inicialize o banco de dados:

   ```bash
   cd src/SalasTech/app
   python db_init.py
   ```
6. Inicie o servidor:

   ```bash
   uvicorn main:app --reload
   ```
7. Acesse a aplicação:

   - Interface Web: http://localhost:8000
   - API: http://localhost:8000/api
   - Documentação da API: http://localhost:8000/api/docs

## Uso da CLI

Após a instalação, a CLI estará disponível:

```bash
# Ver comandos disponíveis
SalasTech --help

# Exemplos
SalasTech user list
SalasTech room create
SalasTech reservation list
```

## Estrutura do Projeto

```
SalasTech-backend/
├── docs/                   # Documentação
├── scripts/                # Scripts de utilidade
├── src/
│   └── SalasTech/
│       ├── app/            # Aplicação principal
│       │   ├── controllers/  # Controladores (API e páginas)
│       │   ├── core/         # Configurações e dependências
│       │   ├── exceptions/   # Tratamento de exceções
│       │   ├── mappers/      # Mapeadores de objetos
│       │   ├── migrations/   # Migrações do banco de dados
│       │   ├── models/       # Modelos de dados
│       │   ├── repos/        # Repositórios de acesso a dados
│       │   ├── schedulers/   # Tarefas agendadas
│       │   ├── services/     # Serviços de negócio
│       │   ├── static/       # Arquivos estáticos
│       │   ├── utils/        # Utilitários
│       │   └── views/        # Views para renderização
│       └── cli/            # Interface de linha de comando
└── tests/                  # Testes automatizados
```

## Desenvolvimento

Para configurar o ambiente de desenvolvimento, consulte o [Guia de Contribuição](docs/Contribuicao.md).

## Testes

Execute os testes com:

```bash
cd tests
pytest
```

Para verificar a cobertura de código:

```bash
pytest --cov=SalasTech
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

Para dúvidas ou sugestões, entre em contato com:

- Email: suporte@salastech.com.br
