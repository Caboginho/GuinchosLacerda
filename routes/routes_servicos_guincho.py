from flask import Blueprint, request, redirect, url_for, render_template, session
from classes.usuario import Administrador

servicos_guincho_bp = Blueprint('servicos_guincho_bp', __name__)

@servicos_guincho_bp.route('/cadastrar_servico_guincho', methods=['POST'])
def cadastrar_servico_guincho():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    dados_servico = {
        'data_solicitacao': request.form['data_solicitacao'],
        'guincho_id': request.form['guincho_id'],
        'tipo_solicitacao': request.form['tipo_solicitacao'],
        'protocolo': request.form.get('protocolo') if request.form.get('protocolo') else None,
        'origem': request.form['origem'],
        'destino': request.form['destino'],
        'status': request.form['status']
    }
    print(f"Recebendo dados do serviço de guincho: {dados_servico}")
    # Salva os dados no banco de dados local
    Adm.criar_registro('servicos_guincho', dados_servico) 
    return redirect(url_for('servicos_guincho_bp.servicos_guincho_pg'))

@servicos_guincho_bp.route('/atualizar_servico_guincho', methods=['POST'])
def atualizar_servico_guincho():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    servico_id = request.form['servico_id']
    dados_servico = {
        'data_solicitacao': request.form['data_solicitacao'],
        'guincho_id': request.form['guincho_id'],
        'tipo_solicitacao': request.form['tipo_solicitacao'],
        'protocolo': request.form.get('protocolo') if request.form.get('protocolo') else None,
        'origem': request.form['origem'],
        'destino': request.form['destino'],
        'status': request.form['status']
    }
    print(f"Atualizando dados do serviço de guincho: {dados_servico}")
    # Atualiza os dados no banco de dados local
    Adm.atualizar_registro('servicos_guincho', servico_id, dados_servico)
    return redirect(url_for('servicos_guincho_bp.servicos_guincho_pg'))

@servicos_guincho_bp.route('/deletar_servico_guincho', methods=['POST'])
def deletar_servico_guincho():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    servico_id = request.form['servico_id']
    print(f"Deletando serviço de guincho com ID: {servico_id}")
    # Deleta o serviço de guincho do banco de dados local
    Adm.deletar_registro('servicos_guincho', servico_id)    
    return redirect(url_for('servicos_guincho_bp.servicos_guincho_pg'))

@servicos_guincho_bp.route('/servicos_guincho_pg')
def servicos_guincho_pg():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    servicos = Adm.ler_registros('servicos_guincho', {})
    guinchos = Adm.ler_registros('guinchos', {})
    return render_template('servicos_guincho.html', servicos=servicos, guinchos=guinchos)

