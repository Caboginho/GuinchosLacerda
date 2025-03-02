import os
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.usuario import Usuario 
from flask import Blueprint, render_template, request, redirect, url_for, session

# Cria a pasta para anexos, se não existir
if not os.path.exists("anexos"):
    os.makedirs("anexos")

main_bp = Blueprint('main_bp', __name__)

google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")

user = Usuario()
@main_bp.route('/')
def inicializacao():
    session['usuario_id'] = user.getId()
    session['nome'] = user.getNome(),
    session['email'] = user.getEmail(),
    session['senha'] = None,
    session['tipo'] = user.getTipo(),
    session['cnh'] = user.getCnh(),
    session['celular'] = user.getCelular(),
    session['justificativa'] = user.getJustificativa()

    return render_template('inicializacao.html')

@main_bp.route('/verificar_inicializacao')
def verificar_inicializacao():
    banco = BancoDados()
     # --- Cadastro de Usuários ---
    admin_existente = banco.ler("usuarios", {"tipo": "Administrador"})
    if admin_existente:
        print("Administrador já existe. O sistema aceita apenas um administrador.")
        return redirect(url_for('main_bp.login'))
    else:
        userOnline = google.ler("usuarios")
        print("Usuários online: ", userOnline)
        if userOnline == []:
            return redirect(url_for('usuario_bp.cadastrar_usuario'))
        else:
            for user in userOnline:
                dados_usuario = {
                    'user_id': user[0],
                    'nome': user[1],
                    'email': user[2],
                    'senha': user[3],
                    'tipo': user[4],
                    'cnh': user[5],
                    'celular': user[6],
                    'justificativa': "NULL"
                }
                banco.inserir("usuarios", dados_usuario)
            return redirect(url_for('main_bp.login'))
        
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    banco = BancoDados()
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = banco.ler('usuarios', {'email': email})
        user.setId(usuario[0][0])
        user.setNome(usuario[0][1])
        user.setEmail(usuario[0][2])
        user.setSenha(usuario[0][3])
        user.setCnh(usuario[0][5])
        user.setCelular(usuario[0][6])
        user.setJustificativa(usuario[0][7])
        """banco.atualizar('usuarios',  user.getId(), {'justificativa': 'offiline'})
        google.atualizar('usuarios',  user.getId(), {'justificativa': 'offiline'})
        exit(0)"""
        if user.verificar_senha(senha, user.getSenha()):
            if usuario[0][4] == 'Administrador':
                # Verifica se já existe um administrador logado  
                if user.getJustificativa() == "online":
                    return "Já existe um administrador logado."
            elif user.getTipo() == 'Secretaria' and user.getJustificativa() == 'online':
                return "Esta secretaria já está logada em outro local."
            # Atualiza o estado do usuário para online
            
            session['usuario_id'] = user.getId()
            session['nome'] = user.getNome()
            session['email'] = user.getEmail()
            session['senha'] = None
            session['cnh'] = user.getCnh()
            session['celular'] = user.getCelular()
            session['justificativa'] = user.getJustificativa()
            
            banco.atualizar('usuarios',  user.getId(), {'justificativa': 'online'})
            google.atualizar('usuarios',  user.getId(), {'justificativa': 'online'})
            
            if usuario[0][4] == 'Administrador':
                
                return render_template('index.html')
            elif usuario[0][4] == 'Secretaria':
                # Sincronizar dados da secretaria
                #google.sincronizar_filial(banco, usuario[0])
                return render_template('index_secretaria.html')
        else:
            return "Credenciais inválidas. Tente novamente."
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    usuario_id = session.get('usuario_id')
    if usuario_id:
        banco = BancoDados()
        banco.atualizar('usuarios',  usuario_id, {'justificativa': 'offline'})
        google.atualizar('usuarios',  usuario_id, {'justificativa': 'offline'})
    session.pop('usuario_id', None)
    session.pop('tipo', None)
    session.pop('usuario_id', None)
    session.pop('nome', None)
    session.pop('email', None)
    session.pop('senha', None)
    session.pop('tipo', None)
    session.pop('cnh', None)
    session.pop('celular', None)
    session.pop('justificativa', None)
    return redirect(url_for('main_bp.login'))
