import sqlite3
from typing import List, Optional, Dict, Tuple
import os
import logging


# Configuração do logger
logging.basicConfig(filename="banco_erros.log", level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class BancoDados:
    def __init__(self, nome_banco: str = "gestao_guinchos.db"):
        try:
            banco_existe = os.path.exists(nome_banco)
            self.conexao = sqlite3.connect(nome_banco, isolation_level=None)
            self.cursor = self.conexao.cursor()
            if not banco_existe:
                self.criar_tabelas()
        except Exception as e:
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def criar_tabelas(self):
        tabelas_sql = {
            "usuarios": '''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE,
                    senha TEXT,
                    tipo TEXT CHECK(tipo IN ('Administrador', 'Secretaria', 'Motorista')) NOT NULL,
                    cnh TEXT UNIQUE,
                    celular TEXT NOT NULL,
                    justificativa TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
            ''',
            "transacoes": '''
                CREATE TABLE IF NOT EXISTS transacoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    valor REAL NOT NULL,
                    categoria TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    metodo_pagamento TEXT CHECK(metodo_pagamento IN ('Pix', 'Cartão', 'Dinheiro')) NOT NULL,
                    secretaria_id INTEGER,
                    status TEXT CHECK(status IN ('Pago', 'Pendente', 'Parcelado')) NOT NULL,
                    FOREIGN KEY(secretaria_id) REFERENCES usuarios(id),
                    FOREIGN KEY(guincho_id) REFERENCES guinchos(id) ON DELETE CASCADE,
                    FOREIGN KEY(motorista_id) REFERENCES usuarios(id)
                );
            ''',
            "guinchos": '''
                CREATE TABLE IF NOT EXISTS guinchos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    placa TEXT UNIQUE NOT NULL,
                    modelo TEXT NOT NULL,
                    motorista_id INTEGER,
                    secretaria_id INTEGER NOT NULL,
                    disponivel BOOLEAN DEFAULT 1,
                    FOREIGN KEY(motorista_id) REFERENCES usuarios(id) ON DELETE SET NULL,
                    FOREIGN KEY(secretaria_id) REFERENCES usuarios(id)
                );
                CREATE INDEX IF NOT EXISTS idx_guinchos_placa ON guinchos(placa);
            ''',
            "servicos_guincho": '''
                CREATE TABLE IF NOT EXISTS servicos_guincho (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_solicitacao TEXT NOT NULL,
                    guincho_id INTEGER NOT NULL,
                    tipo_solicitacao TEXT CHECK(tipo_solicitacao IN ('Particular', 'Seguradora')) NOT NULL,
                    protocolo TEXT,
                    origem TEXT NOT NULL,
                    destino TEXT NOT NULL,
                    status TEXT CHECK(status IN ('Em andamento', 'Finalizado', 'Cancelado')) NOT NULL,
                    FOREIGN KEY(guincho_id) REFERENCES guinchos(id) ON DELETE CASCADE
                );
            ''',
            "anexos": '''
                CREATE TABLE IF NOT EXISTS anexos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transacao_id INTEGER NOT NULL,
                    file_name TEXT NOT NULL,
                    tipo TEXT CHECK(tipo IN ('atestado', 'comprovante_guinchamento', 'nota_fiscal')) NOT NULL,
                    FOREIGN KEY(transacao_id) REFERENCES transacoes(id)
                );
           '''
        }
        try:
            for sql in tabelas_sql.values():
                self.cursor.executescript(sql)
        except Exception as e:
            logging.error(f"Erro ao criar tabelas: {e}")
            raise

    def inserir(self, tabela: str, dados: dict):
        try:
            if tabela == "usuarios":
                if "senha" in dados:
                    dados["senha"] = self.hash_senha(dados["senha"])
            
            colunas = ', '.join(dados.keys())
            placeholders = ', '.join(['?' for _ in dados])
            valores = tuple(dados.values())
            sql = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})"
            self.cursor.execute(sql, valores)
        except Exception as e:
            logging.error(f"Erro ao inserir dados na tabela {tabela}: {e}")
            raise

    def ler(self, tabela: str, filtros: Optional[Dict[str, str]] = None) -> List[Tuple]:
        try:
            sql = f"SELECT * FROM {tabela}"
            parametros = []
            if filtros:
                condicoes = [f"{coluna} = ?" for coluna in filtros]
                sql += " WHERE " + " AND ".join(condicoes)
                parametros = list(filtros.values())
            self.cursor.execute(sql, tuple(parametros))
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Erro ao ler dados da tabela {tabela}: {e}")
            return []

    def atualizar(self, tabela: str, id_registro: int, novos_dados: dict):
        try:
            clausula_set = ', '.join([f"{chave} = ?" for chave in novos_dados.keys()])
            valores = tuple(novos_dados.values()) + (id_registro,)
            sql = f"UPDATE {tabela} SET {clausula_set} WHERE id = ?"
            self.cursor.execute(sql, valores)
        except Exception as e:
            logging.error(f"Erro ao atualizar dados na tabela {tabela}: {e}")
            raise

    def atualizar_celula(self, tabela: str, id_linha: int, id_coluna: str, novo_valor):
        try:
            sql = f"UPDATE {tabela} SET {id_coluna} = ? WHERE id = ?"
            self.cursor.execute(sql, (novo_valor, id_linha))
            if self.cursor.rowcount == 0:
                return f"Registro com id {id_linha} não encontrado na tabela {tabela}."
            return "Atualização realizada com sucesso."
        except Exception as e:
            logging.error(f"Erro ao atualizar célula na tabela {tabela}: {e}")
            return f"Erro ao atualizar célula: {e}"

    def deletar(self, tabela: str, id_registro: int):
        try:
            sql = f"DELETE FROM {tabela} WHERE id = ?"
            self.cursor.execute(sql, (id_registro,))
        except Exception as e:
            logging.error(f"Erro ao deletar registro na tabela {tabela}: {e}")
            raise

    def fechar_conexao(self):
        self.conexao.close()
