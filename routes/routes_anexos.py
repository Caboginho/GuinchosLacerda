from flask import Blueprint, request, redirect, url_for, render_template, session
from classes.usuario import Administrador

anexos_bp = Blueprint('anexos_bp', __name__)

@anexos_bp.route('/upload_anexos', methods=['POST'])
def upload_anexos():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    dados_anexo = {
        'transacao_id': request.form['transacao_id'],
        'caminho': request.files['anexos'].filename,
        'tipo': request.form['tipo']
    }
    print(f"Recebendo dados do anexo: {dados_anexo}")
    # Salva os dados no banco de dados local
    Adm.criar_registro('anexos', dados_anexo)
    return redirect(url_for('anexos_bp.anexos_pg'))

@anexos_bp.route('/atualizar_anexo', methods=['POST'])
def atualizar_anexo():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    anexo_id = request.form['anexo_id']
    dados_anexo = {
        'transacao_id': request.form['transacao_id'],
        'caminho': request.files['anexos'].filename,
        'tipo': request.form['tipo']
    }
    print(f"Atualizando dados do anexo: {dados_anexo}")
    # Atualiza os dados no banco de dados local
    Adm.atualizar_registro('anexos', anexo_id, dados_anexo)    
    return redirect(url_for('anexos_bp.anexos_pg'))

@anexos_bp.route('/deletar_anexo', methods=['POST'])
def deletar_anexo():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    anexo_id = request.form['anexo_id']
    print(f"Deletando anexo com ID: {anexo_id}")
    # Deleta o anexo do banco de dados local
    Adm.deletar_registro('anexos', anexo_id)
    return redirect(url_for('anexos_bp.anexos_pg'))

@anexos_bp.route('/anexos')
def anexos():
    if 'usuario_id' in session and session['tipo'] in ['Administrador', 'Secretaria']:
        return redirect(url_for('anexos_bp.anexos_pg'))
    return render_template('login.html')

@anexos_bp.route('/anexos_pg')
def anexos_pg():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    anexos = Adm.ler_registros('anexos', {})
    transacoes = Adm.ler_registros('transacoes',{})
    return render_template('anexos.html', anexos=anexos, transacoes=transacoes)
