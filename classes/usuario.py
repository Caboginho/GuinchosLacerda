# ==================== Definição das Entidades ====================
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
import bcrypt
class Usuario:
    def __init__(self, id= None, nome = None, email=None, senha=None, cnh=None, celular=None, justificativa=None):
        self.id = id
        self.nome = nome
        self.email = email if email else None
        self.senha = senha if senha else None
        self.tipo = None  # Será definido nas subclasses
        self.cnh = cnh if cnh else None
        self.celular = celular if celular else None
        self.justificativa = justificativa if justificativa else None
        self.banco = BancoDados()
        self.google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")

    def hash_senha(self, senha: str) -> str:
        return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    def verificar_senha(self, senha: str, hash_senha: str) -> bool:
        return bcrypt.checkpw(senha.encode(), hash_senha.encode()) 
    
    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id

    def getNome(self):
        return self.nome

    def setNome(self, nome):
        self.nome = nome

    def getEmail(self):
        return self.email

    def setEmail(self, email):
        self.email = email

    def getSenha(self):
        return self.senha

    def setSenha(self, senha):
        self.senha = senha

    def getTipo(self):
        return self.tipo

    def setTipo(self, tipo):
        self.tipo = tipo

    def getCnh(self):
        return self.cnh

    def setCnh(self, cnh):
        self.cnh = cnh

    def getCelular(self):
        return self.celular

    def setCelular(self, celular):
        self.celular = celular

    def getJustificativa(self):
        return self.justificativa

    def setJustificativa(self, justificativa):
        self.justificativa = justificativa

    def salvar(self, banco, google):
        dados = {
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha,
            "tipo": self.tipo,
            "cnh": self.cnh,
            "celular": self.celular,
            "justificativa": self.justificativa
        }
        self.banco.inserir("usuarios", dados)
        # Atualiza a planilha "usuarios"
        self.google.inserir("usuarios", [list(dados.values())])

class Administrador(Usuario):
    def __init__(self,id = None, nome=None, email=None, senha=None, cnh=None, celular=None, justificativa=None):
        super().__init__(id,nome, email, senha, cnh, celular, justificativa)
        self.tipo = "Administrador"
        
    def criar_registro(self, tabela, dados):
        self.banco.inserir(tabela, dados)
        self.google.inserir(tabela, [list(dados.values())])
        
    def ler_registros(self, tabela, filtros):
        if filtros == {}:
            return self.banco.ler(tabela)
        return self.banco.ler(tabela, filtros)
    
    def atualizar_registro(self, tabela, id_registro, novos_dados):
        self.banco.atualizar(tabela, id_registro, novos_dados)
        self.google.atualizar(tabela, id_registro, novos_dados)
        
    def deletar_registro(self, tabela, id_registro):
        self.banco.deletar(tabela, id_registro)
        self.google.deletar_linha(tabela, id_registro+1)
    
    def atualizar_celula(self, nome_planilha, linha, coluna, valor):
        self.banco.atualizar_celula(nome_planilha, linha, coluna, valor)
        self.google.atualizar_celula(nome_planilha, linha, coluna, valor)

class Secretaria(Usuario):
    def __init__(self, nome, email=None, senha=None, cnh=None, celular=None, justificativa=None):
        super().__init__(nome, email, senha, cnh, celular, justificativa)
        self.tipo = "Secretaria"
        self.logada = False
    
    def login(self, senha):
        if self.senha == senha:
            self.logada = True
            print(f"{self.nome} logada com sucesso!")
        else:
            print("Senha incorreta.")
    
    def logout(self):
        self.logada = False
        print(f"{self.nome} deslogada.")
    
    def criar_transacao(self, transacao):
        transacao.salvar(self.banco, self.google)
    
    def criar_servico_guincho(self, servico):
        servico.salvar(self.banco, self.google)
    
    def atualizar_celula(self, nome_planilha, linha, coluna, valor):
        self.banco.atualizar_celula(nome_planilha, linha, coluna, valor)
        self.google.atualizar_celula(nome_planilha, linha, coluna, valor)

class Motorista(Usuario):
    def __init__(self, nome, email=None, senha=None, cnh=None, celular=None, justificativa=None):
        super().__init__(nome, email, senha, cnh, celular, justificativa)
        self.tipo = "Motorista"
    # Motoristas possuem apenas atributos, sem métodos CRUD.

