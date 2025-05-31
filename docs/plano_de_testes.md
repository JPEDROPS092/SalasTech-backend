# Plano de Testes - Sistema de Gerenciamento de Salas IFAM

## 1. Introdução

Este documento descreve o plano de testes para o Sistema de Gerenciamento de Salas do IFAM. O objetivo é garantir a qualidade do software através de uma estratégia abrangente de testes que cubra todos os componentes e funcionalidades do sistema.

## 2. Escopo de Testes

### 2.1 Componentes a serem testados

- **Modelos de dados**: Validação da estrutura e relacionamentos do banco de dados
- **Serviços**: Lógica de negócio para gerenciamento de salas, reservas e usuários
- **Controladores**: Endpoints da API e controladores de páginas
- **Templates**: Interface do usuário e experiência de navegação
- **Integrações**: Interações entre os diferentes componentes do sistema

### 2.2 Tipos de Testes

- **Testes Unitários**: Validação isolada de componentes individuais
- **Testes de Integração**: Verificação da interação entre componentes
- **Testes Funcionais**: Validação do comportamento do sistema conforme requisitos
- **Testes de Interface**: Verificação da experiência do usuário e usabilidade
- **Testes de Desempenho**: Avaliação do tempo de resposta e capacidade do sistema
- **Testes de Segurança**: Verificação de vulnerabilidades e controle de acesso

## 3. Estratégia de Testes

### 3.1 Testes Unitários

Os testes unitários serão implementados usando o framework pytest e focam em validar o comportamento isolado de:

- **Modelos**: Validação da criação, leitura, atualização e exclusão de entidades
- **Serviços**: Verificação da lógica de negócio para cada operação
- **Utilitários**: Teste de funções auxiliares e componentes de infraestrutura

### 3.2 Testes de Integração

Os testes de integração verificarão a interação entre:

- **Serviços e Repositórios**: Validação da persistência de dados
- **Controladores e Serviços**: Verificação do fluxo de dados entre camadas
- **Autenticação e Autorização**: Teste do sistema de controle de acesso

### 3.3 Testes Funcionais

Os testes funcionais validarão os fluxos completos do sistema:

- **Gerenciamento de Salas**: Criação, edição, visualização e exclusão de salas
- **Reservas**: Ciclo completo de reserva, desde a solicitação até a finalização
- **Relatórios**: Geração e visualização de relatórios diversos
- **Administração**: Funcionalidades de gerenciamento do sistema

### 3.4 Testes de Interface

Os testes de interface verificarão:

- **Responsividade**: Adaptação a diferentes tamanhos de tela
- **Usabilidade**: Facilidade de uso e navegação
- **Acessibilidade**: Conformidade com diretrizes de acessibilidade
- **Compatibilidade**: Funcionamento em diferentes navegadores

### 3.5 Testes de Desempenho

Os testes de desempenho avaliarão:

- **Tempo de Resposta**: Velocidade de carregamento de páginas e execução de operações
- **Escalabilidade**: Comportamento do sistema sob carga
- **Concorrência**: Capacidade de lidar com múltiplos usuários simultâneos

### 3.6 Testes de Segurança

Os testes de segurança verificarão:

- **Autenticação**: Robustez do sistema de login
- **Autorização**: Controle de acesso baseado em papéis
- **Proteção de Dados**: Segurança das informações armazenadas
- **Vulnerabilidades**: Resistência a ataques comuns (SQL Injection, XSS, CSRF)

## 4. Ambiente de Testes

### 4.1 Configuração de Ambiente

- **Banco de Dados**: SQLite para testes unitários e de integração, MySQL para testes de integração completos
- **Servidor**: Ambiente de desenvolvimento local
- **Navegadores**: Chrome, Firefox, Safari, Edge (últimas versões)
- **Dispositivos**: Desktop, tablet e smartphone para testes responsivos

### 4.2 Dados de Teste

- **Dados Sintéticos**: Gerados pelo script de população do banco de dados
- **Casos de Teste**: Cenários específicos para validar comportamentos esperados
- **Dados de Limite**: Valores extremos para testar robustez do sistema

## 5. Ferramentas de Teste

- **pytest**: Framework principal para testes unitários e de integração
- **pytest-cov**: Análise de cobertura de código
- **Selenium/Playwright**: Testes de interface automatizados
- **Locust**: Testes de carga e desempenho
- **OWASP ZAP**: Análise de segurança e vulnerabilidades

## 6. Cronograma de Testes

| Fase | Duração | Atividades |
|------|---------|------------|
| Planejamento | 1 semana | Definição de casos de teste, preparação de ambiente |
| Implementação | 2 semanas | Desenvolvimento dos testes automatizados |
| Execução | 1 semana | Execução de testes e registro de resultados |
| Análise | 1 semana | Avaliação dos resultados e identificação de problemas |
| Correção | 1-2 semanas | Correção de defeitos encontrados |
| Reteste | 1 semana | Verificação das correções implementadas |

## 7. Critérios de Aceitação

- **Cobertura de Código**: Mínimo de 80% de cobertura para código de produção
- **Defeitos Críticos**: Zero defeitos críticos ou bloqueadores
- **Desempenho**: Tempo de resposta máximo de 2 segundos para operações comuns
- **Segurança**: Nenhuma vulnerabilidade de alto risco identificada

## 8. Relatórios e Métricas

Os seguintes relatórios serão gerados durante o processo de teste:

- **Relatório de Cobertura**: Percentual de código coberto pelos testes
- **Relatório de Defeitos**: Lista de problemas encontrados, classificados por severidade
- **Relatório de Desempenho**: Métricas de tempo de resposta e capacidade
- **Relatório de Segurança**: Vulnerabilidades identificadas e recomendações

## 9. Casos de Teste

### 9.1 Testes de Modelos

| ID | Descrição | Pré-condições | Passos | Resultado Esperado |
|----|-----------|---------------|--------|-------------------|
| TM-01 | Criação de Departamento | Banco de dados vazio | 1. Criar objeto Departamento<br>2. Salvar no banco | Departamento criado com sucesso |
| TM-02 | Criação de Usuário | Departamento existente | 1. Criar objeto Usuário<br>2. Associar a um departamento<br>3. Salvar no banco | Usuário criado com sucesso |
| TM-03 | Criação de Sala | Departamento existente | 1. Criar objeto Sala<br>2. Associar a um departamento<br>3. Salvar no banco | Sala criada com sucesso |
| TM-04 | Criação de Reserva | Sala e Usuário existentes | 1. Criar objeto Reserva<br>2. Associar a uma sala e usuário<br>3. Salvar no banco | Reserva criada com sucesso |

### 9.2 Testes de Serviços

| ID | Descrição | Pré-condições | Passos | Resultado Esperado |
|----|-----------|---------------|--------|-------------------|
| TS-01 | Listar Salas Disponíveis | Salas cadastradas | 1. Definir período de busca<br>2. Chamar serviço de busca | Lista de salas disponíveis retornada |
| TS-02 | Criar Reserva | Sala disponível e usuário válido | 1. Preparar dados da reserva<br>2. Chamar serviço de criação | Reserva criada com status pendente |
| TS-03 | Aprovar Reserva | Reserva pendente existente | 1. Identificar reserva<br>2. Chamar serviço de aprovação | Reserva com status alterado para confirmada |
| TS-04 | Autenticar Usuário | Usuário cadastrado | 1. Fornecer credenciais<br>2. Chamar serviço de autenticação | Usuário autenticado com sucesso |

### 9.3 Testes Funcionais

| ID | Descrição | Pré-condições | Passos | Resultado Esperado |
|----|-----------|---------------|--------|-------------------|
| TF-01 | Fluxo de Reserva | Usuário autenticado | 1. Buscar sala disponível<br>2. Criar reserva<br>3. Aprovar reserva<br>4. Verificar status | Reserva confirmada visível no sistema |
| TF-02 | Geração de Relatório | Dados de reservas existentes | 1. Acessar área de relatórios<br>2. Selecionar tipo de relatório<br>3. Definir parâmetros<br>4. Gerar relatório | Relatório gerado com dados corretos |
| TF-03 | Manutenção de Sala | Sala ativa existente | 1. Acessar detalhes da sala<br>2. Agendar manutenção<br>3. Verificar status | Sala com status alterado para manutenção |

## 10. Riscos e Mitigação

| Risco | Probabilidade | Impacto | Estratégia de Mitigação |
|-------|--------------|---------|-------------------------|
| Atrasos no cronograma | Média | Alto | Priorização de testes críticos, automação de testes repetitivos |
| Falsos positivos/negativos | Média | Médio | Revisão manual dos resultados, melhoria contínua dos casos de teste |
| Ambiente instável | Baixa | Alto | Configuração de ambiente dedicado, isolamento de testes |
| Cobertura insuficiente | Média | Alto | Monitoramento constante da cobertura, adição de testes para áreas críticas |

## 11. Responsabilidades

| Papel | Responsabilidades |
|-------|------------------|
| Gerente de Testes | Coordenação geral, planejamento, relatórios |
| Analista de Testes | Especificação de casos de teste, análise de resultados |
| Desenvolvedor de Testes | Implementação de testes automatizados |
| Testador | Execução de testes manuais, validação de correções |
| Desenvolvedor | Correção de defeitos, suporte à equipe de testes |

## 12. Aprovação

Este plano de testes deve ser revisado e aprovado pelos seguintes stakeholders:

- Gerente de Projeto
- Líder Técnico
- Representante do Cliente
- Gerente de Qualidade

## Anexos

- Modelo de Relatório de Defeitos
- Checklist de Testes Manuais
- Guia de Configuração do Ambiente de Testes
