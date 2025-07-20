import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import requests
from typing import Optional

class GoogleDriveSheets:
    def __init__(self, credentials_file: str):
        """Inicializa conexão com Google Drive/Sheets"""
        self.credentials_file = credentials_file
        self.scope = ['https://www.googleapis.com/auth/drive',
                     'https://www.googleapis.com/auth/spreadsheets']
        self.creds = Credentials.from_service_account_file(credentials_file, scopes=self.scope)
        self.gc = gspread.authorize(self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        
        # Configurações da pasta raiz e anexos
        self.root_folder_name = "LacerdaGuinchos"
        self.root_folder_id = None
        self.anexos_folder_id = None
        
        # Inicializa estrutura básica
        self._initialize_structure()

    def _initialize_structure(self):
        """Inicializa estrutura básica do Drive"""
        self.root_folder_id = self._get_or_create_root_folder()
        self.anexos_folder_id = self._get_or_create_anexos_folder()
        
        try:
            self.usuarios_sheet = self._get_spreadsheet("usuarios")
            self.guinchos_sheet = self._get_spreadsheet("guinchos")
            print("Planilhas principais encontradas.")
        except gspread.exceptions.SpreadsheetNotFound:
            self.usuarios_sheet = self._create_spreadsheet("usuarios")
            self.guinchos_sheet = self._create_spreadsheet("guinchos")
            print("Planilhas principais criadas com sucesso.")
            self.inicializar_planilha_usuarios()
            self.inicializar_planilha_guinchos()

    def _get_or_create_root_folder(self) -> str:
        """Obtém ou cria a pasta raiz LacerdaGuinchos"""
        query = f"name='{self.root_folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if items:
            print(f"Pasta '{self.root_folder_name}' encontrada.")
            return items[0]['id']
        
        # Cria pasta raiz
        folder_metadata = {
            'name': self.root_folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive_service.files().create(
            body=folder_metadata, fields='id').execute()
        print(f"Pasta '{self.root_folder_name}' criada com sucesso.")
        return folder.get('id')

    def _get_or_create_anexos_folder(self) -> str:
        """Obtém ou cria a pasta anexos dentro da pasta raiz"""
        query = f"'{self.root_folder_id}' in parents and name='anexos' and mimeType='application/vnd.google-apps.folder'"
        results = self.drive_service.files().list(q=query, fields="files(id)").execute()
        items = results.get('files', [])
        
        if items:
            print("Pasta 'anexos' encontrada.")
            return items[0]['id']
            
        # Cria pasta anexos
        folder_metadata = {
            'name': 'anexos',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [self.root_folder_id]
        }
        folder = self.drive_service.files().create(
            body=folder_metadata, fields='id').execute()
        print("Pasta 'anexos' criada com sucesso.")
        return folder.get('id')

    def _get_spreadsheet(self, name: str):
        """Obtém planilha pelo nome dentro da pasta LacerdaGuinchos"""
        query = f"'{self.root_folder_id}' in parents and name='{name}' and mimeType='application/vnd.google-apps.spreadsheet'"
        results = self.drive_service.files().list(q=query, fields="files(id)").execute()
        items = results.get('files', [])
        
        if not items:
            raise gspread.exceptions.SpreadsheetNotFound
            
        return self.gc.open_by_key(items[0]['id'])

    def _create_spreadsheet(self, name: str):
        """Cria nova planilha dentro da pasta LacerdaGuinchos"""
        spreadsheet = self.gc.create(name)
        
        # Move para pasta correta e compartilha
        spreadsheet.share(self.creds.service_account_email, 
                         perm_type='user', role='writer')
        self.drive_service.files().update(
            fileId=spreadsheet.id,
            addParents=self.root_folder_id,
            removeParents='root').execute()
            
        return spreadsheet

    def inicializar_planilha_usuarios(self):
        """Garante que a planilha usuarios tem os cabeçalhos corretos"""
        try:
            worksheet = self.usuarios_sheet.sheet1
            worksheet.clear()  # Limpa toda a planilha
            headers = ['id', 'nome', 'email', 'senha', 'tipo', 'cnh', 'celular', 'justificativa']
            worksheet.append_row(headers)
            print("Planilha 'usuarios' inicializada com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao inicializar planilha usuarios: {e}")
            return False

    def inicializar_planilha_guinchos(self):
        """Inicializa planilha de guinchos com cabeçalhos"""
        try:
            worksheet = self.guinchos_sheet.sheet1
            worksheet.clear()
            headers = ['id', 'modelo', 'placa', 'secretaria_id', 'status']
            worksheet.append_row(headers)
            print("Planilha 'guinchos' inicializada com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao inicializar planilha guinchos: {e}")
            return False

    def inserir(self, dados: dict, tabela: str = 'usuarios'):
        """Insere um registro na planilha específica"""
        try:
            # Seleciona a planilha correta
            worksheet = None
            if tabela == 'usuarios':
                worksheet = self.usuarios_sheet.sheet1
            elif tabela == 'guinchos':
                worksheet = self.guinchos_sheet.sheet1
            else:
                raise ValueError(f"Tabela não suportada: {tabela}")

            # Verifica headers
            headers = self._get_headers_for_table(tabela)
            
            # Prepara e insere nova linha
            row_data = []
            for header in headers:
                value = str(dados.get(header, '')) if header in dados else ''
                if value.lower() == 'none':
                    value = ''
                row_data.append(value)
            
            # Insere nova linha
            worksheet.append_row(row_data)
            print(f"[DEBUG] Novo registro inserido na planilha {tabela}")
            print(f"[DEBUG] Dados inseridos: {dict(zip(headers, row_data))}")
            
            return True
                
        except Exception as e:
            print(f"[DEBUG] Erro ao inserir na planilha {tabela}: {e}")
            raise

    def ler(self, tabela: str = 'usuarios') -> pd.DataFrame:
        """Lê registros da planilha especificada"""
        try:
            # Seleciona a planilha correta
            worksheet = None
            if (tabela == 'usuarios'):
                worksheet = self.usuarios_sheet.sheet1
            elif (tabela == 'guinchos'):
                worksheet = self.guinchos_sheet.sheet1
            else:
                raise ValueError(f"Tabela não suportada: {tabela}")

            # Lê os registros
            records = worksheet.get_all_records()
            df = pd.DataFrame(records) if records else pd.DataFrame()
            
            if not df.empty and 'id' in df.columns:
                df['id'] = df['id'].apply(lambda x: int(float(x)) if pd.notna(x) and str(x).strip() else None)
                df = df.dropna(subset=['id'])
                
            return df
        except Exception as e:
            print(f"Erro ao ler planilha {tabela}: {e}")
            return pd.DataFrame()

    def atualizar(self, linha: int, novos_dados: dict):
        """
        Atualiza um registro na planilha usuarios.
        A linha é baseada em índice zero, cabeçalho é linha 1.
        """
        try:
            worksheet = self.usuarios_sheet.sheet1
            for key, val in novos_dados.items():
                # Encontra a coluna do campo
                cell = worksheet.find(key)
                if cell:
                    # Atualiza na linha correta (linha+2 pois: +1 pelo cabeçalho, +1 pelo índice começar em 0)
                    worksheet.update_cell(linha+2, cell.col, str(val))
                    print(f"Atualizado campo {key} na linha {linha+2}")
        except Exception as e:
            print(f"Erro ao atualizar planilha: {e}")

    def deletar(self, linha: Optional[int] = None):
        """Deleta registros da planilha usuarios"""
        worksheet = self.usuarios_sheet.sheet1
        if (linha is not None):
            worksheet.delete_rows(linha + 2)
        else:
            headers = worksheet.row_values(1)
            worksheet.clear()
            worksheet.append_row(headers)

    def check_internet(self) -> bool:
        """Verifica conexão com internet"""
        try:
            requests.get("http://www.google.com", timeout=3)
            return True
        except requests.RequestException:
            return False

    def sincronizar_com_nuvem(self, tabela: str, dados_locais: pd.DataFrame):
        """Sincroniza dados locais com a planilha na nuvem"""
        try:
            worksheet = self.usuarios_sheet.sheet1
            
            # Reinicializa a planilha com headers
            self.inicializar_planilha_usuarios()
            
            # Insere dados formatados linha por linha
            for _, row in dados_locais.iterrows():
                row_data = []
                for col in ['id', 'nome', 'email', 'senha', 'tipo', 'cnh', 'celular', 'justificativa']:
                    value = row.get(col, '')
                    if pd.isna(value) or value is None:
                        value = ''
                    row_data.append(str(value))
                worksheet.append_row(row_data)
                
            print(f"Dados sincronizados com sucesso para nuvem")
            return True
            
        except Exception as e:
            print(f"Erro ao sincronizar com nuvem: {e}")
            return False

    def sincronizar_com_local(self, tabela: str, banco_local):
        """Sincroniza dados da nuvem para o banco local"""
        try:
            # Lê dados da planilha
            dados_nuvem = self.ler()
            if dados_nuvem.empty:
                print(f"Nenhum dado encontrado na planilha {tabela}")
                return

            # Atualiza banco local
            banco_local.deletar(tabela)  # Limpa tabela local
            dados_nuvem.to_sql(tabela, banco_local.conexao, if_exists='append', index=False)
            print(f"Sincronizados {len(dados_nuvem)} registros para tabela local {tabela}")
            
        except Exception as e:
            print(f"Erro ao sincronizar com local: {e}")

    def sincronizar_pendentes(self, banco_local):
        """Sincroniza registros pendentes"""
        pendentes = banco_local.get_pendentes_sincronizacao()
        
        for _, registro in pendentes.iterrows():
            try:
                # Busca dados do registro
                dados = banco_local.ler(registro['tabela'], {'id': registro['registro_id']})
                if dados.empty:
                    continue
                    
                # Realiza operação pendente
                if registro['tipo_operacao'] == 'insert':
                    self.inserir(dados.iloc[0].to_dict(), registro['tabela'])
                elif registro['tipo_operacao'] == 'update':
                    self.atualizar(registro['registro_id']-1, dados.iloc[0].to_dict())
                elif registro['tipo_operacao'] == 'delete':
                    self.deletar(registro['registro_id']-1)
                    
                # Remove da lista de pendências
                banco_local.remover_sincronizacao_pendente(registro['id'])
                
            except Exception as e:
                print(f"Erro ao sincronizar registro pendente {registro['id']}: {e}")

    def criar_pasta_secretaria(self, email: str) -> str:
        """Cria pasta para secretaria e suas planilhas"""
        try:
            print(f"[DEBUG] Criando estrutura para secretaria: {email}")
            
            # Verifica se a pasta já existe
            query = f"name='secretaria_{email}' and mimeType='application/vnd.google-apps.folder' and '{self.root_folder_id}' in parents"
            results = self.drive_service.files().list(q=query).execute()
            if results.get('files'):
                print(f"[DEBUG] Pasta para secretaria {email} já existe")
                return results['files'][0]['id']
            
            # Cria pasta da secretaria
            folder_metadata = {
                'name': f"secretaria_{email}",
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [self.root_folder_id]
            }
            pasta = self.drive_service.files().create(
                body=folder_metadata, fields='id').execute()
            pasta_id = pasta.get('id')
            
            print(f"[DEBUG] Pasta criada com ID: {pasta_id}")
            
            # Cria planilhas dentro da pasta
            planilhas = ['guinchos', 'transacoes', 'servicos_guincho']
            for nome in planilhas:
                sheet = self.gc.create(nome)
                print(f"[DEBUG] Criando planilha {nome}")
                
                # Compartilha e move para pasta correta
                sheet.share(self.creds.service_account_email, 
                           perm_type='user', role='writer')
                self.drive_service.files().update(
                    fileId=sheet.id,
                    addParents=pasta_id,
                    removeParents='root').execute()
                
                # Inicializa cabeçalhos
                worksheet = sheet.sheet1
                headers = self._get_headers_for_table(nome)
                worksheet.append_row(headers)
                print(f"[DEBUG] Planilha {nome} inicializada")
            
            return pasta_id
        except Exception as e:
            print(f"[DEBUG] Erro ao criar pasta da secretaria: {e}")
            raise

    def _get_headers_for_table(self, table_name: str) -> list:
        """Retorna cabeçalhos para cada tipo de tabela"""
        headers = {
            'usuarios': ['id', 'nome', 'email', 'senha', 'tipo', 'cnh', 'celular', 'justificativa'],
            'guinchos': ['id', 'modelo', 'placa', 'secretaria_id', 'status'],
            'transacoes': ['id', 'data', 'tipo', 'valor', 'descricao', 'metodo_pagamento', 'status', 'secretaria_id', 'servico_id'],
            'servicos_guincho': ['id', 'data_solicitacao', 'data_fim', 'guincho_id', 'tipo_solicitacao', 
                                'protocolo', 'origem', 'destino', 'status', 'secretaria_id', 'transacao_id']
        }
        return headers.get(table_name, [])

    def ler_dados_secretaria(self, email: str) -> dict:
        """Lê todas as planilhas de uma secretaria"""
        try:
            query = f"name='secretaria_{email}' and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(q=query).execute()
            pasta = results.get('files', [])[0]
            
            dados = {}
            planilhas = ['guinchos', 'transacoes', 'servicos_guincho']
            for nome in planilhas:
                sheet = self._get_spreadsheet_in_folder(nome, pasta['id'])
                if sheet:
                    dados[nome] = pd.DataFrame(sheet.sheet1.get_all_records())
            
            return dados
        except Exception as e:
            print(f"Erro ao ler dados da secretaria: {e}")
            return {}

    def _get_spreadsheet_in_folder(self, name: str, folder_id: str):
        """Obtém planilha específica dentro de uma pasta"""
        query = f"name='{name}' and '{folder_id}' in parents"
        results = self.drive_service.files().list(q=query).execute()
        if results.get('files'):
            return self.gc.open_by_key(results['files'][0]['id'])
        return None

    def renomear_pasta_secretaria(self, email_antigo: str, email_novo: str) -> bool:
        """
        Renomeia a pasta de uma secretaria quando seu email é alterado
        """
        try:
            # Busca pasta atual
            query = f"name='secretaria_{email_antigo}' and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(q=query).execute()
            pastas = results.get('files', [])
            
            if not pastas:
                print(f"[DEBUG] Pasta da secretaria {email_antigo} não encontrada")
                return False
                
            pasta = pastas[0]
            
            # Atualiza nome da pasta
            novo_nome = f"secretaria_{email_novo}"
            file_metadata = {'name': novo_nome}
            
            self.drive_service.files().update(
                fileId=pasta['id'],
                body=file_metadata
            ).execute()
            
            print(f"[DEBUG] Pasta renomeada: {email_antigo} -> {email_novo}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Erro ao renomear pasta: {e}")
            raise

    def deletar_pasta_secretaria(self, email: str) -> bool:
        """
        Deleta a pasta e todo conteúdo de uma secretaria do Drive
        """
        try:
            # Busca pasta da secretaria
            query = f"name='secretaria_{email}' and mimeType='application/vnd.google-apps.folder'"
            results = self.drive_service.files().list(q=query).execute()
            pastas = results.get('files', [])
            
            if not pastas:
                print(f"[DEBUG] Pasta da secretaria {email} não encontrada")
                return False
                
            # Deleta a pasta e todo seu conteúdo
            self.drive_service.files().delete(fileId=pastas[0]['id']).execute()
            print(f"[DEBUG] Pasta da secretaria {email} deletada com sucesso")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Erro ao deletar pasta da secretaria: {e}")
            raise

    def inserir_guincho(self, dados: dict):
        """Insere guincho na planilha global"""
        try:
            worksheet = self.guinchos_sheet.sheet1
            headers = self._get_headers_for_table('guinchos')
            row_data = [str(dados.get(h, '')) for h in headers]
            worksheet.append_row(row_data)
            print(f"[DEBUG] Guincho inserido na planilha global")
            return True
        except Exception as e:
            print(f"[DEBUG] Erro ao inserir guincho global: {e}")
            raise

    def inserir_guincho_secretaria(self, email_secretaria: str, dados: dict):
        """Insere guincho na planilha específica da secretaria"""
        try:
            print(f"[DEBUG] Iniciando inserção na planilha da secretaria {email_secretaria}")
            
            # Busca pasta da secretaria
            query = f"name='secretaria_{email_secretaria}' and mimeType='application/vnd.google-apps.folder' and '{self.root_folder_id}' in parents"
            results = self.drive_service.files().list(q=query).execute()
            
            if not results.get('files'):
                raise Exception(f"Pasta da secretaria {email_secretaria} não encontrada")
                
            pasta_id = results['files'][0]['id']
            print(f"[DEBUG] Pasta da secretaria encontrada: {pasta_id}")
            
            # Busca planilha de guinchos
            query = f"name='guinchos' and '{pasta_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
            results = self.drive_service.files().list(q=query).execute()
            
            if not results.get('files'):
                raise Exception(f"Planilha de guinchos não encontrada para secretaria {email_secretaria}")
            
            # Usa gspread para abrir e manipular a planilha
            planilha = self.gc.open_by_key(results['files'][0]['id'])
            worksheet = planilha.sheet1
            
            headers = self._get_headers_for_table('guinchos')
            row_data = [str(dados.get(h, '')) for h in headers]
            worksheet.append_row(row_data)
            
            print(f"[DEBUG] Guincho inserido com sucesso na planilha da secretaria {email_secretaria}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] Erro ao inserir guincho na secretaria: {e}")
            raise

    def atualizar_guincho(self, id_guincho: int, dados: dict):
        """Atualiza guincho na planilha global"""
        try:
            print(f"[DEBUG] Atualizando guincho {id_guincho} na planilha global")
            worksheet = self.guinchos_sheet.sheet1
            registros = worksheet.get_all_records()
            
            # Encontra linha do guincho
            linha_encontrada = None
            for i, reg in enumerate(registros, 2):  # +2 pelo cabeçalho e índice 0
                if str(reg['id']) == str(id_guincho):
                    linha_encontrada = i
                    break
                    
            if not linha_encontrada:
                raise Exception(f"Guincho {id_guincho} não encontrado na planilha global")
                
            # Atualiza cada campo
            headers = self._get_headers_for_table('guinchos')
            for col, header in enumerate(headers, 1):
                if header in dados:
                    valor = str(dados[header] or '')
                    worksheet.update_cell(linha_encontrada, col, valor)
                    print(f"[DEBUG] Campo {header} atualizado para '{valor}'")
                        
            print(f"[DEBUG] Guincho {id_guincho} atualizado com sucesso na planilha global")
                
        except Exception as e:
            print(f"[DEBUG] Erro ao atualizar guincho na planilha global: {e}")
            raise

    def deletar_guincho(self, id_guincho: int):
        """Deleta guincho da planilha global"""
        try:
            worksheet = self.guinchos_sheet.sheet1
            registros = worksheet.get_all_records()
            
            # Encontra linha do guincho
            linha_remover = None
            for i, reg in enumerate(registros, 2):
                if str(reg['id']) == str(id_guincho):
                    linha_remover = i
                    break
                    
            if linha_remover:
                worksheet.delete_rows(linha_remover)
                print(f"[DEBUG] Guincho {id_guincho} removido da planilha global")
                
        except Exception as e:
            print(f"[DEBUG] Erro ao deletar guincho global: {e}")
            raise

    def remover_guincho_secretaria(self, email: str, id_guincho: int):
        """Remove guincho da planilha da secretaria"""
        try:
            pasta = self._get_secretaria_folder(email)
            if not pasta:
                raise Exception(f"Pasta da secretaria {email} não encontrada")
                
            planilha = self._get_spreadsheet_in_folder('guinchos', pasta['id'])
            if planilha:
                worksheet = planilha.sheet1
                dados = worksheet.get_all_records()
                
                # Encontra e remove o guincho
                linha_remover = None
                for i, guincho in enumerate(dados, 2):  # +2 pelo cabeçalho e índice 0
                    if str(guincho['id']) == str(id_guincho):
                        linha_remover = i
                        break
                
                if linha_remover:
                    worksheet.delete_rows(linha_remover)
                    
        except Exception as e:
            print(f"[DEBUG] Erro ao remover guincho da secretaria: {e}")
            raise

    def sincronizar_guincho_secretaria(self, email: str, dados: dict):
        """Sincroniza um guincho específico na planilha da secretaria"""
        try:
            print(f"[DEBUG] Iniciando sincronização de guincho para secretaria {email}")
            
            # Busca pasta da secretaria
            query = f"name='secretaria_{email}' and mimeType='application/vnd.google-apps.folder' and '{self.root_folder_id}' in parents"
            results = self.drive_service.files().list(q=query).execute()
            
            if not results.get('files'):
                raise Exception(f"Pasta da secretaria {email} não encontrada")
                
            pasta_id = results['files'][0]['id']
            
            # Busca planilha de guinchos
            query = f"name='guinchos' and '{pasta_id}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
            results = self.drive_service.files().list(q=query).execute()
            
            if not results.get('files'):
                raise Exception(f"Planilha de guinchos não encontrada")
                
            planilha = self.gc.open_by_key(results['files'][0]['id'])
            worksheet = planilha.sheet1
            
            # Verifica se guincho já existe
            registros = worksheet.get_all_records()
            linha_existente = None
            for i, reg in enumerate(registros, 2):  # +2 pelo cabeçalho e índice 0
                if str(reg['id']) == str(dados['id']):
                    linha_existente = i
                    break
            
            headers = self._get_headers_for_table('guinchos')
            if linha_existente:
                # Atualiza registro existente
                for col, header in enumerate(headers, 1):
                    if header in dados:
                        worksheet.update_cell(linha_existente, col, str(dados[header]))
            else:
                # Insere novo registro
                row_data = [str(dados.get(h, '')) for h in headers]
                worksheet.append_row(row_data)
            
            print(f"[DEBUG] Guincho sincronizado com sucesso na planilha da secretaria {email}")
            
        except Exception as e:
            print(f"[DEBUG] Erro ao sincronizar guincho com secretaria: {e}")
            raise

    def _get_secretaria_folder(self, email: str):
        """Obtém pasta de uma secretaria específica"""
        query = f"name='secretaria_{email}' and mimeType='application/vnd.google-apps.folder'"
        results = self.drive_service.files().list(q=query).execute()
        return results.get('files', [])[0] if results.get('files') else None

    def get_planilha_secretaria(self, email: str, nome_planilha: str = 'guinchos'):
        """Obtém planilha específica da pasta da secretaria"""
        try:
            # Busca pasta da secretaria
            pasta = self._get_secretaria_folder(email)
            if not pasta:
                raise Exception(f"Pasta da secretaria {email} não encontrada")

            # Busca planilha específica
            planilha = self._get_spreadsheet_in_folder(nome_planilha, pasta['id'])
            if not planilha:
                raise Exception(f"Planilha {nome_planilha} não encontrada")

            return planilha.sheet1
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar planilha {nome_planilha} da secretaria {email}: {e}")
            raise

    def sincronizar_guincho_com_secretaria(self, email_secretaria: str, dados_guincho: dict):
        """Sincroniza guincho na planilha da secretaria"""
        try:
            print(f"[DEBUG] Iniciando sincronização com secretaria {email_secretaria}")
            # Busca planilha da secretaria
            pasta = self._get_secretaria_folder(email_secretaria)
            if not pasta:
                raise Exception(f"Pasta da secretaria {email_secretaria} não encontrada")
                
            planilha = self._get_spreadsheet_in_folder('guinchos', pasta['id'])
            if not planilha:
                raise Exception(f"Planilha de guinchos não encontrada para secretaria {email_secretaria}")
                
            worksheet = planilha.sheet1
            records = worksheet.get_all_records()
            
            # Verifica se guincho já existe
            linha_existente = None
            for i, reg in enumerate(records, 2):
                if str(reg['id']) == str(dados_guincho['id']):
                    linha_existente = i
                    break

            headers = self._get_headers_for_table('guinchos')
            if linha_existente:
                # Atualiza registro existente
                for col, header in enumerate(headers, 1):
                    if header in dados_guincho:
                        valor = str(dados_guincho[header] or '')
                        worksheet.update_cell(linha_existente, col, valor)
                print(f"[DEBUG] Guincho atualizado na planilha da secretaria")
            else:
                # Insere novo registro
                row_data = [str(dados_guincho.get(h, '')) for h in headers]
                worksheet.append_row(row_data)
                print(f"[DEBUG] Guincho inserido na planilha da secretaria")
            
        except Exception as e:
            print(f"[DEBUG] Erro ao sincronizar com secretaria: {e}")
            raise

    def inserir_em_planilha_secretaria(self, email: str, nome_planilha: str, dados: dict):
        """Insere dados em uma planilha específica da secretaria"""
        try:
            print(f"[DEBUG] Inserindo em {nome_planilha} para secretaria {email}")
            worksheet = self.get_planilha_secretaria(email, nome_planilha)
            
            # Garante que temos os headers corretos
            headers = self._get_headers_for_table(nome_planilha)
            if not headers:
                raise ValueError(f"Headers não definidos para tabela: {nome_planilha}")
                
            # Prepara dados na ordem correta
            row_data = []
            for header in headers:
                value = str(dados.get(header, '')) if header in dados else ''
                if value.lower() == 'none':
                    value = ''
                row_data.append(value)
                
            print(f"[DEBUG] Dados a inserir: {dict(zip(headers, row_data))}")
            worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            print(f"[DEBUG] Erro ao inserir na planilha {nome_planilha} da secretaria {email}: {e}")
            raise
