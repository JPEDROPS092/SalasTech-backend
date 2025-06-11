# Guia de Contribuição - SalasTech

Este documento apresenta as diretrizes para contribuir com o desenvolvimento do sistema SalasTech.

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos

- Python 3.10 ou superior
- Git
- Editor de código (recomendamos VS Code ou PyCharm)
- Conhecimento básico de FastAPI, SQLAlchemy e Pydantic

### Configuração Inicial

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/SalsTech-backend.git
   cd SalsTech-backend
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências de desenvolvimento:
   ```bash
   pip install -e ".[dev]"
   ```

4. Configure o banco de dados:
   ```bash
   cd src/SalasTech/app
   python db_init.py
   ```

## Estrutura do Projeto

O projeto segue a arquitetura MVC (Model-View-Controller) com as seguintes camadas:

- **Models**: Definição das entidades e DTOs
- **Repositories**: Acesso a dados
- **Services**: Lógica de negócio
- **Controllers**: Endpoints da API e páginas
- **Views**: Renderização de templates

## Fluxo de Trabalho

### 1. Escolha uma Tarefa

- Verifique as issues abertas no repositório
- Escolha uma tarefa que esteja marcada como "disponível"
- Atribua a issue a você mesmo e mude o status para "em andamento"

### 2. Crie uma Branch

Crie uma branch a partir da `main` com um nome descritivo:

```bash
git checkout main
git pull
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

### 3. Desenvolva a Solução

Siga as práticas de código e padrões do projeto:

- Escreva testes para novas funcionalidades
- Mantenha a cobertura de código acima de 80%
- Siga as convenções de nomenclatura
- Documente seu código

### 4. Execute os Testes

Antes de enviar sua contribuição, execute os testes:

```bash
cd tests
pytest
```

Verifique também a cobertura de código:

```bash
pytest --cov=SalasTech
```

### 5. Envie um Pull Request

1. Faça commit das suas alterações:
   ```bash
   git add .
   git commit -m "Descrição clara das alterações"
   ```

2. Envie para o repositório:
   ```bash
   git push origin feature/nome-da-feature
   ```

3. Abra um Pull Request no GitHub
4. Preencha o template com detalhes sobre suas alterações
5. Aguarde a revisão

## Padrões de Código

### Estilo de Código

- Siga o PEP 8 para estilo de código Python
- Use type hints em todas as funções e métodos
- Limite linhas a 100 caracteres
- Use docstrings no formato Google para documentação

### Nomenclatura

- **Classes**: PascalCase (ex: `UserService`)
- **Funções e métodos**: snake_case (ex: `get_user_by_id`)
- **Variáveis**: snake_case (ex: `user_name`)
- **Constantes**: UPPER_SNAKE_CASE (ex: `MAX_USERS`)
- **Arquivos**: snake_case (ex: `user_service.py`)

### Estrutura de Arquivos

- Um arquivo por classe principal
- Agrupe funcionalidades relacionadas no mesmo módulo
- Mantenha a hierarquia de diretórios consistente

## Documentação

### Docstrings

Todas as funções, métodos e classes devem ter docstrings:

```python
def calculate_duration(start_datetime: datetime, end_datetime: datetime) -> float:
    """
    Calcula a duração da reserva em horas.

    Args:
        start_datetime: Data e hora de início da reserva
        end_datetime: Data e hora de término da reserva

    Returns:
        Duração em horas (float)
    """
    duration = end_datetime - start_datetime
    return duration.total_seconds() / 3600
```

### Comentários

- Use comentários para explicar "por quê", não "o quê"
- Mantenha comentários atualizados com o código
- Evite comentários óbvios

## Testes

### Tipos de Testes

- **Testes Unitários**: Testam componentes isolados
- **Testes de Integração**: Testam interações entre componentes
- **Testes Funcionais**: Testam fluxos completos

### Estrutura de Testes

- Organize testes em diretórios espelhando a estrutura do código
- Use fixtures para configuração de testes
- Nomeie testes de forma descritiva

### Exemplo de Teste

```python
def test_calculate_duration():
    # Arrange
    start = datetime(2023, 1, 1, 10, 0)
    end = datetime(2023, 1, 1, 12, 30)
    
    # Act
    duration = calculate_duration(start, end)
    
    # Assert
    assert duration == 2.5
```

## Migrações de Banco de Dados

### Criar Nova Migração

```bash
cd src/SalasTech/app
bash migration_manager.sh revision -m "descrição da migração"
```

### Aplicar Migrações

```bash
bash migration_manager.sh upgrade head
```

### Reverter Migrações

```bash
bash migration_manager.sh downgrade -1
```

## Revisão de Código

### Critérios de Aceitação

- Código segue os padrões do projeto
- Testes passam e cobrem as alterações
- Documentação atualizada
- Não introduz vulnerabilidades de segurança
- Não quebra funcionalidades existentes

### Processo de Revisão

1. O revisor verifica o código e deixa comentários
2. O autor faz as alterações necessárias
3. O revisor aprova ou solicita mais alterações
4. Após aprovação, o código é mesclado à branch principal

## Versionamento

Seguimos o Versionamento Semântico (SemVer):

- **MAJOR**: Alterações incompatíveis com versões anteriores
- **MINOR**: Adições de funcionalidades compatíveis
- **PATCH**: Correções de bugs compatíveis

## Contato

Para dúvidas ou sugestões, entre em contato com:

- Email: suporte@salastech.com.br
- Discord: [Link para o servidor]