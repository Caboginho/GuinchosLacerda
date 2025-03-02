from flask import Blueprint, request, redirect, url_for, render_template, session
from classes.usuario import Administrador

transacoes_bp = Blueprint('transacoes_bp', __name__)

@transacoes_bp.route('/cadastrar_transacao', methods=['POST'])
def cadastrar_transacao():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    dados_transacao = {
        'data': request.form['data'],
        'valor': request.form['valor'],
        'categoria': request.form['categoria'],
        'descricao': request.form['descricao'],
        'metodo_pagamento': request.form['metodo_pagamento'],
        'status': request.form['status']
    }
    Adm.criar_registro('transacoes', dados_transacao)
    return redirect(url_for('transacoes_bp.transacoes_pg'))

@transacoes_bp.route('/atualizar_transacao', methods=['POST'])
def atualizar_transacao():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    transacao_id = request.form['transacao_id']
    dados_transacao = {
        'data': request.form['data'],
        'valor': request.form['valor'],
        'categoria': request.form['categoria'],
        'descricao': request.form['descricao'],
        'metodo_pagamento': request.form['metodo_pagamento'],
        'status': request.form['status']
    }
    Adm.atualizar_registro('transacoes', transacao_id, dados_transacao)
    return redirect(url_for('transacoes_bp.transacoes_pg'))

@transacoes_bp.route('/deletar_transacao', methods=['POST'])
def deletar_transacao():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    transacao_id = request.form['transacao_id']
    Adm.deletar_registro('transacoes', transacao_id)
    return redirect(url_for('transacoes_bp.transacoes_pg'))

@transacoes_bp.route('/transacoes_pg')
def transacoes_pg():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    transacoes = Adm.ler_registros('transacoes',{})
    secretarias = Adm.ler_registros('usuarios', {'tipo': 'Secretaria'})
    return render_template('transacoes.html', transacoes=transacoes, secretarias=secretarias)
