from typing import List, Union
from classes.usuario import Usuario
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
# usuarios.py
import pandas as pd
class Secretaria(Usuario):
    def __init__(self, id: int, nome: str, email: str, senha: str,
                 cnh: str = None, celular: str = None, justificativa: str = None,
                 local_db: BancoDados = None, cloud_db: GoogleDriveSheets = None):
        super().__init__(id, nome, email, senha, "Secretaria", cnh, celular, justificativa)
        self.local_db = local_db if local_db is not None else BancoDados()
        self.cloud_db = cloud_db if cloud_db is not None else GoogleDriveSheets()

    # Permite apenas cadastro e visualização de transações
    def cadastrar_transacao(self, dados: dict):
        """Cadastra transação na pasta específica da secretaria"""
        try:
            # Primeiro salva localmente
            transacao_id = self.local_db.inserir("transacoes", dados)
            
            # Depois tenta salvar na nuvem
            if self.cloud_db.check_internet():
                try:
                    # Usa o método específico para salvar na planilha da secretaria
                    self.cloud_db.inserir_em_planilha_secretaria(
                        email=self.email,
                        nome_planilha='transacoes',
                        dados={**dados, 'id': transacao_id}
                    )
                except Exception as e:
                    print(f"[DEBUG] Erro ao salvar na nuvem: {e}")
                    self.local_db.marcar_para_sincronizacao('transacoes', transacao_id, 'insert')
            else:
                self.local_db.marcar_para_sincronizacao('transacoes', transacao_id, 'insert')
                
            return transacao_id
            
        except Exception as e:
            print(f"[DEBUG] Erro ao cadastrar transação: {e}")
            raise

    def visualizar_transacoes(self):
        # Retorna os dados locais e os espelhados na nuvem
        local_data = self.local_db.ler("transacoes")
        cloud_data = self.cloud_db.ler("transacoes")
        return local_data, cloud_data

    # Permite apenas cadastro e visualização de serviços de guincho
    def cadastrar_servico_guincho(self, dados: dict):
        self.local_db.inserir("servicos_guincho", dados)
        self.cloud_db.inserir("servicos_guincho", dados)

    def visualizar_servicos_guincho(self):
        local_data = self.local_db.ler("servicos_guincho")
        cloud_data = self.cloud_db.ler("servicos_guincho")
        return local_data, cloud_data

    # Opcional: cadastro de anexos para transações e serviços, caso necessário
    def cadastrar_anexo_transacao(self, transacao_id: int, usuario_id: int,
                                  local_file_path: str, file_name: str):
        url = self.cloud_db.upload_file_to_anexos(local_file_path, file_name)
        if url:
            self.local_db.inserir_anexo_transacao(transacao_id, usuario_id, url)
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
    
    def ler_registros(self, tabela: str, parametros: List[str] = None) -> Union[pd.DataFrame, None]:
        """
        Lê registros filtrados pelo ID da secretaria
        """
        df = self.local_db.ler(tabela)
        if df is None:
            return None
            
        # Filtra registros pela secretaria
        if tabela == 'transacoes':
            df = df[df['secretaria_id'] == self.id]
        elif tabela == 'servicos_guincho':
            df = df[df['guincho_id'].isin(
                self.local_db.ler('guinchos', {'secretaria_id': self.id})['id']
            )]
            
        if parametros:
            return df[parametros]
        return df

    def carregar_dados_secretaria(self):
        """Carrega dados específicos da pasta da secretaria para o banco local"""
        pasta_secretaria = f"{self.nome}_{self.id}"
        
        # Carrega transações da secretaria
        transacoes_df = self.cloud_db.ler_planilha_secretaria("transacoes", pasta_secretaria)
        if not transacoes_df.empty:
            transacoes_df.to_sql("transacoes", self.local_db.conexao, if_exists='replace', index=False)
            
        # Carrega serviços de guincho da secretaria
        servicos_df = self.cloud_db.ler_planilha_secretaria("servicos_guincho", pasta_secretaria)
        if not servicos_df.empty:
            servicos_df.to_sql("servicos_guincho", self.local_db.conexao, if_exists='replace', index=False)
            
        # Carrega guinchos da secretaria
        guinchos_df = self.cloud_db.ler_planilha_secretaria("guinchos", pasta_secretaria)
        if not guinchos_df.empty:
            guinchos_df.to_sql("guinchos", self.local_db.conexao, if_exists='replace', index=False)

    def salvar_transacao(self, dados: dict):
        """Salva transação na pasta específica da secretaria"""
        pasta_secretaria = f"{self.nome}_{self.id}"
        self.local_db.inserir("transacoes", dados)
        self.cloud_db.inserir_planilha_secretaria("transacoes", pasta_secretaria, dados)

    def salvar_servico_guincho(self, dados: dict):
        """Salva serviço na pasta específica da secretaria"""
        pasta_secretaria = f"{self.nome}_{self.id}"
        self.local_db.inserir("servicos_guincho", dados)
        self.cloud_db.inserir_planilha_secretaria("servicos_guincho", pasta_secretaria, dados)

    def sincronizar_meus_dados(self):
        """Sincroniza apenas os dados desta secretaria"""
        dados = self.cloud_db.ler_dados_secretaria(self.email)
        self.local_db.sincronizar_dados_secretaria(dados, self.id)

class Motorista(Usuario):
    def __init__(self, id: int, nome: str, email: str, senha: str,
                 cnh: str = None, celular: str = None, justificativa: str = None):
        super().__init__(id, nome, email, senha, "Motorista", cnh, celular, justificativa)

    def interagir(self):
        print("O motorista não interage com o sistema.")