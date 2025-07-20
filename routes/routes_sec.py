from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from classes.secretaria import Secretaria
from classes.googledrivesheets import GoogleDriveSheets
from classes.bancodados import BancoDados

sec_bp = Blueprint('sec_bp', __name__)

def get_secretaria():
    """Retorna instância da secretaria atual"""
    banco = BancoDados()
    google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
    return Secretaria(
        id=session['usuario_id'],
        nome=session['nome'],
        email=session['email'],
        senha=None,
        cnh=session['cnh'],
        celular=session['celular'],
        justificativa=session['justificativa'],
        local_db=banco,
        cloud_db=google
    )

@sec_bp.before_request
def verificar_secretaria():
    """Verifica se o usuário é secretária antes de cada requisição"""
    if 'tipo' not in session or session['tipo'] != 'Secretaria':
        return redirect(url_for('main_bp.login'))

@sec_bp.route('/index')
def index():
    """Renderiza dashboard da secretária"""
    if 'nome' not in session:
        return redirect(url_for('main_bp.login'))
    return render_template('sec.html', nome=session['nome'])

@sec_bp.route('/transacoes_pg')
def transacoes():
    """Renderiza página de transações da secretaria"""
    try:
        if 'tipo' not in session or session['tipo'] != 'Secretaria':
            return redirect(url_for('main_bp.login'))
            
        secretaria = get_secretaria()
        
        # Tenta buscar dados da nuvem primeiro
        if secretaria.cloud_db.check_internet():
            try:
                planilha = secretaria.cloud_db.get_planilha_secretaria(secretaria.email, 'transacoes')
                transacoes = pd.DataFrame(planilha.get_all_records())
                
                # Filtra apenas transações desta secretaria
                if not transacoes.empty:
                    transacoes = transacoes[transacoes['secretaria_id'] == secretaria.id]
            except Exception as e:
                print(f"[DEBUG] Erro ao ler da nuvem: {e}")
                # Se falhar, usa dados locais
                transacoes = secretaria.local_db.ler('transacoes', {'secretaria_id': secretaria.id})
        else:
            # Sem internet, usa banco local
            transacoes = secretaria.local_db.ler('transacoes', {'secretaria_id': secretaria.id})

        # Converte para lista de dicionários para o template
        if transacoes is not None and not transacoes.empty:
            transacoes_list = transacoes.to_dict('records')
            return render_template('transacoes.html', transacoes=transacoes_list)
            
        return render_template('transacoes.html', transacoes=[])
        
    except Exception as e:
        print(f"[DEBUG] Erro ao carregar transações: {e}")
        return render_template('transacoes.html', transacoes=[])

@sec_bp.route('/servicos_guincho_pg')
def servicos_guincho():
    """Redireciona para serviços da secretaria"""
    if 'tipo' not in session or session['tipo'] != 'Secretaria':
        return redirect(url_for('main_bp.login'))
    # Renderiza diretamente ao invés de redirecionar    
    return render_template('servicos_guincho.html')

@sec_bp.route('/cadastrar_transacao', methods=['POST'])
def cadastrar_transacao():
    """Rota para secretaria cadastrar transação"""
    try:
        secretaria = get_secretaria()
        
        # Garante que a tabela existe com estrutura correta
        secretaria.local_db.criar_tabela_transacoes()
        
        dados_transacao = {
            'data': request.form['data'],
            'tipo': request.form['categoria'].lower(),  # Garante lowercase
            'valor': float(request.form['valor']),
            'descricao': request.form['descricao'],
            'metodo_pagamento': request.form['metodo_pagamento'],
            'status': request.form['status'],
            'secretaria_id': session['usuario_id']
        }
        
        # Cadastra a transação e obtém o ID
        transacao_id = secretaria.cadastrar_transacao(dados_transacao)
        
        # Se for guinchamento, cria serviço vinculado
        if dados_transacao['tipo'] == 'guinchamento':
            servico_dados = {
                'data_solicitacao': dados_transacao['data'],
                'status': 'Em espera',
                'secretaria_id': session['usuario_id'],
                'transacao_id': transacao_id,
                'tipo_solicitacao': 'Pendente',
                'protocolo': '',
                'origem': '',
                'destino': '',
                'guincho_id': None
            }
            
            servico_id = secretaria.cadastrar_servico_guincho(servico_dados)
            secretaria.local_db.atualizar('transacoes', transacao_id, {'servico_id': servico_id})
        
        return jsonify({
            'success': True,
            'message': 'Transação cadastrada com sucesso',
            'id': transacao_id
        })
        
    except Exception as e:
        print(f"[DEBUG] Erro ao cadastrar transação: {e}")
        return jsonify({'error': str(e)}), 400


