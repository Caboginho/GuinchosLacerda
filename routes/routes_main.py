import os
from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.usuario import Usuario
from classes.administrador import Administrador
from classes.secretaria import Secretaria
import pandas as pd
import requests

main_bp = Blueprint('main_bp', __name__)

def get_google_drive():
    return GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")

def check_internet():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.RequestException:
        return False

def get_admin():
    """Retorna instância do admin atual"""
    banco = BancoDados()
    google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
    return Administrador(
        id=session.get('usuario_id'),
        nome=session.get('nome'),
        email=session.get('email'),
        senha=None,
        cnh=session.get('cnh'),
        celular=session['celular'],
        justificativa=session['justificativa'],
        local_db=banco,
        cloud_db=google
    )

@main_bp.route('/')
def inicializacao():
    """Tela inicial do sistema"""
    return render_template('inicializacao.html')

@main_bp.route('/verificar_estruturas')
def verificar_estruturas():
    def generate():
        try:
            # 1. Verificar conexão
            yield "data: 25\n\n"
            has_internet = check_internet()
            print("Status da conexão:", "Online" if has_internet else "Offline")
            
            # 2. Criar pasta anexos local
            yield "data: 50\n\n"
            if not os.path.exists("anexos"):
                os.makedirs("anexos")
                print("Pasta 'anexos' criada localmente")
            
            # 3. Inicializar banco local
            banco = BancoDados()
            banco.criar_tabela_usuario()
            banco.criar_tabela_guincho()
            
            yield "data: 75\n\n"
            
            if has_internet:
                try:
                    google = get_google_drive()
                    # Verifica usuários na nuvem
                    cloud_users = google.ler('usuarios')
                    print(f"Encontrados {len(cloud_users)} usuários na nuvem")
                    
                    if not cloud_users.empty:
                        # Sincroniza usuários da nuvem para local
                        banco.deletar("usuarios")  # Limpa tabela local
                        cloud_users.to_sql("usuarios", banco.conexao, if_exists='replace', index=False)
                        print("Banco local atualizado com dados da nuvem")
                        yield "data: redirect_login\n\n"
                        return
                        
                    # Se não há usuários na nuvem, verifica local
                    local_users = banco.ler("usuarios")
                    if not local_users.empty:
                        # Sincroniza local para nuvem
                        google.sincronizar_com_nuvem('usuarios', local_users)
                        yield "data: redirect_login\n\n"
                    else:
                        yield "data: redirect_primeiro_cadastro\n\n"
                    return
                    
                except Exception as e:
                    print(f"Erro ao sincronizar com nuvem: {e}")
                    # Continua verificação local
            
            # Modo offline ou erro de sincronização
            local_users = banco.ler("usuarios")
            if local_users.empty:
                yield "data: redirect_primeiro_cadastro\n\n"
            else:
                yield "data: redirect_login\n\n"
            return

        except Exception as e:
            print(f"Erro durante verificação: {e}")
            yield "data: redirect_primeiro_cadastro\n\n"

    return Response(generate(), mimetype="text/event-stream")

@main_bp.route('/primeiro_cadastro', methods=['GET', 'POST'])
def primeiro_cadastro():
    """Rota exclusiva para primeiro cadastro do administrador"""
    banco = BancoDados()
    
    # Verifica se já existe algum usuário cadastrado
    usuarios = banco.ler("usuarios")
    if not usuarios.empty:
        return redirect(url_for('main_bp.login'))
    
    if request.method == 'POST':
        try:
            google = get_google_drive()
            user = Usuario()
            
            dados = {
                'id': 1,
                'nome': request.form['nome'].strip(),
                'email': request.form['email'].strip(),
                'senha': user.hash_senha(request.form['senha']),
                'tipo': 'Administrador',
                'cnh': request.form.get('cnh', '').strip(),
                'celular': request.form['celular'].strip(),
                'justificativa': 'offline'
            }
            
            # Se tiver internet, salva primeiro na nuvem
            if check_internet():
                try:
                    # Inicializa a planilha de usuários
                    google.inicializar_planilha_usuarios()
                    # Insere dados preenchendo todas as colunas
                    headers = ['id', 'nome', 'email', 'senha', 'tipo', 'cnh', 'celular', 'justificativa']
                    row_data = [str(dados.get(h, '')) for h in headers]
                    google.usuarios_sheet.sheet1.append_row(row_data)
                    print("[DEBUG] Administrador cadastrado na nuvem")
                    print(f"[DEBUG] Dados enviados para nuvem: {dict(zip(headers, row_data))}")
                except Exception as e:
                    print(f"[DEBUG] Erro ao cadastrar na nuvem: {e}")
                    # Se falhar na nuvem, continua com cadastro local
            
            # Depois insere no banco local
            banco.inserir("usuarios", dados)
            print("[DEBUG] Administrador cadastrado localmente")
            
            # Cria outras tabelas necessárias
            banco.criar_tabela_guincho()
            banco.criar_tabela_transacoes()
            banco.criar_tabela_servicos_guincho()
            
            # Se houver erro na nuvem, marca para sincronização futura
            if not google.check_internet():
                banco.marcar_para_sincronizacao("usuarios", 1, "insert")
            
            return redirect(url_for('main_bp.login'))
            
        except Exception as e:
            print(f"[DEBUG] Erro no cadastro: {e}")
            return render_template('usuarios.html', 
                                primeiro_cadastro=True, 
                                erro="Erro ao cadastrar. Tente novamente.")
    
    return render_template('usuarios.html', primeiro_cadastro=True)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de autenticação com inicialização específica por tipo de usuário"""
    if request.method == 'POST':
        try:
            banco = BancoDados()
            email = request.form['email']
            senha_digitada = request.form['senha']
            
            print(f"[DEBUG] Iniciando login para: {email}")
            
            resultado = banco.ler('usuarios', {'email': email})
            if resultado.empty:
                return render_template('login.html', erro="Email ou senha inválidos")

            user_data = resultado.iloc[0]
            user = Usuario()
            
            if not user.verificar_senha(senha_digitada, str(user_data['senha'])):
                return render_template('login.html', erro="Email ou senha inválidos")

            # Configura sessão básica
            user_id = int(float(user_data['id']))
            session.update({
                'usuario_id': user_id,
                'tipo': str(user_data['tipo']),
                'nome': str(user_data['nome']),
                'email': str(user_data['email']),
                'cnh': str(user_data['cnh']) if pd.notna(user_data['cnh']) else '',
                'celular': str(user_data['celular']),
                'justificativa': 'online'
            })

            # Inicialização específica por tipo
            if user_data['tipo'] == 'Administrador':
                print("[DEBUG] Iniciando como Administrador")
                try:
                    # Cria todas as tabelas locais
                    banco.criar_tabela_guincho()
                    banco.criar_tabela_transacoes()
                    banco.criar_tabela_servicos_guincho()
                    
                    # Sincroniza dados de todas as secretarias
                    admin = get_admin()  # Agora a função existe
                    if admin:
                        admin.sincronizar_todas_secretarias()
                        print("[DEBUG] Sincronização de secretarias concluída")
                    return redirect(url_for('admin_bp.index'))
                except Exception as e:
                    print(f"[DEBUG] Erro na inicialização do admin: {e}")
                    return render_template('login.html', erro="Erro na inicialização")

            elif user_data['tipo'] == 'Secretaria':
                print(f"[DEBUG] Iniciando como Secretaria: {email}")
                # Sincroniza apenas dados da secretaria logada
                google = get_google_drive()
                dados_secretaria = google.ler_dados_secretaria(email)
                banco.sincronizar_dados_secretaria(dados_secretaria, user_id)
                return redirect(url_for('sec_bp.index'))

        except Exception as e:
            print(f"[DEBUG] Erro no login: {e}")
            return render_template('login.html', erro="Erro ao fazer login")

    return render_template('login.html')

@main_bp.route('/login', methods=['POST'])
def login_post():
    try:
        email = request.form.get('email')
        senha = request.form.get('senha')
        print(f"[DEBUG] Iniciando login para: {email}")

        banco = BancoDados()
        usuario_df = banco.ler('usuarios', {'email': email})
        
        if usuario_df.empty:
            print("[DEBUG] Usuário não encontrado")
            return jsonify({'error': 'Usuário não encontrado'}), 401

        usuario = usuario_df.iloc[0]
        if usuario['senha'] != senha:
            print("[DEBUG] Senha incorreta")
            return jsonify({'error': 'Senha incorreta'}), 401

        print(f"[DEBUG] Iniciando como {usuario['tipo']}")
        
        # Configura a sessão
        session['logado'] = True
        session['usuario_id'] = int(usuario['id'])
        session['nome'] = usuario['nome']
        session['email'] = usuario['email']
        session['tipo'] = usuario['tipo']
        session['celular'] = usuario['celular']
        session['justificativa'] = usuario['justificativa']
        session['cnh'] = usuario['cnh']

        # Se for admin, sincroniza dados
        if usuario['tipo'] == 'Administrador':
            try:
                admin = Administrador(
                    id=usuario['id'],
                    nome=usuario['nome'],
                    email=usuario['email'],
                    senha=usuario['senha'],
                    cnh=usuario['cnh'],
                    celular=usuario['celular'],
                    justificativa=usuario['justificativa']
                )
                admin.sincronizar_todas_secretarias()
            except Exception as e:
                print(f"[DEBUG] Erro na inicialização do admin: {e}")
                # Continua mesmo se houver erro na sincronização

        return jsonify({
            'success': True,
            'tipo': usuario['tipo']
        })

    except Exception as e:
        print(f"[DEBUG] Erro no login: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/logout')
def logout():
    """Rota de logout"""
    user_id = session.get('usuario_id')
    if user_id:
        try:
            banco = BancoDados()
            novos_dados = {'justificativa': 'offline'}
            
            # Atualiza banco local
            banco.atualizar('usuarios', linha=user_id, novos_dados=novos_dados)
            
            # Atualiza planilha se houver internet
            if check_internet():
                google = get_google_drive()
                # Atualiza na linha correta (ID-1 para posição real na planilha)
                google.atualizar(linha=user_id-1, novos_dados=novos_dados)
                
        except Exception as e:
            print(f"Erro ao fazer logout: {e}")
            
    session.clear()
    return redirect(url_for('main_bp.login'))

