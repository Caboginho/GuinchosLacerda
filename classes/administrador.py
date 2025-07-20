from typing import List, Union, Optional
from classes.usuario import Usuario
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
import pandas as pd

class Administrador(Usuario):
    def __init__(self, id: int, nome: str, email: str, senha: str,
                 cnh: str = None, celular: str = None, justificativa: str = None,
                 local_db: BancoDados = None, cloud_db: GoogleDriveSheets = None):
        super().__init__(id, nome, email, senha, "Administrador", cnh, celular, justificativa)
        self.local_db = local_db if local_db is not None else BancoDados()
        self.cloud_db = cloud_db if cloud_db is not None else GoogleDriveSheets()

    # Operações com usuários
    def cadastrar_usuario(self, dados: dict):
        self.local_db.inserir("usuarios", dados)
        self.cloud_db.inserir("usuarios", dados)

    def atualizar_usuario(self, id_usuario: int, novos_dados: dict):
        """
        Atualiza usuário no sistema e mantém consistência das pastas de secretaria
        """
        try:
            print(f"[DEBUG] Iniciando atualização do usuário {id_usuario}")
            
            # Verifica se é secretaria e se houve mudança de email
            usuario_atual = self.local_db.ler("usuarios", {"id": id_usuario})
            if not usuario_atual.empty:
                usuario = usuario_atual.iloc[0]
                email_antigo = usuario['email']
                email_novo = novos_dados.get('email')
                
                if (usuario['tipo'] == 'Secretaria' and 
                    email_novo and email_novo != email_antigo):
                    print(f"[DEBUG] Detectada mudança de email da secretaria: {email_antigo} -> {email_novo}")
                    
                    # Atualiza nome da pasta no Drive
                    if self.cloud_db.check_internet():
                        try:
                            self.cloud_db.renomear_pasta_secretaria(email_antigo, email_novo)
                            print(f"[DEBUG] Pasta da secretaria renomeada com sucesso")
                        except Exception as e:
                            print(f"[DEBUG] Erro ao renomear pasta: {e}")
                            raise
            
            # Continua com a atualização normal
            self.local_db.atualizar("usuarios", linha=id_usuario, novos_dados=novos_dados)
            print(f"[DEBUG] Usuário {id_usuario} atualizado localmente")
            
            if self.cloud_db.check_internet():
                try:
                    self.cloud_db.atualizar(id_usuario-1, novos_dados)
                    print(f"[DEBUG] Usuário {id_usuario} atualizado na nuvem")
                except Exception as e:
                    print(f"[DEBUG] Erro ao atualizar na nuvem: {e}")
                    self.local_db.marcar_para_sincronizacao("usuarios", id_usuario, "update")
            else:
                self.local_db.marcar_para_sincronizacao("usuarios", id_usuario, "update")

        except Exception as e:
            print(f"[DEBUG] Erro durante atualização: {e}")
            raise

    def deletar_usuario(self, id_usuario: int):
        """
        Deleta um usuário do sistema, tanto local quanto na nuvem
        """
        try:
            print(f"[DEBUG] Iniciando processo de deleção para usuário {id_usuario}")
            
            # Verifica se é uma secretaria
            usuario = self.local_db.ler('usuarios', {'id': id_usuario}).iloc[0]
            if usuario['tipo'] == 'Secretaria':
                print(f"[DEBUG] Usuário é uma secretaria, deletando pasta no Drive")
                if self.cloud_db.check_internet():
                    try:
                        self.cloud_db.deletar_pasta_secretaria(usuario['email'])
                    except Exception as e:
                        print(f"[DEBUG] Erro ao deletar pasta da secretaria: {e}")
                        # Continua com a deleção mesmo se falhar ao deletar pasta
            
            # Primeiro tenta deletar na nuvem
            if self.cloud_db.check_internet():
                try:
                    self.cloud_db.deletar(id_usuario-1)
                    print(f"[DEBUG] Usuário {id_usuario} deletado na nuvem")
                except Exception as e:
                    print(f"[DEBUG] Erro ao deletar na nuvem: {e}")
                    raise

            # Depois deleta localmente
            self.local_db.deletar("usuarios", id_usuario)
            print(f"[DEBUG] Usuário {id_usuario} deletado localmente")
            print(f"[DEBUG] Processo de deleção concluído com sucesso")
            
        except Exception as e:
            print(f"[DEBUG] Erro durante deleção: {e}")
            raise

    # Operações com transações
    def cadastrar_transacao(self, dados: dict):
        self.local_db.inserir("transacoes", dados)
        self.cloud_db.inserir("transacoes", dados)
        self.sincronizar_tudo()  # Mantém tudo sincronizado

    def atualizar_transacao(self, id_transacao: int, novos_dados: dict):
        self.local_db.atualizar("transacoes", linha=id_transacao, novos_dados=novos_dados)
        self.cloud_db.atualizar("transacoes", linha=id_transacao, novos_dados=novos_dados)

    def deletar_transacao(self, id_transacao: int):
        self.local_db.deletar("transacoes", linha=id_transacao)
        self.cloud_db.deletar("transacoes", linha=id_transacao)

    # Operações com serviços de guincho
    def cadastrar_servico_guincho(self, dados: dict):
        self.local_db.inserir("servicos_guincho", dados)
        self.cloud_db.inserir("servicos_guincho", dados)

    def atualizar_servico_guincho(self, id_servico: int, novos_dados: dict):
        self.local_db.atualizar("servicos_guincho", linha=id_servico, novos_dados=novos_dados)
        self.cloud_db.atualizar("servicos_guincho", linha=id_servico, novos_dados=novos_dados)

    def deletar_servico_guincho(self, id_servico: int):
        self.local_db.deletar("servicos_guincho", linha=id_servico)
        self.cloud_db.deletar("servicos_guincho", linha=id_servico)

    # Operações com guinchos
    def cadastrar_guincho(self, dados: dict) -> int:
        """Cadastra guincho local e na nuvem"""
        try:
            # Verifica placa
            placa = dados.get('placa')
            if self.local_db.ler('guinchos', {'placa': placa}).shape[0] > 0:
                raise Exception('Placa já cadastrada')

            # Gera ID
            ultimo_guincho = self.local_db.ler('guinchos')
            novo_id = 1 if ultimo_guincho.empty else int(ultimo_guincho['id'].max()) + 1
            dados['id'] = novo_id
            
            # Salva local
            self.local_db.inserir('guinchos', dados)
            print(f"[DEBUG] Guincho cadastrado localmente com ID {novo_id}")
            
            # Sincroniza com nuvem
            if self.cloud_db.check_internet():
                try:
                    # Planilha global
                    self.cloud_db.inserir(dados, 'guinchos')
                    print("[DEBUG] Guincho inserido na planilha global")
                    
                    # Planilha da secretaria
                    if secretaria_id := dados.get('secretaria_id'):
                        secretaria = self.local_db.ler('usuarios', {'id': int(secretaria_id)})
                        if not secretaria.empty:
                            email = secretaria.iloc[0]['email']
                            self.cloud_db.inserir_guincho_secretaria(email, dados)
                            print(f"[DEBUG] Guincho inserido na planilha da secretaria {email}")
                except Exception as e:
                    print(f"[DEBUG] Erro na sincronização: {e}")
                    self.local_db.marcar_para_sincronizacao('guinchos', novo_id, 'insert')
            else:
                print("[DEBUG] Sem conexão, marcando para sincronização posterior")
                self.local_db.marcar_para_sincronizacao('guinchos', novo_id, 'insert')
            
            return novo_id
            
        except Exception as e:
            print(f"[DEBUG] Erro ao cadastrar guincho: {e}")
            raise

    def atualizar_guincho(self, id_guincho: int, dados: dict):
        """Atualiza um guincho existente mantendo consistência local/nuvem"""
        try:
            # Verifica se guincho existe
            guincho_atual = self.local_db.ler('guinchos', {'id': id_guincho})
            if guincho_atual.empty:
                raise Exception('Guincho não encontrado')
                
            guincho_atual = guincho_atual.iloc[0]
            
            # Verifica se nova placa já existe
            if (nova_placa := dados.get('placa')) != guincho_atual['placa']:
                if self.local_db.ler('guinchos', {'placa': nova_placa}).shape[0] > 0:
                    raise Exception('Nova placa já cadastrada')
            
            # Atualiza local
            self.local_db.atualizar('guinchos', id_guincho, dados)
            print(f"[DEBUG] Guincho atualizado localmente")
            
            # Tenta atualizar na nuvem
            if self.cloud_db.check_internet():
                try:
                    # Atualiza planilha global
                    self.cloud_db.atualizar_guincho(id_guincho, dados)
                    print(f"[DEBUG] Guincho atualizado na planilha global")
                    
                    # Trata mudança de secretaria
                    sec_antiga_id = guincho_atual['secretaria_id']
                    sec_nova_id = dados.get('secretaria_id')
                    
                    if sec_antiga_id != sec_nova_id:
                        # Remove da secretaria antiga
                        if sec_antiga_id:
                            sec_antiga = self.local_db.ler('usuarios', {'id': sec_antiga_id}).iloc[0]
                            self.cloud_db.remover_guincho_secretaria(sec_antiga['email'], id_guincho)
                            print(f"[DEBUG] Guincho removido da secretaria antiga")
                            
                        # Adiciona na nova secretaria
                        if sec_nova_id:
                            sec_nova = self.local_db.ler('usuarios', {'id': sec_nova_id}).iloc[0]
                            self.cloud_db.sincronizar_guincho_com_secretaria(sec_nova['email'], {**dados, 'id': id_guincho})
                            print(f"[DEBUG] Guincho adicionado à nova secretaria")
                    else:
                        # Atualiza na mesma secretaria
                        if sec_antiga_id:
                            secretaria = self.local_db.ler('usuarios', {'id': sec_antiga_id}).iloc[0]
                            self.cloud_db.sincronizar_guincho_com_secretaria(secretaria['email'], {**dados, 'id': id_guincho})
                            print(f"[DEBUG] Guincho atualizado na planilha da secretaria")
                            
                except Exception as e:
                    print(f"[DEBUG] Erro ao sincronizar com nuvem: {e}")
                    self.local_db.marcar_para_sincronizacao('guinchos', id_guincho, 'update')
            else:
                self.local_db.marcar_para_sincronizacao('guinchos', id_guincho, 'update')
                
        except Exception as e:
            print(f"[DEBUG] Erro ao atualizar guincho: {e}")
            raise

    def deletar_guincho(self, id_guincho: int):
        """Remove guincho do sistema"""
        try:
            # Busca dados antes de deletar
            guincho = self.local_db.ler('guinchos', {'id': id_guincho})
            if guincho.empty:
                raise Exception('Guincho não encontrado')
            
            dados_guincho = guincho.iloc[0]
            
            # Remove local
            self.local_db.deletar('guinchos', id_guincho)
            
            # Remove da nuvem
            if self.cloud_db.check_internet():
                try:
                    # Remove da planilha global
                    self.cloud_db.deletar_guincho(id_guincho)
                    
                    # Remove da planilha da secretaria
                    if secretaria_id := dados_guincho['secretaria_id']:
                        secretaria = self.local_db.ler('usuarios', {'id': int(secretaria_id)})
                        if not secretaria.empty:
                            email = secretaria.iloc[0]['email']
                            self.cloud_db.remover_guincho_secretaria(email, id_guincho)
                except Exception as e:
                    print(f"[DEBUG] Erro ao sincronizar deleção: {e}")
            
        except Exception as e:
            print(f"[DEBUG] Erro ao deletar guincho: {e}")
            raise

    def sincronizar_guincho(self, id_guincho: int):
        """Força sincronização de um guincho específico"""
        try:
            # Busca dados do guincho
            guincho = self.local_db.ler('guinchos', {'id': id_guincho})
            if guincho.empty:
                raise Exception('Guincho não encontrado')
                
            guincho = guincho.iloc[0].to_dict()
            
            if self.cloud_db.check_internet():
                # Sincroniza com planilha global
                self.cloud_db.atualizar_guincho(id_guincho, guincho)
                
                # Sincroniza com planilha da secretaria
                if secretaria_id := guincho.get('secretaria_id'):
                    secretaria = self.local_db.ler('usuarios', {'id': int(secretaria_id)})
                    if not secretaria.empty:
                        email = secretaria.iloc[0]['email']
                        self.cloud_db.sincronizar_guincho_com_secretaria(email, guincho)
                        print(f"[DEBUG] Guincho sincronizado com secretaria {email}")
                    
        except Exception as e:
            print(f"[DEBUG] Erro ao sincronizar guincho: {e}")
            raise

    def ler_guinchos_secretaria(self, email: str) -> pd.DataFrame:
        """Lê guinchos específicos de uma secretaria"""
        try:
            if self.cloud_db.check_internet():
                # Se online, busca da planilha da secretaria
                worksheet = self.cloud_db.get_planilha_secretaria(email)
                dados = pd.DataFrame(worksheet.get_all_records())
                return dados
            else:
                # Se offline, filtra do banco local
                usuario = self.local_db.ler('usuarios', {'email': email}).iloc[0]
                return self.local_db.ler('guinchos', {'secretaria_id': usuario['id']})
        except Exception as e:
            print(f"[DEBUG] Erro ao ler guinchos da secretaria: {e}")
            return pd.DataFrame()

    # Operações com anexos (para transações e serviços de guincho)
    def cadastrar_anexo_transacao(self, transacao_id: int, usuario_id: int,
                                  local_file_path: str, file_name: str):
        # Realiza upload do arquivo na pasta 'anexos' do Drive para obter a URL
        url = self.cloud_db.upload_file_to_anexos(local_file_path, file_name)
        if url:
            # Registra o anexo no banco de dados local usando a URL obtida
            self.local_db.inserir_anexo_transacao(transacao_id, usuario_id, url)
            # Registra o anexo na planilha do Drive
            dados = {
                "url": url,
                "usuario_id": usuario_id,
                "transacao_id": transacao_id,
                "servico_guincho_id": ""
            }
            self.cloud_db.inserir("anexos", dados)
        else:
            print("Falha ao cadastrar anexo para transação.")

    def cadastrar_anexo_servico(self, servico_id: int, usuario_id: int,
                                local_file_path: str, file_name: str):
        url = self.cloud_db.upload_file_to_anexos(local_file_path, file_name)
        if url:
            self.local_db.inserir_anexo_servico(servico_id, usuario_id, url)
            dados = {
                "url": url,
                "usuario_id": usuario_id,
                "transacao_id": "",
                "servico_guincho_id": servico_id
            }
            self.cloud_db.inserir("anexos", dados)
        else:
            print("Falha ao cadastrar anexo para serviço de guincho.")
        
    def ler_registros(self, tabela: str, condicoes: Optional[dict] = None) -> Union[pd.DataFrame, None]:
        """
        Lê registros da tabela especificada com base nas condições fornecidas.
        :param tabela: Nome da tabela.
        :param condicoes: Dicionário de condições para a consulta.
        :return: DataFrame com os resultados da consulta.
        """
        return self.local_db.ler(tabela, condicoes)

    def sincronizar_com_nuvem(self, tabela: str):
        """
        Sincroniza os dados do banco de dados local com a planilha na nuvem.
        """
        dados = self.local_db.ler(tabela)
        if dados is not None and not dados.empty:
            self.cloud_db.sincronizar_com_nuvem(tabela, dados)

    def sincronizar_com_local(self, tabela: str):
        """
        Sincroniza os dados da planilha na nuvem com o banco de dados local.
        """
        self.cloud_db.sincronizar_com_local(tabela, self.local_db)

    def sincronizar_tudo(self):
        """
        Sincroniza todas as tabelas com a nuvem
        """
        tabelas = ['usuarios', 'guinchos']#, 'transacoes', 'servicos_guincho', 'anexos']
        for tabela in tabelas:
            self.sincronizar_com_nuvem(tabela)
            self.sincronizar_com_local(tabela)

    def sincronizar_todas_secretarias(self):
        """Sincroniza dados de todas as secretarias para visão do admin"""
        try:
            print("[DEBUG] Iniciando sincronização de todas as secretarias")
            secretarias = self.local_db.ler("usuarios", {"tipo": "Secretaria"})
            
            for _, sec in secretarias.iterrows():
                print(f"[DEBUG] Sincronizando secretaria: {sec['email']}")
                dados = self.cloud_db.ler_dados_secretaria(sec['email'])
                if dados:
                    self.local_db.sincronizar_dados_secretaria(dados, sec['id'])
                    
            print("[DEBUG] Sincronização de secretarias concluída")
            
        except Exception as e:
            print(f"[DEBUG] Erro ao sincronizar secretarias: {e}")
            raise

    def cadastrar_secretaria(self, dados: dict):
        """Cadastra nova secretaria e cria sua estrutura completa"""
        try:
            print(f"[DEBUG] Iniciando cadastro de secretaria: {dados['email']}")
            
            if self.cloud_db.check_internet():
                # 1. Primeiro cadastra na nuvem
                self.cloud_db.inserir(dados=dados, tabela='usuarios')
                print("[DEBUG] Secretaria cadastrada na nuvem")
                
                # 2. Cria estrutura na nuvem
                pasta_id = self.cloud_db.criar_pasta_secretaria(dados['email'])
                if not pasta_id:
                    raise Exception("Falha ao criar pasta da secretaria")
                print("[DEBUG] Estrutura no Drive criada")

            # 3. Cadastra no banco local
            self.local_db.inserir("usuarios", dados)
            print("[DEBUG] Secretaria cadastrada localmente")
                
            # 4. Cria tabelas locais se não existirem
            self.local_db.criar_tabela_guincho()
            self.local_db.criar_tabela_transacoes()
            self.local_db.criar_tabela_servicos_guincho()
            
            print(f"[DEBUG] Secretaria {dados['email']} cadastrada com sucesso")
            return True
                
        except Exception as e:
            print(f"[DEBUG] Erro ao cadastrar secretaria: {e}")
            # Tenta reverter alterações em caso de erro
            try:
                if self.cloud_db.check_internet():
                    self.cloud_db.deletar(dados['id']-1)
                    self.cloud_db.deletar_pasta_secretaria(dados['email'])
            except:
                pass
            raise