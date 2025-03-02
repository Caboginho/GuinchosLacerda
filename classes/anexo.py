
class Anexo:
    def __init__(self, operacao_id, file_name, tipo, usuario_id=None):
        self.operacao_id = operacao_id
        self.file_name = file_name  # utiliza a coluna "file_name" conforme a tabela no banco
        self.tipo = tipo
        self.usuario_id = usuario_id
    
    def salvar(self, banco, google):
        dados = {
            "transacao_id": self.operacao_id,
            "file_name": self.file_name,  # chave ajustada para "file_name"
            "tipo": self.tipo
        }
        banco.inserir("anexos", dados)
        google.inserir("anexos", [list(dados.values())])
        google.upload_anexo(self.file_name)
