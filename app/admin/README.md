# 🔧 Painel Administrativo SalasTech

## 📋 Visão Geral

O painel administrativo do SalasTech é uma interface web moderna e intuitiva para gerenciar todos os aspectos do sistema de reservas de salas. Desenvolvido com FastAPI, Jinja2 e Bootstrap 5, oferece uma experiência rica e responsiva.

## ✨ Funcionalidades

### 🔐 **Autenticação Segura**

- Login exclusivo para administradores
- Sessões seguras com timeout automático
- Integração com sistema de autenticação existente

### 📊 **Dashboard Interativo**

- Estatísticas em tempo real
- Gráficos e métricas importantes
- Visão geral do sistema
- Ações rápidas para operações comuns

### 👥 **Gerenciamento de Usuários**

- Lista paginada de usuários
- Busca e filtros avançados
- Visualização de papéis e departamentos
- Ações em lote para administração

### 🏢 **Administração de Departamentos**

- Cards visuais com informações resumidas
- Estatísticas por departamento
- Gerenciamento de gerentes
- Visualização hierárquica

### 🚪 **Controle de Salas**

- Lista detalhada de salas
- Filtros por localização e capacidade
- Status em tempo real
- Gerenciamento de recursos

### 📅 **Supervisão de Reservas**

- Lista completa de reservas
- Filtros por status e data
- Aprovação/rejeição rápida
- Visualização detalhada

## 🚀 Como Usar

### 1. **Criar Usuário Administrador**

```bash
# Execute o script para criar o primeiro admin
python create_admin.py
```

### 2. **Iniciar o Servidor**

```bash
# Instalar dependências (se não feito)
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

### 3. **Acessar o Painel**

1. Abra o navegador em: `http://localhost:8000/admin`
2. Faça login com as credenciais do administrador
3. Explore as funcionalidades disponíveis

## 🎨 Interface

### **Design Moderno**

- Layout responsivo para desktop e mobile
- Sidebar de navegação intuitiva
- Cards e componentes visuais elegantes
- Cores e tipografia profissionais

### **Experiência do Usuário**

- Navegação fluida entre seções
- Feedback visual para ações
- Loading states e confirmações
- Mensagens de erro claras

### **Componentes Interativos**

- Tabelas com ordenação e paginação
- Modais para ações rápidas
- Filtros dinâmicos
- Badges de status coloridos

## 📱 Responsividade

O painel administrativo é totalmente responsivo:

- **Desktop**: Sidebar fixa com layout completo
- **Tablet**: Layout adaptado com navegação otimizada
- **Mobile**: Sidebar retrátil e layout mobile-first

## 🔧 Tecnologias Utilizadas

### **Backend**

- **FastAPI**: Framework web moderno e rápido
- **Jinja2**: Template engine para renderização HTML
- **SQLAlchemy**: ORM para interação com banco de dados
- **Starlette**: Framework ASGI subjacente

### **Frontend**

- **Bootstrap 5**: Framework CSS moderno
- **Font Awesome**: Ícones vetoriais
- **JavaScript Vanilla**: Interatividade sem dependências extras

### **Segurança**

- **Session Middleware**: Gerenciamento seguro de sessões
- **Password Hashing**: bcrypt para senhas
- **CSRF Protection**: Proteção contra ataques CSRF

## 📋 Funcionalidades Detalhadas

### **Dashboard**

- ✅ Estatísticas gerais do sistema
- ✅ Reservas recentes
- ✅ Novos usuários
- ✅ Ações rápidas
- ✅ Widgets informativos

### **Usuários**

- ✅ Lista paginada com busca
- ✅ Filtros por papel e departamento
- ✅ Visualização de avatares
- ⚠️ Edição inline (próxima versão)
- ⚠️ Criação de novos usuários (próxima versão)

### **Salas**

- ✅ Lista com filtros avançados
- ✅ Indicadores de status coloridos
- ✅ Informações de localização
- ⚠️ Gerenciamento de recursos (próxima versão)
- ⚠️ Upload de imagens (próxima versão)

### **Reservas**

- ✅ Visualização completa
- ✅ Filtros por status e data
- ✅ Aprovação/rejeição
- ⚠️ Edição de reservas (próxima versão)
- ⚠️ Notificações automáticas (próxima versão)

### **Departamentos**

- ✅ Cards visuais com estatísticas
- ✅ Informações de gerentes
- ✅ Contadores dinâmicos
- ⚠️ Formulários de edição (próxima versão)
- ⚠️ Hierarquia visual (próxima versão)

## 🔒 Segurança

### **Autenticação**

- Login obrigatório para acesso
- Verificação de papel de administrador
- Sessões com timeout configurável
- Logout automático em caso de inatividade

### **Autorização**

- Controle de acesso baseado em papéis
- Verificação a cada requisição
- Proteção de rotas sensíveis
- Logs de auditoria para ações críticas

### **Proteções**

- Sanitização de inputs
- Validação de dados no backend
- Proteção contra injection attacks
- Headers de segurança configurados

## 🚨 Próximas Implementações

### **Curto Prazo**

- [ ] Formulários de criação/edição
- [ ] Confirmações para ações destrutivas
- [ ] Filtros salvos e favoritos
- [ ] Exportação de dados

### **Médio Prazo**

- [ ] Notificações em tempo real
- [ ] Sistema de auditoria visual
- [ ] Relatórios integrados
- [ ] Dashboard customizável

### **Longo Prazo**

- [ ] API para integrações
- [ ] Múltiplos idiomas
- [ ] Temas personalizáveis
- [ ] App móvel dedicado

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o painel administrativo:

- **Email**: salastech@ifam.edu.br
- **Documentação**: `/docs` (API Swagger)
- **Issues**: Reportar problemas no repositório

---

**SalasTech Admin** - Desenvolvido com ❤️ para o IFAM
