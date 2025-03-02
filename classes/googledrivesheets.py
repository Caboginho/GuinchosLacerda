import os
import zipfile
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import gspread.exceptions

class GoogleDriveSheets:
    def __init__(self, credenciais_json: str, id_pasta_principal: str = "1YXTazfxjcKE8rmv_nnF80pQZMIor8XKz", nome_planilha: str = "LacerdaGuinchos_Database"):
        # Define os escopos de acesso
        self.worksheets_cache = {}  # novo cache
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(credenciais_json, scope)
        self.client = gspread.authorize(creds)
        # Inicializa o serviço do Google Drive para mover a planilha
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.id_pasta_principal = id_pasta_principal

        # Tenta abrir uma planilha com o nome informado. Se não existir, cria uma nova.
        try:
            self.spreadsheet = self.client.open(nome_planilha)
        except Exception as e:
            self.spreadsheet = self.client.create(nome_planilha)
            file_id = self.spreadsheet.id
            # Recupera os pais atuais (geralmente a raiz) para removê-los
            file = self.drive_service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            # Move a planilha para a pasta desejada
            self.drive_service.files().update(
                fileId=file_id,
                addParents=self.id_pasta_principal,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()

    def criar_planilha(self, nome_planilha: str):
        if nome_planilha in self.worksheets_cache:
            return self.worksheets_cache[nome_planilha]
        try:
            worksheet = self.spreadsheet.worksheet(nome_planilha)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = self.spreadsheet.add_worksheet(title=nome_planilha, rows="1000", cols="10")
        self.worksheets_cache[nome_planilha] = worksheet
        return worksheet

    def inserir(self, nome_planilha: str, dados: list):
        """
        Insere os dados (lista de listas) na worksheet especificada.
        Implementa retry em caso de erro 429 (Quota exceeded).
        """
        max_retries = 3
        delay = 1  # segundos de espera entre as tentativas
        for tentativa in range(max_retries):
            try:
                worksheet = self.criar_planilha(nome_planilha)
                worksheet.append_rows(dados)
                return  # sucesso
            except gspread.exceptions.APIError as e:
                if "429" in str(e):
                    print(f"Quota exceeded. Tentativa {tentativa+1} de {max_retries}. Aguardando {delay} segundos...")
                    time.sleep(delay)
                else:
                    raise e
        print(f"Falha ao inserir dados na planilha '{nome_planilha}' após {max_retries} tentativas.")

    def ler(self, nome_planilha: str) -> list:
        """
        Retorna todos os valores da worksheet especificada.
        """
        try:
            worksheet = self.criar_planilha(nome_planilha)
            return self.retry_with_backoff(worksheet.get_all_values)
        except Exception as e:
            print(f"Erro ao ler dados da planilha '{nome_planilha}': {e}")
            return []

    def atualizar_celula(self, nome_planilha: str, linha: int, coluna: int, valor):
        """
        Atualiza uma única célula (linha, coluna) na worksheet especificada.
        """
        try:
            worksheet = self.criar_planilha(nome_planilha)
            self.retry_with_backoff(worksheet.update_cell, linha, coluna, valor)
        except Exception as e:
            print(f"Erro ao atualizar a célula na planilha '{nome_planilha}': {e}")

    def atualizar_registro(self, nome_planilha: str, linha: int, dados: dict):
        """
        Atualiza os campos especificados em 'dados' na linha da worksheet.
        Por exemplo, para atualizar a justificativa para 'online' do usuário na linha 'linha':
        
        atualizar_registro('usuarios', usuario_id, {'justificativa': 'online'})
        
        É necessário definir o mapeamento de nomes de campos para o índice da coluna.
        """
        try:
            worksheet = self.criar_planilha(nome_planilha)
            # Mapeamento de campos para a planilha "usuarios". Ajuste para outras tabelas se necessário.
            if nome_planilha.lower() == 'usuarios':
                mapping = {
                    'nome': 1,
                    'email': 2,
                    'senha': 3,
                    'tipo': 4,
                    'cnh': 5,
                    'celular': 6,
                    'justificativa': 7
                }
            else:
                mapping = {}
            for campo, novo_valor in dados.items():
                if campo in mapping:
                    coluna = mapping[campo]
                    self.retry_with_backoff(worksheet.update_cell, linha, coluna, novo_valor)
                else:
                    print(f"Campo '{campo}' não mapeado para a planilha '{nome_planilha}'.")
        except Exception as e:
            print(f"Erro ao atualizar o registro na planilha '{nome_planilha}': {e}")

    def atualizar(self, nome_planilha: str, linha, coluna_or_dados, valor=None):
        """
        Método sobrecarregado para atualização:
        - Se 'coluna_or_dados' for um inteiro, assume atualização de uma única célula,
            utilizando (linha, coluna, valor).
        - Se 'coluna_or_dados' for um dicionário, assume atualização de um registro completo,
            onde 'linha' é o número da linha e 'coluna_or_dados' contém os campos a atualizar.
        
        Exemplo de uso:
        google.atualizar('usuarios', usuario_id, 7, 'online')         -> Atualiza a célula (usuario_id, 7)
        google.atualizar('usuarios', usuario_id, {'justificativa': 'online'})  -> Atualiza o campo 'justificativa'
        """
        if isinstance(coluna_or_dados, int):
            self.atualizar_celula(nome_planilha, linha, coluna_or_dados, valor)
        elif isinstance(coluna_or_dados, dict):
            self.atualizar_registro(nome_planilha, linha, coluna_or_dados)
        else:
            print("Parâmetros inválidos para atualizar.")


    def deletar_linha(self, nome_planilha: str, linha: int ):
        """
        Deleta a linha especificada na worksheet.
        """
        try:
            worksheet = self.criar_planilha(nome_planilha)
            self.retry_with_backoff(worksheet.delete_rows, linha)
        except Exception as e:
            print(f"Erro ao deletar a linha na planilha '{nome_planilha}': {e}")

    def upload_anexo(self, zip_filename):
        try:
            file_path = os.path.join("anexos", zip_filename)
            # Verifica ou cria a pasta "anexos" dentro da pasta LacerdaGuinchos
            anexos_folder_id = self.obter_ou_criar_pasta("anexos", self.id_pasta_principal)
            file_metadata = {'name': zip_filename, 'parents': [anexos_folder_id]}
            media = MediaFileUpload(file_path, mimetype='application/zip')
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Arquivo {zip_filename} enviado com ID: {file.get('id')}")
        except Exception as e:
            print(f"Erro ao enviar anexos zipados: {e}")

    def obter_ou_criar_pasta(self, nome_pasta: str, id_pai: str) -> str:
        """
        Verifica se a pasta com o nome especificado existe (dentro do pai, se informado).
        Se não existir, cria a pasta e retorna seu ID.
        """
        query = f"name = '{nome_pasta}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if id_pai:
            query += f" and '{id_pai}' in parents"
        resultados = self.drive_service.files().list(q=query, fields="files(id)").execute()
        arquivos = resultados.get('files', [])
        if arquivos:
            return arquivos[0]['id']
        else:
            metadata = {'name': nome_pasta, 'mimeType': 'application/vnd.google-apps.folder'}
            if id_pai:
                metadata['parents'] = [id_pai]
            pasta = self.drive_service.files().create(body=metadata, fields='id').execute()
            return pasta.get('id')

    def retry_with_backoff(self, func, *args, **kwargs):
        """
        Implementa um mecanismo de retry com backoff exponencial para lidar com limitações de cota da API.
        """
        max_retries = 5
        backoff_factor = 2
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except gspread.exceptions.APIError as e:
                if e.response.status_code == 429:
                    wait_time = backoff_factor ** attempt
                    print(f"Quota exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
        raise Exception("Max retries exceeded")
