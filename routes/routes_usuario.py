import os
from flask import Blueprint, request, redirect, url_for, render_template, session
from classes.usuario import Administrador

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    if request.method == 'POST':
        tipo = request.form['tipo']
        if tipo == 'Administrador':
            # Verifica se já existe um administrador cadastrado
            admin_existente = Adm.ler_registros('usuarios', {'tipo': 'Administrador'})
            if admin_existente:
                return "Já existe um administrador cadastrado."
        senha = request.form['senha'] if tipo != 'Motorista' else None
        if senha != None:
            senha = Adm.hash_senha(senha)
        dados_usuario = {
            'nome': request.form['nome'],
            'email': request.form['email'],
            'senha': senha,
            'tipo': tipo,
            'cnh': request.form.get('cnh') if request.form.get('cnh') else None,
            'celular': request.form['celular'],
            'justificativa': 'offline'
        }
        Adm.criar_registro('usuarios', dados_usuario)
        if session['usuario_id'] is None:
            return redirect(url_for('main_bp.login'))
    return render_template('usuarios.html', usuarios=Adm.ler_registros('usuarios', {}))

@usuario_bp.route('/atualizar_usuario', methods=['POST'])
def atualizar_usuario():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    usuario_id = request.form['usuario_id']
    senha = request.form['senha'] if request.form['tipo'] != 'Motorista' else None
    dados_usuario = {
        'nome': request.form['nome'],
        'email': request.form['email'],
        'senha': senha,
        'tipo': request.form['tipo'],
        'cnh': request.form.get('cnh') if request.form.get('cnh') else None,
        'celular': request.form['celular'],
        'justificativa': request.form.get('justificativa') if request.form.get('justificativa') else 'offline'
    }
    Adm.atualizar_registro('usuarios', int(usuario_id), dados_usuario)
    return render_template('usuarios.html', usuarios=Adm.ler_registros('usuarios', {}))

@usuario_bp.route('/deletar_usuario', methods=['POST'])
def deletar_usuario():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],         
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    usuario_id = request.form['usuario_id']
    Adm.deletar_registro('usuarios', usuario_id)
    return render_template('usuarios.html', usuarios=Adm.ler_registros('usuarios', {}))

@usuario_bp.route('/usuarios_pg')
def usuarios_pg():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],         
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    return render_template('usuarios.html', usuarios=Adm.ler_registros('usuarios', {}))