import bcrypt

class Usuario:
    def __init__(self, id: int = None, nome: str = None, email: str = None, senha: str = None, tipo: str = None,
                 cnh: str = None, celular: str = None, justificativa: str = None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo
        self.cnh = cnh
        self.celular = celular
        self.justificativa = justificativa

    def __str__(self):
        return f"Usuario({self.tipo}): {self.nome} - {self.email}"

    def hash_senha(self, senha: str) -> str:
        """
        Gera um hash bcrypt para a senha fornecida.
        :param senha: Senha em texto plano
        :return: Hash da senha
        """
        try:
            # Garante que a senha é uma string válida
            if not senha:
                raise ValueError("Senha não pode ser vazia")
                
            # Gera o salt e o hash
            senha_bytes = senha.encode('utf-8')
            salt = bcrypt.gensalt()
            hash_bytes = bcrypt.hashpw(senha_bytes, salt)
            
            # Retorna o hash como string
            return hash_bytes.decode('utf-8')
            
        except Exception as e:
            print(f"Erro ao gerar hash da senha: {e}")
            raise

    def verificar_senha(self, senha: str, hash_senha: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.
        :param senha: Senha em texto plano
        :param hash_senha: Hash da senha armazenada
        :return: True se a senha corresponder, False caso contrário
        """
        try:
            # Garante que a senha e o hash são strings válidas
            if not senha or not hash_senha:
                print("Senha ou hash vazios")
                return False
                
            # Garante que estamos trabalhando com bytes
            senha_bytes = senha.encode('utf-8')
            hash_bytes = hash_senha.encode('utf-8')
            
            # Faz a verificação
            resultado = bcrypt.checkpw(senha_bytes, hash_bytes)
            print(f"Verificação de senha: {'sucesso' if resultado else 'falha'}")
            return resultado
            
        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False
    
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
        return self.hash_senha(self.senha)

    def setSenha(self, senha):
        self.senha = self.hash_senha(senha)

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





