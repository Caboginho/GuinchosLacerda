from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.usuario import Usuario
from classes.administrador import Administrador
import pandas as pd

usuarios_bp = Blueprint('usuarios_bp', __name__)

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

@usuarios_bp.route('/admin/usuarios', methods=['GET'])
def usuarios():
    """Página principal de gestão de usuários"""
    try:
        admin = get_admin()
        # Força sincronização antes de ler
        admin.sincronizar_tudo()
        usuarios_df = admin.ler_registros('usuarios')
        usuarios_list = usuarios_df.to_dict('records') if not usuarios_df.empty else []
        return render_template('usuarios.html', usuarios=usuarios_list)
    except Exception as e:
        print(f"Erro ao carregar usuários: {e}")
        return render_template('usuarios.html', usuarios=[], erro="Erro ao carregar usuários")

@usuarios_bp.route('/admin/usuarios/cadastrar', methods=['POST'])
def cadastrar():
    """Cadastra novo usuário"""
    try:
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Requisição inválida'}), 400

        admin = get_admin()
        email = request.form['email'].strip()
        tipo = request.form['tipo'].strip()
        
        if admin.local_db.ler('usuarios', {'email': email}).empty:
            # Gera próximo ID e prepara dados
            ultimo_registro = admin.local_db.ler('usuarios')
            proximo_id = 1 if ultimo_registro.empty else int(ultimo_registro['id'].max()) + 1
            value = admin.cloud_db.check_internet() or False        
            dados = {
                'id': proximo_id,
                'nome': request.form['nome'].strip(),
                'email': email,
                'senha': Usuario().hash_senha(request.form['senha']) if request.form.get('senha') else '',
                'tipo': tipo,
                'cnh': request.form.get('cnh', '').strip() or None,
                'celular': request.form['celular'].strip(),
                'justificativa': request.form.get('justificativa', 'offline').strip()
            }
            
            try:
                # Se for secretaria e tiver internet, usa fluxo específico
                if tipo == 'Secretaria' and value:
                    admin.cadastrar_secretaria(dados)
                else:
                    # Fluxo normal para outros tipos de usuário
                    if value:
                        # Primeiro salva na nuvem
                        admin.cloud_db.inserir(dados=dados, tabela='usuarios')
                    
                    # Depois salva localmente
                    admin.local_db.inserir('usuarios', dados)
                    
                    # Se estiver offline, marca para sincronização
                    if not value:
                        admin.local_db.marcar_para_sincronizacao('usuarios', proximo_id, 'insert')

                return jsonify({
                    'success': True,
                    'message': f'{tipo} cadastrado(a) com sucesso',
                    'redirect': '/admin/usuarios'
                })

            except Exception as e:
                print(f"[DEBUG] Erro no cadastro: {e}")
                try:
                    if value:
                        admin.cloud_db.deletar(proximo_id-1)
                        if tipo == 'Secretaria':
                            admin.cloud_db.deletar_pasta_secretaria(email)
                except:
                    pass
                raise

        else:
            return jsonify({
                'error': 'Email já cadastrado',
                'redirect': '/admin/usuarios'
            }), 400

    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return jsonify({
            'error': str(e),
            'redirect': '/admin/usuarios'
        }), 400

@usuarios_bp.route('/admin/usuarios/atualizar', methods=['POST'])
def atualizar():
    """Atualiza usuário existente"""
    try:
        print("[DEBUG] Iniciando atualização de usuário")
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Requisição inválida'}), 400

        # Validação do ID do usuário
        usuario_id = request.form.get('usuario_id')
        print(f"[DEBUG] ID recebido: {usuario_id}")
        
        if not usuario_id:
            return jsonify({
                'error': 'ID do usuário não fornecido',
                'redirect': '/admin/usuarios'
            }), 400

        try:
            id_usuario = int(usuario_id)
            admin = get_admin()
            
            # Prepara dados para atualização
            dados = {
                'nome': request.form['nome'].strip(),
                'email': request.form['email'].strip(),
                'tipo': request.form['tipo'],
                'cnh': request.form.get('cnh', '').strip() or None,
                'celular': request.form['celular'].strip(),
                'justificativa': request.form.get('justificativa', 'offline').strip()
            }

            # Se forneceu nova senha, atualiza
            if senha := request.form.get('senha', '').strip():
                dados['senha'] = Usuario().hash_senha(senha)

            try:
                # Tenta atualizar
                admin.atualizar_usuario(id_usuario, dados)
                return jsonify({
                    'success': True,
                    'message': 'Usuário atualizado com sucesso',
                    'redirect': '/admin/usuarios'
                })
            except Exception as e:
                print(f"[DEBUG] Erro ao atualizar usuário: {e}")
                return jsonify({
                    'error': 'Erro ao atualizar usuário. Tente novamente.',
                    'redirect': '/admin/usuarios'
                }), 500

        except ValueError:
            return jsonify({
                'error': 'ID do usuário inválido',
                'redirect': '/admin/usuarios'
            }), 400

    except Exception as e:
        print(f"[DEBUG] Erro crítico: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'redirect': '/admin/usuarios'
        }), 500

@usuarios_bp.route('/admin/usuarios/deletar/<int:id_usuario>', methods=['POST'])
def deletar(id_usuario):
    """Remove usuário do sistema"""
    try:
        print(f"[DEBUG] Recebida requisição DELETE para usuário ID: {id_usuario}")
        admin = get_admin()
        
        if id_usuario == session.get('usuario_id'):
            return jsonify({
                'error': 'Não é possível deletar o usuário logado',
                'redirect': '/admin/usuarios'
            }), 400

        usuario = admin.local_db.ler('usuarios', {'id': id_usuario})
        if usuario.empty:
            return jsonify({
                'error': 'Usuário não encontrado',
                'redirect': '/admin/usuarios'
            }), 404

        try:
            # Deleta o usuário
            print(f"[DEBUG] Iniciando deleção do usuário {id_usuario}")
            admin.deletar_usuario(id_usuario)
            
            # Força sincronização geral após deleção
            admin.sincronizar_tudo()
            print(f"[DEBUG] Sincronização geral realizada após deleção")
            
            return jsonify({
                'success': True,
                'message': 'Usuário removido com sucesso',
                'redirect': '/admin/usuarios'
            })

        except Exception as e:
            print(f"[DEBUG] Erro ao deletar usuário: {str(e)}")
            return jsonify({
                'error': f'Erro ao deletar usuário: {str(e)}',
                'redirect': '/admin/usuarios'
            }), 500

    except Exception as e:
        print(f"[DEBUG] Erro crítico na deleção: {str(e)}")
        return jsonify({
            'error': 'Erro ao deletar usuário. Tente novamente.',
            'redirect': '/admin/usuarios'
        }), 500