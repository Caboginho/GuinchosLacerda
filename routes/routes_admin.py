from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.administrador import Administrador
from classes.usuario import Usuario

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.before_request
def verificar_admin():
    """Verifica se o usuário é admin antes de cada requisição"""
    if 'tipo' not in session or session['tipo'] != 'Administrador':
        return redirect(url_for('main_bp.login'))

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

@admin_bp.route('/index')
def index():
    """Renderiza dashboard do administrador"""
    if 'nome' not in session:
        return redirect(url_for('main_bp.login'))
    return render_template('admin.html', nome=session['nome'])

@admin_bp.route('/usuarios', methods=['GET', 'POST'])
def usuarios():
    """Redireciona para gestão de usuários"""
    try:
        admin = get_admin()
            
        # GET: Carrega lista de usuários
        usuarios_df = admin.ler_registros('usuarios')
        usuarios_list = usuarios_df.to_dict('records') if not usuarios_df.empty else []
        return render_template('usuarios.html', usuarios=usuarios_list)
        
    except Exception as e:
        print(f"Erro ao processar usuários: {e}")
        if request.method == 'POST':
            return jsonify({'error': str(e)}), 400
        return render_template('usuarios.html', usuarios=[], erro="Erro ao carregar usuários")

@admin_bp.route('/guinchos')
def guinchos():
    """Redireciona para gestão de guinchos com dados necessários"""
    try:
        if 'tipo' not in session or session['tipo'] != 'Administrador':
            return redirect(url_for('main_bp.login'))

        admin = get_admin()
        
        # Busca dados necessários
        guinchos = admin.ler_registros('guinchos')
        secretarias = admin.ler_registros('usuarios', {'tipo': 'Secretaria'})
        motoristas = admin.ler_registros('usuarios', {'tipo': 'Motorista'})
        
        # Prepara dicionários
        guinchos_dict = []
        if not guinchos.empty:
            guinchos_dict = guinchos.to_dict('records')
            for guincho in guinchos_dict:
                # Adiciona nome da secretária
                if guincho['secretaria_id']:
                    secretaria = secretarias[secretarias['id'] == guincho['secretaria_id']].iloc[0]
                    guincho['secretaria_nome'] = secretaria['nome']
                else:
                    guincho['secretaria_nome'] = 'Não atribuído'
                
                # Adiciona nome do motorista
                if guincho['motorista_id']:
                    motorista = motoristas[motoristas['id'] == guincho['motorista_id']].iloc[0]
                    guincho['motorista_nome'] = motorista['nome']
                else:
                    guincho['motorista_nome'] = 'Não atribuído'

        return render_template('guinchos.html',
                            guinchos=guinchos_dict,
                            secretarias=secretarias.to_dict('records') if not secretarias.empty else [],
                            motoristas=motoristas.to_dict('records') if not motoristas.empty else [],
                            titulo="Gestão de Guinchos")
                            
    except Exception as e:
        print(f"Erro ao carregar página de guinchos: {e}")
        return render_template('guinchos.html', 
                             erro="Erro ao carregar dados",
                             guinchos=[],
                             secretarias=[],
                             motoristas=[])

@admin_bp.route('/transacoes')
def transacoes():
    """Redireciona para gestão de transações"""
    if 'tipo' not in session or session['tipo'] != 'Administrador':
        return redirect(url_for('main_bp.login'))
    return render_template('transacoes.html')

@admin_bp.route('/servicos_guincho')
def servicos_guincho():
    """Redireciona para gestão de serviços"""
    try:
        if 'tipo' not in session or session['tipo'] != 'Administrador':
            return redirect(url_for('main_bp.login'))
            
        # Instancia admin com dados da sessão
        admin = Administrador(
            id=session['usuario_id'],
            nome=session['nome'],
            email=session['email'],
            senha=None,
            cnh=session.get('cnh'),
            celular=session['celular'],
            justificativa=session['justificativa']
        )
        
        # Busca serviços do banco
        servicos = admin.ler_registros('servicos_guincho')
        servicos_list = servicos.to_dict('records') if not servicos.empty else []
        
        return render_template('servicos_guincho.html', servicos=servicos_list)
        
    except Exception as e:
        print(f"Erro ao carregar serviços: {e}")
        return render_template('servicos_guincho.html', servicos=[], erro="Erro ao carregar serviços")

@admin_bp.route('/financeiro')
def financeiro():
    """Redireciona para gestão financeira"""
    try:
        if 'tipo' not in session or session['tipo'] != 'Administrador':
            return redirect(url_for('main_bp.login'))
            
        admin = Administrador(
            id=session['usuario_id'],
            nome=session['nome'],
            email=session['email'],
            senha=None,
            cnh=session.get('cnh'),
            celular=session['celular'],
            justificativa=session['justificativa']
        )
        
        # Busca dados financeiros
        transacoes = admin.ler_registros('transacoes')
        servicos = admin.ler_registros('servicos_guincho')
        
        # Prepara dados para os gráficos
        dados_financeiros = {
            'transacoes': transacoes.to_dict('records') if not transacoes.empty else [],
            'servicos': servicos.to_dict('records') if not servicos.empty else [],
            'total_receitas': float(transacoes['valor'].sum()) if not transacoes.empty else 0,
            'total_servicos': len(servicos) if not servicos.empty else 0
        }
        
        return render_template('financeiro.html', dados=dados_financeiros)
        
    except Exception as e:
        print(f"Erro ao carregar dados financeiros: {e}")
        dados_vazios = {
            'transacoes': [],
            'servicos': [],
            'total_receitas': 0,
            'total_servicos': 0
        }
        return render_template('financeiro.html', dados=dados_vazios, erro="Erro ao carregar dados")

@admin_bp.route('/admin/carregar_dados_secretaria/<int:secretaria_id>', methods=['POST'])
def carregar_dados_secretaria(secretaria_id):
    """Carrega dados de uma secretaria específica"""
    try:
        admin = get_admin()
        secretaria = admin.ler_registros('usuarios', {'id': secretaria_id}).iloc[0]
        
        if admin.cloud_db.check_internet():
            # Busca dados da pasta da secretaria
            dados = admin.cloud_db.ler_dados_secretaria(secretaria['email'])
            # Sincroniza com banco local
            admin.local_db.sincronizar_dados_secretaria(dados, secretaria_id)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
