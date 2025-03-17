# GuinchoLacerda

Sistema para gerenciamento de serviços de guincho, controle financeiro e gestão de despesas.

## Estrutura do Projeto

```
d:\Trabalho\GuinchoLacerda\
├── app.py                         # Arquivo principal da aplicação
├── requirements.txt               # Dependências do projeto
│
├── app\                          # Configurações da aplicação
│   └── __init__.py
│
├── classes\                      # Classes do sistema
│   ├── administrador.py         # Classe para administradores
│   ├── bancodados.py           # Classe para gerenciamento do banco SQLite
│   ├── googledrivesheets.py    # Classe para integração com Google Sheets/Drive
│   ├── secretaria.py           # Classe para secretárias
│   └── usuario.py              # Classe base de usuários
│
├── routes\                      # Rotas da aplicação
│   ├── routes_admin.py         # Rotas administrativas
│   ├── routes_financeiro.py    # Rotas financeiras
│   ├── routes_guinchos.py      # Rotas de guinchos
│   ├── routes_main.py          # Rotas principais
│   ├── routes_sec.py           # Rotas da secretaria
│   ├── routes_servicos_guincho.py  # Rotas de serviços
│   ├── routes_transacoes.py    # Rotas de transações
│   └── routes_usuario.py       # Rotas de usuários
│
├── static\                      # Arquivos estáticos
│   ├── css\                    # Estilos CSS
│   ├── js\                     # Scripts JavaScript
│   │   ├── admin.js
│   │   ├── financeiro.js
│   │   ├── sec.js
│   │   ├── servicos_guincho.js
│   │   ├── transacoes.js
│   │   └── usuarios.js
│   └── src\                    # Recursos (imagens, ícones)
│       └── favicon.ico
│
├── templates\                   # Templates HTML
│   ├── admin.html              # Dashboard do administrador
│   ├── financeiro.html         # Página financeira
│   ├── inicializacao.html      # Página inicial
│   ├── login.html              # Página de login
│   ├── sec.html               # Dashboard da secretária
│   ├── servicos_guincho.html  # Página de serviços
│   ├── transacoes.html        # Página de transações
│   └── usuarios.html          # Página de usuários
│
├── anexos\                     # Pasta para arquivos anexados
└── credentials\               # Credenciais e configurações
    └── lacerdaguinchos-8e2aeaf562ce.json
        key app 8e2aeaf562ce59676d8ed677f7e88935acc3fe44
```

## Fluxo do Sistema

```
inicializacao.html
├── Verifica Admin Cadastrado
│   ├── NÃO
│   │   └── Cadastro Inicial Admin
│   │       ├── Sucesso -> Login
│   │       └── Falha -> Retorna Cadastro
│   │
│   └── SIM
│       └── Login
│           ├── Admin (admin.html)
│           │   ├── Gestão de Usuários
│           │   │   ├── Criar (POST /usuarios/novo)
│           │   │   ├── Editar (PUT /usuarios/<id>)
│           │   │   └── Deletar (DELETE /usuarios/<id>)
│           │   │
│           │   ├── Gestão de Guinchos
│           │   │   ├── Cadastrar (POST /guinchos/novo)
│           │   │   ├── Atualizar (PUT /guinchos/<id>)
│           │   │   └── Remover (DELETE /guinchos/<id>)
│           │   │
│           │   └── Relatórios Financeiros
│           │       ├── Visualizar (GET /financeiro/relatorios)
│           │       └── Exportar (GET /financeiro/exportar)
│           │
│           └── Secretária (sec.html)
│               ├── Serviços de Guincho
│               │   ├── Registrar (POST /servicos/novo)
│               │   ├── Atualizar Status (PUT /servicos/<id>)
│               │   └── Consultar (GET /servicos)
│               │
│               ├── Transações
│               │   ├── Registrar (POST /transacoes/nova)
│               │   └── Consultar (GET /transacoes)
│               │
│               └── Anexos
│                   ├── Upload (POST /anexos/upload)
│                   └── Download (GET /anexos/<id>)
```

## Permissões por Perfil

### Administrador
- Acesso total ao sistema
- Gerenciamento de usuários
- Configurações do sistema
- Relatórios gerenciais
- Gestão financeira completa

### Secretária
- Registro de serviços
- Gestão de transações
- Consulta de relatórios básicos
- Upload de anexos
- Atualização de status de serviços

## Templates e Funcionalidades

### inicializacao.html
- Verificação inicial do sistema
- Redirecionamento para cadastro ou login

### login.html
- Autenticação de usuários
- Redirecionamento baseado em perfil

### admin.html
- Dashboard administrativo
- Métricas e indicadores
- Acesso a todas as funcionalidades

### sec.html
- Interface da secretária
- Gestão de serviços diários
- Registro de transações

### servicos_guincho.html
- Cadastro de serviços
- Acompanhamento de status
- Histórico de atendimentos

### transacoes.html
- Registro financeiro
- Controle de pagamentos
- Histórico de transações

### usuarios.html
- Gestão de contas
- Permissões e acessos
- Dados cadastrais

### financeiro.html
- Balanço financeiro
- Relatórios e exportações
- Análise de receitas/despesas

## Tecnologias Utilizadas

- Python 3.11
- Flask 3.1.0
- SQLite 3
- Google Drive API v3
- Google Sheets API v4
- HTML5/CSS3/JavaScript
- Bootstrap 5.3
- JQuery 3.7

## Integrações

- Google Drive: Armazenamento de anexos
- Google Sheets: Sincronização de dados
- SQLite: Banco de dados local
- API REST: Comunicação entre módulos

## Segurança

- Autenticação por sessão
- Criptografia de senhas
- Controle de acesso por perfil
- Validação de dados
- Proteção contra CSRF
