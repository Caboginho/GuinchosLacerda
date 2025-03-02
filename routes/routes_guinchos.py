from flask import Blueprint, request, redirect, url_for, render_template, jsonify, session
from classes.usuario import Administrador

guinchos_bp = Blueprint('guinchos_bp', __name__)

@guinchos_bp.route('/cadastrar_guincho', methods=['POST'])
def cadastrar_guincho():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    dados_guincho = {
        'placa': request.form['placa'],
        'modelo': request.form['modelo'],
        'motorista_id': request.form.get('motorista_id'),
        'secretaria_id': request.form['secretaria_id'],
        'disponivel': request.form['disponivel']
    }
    print(f"Recebendo dados do guincho: {dados_guincho}")
    # Salva os dados no banco de dados local e na nuvem
    Adm.criar_registro('guinchos', dados_guincho)
    
    return redirect(url_for('guinchos_bp.guinchos_pg'))

@guinchos_bp.route('/atualizar_guincho', methods=['POST'])
def atualizar_guincho():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    guincho_id = request.form['guincho_id']
    dados_guincho = {
        'placa': request.form['placa'],
        'modelo': request.form['modelo'],
        'motorista_id': request.form.get('motorista_id') if request.form.get('motorista_id') else None,
        'secretaria_id': request.form['secretaria_id'],
        'disponivel': request.form['disponivel']
    }
    print(f"Atualizando dados do guincho: {dados_guincho}")
    # Atualiza os dados no banco de dados local
    Adm.atualizar_registro('guinchos', guincho_id, dados_guincho)
    return redirect(url_for('guinchos_bp.guinchos_pg'))

@guinchos_bp.route('/deletar_guincho', methods=['POST'])
def deletar_guincho():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    guincho_id = request.form['guincho_id']
    print(f"Deletando guincho com ID: {guincho_id}")
    # Obter dados do guincho antes de deletar
    guincho = Adm.ler_registros('guinchos', {'id': guincho_id})
    if not guincho:
        print(f"Guincho com ID {guincho_id} não encontrado.")
        return redirect(url_for('guinchos_bp.guinchos_pg'))
    # Deleta o guincho do banco de dados local e da nuvem
    Adm.deletar_registro('guinchos', guincho_id)
    return redirect(url_for('guinchos_bp.guinchos_pg'))

@guinchos_bp.route('/guinchos_pg')
def guinchos_pg():
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    guinchos = Adm.ler_registros('guinchos',{})
    motoristas = Adm.ler_registros('usuarios', {'tipo': 'Motorista'})
    secretarias = Adm.ler_registros('usuarios', {'tipo': 'Secretaria'})
    return render_template('guinchos.html', guinchos=guinchos, motoristas=motoristas, secretarias=secretarias)

@guinchos_bp.route('/guinchos_secretaria/<int:secretaria_id>')
def guinchos_secretaria(secretaria_id):
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    guinchos = Adm.ler_registros('guinchos', {'secretaria_id': secretaria_id})
    return jsonify(guinchos=[{'id': g[0], 'placa': g[1]} for g in guinchos])

@guinchos_bp.route('/motorista_guincho/<int:guincho_id>')
def motorista_guincho(guincho_id):
    Adm = Administrador(
    session['usuario_id'],
    session['nome'],
    session['email'],
    session['senha'],
    session['cnh'],
    session['celular'],
    session['justificativa']
    )
    guincho = Adm.ler_registros('guinchos', {'id': guincho_id})
    if guincho:
        motorista_id = guincho[0][3]
        motorista = Adm.ler_registros('usuarios', {'id': motorista_id})
        if motorista:
            return jsonify(motorista=motorista[0][1])
    return jsonify(motorista="")
