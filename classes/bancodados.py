import sqlite3
import pandas as pd

class BancoDados:
    def __init__(self, nome_banco: str = 'gestao_guinchos.db'):
        self.nome_banco = nome_banco
        self.conexao = sqlite3.connect(self.nome_banco)
        self.cursor = self.conexao.cursor()
        self.criar_tabela_usuario()
    
    def criar_tabela_usuario(self):
        """Cria todas as tabelas necessárias"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE,
            senha TEXT,
            tipo TEXT CHECK(tipo IN ('Administrador', 'Secretaria', 'Motorista')) NOT NULL,
            cnh TEXT,
            celular TEXT NOT NULL,
            justificativa TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS sync_pendente
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela TEXT NOT NULL,
            registro_id INTEGER NOT NULL,
            tipo_operacao TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conexao.commit()
   
    def criar_tabela_guincho(self):        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS guinchos
            (id INTEGER PRIMARY KEY,
            modelo TEXT NOT NULL,
            placa TEXT UNIQUE,
            secretaria_id INTEGER,
            motorista_id INTEGER,
            status TEXT,
            FOREIGN KEY(secretaria_id) REFERENCES usuarios(id),
            FOREIGN KEY(motorista_id) REFERENCES usuarios(id))''')
        self.conexao.commit()
        
    def criar_tabela_transacoes(self):            
        # Primeiro dropa a tabela se existir para recriar com nova estrutura
        self.cursor.execute('DROP TABLE IF EXISTS transacoes')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transacoes
            (id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('guinchamento', 'entrada', 'despesa_fixa', 'despesa_variavel')) COLLATE NOCASE,
            valor REAL,
            descricao TEXT,
            metodo_pagamento TEXT CHECK(metodo_pagamento IN ('Pix', 'Cartão', 'Dinheiro')),
            status TEXT CHECK(status IN ('Pago', 'Pendente', 'Parcelado')),
            secretaria_id INTEGER,
            servico_id INTEGER,
            FOREIGN KEY(secretaria_id) REFERENCES usuarios(id),
            FOREIGN KEY(servico_id) REFERENCES servicos_guincho(id))''')
        self.conexao.commit()
        print("[DEBUG] Tabela transacoes (re)criada com sucesso")
        
    def criar_tabela_servicos_guincho(self):        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS servicos_guincho
            (id INTEGER PRIMARY KEY,
            data_solicitacao TEXT NOT NULL,
            data_fim TEXT,
            guincho_id INTEGER,
            tipo_solicitacao TEXT DEFAULT 'Pendente',
            protocolo TEXT,
            origem TEXT,
            destino TEXT,
            status TEXT DEFAULT 'Em espera',
            secretaria_id INTEGER,
            transacao_id INTEGER,
            FOREIGN KEY(guincho_id) REFERENCES guinchos(id),
            FOREIGN KEY(secretaria_id) REFERENCES usuarios(id),
            FOREIGN KEY(transacao_id) REFERENCES transacoes(id))''')   
        self.conexao.commit()

    def criar_tabela_anexos(self):
        """Cria tabela para armazenar anexos"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS anexos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            transacao_id INTEGER,
            servico_id INTEGER,
            data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(transacao_id) REFERENCES transacoes(id),
            FOREIGN KEY(servico_id) REFERENCES servicos_guincho(id))''')
        self.conexao.commit()

    def inserir(self, tabela: str, dados: dict):
        """Insere um registro em uma tabela"""
        try:
            # Recria tabelas se necessário
            if tabela == 'transacoes':
                self.criar_tabela_transacoes()
            elif tabela == 'servicos_guincho':
                self.criar_tabela_servicos_guincho()

            # Verifica se já existe email (para usuários)
            if tabela == 'usuarios' and 'email' in dados:
                existente = self.ler(tabela, {'email': dados['email']})
                if not existente.empty:
                    raise Exception(f"Já existe um usuário com o email {dados['email']}")

            # Prepara a query
            dados_limpos = {k: v for k, v in dados.items() if v is not None}
            colunas = ', '.join(dados_limpos.keys())
            placeholders = ', '.join(['?' for _ in dados_limpos])
            sql = f'INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})'
            
            print(f"[DEBUG] SQL: {sql}")
            print(f"[DEBUG] Valores: {list(dados_limpos.values())}")
            
            self.cursor.execute(sql, list(dados_limpos.values()))
            self.conexao.commit()
            
            ultimo_id = self.cursor.lastrowid
            print(f"[DEBUG] Registro inserido com ID: {ultimo_id}")
            return ultimo_id

        except Exception as e:
            print(f"[DEBUG] Erro ao inserir no banco: {e}")
            self.conexao.rollback()
            raise

    def ler(self, tabela: str, filtros: dict = None) -> pd.DataFrame:
        """Lê registros de uma tabela, opcionalmente com filtros"""
        try:
            sql = f'SELECT * FROM {tabela}'
            if filtros:
                condicoes = ' AND '.join([f'{k}=?' for k in filtros.keys()])
                sql += f' WHERE {condicoes}'
                params = list(filtros.values())
            else:
                params = []

            # Lê dados do banco
            df = pd.read_sql(sql, self.conexao, params=params)
            
            # Garante que o ID é inteiro
            if not df.empty and 'id' in df.columns:
                df['id'] = df['id'].apply(lambda x: int(x) if pd.notna(x) else None)
                
            print(f"Lidos {len(df)} registros da tabela {tabela}")
            return df
            
        except Exception as e:
            print(f"Erro ao ler tabela {tabela}: {e}")
            return pd.DataFrame()

    def ler_anexos_transacao(self, transacao_id: int) -> pd.DataFrame:
        """Lê anexos de uma transação específica"""
        try:
            self.criar_tabela_anexos()  # Garante que a tabela existe
            sql = "SELECT * FROM anexos WHERE transacao_id = ?"
            df = pd.read_sql(sql, self.conexao, params=[transacao_id])
            return df
        except Exception as e:
            print(f"[DEBUG] Erro ao ler anexos da transação {transacao_id}: {e}")
            return pd.DataFrame()

    def inserir_anexo_transacao(self, transacao_id: int, url: str):
        """Insere um novo anexo para uma transação"""
        try:
            self.criar_tabela_anexos()
            sql = "INSERT INTO anexos (transacao_id, url) VALUES (?, ?)"
            self.cursor.execute(sql, [transacao_id, url])
            self.conexao.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"[DEBUG] Erro ao inserir anexo: {e}")
            self.conexao.rollback()
            raise

    def atualizar(self, tabela: str, linha: int, novos_dados: dict):
        """Atualiza registros em uma tabela"""
        sets = ', '.join([f'{k}=?' for k in novos_dados.keys()])
        sql = f'UPDATE {tabela} SET {sets} WHERE id=?'
        valores = list(novos_dados.values()) + [linha]
        self.cursor.execute(sql, valores)
        self.conexao.commit()

    def deletar(self, tabela: str, linha: int = None):
        """Deleta registros de uma tabela"""
        if linha:
            self.cursor.execute(f'DELETE FROM {tabela} WHERE id=?', [linha])
        else:
            self.cursor.execute(f'DELETE FROM {tabela}')
        self.conexao.commit()

    def sincronizar_dados_secretaria(self, dados: dict, secretaria_id: int):
        """Sincroniza dados de uma secretaria específica"""
        try:
            print(f"[DEBUG] Sincronizando dados para secretaria_id: {secretaria_id}")
            for tabela, df in dados.items():
                if not df.empty:
                    print(f"[DEBUG] Processando tabela: {tabela}")
                    # Adiciona ID da secretaria
                    df['secretaria_id'] = secretaria_id
                    
                    # Remove registros existentes
                    self.cursor.execute(f"DELETE FROM {tabela} WHERE secretaria_id = ?", (secretaria_id,))
                    
                    # Insere novos registros um a um
                    for _, row in df.iterrows():
                        colunas = ', '.join(row.index)
                        placeholders = ', '.join(['?' for _ in row])
                        sql = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"
                        self.cursor.execute(sql, row.values.tolist())
                        
                    print(f"[DEBUG] Sincronizados {len(df)} registros para {tabela}")
                    
            self.conexao.commit()
            print(f"[DEBUG] Sincronização concluída para secretaria {secretaria_id}")
            
        except Exception as e:
            print(f"[DEBUG] Erro ao sincronizar dados: {e}")
            self.conexao.rollback()
            raise

    def marcar_para_sincronizacao(self, tabela: str, registro_id: int, tipo_operacao: str = 'insert'):
        """Marca um registro para sincronização futura"""
        sql = 'INSERT INTO sync_pendente (tabela, registro_id, tipo_operacao) VALUES (?, ?, ?)'
        self.cursor.execute(sql, (tabela, registro_id, tipo_operacao))
        self.conexao.commit()

    def marcar_para_sincronizacao(self, tabela: str, registro_id: int, operacao: str):
        """
        Marca um registro para sincronização posterior
        :param operacao: 'insert', 'update' ou 'delete'
        """
        try:
            sql = '''INSERT INTO sync_pendente 
                     (tabela, registro_id, tipo_operacao) 
                     VALUES (?, ?, ?)'''
            self.cursor.execute(sql, (tabela, registro_id, operacao))
            self.conexao.commit()
            print(f"[DEBUG] Registro {registro_id} da tabela {tabela} marcado para {operacao}")
        except Exception as e:
            print(f"[DEBUG] Erro ao marcar para sincronização: {e}")
            self.conexao.rollback()

    def get_pendentes_sincronizacao(self) -> pd.DataFrame:
        """Retorna registros pendentes de sincronização"""
        return pd.read_sql('SELECT * FROM sync_pendente', self.conexao)

    def remover_sincronizacao_pendente(self, id: int):
        """Remove registro da tabela de pendências após sincronização"""
        self.cursor.execute('DELETE FROM sync_pendente WHERE id = ?', (id,))
        self.conexao.commit()
