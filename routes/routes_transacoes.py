from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.administrador import Administrador
import os
import zipfile
from datetime import datetime
import pandas as pd

from classes.secretaria import Secretaria

transacoes_bp = Blueprint('transacoes_bp', __name__)

def get_admin():
    banco = BancoDados()
    google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
    return Administrador(
        id=session['usuario_id'],
        nome=session['nome'],
        email=session['email'],
        senha=None,
        tiopo=session['tipo'],
        cnh=session['cnh'],
        celular=session['celular'],
        justificativa=session['justificativa'],
        local_db=banco,
        cloud_db=google
    )

def get_secretaria():
    banco = BancoDados()
    google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
    return Secretaria(
        id=session['usuario_id'],
        nome=session['nome'],
        email=session['email'],
        senha=None,
        tipo=session['tipo'],
        cnh=session['cnh'],
        celular=session['celular'],
        justificativa=session['justificativa'],
        local_db=banco,
        cloud_db=google
    )

@transacoes_bp.route('/admin/transacoes/cadastrar', methods=['POST'])
def cadastrar():
    try:
        admin = get_admin()
        dados_transacao = {
            'data': request.form['data'],
            'tipo': request.form['categoria'],
            'valor': float(request.form['valor']),
            'descricao': request.form['descricao'],
            'metodo_pagamento': request.form['metodo_pagamento'],
            'status': request.form['status'],
            'secretaria_id': request.form.get('secretaria_id')
        }

        # Salva transação e obtém ID
        if admin.cloud_db.check_internet():
            try:
                # Busca email da secretaria
                secretaria = admin.ler_registros('usuarios', 
                    {'id': dados_transacao['secretaria_id']}).iloc[0]
                
                # Salva transação na pasta da secretaria
                admin.cloud_db.inserir_em_planilha_secretaria(
                    secretaria['email'], 
                    'transacoes',
                    dados_transacao
                )
            except Exception as e:
                print(f"Erro ao salvar na nuvem: {e}")
                admin.local_db.marcar_para_sincronizacao('transacoes', 
                    dados_transacao['id'], 'insert')

        # Salva localmente
        transacao_id = admin.local_db.inserir('transacoes', dados_transacao)

        # Se for guinchamento, cria serviço vinculado
        if dados_transacao['tipo'] == 'guinchamento':
            servico_dados = {
                'data_solicitacao': dados_transacao['data'],
                'status': 'Em espera',
                'secretaria_id': dados_transacao['secretaria_id'],
                'transacao_id': transacao_id
            }
            
            # Salva serviço na nuvem
            if admin.cloud_db.check_internet():
                try:
                    admin.cloud_db.inserir_em_planilha_secretaria(
                        secretaria['email'],
                        'servicos_guincho',
                        servico_dados
                    )
                except Exception as e:
                    print(f"Erro ao salvar serviço na nuvem: {e}")
                    admin.local_db.marcar_para_sincronizacao('servicos_guincho',
                        servico_dados['id'], 'insert')

            # Salva serviço localmente
            servico_id = admin.local_db.inserir('servicos_guincho', servico_dados)
            
            # Atualiza transação com ID do serviço
            admin.local_db.atualizar('transacoes', transacao_id, 
                {'servico_id': servico_id})

        return jsonify({
            'success': True,
            'message': 'Transação cadastrada com sucesso',
            'id': transacao_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@transacoes_bp.route('/atualizar_transacao', methods=['POST'])
def atualizar_transacao():
    """Rota para atualizar uma transação existente"""
    try:
        if session.get('tipo') == 'Secretaria':
            secretaria = get_secretaria()
            user = secretaria
        else:
            user = get_admin()

        transacao_id = int(request.form['transacao_id'])
        dados = {
            'data': request.form['data'],
            'tipo': request.form['categoria'].lower(),
            'valor': float(request.form['valor']),
            'descricao': request.form['descricao'],
            'metodo_pagamento': request.form['metodo_pagamento'],
            'status': request.form['status']
        }

        # Atualiza no banco local
        user.local_db.atualizar('transacoes', transacao_id, dados)

        # Se tiver internet, atualiza na nuvem
        if user.cloud_db.check_internet():
            try:
                secretaria_id = user.local_db.ler('transacoes', {'id': transacao_id}).iloc[0]['secretaria_id']
                secretaria = user.local_db.ler('usuarios', {'id': secretaria_id}).iloc[0]
                
                planilha = user.cloud_db.get_planilha_secretaria(secretaria['email'], 'transacoes')
                # Atualiza na planilha da secretaria
                # TODO: Implementar atualização na planilha
            except Exception as e:
                print(f"[DEBUG] Erro ao atualizar na nuvem: {e}")
                user.local_db.marcar_para_sincronizacao('transacoes', transacao_id, 'update')

        return jsonify({
            'success': True,
            'message': 'Transação atualizada com sucesso'
        })
    except Exception as e:
        print(f"[DEBUG] Erro ao atualizar transação: {e}")
        return jsonify({'error': str(e)}), 400

@transacoes_bp.route('/admin/transacoes/deletar/<int:id_transacao>', methods=['POST'])
def deletar(id_transacao):
    try:
        admin = get_admin()
        admin.deletar_transacao(id_transacao)
        return jsonify({'success': True, 'message': 'Transação removida com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@transacoes_bp.route('/transacoes_pg')
def transacoes_pg():
    user = get_admin()
    
    # Se o usuário for Secretaria
    if session.get('tipo') == 'Secretaria':
        email = session.get('email')
        try:
            # Busca dados da pasta específica da secretaria
            planilha = user.cloud_db.get_planilha_secretaria(email, 'transacoes')
            transacoes = pd.DataFrame(planilha.get_all_records())
            transacoes = transacoes[transacoes['secretaria_id'] == session['usuario_id']]
            secretarias = None
        except Exception as e:
            print(f"Erro ao ler planilha da secretaria: {e}")
            transacoes = user.ler_registros('transacoes', {'secretaria_id': session['usuario_id']})
            secretarias = None
    else:
        # Para admin, primeiro carrega lista de secretarias
        secretarias = user.ler_registros('usuarios', {'tipo': 'Secretaria'})
        
        if secretarias is not None and not secretarias.empty:
            # Se houver secretaria selecionada no formulário
            secretaria_id = request.args.get('secretaria_id')
            if secretaria_id:
                try:
                    # Busca email da secretaria selecionada
                    secretaria = secretarias[secretarias['id'] == int(secretaria_id)].iloc[0]
                    
                    # Carrega dados da pasta da secretaria no Drive
                    if user.cloud_db.check_internet():
                        planilha = user.cloud_db.get_planilha_secretaria(secretaria['email'], 'transacoes')
                        transacoes = pd.DataFrame(planilha.get_all_records())
                        
                        # Atualiza banco local com dados da nuvem
                        user.local_db.sincronizar_dados_secretaria(
                            {'transacoes': transacoes}, int(secretaria_id))
                    else:
                        # Sem internet, usa dados locais
                        transacoes = user.ler_registros('transacoes', 
                            {'secretaria_id': secretaria_id})
                except Exception as e:
                    print(f"Erro ao carregar dados da secretaria: {e}")
                    transacoes = pd.DataFrame()
            else:
                # Nenhuma secretaria selecionada ainda
                transacoes = pd.DataFrame()
        else:
            # Não há secretarias cadastradas
            transacoes = pd.DataFrame()
            secretarias = pd.DataFrame()

    if transacoes is not None and not transacoes.empty:
        # Verifica se todas as colunas necessárias existem
        colunas_necessarias = ['id', 'data', 'valor', 'categoria', 'descricao', 
                             'metodo_pagamento', 'status']
        
        # Adiciona colunas faltantes com valores vazios
        for coluna in colunas_necessarias:
            if coluna not in transacoes.columns:
                transacoes[coluna] = None

        # Converte para dicionário para manipulação
        transacoes_dict = transacoes.to_dict(orient='records')
        transacoes_unicas = {}
        
        for transacao in transacoes_dict:
            if transacao['id'] is not None:  # Verifica se o ID é válido
                try:
                    data_atual = datetime.strptime(str(transacao['data']), "%Y-%m-%d")
                    transacao_id = str(transacao['id'])
                    
                    if transacao_id not in transacoes_unicas:
                        transacoes_unicas[transacao_id] = transacao
                    else:
                        data_anterior = datetime.strptime(
                            str(transacoes_unicas[transacao_id]['data']), 
                            "%Y-%m-%d"
                        )
                        if data_atual > data_anterior:
                            transacoes_unicas[transacao_id] = transacao
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar transação {transacao.get('id')}: {e}")
                    continue
        
        # Converte de volta para lista
        transacoes_dict = list(transacoes_unicas.values())
        
        return render_template('transacoes.html', 
                             transacoes=transacoes_dict,
                             secretarias=secretarias.to_dict(orient='records') if secretarias is not None else [])
    
    return render_template('transacoes.html', 
                         transacoes=[],
                         secretarias=[])

@transacoes_bp.route('/buscar_anexos_transacao/<int:transacao_id>')
def buscar_anexos_transacao(transacao_id):
    admin = get_admin()
    anexos = admin.local_db.ler_anexos_transacao(transacao_id)
    if anexos is not None and not anexos.empty:
        anexos_list = anexos.to_dict(orient='records')
        return jsonify({'anexos': anexos_list})
    return jsonify({'anexos': []})

@transacoes_bp.route('/admin/transacoes/por_secretaria/<int:secretaria_id>')
def transacoes_por_secretaria(secretaria_id):
    try:
        admin = get_admin()
        
        # Tenta buscar da pasta específica da secretaria no Drive
        if admin.cloud_db.check_internet():
            try:
                secretaria = admin.ler_registros('usuarios', {'id': secretaria_id}).iloc[0]
                planilha = admin.cloud_db.get_planilha_secretaria(secretaria['email'], 'transacoes')
                transacoes = pd.DataFrame(planilha.get_all_records())
            except Exception as e:
                print(f"Erro ao ler do Drive: {e}")
                # Se falhar, busca do banco local
                transacoes = admin.ler_registros('transacoes', {'secretaria_id': secretaria_id})
        else:
            # Sem internet, usa banco local
            transacoes = admin.ler_registros('transacoes', {'secretaria_id': secretaria_id})
            
        if not transacoes.empty:
            return jsonify({'transacoes': transacoes.to_dict('records')})
        return jsonify({'transacoes': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
