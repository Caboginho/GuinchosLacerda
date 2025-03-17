from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
import pandas as pd
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.administrador import Administrador
from datetime import datetime

servicos_guincho_bp = Blueprint('servicos_guincho_bp', __name__)

def get_admin():
    """
    Instancia e retorna um objeto Administrador com acesso ao banco local e à nuvem.
    """
    local_db = BancoDados()
    cloud_db = GoogleDriveSheets(r"classes/lacerdaguinchos-8e2aeaf562ce.json")
    return Administrador(
        id=session['usuario_id'],
        nome=session['nome'],
        email=session['email'],
        senha=None,
        cnh=session['cnh'],
        celular=session['celular'],
        justificativa=session['justificativa'],
        local_db=local_db,
        cloud_db=cloud_db
    )

@servicos_guincho_bp.route('/cadastrar_servico_guincho', methods=['POST'])
def cadastrar_servico_guincho():
    admin = get_admin()
    try:
        # Dados do serviço
        dados_servico = {
            'data_solicitacao': request.form['data_solicitacao'],
            'guincho_id': request.form['guincho_id'],
            'tipo_solicitacao': request.form['tipo_solicitacao'],
            'protocolo': request.form.get('protocolo'),
            'origem': request.form['origem'],
            'destino': request.form['destino'],
            'status': request.form['status']
        }
        
        # Se for secretaria, adiciona id
        if session.get('tipo') == 'Secretaria':
            dados_servico['secretaria_id'] = session['usuario_id']
        
        # Cadastra o serviço
        servico_id = admin.cadastrar_servico_guincho(dados_servico)
        
        # Cria transação vinculada
        dados_transacao = {
            'data': request.form['data_solicitacao'],
            'tipo': 'servico',
            'valor': float(request.form['valor']),
            'descricao': f"Serviço de guincho #{servico_id}",
            'metodo_pagamento': request.form['metodo_pagamento'],
            'status': 'Pendente',
            'servico_id': servico_id
        }
        
        if session.get('tipo') == 'Secretaria':
            dados_transacao['secretaria_id'] = session['usuario_id']
            
        admin.cadastrar_transacao(dados_transacao)
        
        return jsonify({'success': True, 'message': 'Serviço cadastrado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@servicos_guincho_bp.route('/atualizar_servico_guincho', methods=['POST'])
def atualizar_servico_guincho():
    admin = get_admin()
    try:
        servico_id = request.form['servico_id']
        novo_status = request.form['status']
        
        dados_servico = {
            'data_solicitacao': request.form['data_solicitacao'],
            'guincho_id': request.form['guincho_id'],
            'tipo_solicitacao': request.form['tipo_solicitacao'],
            'protocolo': request.form.get('protocolo'),
            'origem': request.form['origem'],
            'destino': request.form['destino'],
            'status': novo_status
        }
        
        # Adiciona data_fim se o status for Finalizado ou Cancelado
        if novo_status in ['Finalizado', 'Cancelado']:
            dados_servico['data_fim'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        admin.atualizar_servico_guincho(int(servico_id), dados_servico)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@servicos_guincho_bp.route('/deletar_servico_guincho', methods=['POST'])
def deletar_servico_guincho():
    admin = get_admin()
    servico_id = request.form['servico_id']
    print(f"Deletando serviço de guincho com ID: {servico_id}")
    admin.deletar_servico_guincho(int(servico_id))
    return redirect(url_for('servicos_guincho_bp.servicos_guincho_pg'))

@servicos_guincho_bp.route('/servicos_guincho_pg')
def servicos_guincho_pg():
    admin = get_admin()
    
    # Se for Secretaria, filtra por seus guinchos/serviços
    if session.get('tipo') == 'Secretaria':
        try:
            # Busca guinchos da secretaria
            guinchos = admin.ler_registros('guinchos', {'secretaria_id': session['usuario_id']})
            
            # Busca serviços da secretaria
            servicos = admin.ler_registros('servicos_guincho', {'secretaria_id': session['usuario_id']})
            secretarias = None  # Secretaria não precisa escolher secretaria
        except Exception as e:
            print(f"Erro ao carregar dados da secretaria: {e}")
            servicos = pd.DataFrame()
            guinchos = pd.DataFrame()
            secretarias = None
    else:
        # Para admin, carrega todos os dados
        servicos = admin.ler_registros('servicos_guincho')
        guinchos = admin.ler_registros('guinchos', {'disponivel': 1})
        secretarias = admin.ler_registros('usuarios', {'tipo': 'Secretaria'})

    if servicos is not None and not servicos.empty:
        # Verifica e adiciona colunas necessárias
        colunas_necessarias = ['id', 'data_solicitacao', 'guincho_id', 'tipo_solicitacao',
                              'protocolo', 'origem', 'destino', 'status']
        
        for coluna in colunas_necessarias:
            if coluna not in servicos.columns:
                servicos[coluna] = None

        # Converte para dicionário e trata dados
        servicos_dict = servicos.to_dict(orient='records')
        servicos_unicos = {}
        
        for servico in servicos_dict:
            if servico['id'] is not None:  # Verifica se o ID é válido
                try:
                    data_str = str(servico['data_solicitacao'])
                    data_atual = None
                    
                    # Tenta diferentes formatos de data
                    for fmt in ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                        try:
                            data_atual = datetime.strptime(data_str, fmt)
                            break
                        except ValueError:
                            continue
                    
                    if data_atual:
                        servico_id = str(servico['id'])
                        if servico_id not in servicos_unicos:
                            servicos_unicos[servico_id] = servico
                        else:
                            data_anterior = datetime.strptime(
                                servicos_unicos[servico_id]['data_solicitacao'].split('T')[0], 
                                "%Y-%m-%d"
                            )
                            if data_atual > data_anterior:
                                servicos_unicos[servico_id] = servico
                except Exception as e:
                    print(f"Erro ao processar serviço {servico.get('id')}: {e}")
                    continue
        
        servicos_dict = list(servicos_unicos.values())
        
        # Adiciona informações do guincho
        if guinchos is not None and not guinchos.empty:
            guinchos_dict = guinchos.to_dict(orient='records')
            for servico in servicos_dict:
                servico['guincho_nome'] = 'Não definido'  # Valor padrão
                for guincho in guinchos_dict:
                    if str(servico['guincho_id']) == str(guincho['id']):
                        servico['guincho_nome'] = guincho['modelo']
                        break
        return render_template('servicos_guincho.html', 
                             servicos=servicos_dict, 
                             guinchos=guinchos_dict if guinchos is not None else [])
    
    return render_template('servicos_guincho.html', 
                         servicos=[], 
                         guinchos=[])

@servicos_guincho_bp.route('/buscar_anexos_servico/<int:servico_id>')
def buscar_anexos_servico(servico_id):
    admin = get_admin()
    anexos = admin.local_db.ler_anexos_servico(servico_id)
    if anexos is not None and not anexos.empty:
        anexos_list = anexos.to_dict(orient='records')
        return jsonify({'anexos': anexos_list})
    return jsonify({'anexos': []})

@servicos_guincho_bp.route('/guinchos_secretaria/<int:secretaria_id>')
def guinchos_secretaria(secretaria_id):
    """Retorna guinchos disponíveis de uma secretaria específica"""
    admin = get_admin()
    guinchos = admin.ler_registros('guinchos', {
        'secretaria_id': secretaria_id,
        'disponivel': 1
    })
    
    return jsonify({
        'guinchos': guinchos.to_dict('records') if not guinchos.empty else []
    })
