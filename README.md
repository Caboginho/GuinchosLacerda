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

## Tecnologias Utilizadas

- Python 3.x
- Flask (Framework Web)
- SQLite (Banco de dados local)
- Google Drive API
- Google Sheets API
- HTML/CSS/JavaScript

## Funcionalidades

- Gestão de usuários (Administradores, Secretárias, Motoristas)
- Controle de transações financeiras
- Gerenciamento de serviços de guincho
- Registro de veículos/guinchos
- Integração com Google Drive para anexos
- Sincronização com Google Sheets
- Interface responsiva
