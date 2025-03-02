
class Guincho:
    def __init__(self, placa, modelo, motorista_id, secretaria_id, disponivel=True):
        self.placa = placa if placa else None
        self.modelo = modelo if modelo else None
        self.motorista_id = motorista_id if motorista_id else None
        self.secretaria_id = secretaria_id if secretaria_id else None
        self.disponivel = disponivel

    def salvar(self, banco, google):
        dados = {
            "placa": self.placa,
            "modelo": self.modelo,
            "motorista_id": self.motorista_id,
            "secretaria_id": self.secretaria_id,
            "disponivel": self.disponivel
        }
        banco.inserir("guinchos", dados)
        google.inserir("guinchos", [list(dados.values())])
