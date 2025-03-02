
class Transacao:
    def __init__(self, data, valor, categoria, descricao, metodo_pagamento,
                 secretaria_id, guincho_id, motorista_id, status):
        self.data = data
        self.valor = valor
        self.categoria = categoria
        self.descricao = descricao
        self.metodo_pagamento = metodo_pagamento
        self.secretaria_id = secretaria_id
        self.guincho_id = guincho_id
        self.motorista_id = motorista_id
        self.status = status

    def salvar(self, banco, google):
        dados = {
            "data": self.data,
            "valor": self.valor,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "metodo_pagamento": self.metodo_pagamento,
            "secretaria_id": self.secretaria_id,
            "guincho_id": self.guincho_id,
            "motorista_id": self.motorista_id,
            "status": self.status
        }
        banco.inserir("transacoes", dados)
        google.inserir("transacoes", [list(dados.values())])
