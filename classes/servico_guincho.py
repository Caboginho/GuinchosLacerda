
class ServicoGuincho:
    def __init__(self, data_solicitacao, guincho_id, tipo_solicitacao, protocolo,
                 origem, destino, status):
        self.data_solicitacao = data_solicitacao
        self.guincho_id = guincho_id
        self.tipo_solicitacao = tipo_solicitacao
        self.protocolo = protocolo
        self.origem = origem
        self.destino = destino
        self.status = status

    def salvar(self, banco, google):
        dados = {
            "data_solicitacao": self.data_solicitacao,
            "guincho_id": self.guincho_id,
            "tipo_solicitacao": self.tipo_solicitacao,
            "protocolo": self.protocolo,
            "origem": self.origem,
            "destino": self.destino,
            "status": self.status
        }
        banco.inserir("servicos_guincho", dados)
        google.inserir("servicos_guincho", [list(dados.values())])
