from flask import Blueprint, request, jsonify, render_template, session
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.administrador import Administrador

guinchos_bp = Blueprint('guinchos_bp', __name__)

def get_admin():
    """Retorna instância do admin com conexões"""
    local_db = BancoDados()
    cloud_db = GoogleDriveSheets(r"classes/lacerdaguinchos-8e2aeaf562ce.json")
    return Administrador(
        id=session['usuario_id'],
        nome=session['nome'],
        email=session['email'],
        senha=None,
        celular=session['celular'],
        local_db=local_db,
        cloud_db=cloud_db
    )

@guinchos_bp.route('/admin/guinchos', methods=['GET'])
def listar_guinchos():
    try:
        admin = get_admin()
        
        # Define contexto (admin vê tudo, secretaria vê só seus guinchos)
        if session.get('tipo') == 'Secretaria':
            # Busca guinchos da secretaria específica
            email = session.get('email')
            guinchos = admin.ler_guinchos_secretaria(email)
        else:
            # Admin vê todos os guinchos
            guinchos = admin.ler_registros('guinchos')

        secretarias = admin.ler_registros('usuarios', {'tipo': 'Secretaria'})
        motoristas = admin.ler_registros('usuarios', {'tipo': 'Motorista'})
        
        # Prepara dados para template
        guinchos_dict = []
        if not guinchos.empty:
            guinchos_dict = guinchos.to_dict('records')
            for guincho in guinchos_dict:
                # Adiciona nomes de secretária e motorista
                secretaria = secretarias[secretarias['id'] == guincho['secretaria_id']].iloc[0] if guincho['secretaria_id'] else None
                motorista = motoristas[motoristas['id'] == guincho['motorista_id']].iloc[0] if guincho['motorista_id'] else None
                
                guincho['secretaria_nome'] = secretaria['nome'] if secretaria is not None else 'Não atribuído'
                guincho['motorista_nome'] = motorista['nome'] if motorista is not None else 'Não atribuído'

        return render_template('guinchos.html',
                             guinchos=guinchos_dict,
                             secretarias=secretarias.to_dict('records') if not secretarias.empty else [],
                             motoristas=motoristas.to_dict('records') if not motoristas.empty else [])

    except Exception as e:
        print(f"Erro ao listar guinchos: {e}")
        return render_template('guinchos.html', erro="Erro ao carregar dados")

@guinchos_bp.route('/admin/guinchos/cadastrar', methods=['POST'])
def cadastrar_guincho():
    try:
        if not request.headers.get('X-Requested-With'):
            return jsonify({'error': 'Requisição inválida'}), 400

        admin = get_admin()
        dados = {
            'modelo': request.form.get('modelo', '').strip(),
            'placa': request.form.get('placa', '').strip(),
            'secretaria_id': request.form.get('secretaria_id'),
            'motorista_id': request.form.get('motorista_id'),
            'status': request.form.get('status')
        }
        
        # Validações
        if not dados['modelo'] or not dados['placa']:
            return jsonify({'error': 'Modelo e placa são obrigatórios'}), 400
            
        # Remove IDs vazios
        if not dados['secretaria_id']: 
            dados.pop('secretaria_id')
        if not dados['motorista_id']:
            dados.pop('motorista_id')

        guincho_id = admin.cadastrar_guincho(dados)
        if guincho_id:
            return jsonify({
                'success': True,
                'message': 'Guincho cadastrado com sucesso',
                'id': guincho_id
            })

        return jsonify({'error': 'Erro ao cadastrar guincho'}), 400

    except Exception as e:
        print(f"Erro ao cadastrar guincho: {e}")
        return jsonify({'error': str(e)}), 400

@guinchos_bp.route('/admin/guinchos/atualizar', methods=['POST'])
def atualizar_guincho():
    try:
        guincho_id = request.form.get('guincho_id')
        if not guincho_id:
            return jsonify({'error': 'ID do guincho não fornecido'}), 400

        dados = {
            'modelo': request.form['modelo'].strip(),
            'placa': request.form['placa'].strip(),
            'secretaria_id': request.form['secretaria_id'],
            'motorista_id': request.form['motorista_id'],
            'status': request.form['status']
        }

        admin = get_admin()
        admin.atualizar_guincho(int(guincho_id), dados)
        admin.sincronizar_guincho(int(guincho_id))
        
        return jsonify({'message': 'Guincho atualizado com sucesso'})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@guinchos_bp.route('/admin/guinchos/deletar/<int:id_guincho>', methods=['POST'])
def deletar_guincho(id_guincho):
    try:
        admin = get_admin()
        admin.deletar_guincho(id_guincho)
        return jsonify({'message': 'Guincho removido com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
