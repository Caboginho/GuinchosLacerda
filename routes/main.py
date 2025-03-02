import os
import datetime
import zipfile
from classes.bancodados import BancoDados
from classes.googledrivesheets import GoogleDriveSheets
from classes.guincho import Guincho
from classes.transacao import Transacao
from classes.usuario import Administrador, Motorista, Secretaria
from classes.anexo import Anexo
from classes.servico_guincho import ServicoGuincho

# Cria a pasta para anexos, se não existir
if not os.path.exists("anexos"):
    os.makedirs("anexos")

def criar_attachment(conteudo, base_name, contador, usuario_ref):
    """
    Cria um arquivo TXT com nome incremental e, em seguida, gera um ZIP desse arquivo.
    Retorna o nome do arquivo ZIP, que será armazenado na tabela.
    """
    # Gera o nome do arquivo TXT
    file_txt = f"{base_name}_{contador}_{usuario_ref}.txt"
    caminho_txt = os.path.join("anexos", file_txt)
    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(conteudo)
    
    # Gera o nome do arquivo ZIP
    file_zip = f"{base_name}_{contador}_{usuario_ref}.zip"
    caminho_zip = os.path.join("anexos", file_zip)
    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(caminho_txt, arcname=file_txt)
    
    return file_zip

def zipar_anexos():
    zip_filename = "anexos.zip"
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for root, _, files in os.walk("anexos"):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    return zip_filename

# ==================== Funções Auxiliares para Teste ====================
def print_sheet_data(google, sheet_name):
    print(f"\nDados na planilha '{sheet_name}':")
    data = google.ler(sheet_name)
    for row in data:
        print(row)

def delete_rows_by_condition(google, sheet_name, col_index, target_value):
    data = google.ler(sheet_name)
    # Itera de baixo para cima para não alterar os índices
    for i in range(len(data), 0, -1):
        if len(data[i-1]) >= col_index and data[i-1][col_index-1] == target_value:
            google.deletar_linha(sheet_name, i)
            print(f"Linha {i} da planilha '{sheet_name}' deletada por condição: {target_value}.")

def update_cells_by_condition(google, sheet_name, col_index, target_value, new_value):
    data = google.ler(sheet_name)
    for i in range(1, len(data)+1):
        if len(data[i-1]) >= col_index and data[i-1][col_index-1] == target_value:
            google.atualizar(sheet_name, i, col_index, new_value)
            print(f"Célula na linha {i}, coluna {col_index} da planilha '{sheet_name}' atualizada de {target_value} para {new_value}.")

# ==================== Função Main ====================
def main():
    # Instancia o banco de dados local e a sincronização na nuvem
    banco = BancoDados()
    # Use o caminho completo para o arquivo de credenciais (lembre-se de usar r"..." ou escapar as barras)
    google = GoogleDriveSheets(r"classes\lacerdaguinchos-8e2aeaf562ce.json")
    
    # Criação (ou verificação) das worksheets online para cada "tabela"
    for tabela in ["usuarios", "transacoes", "guinchos", "servicos_guincho", "anexos"]:
        try:
            google.criar_planilha(tabela)
        except Exception as e:
            print(f"Planilha '{tabela}' pode já existir ou houve erro ao criar: {e}")
    
    # --- Cadastro de Usuários ---
    admin_existente = banco.ler("usuarios", {"tipo": "Administrador"})
    if admin_existente:
        print("Administrador já existe. O sistema aceita apenas um administrador.")
    else:
        admin = Administrador(nome="Admin", email="admin@example.com", senha="admin123",
                              cnh="000", celular="1111111111")
        admin.salvar(banco, google)
        print("Administrador cadastrado.")
    
    secretarias = []
    for i in range(1, 6):
        sec = Secretaria(nome=f"Secretaria {i}", email=f"secretaria{i}@example.com",
                         senha="sec123", celular=f"222222222{i}")
        sec.salvar(banco, google)
        secretarias.append(sec)
        print(f"Secretaria {i} cadastrada.")
    
    motoristas = []
    for i in range(1, 26):
        mot = Motorista(nome=f"Motorista {i}", email=f"motorista{i}@example.com",
                        senha="mot123", cnh=f"{100+i}", celular=f"333333333{i}")
        mot.salvar(banco, google)
        motoristas.append(mot)
        print(f"Motorista {i} cadastrado.")
    
    # --- Cadastro de Guinchos ---
    guinchos = []
    motorista_pool = motoristas.copy()
    for sec_index, sec in enumerate(secretarias, start=1):
        for j in range(1, 6):
            if motorista_pool:
                motorista = motorista_pool.pop(0)
                motorista_id = motorista.nome
            else:
                motorista_id = None
            placa = f"PLACA_{sec_index}_{j}"
            modelo = "Modelo X"
            guincho = Guincho(placa=placa, modelo=modelo, motorista_id=motorista_id, secretaria_id=sec.nome)
            guincho.salvar(banco, google)
            guinchos.append(guincho)
            print(f"Guincho {placa} cadastrado por {sec.nome} com motorista {motorista_id}")
    
    # --- Simulação de Transações ---
    for i in range(1, 11):
        data = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valor = 100.0 * i
        categoria = f"Categoria {i}"
        descricao = f"Transação de teste {i}"
        metodo_pagamento = ["Pix", "Cartão", "Dinheiro"][i % 3]
        secretaria_id = secretarias[i % len(secretarias)].nome
        guincho_id = guinchos[i % len(guinchos)].placa
        motorista_id = motoristas[i % len(motoristas)].nome
        status = ["Pago", "Pendente", "Parcelado"][i % 3]
        
        transacao = Transacao(data, valor, categoria, descricao, metodo_pagamento,
                              secretaria_id, guincho_id, motorista_id, status)
        transacao.salvar(banco, google)
        print(f"Transação {i} cadastrada.")
        
        # Exemplo para Transações:
        conteudo = (
            f"Transação {i}:\n"
            f"Data: {data}\nValor: {valor}\nCategoria: {categoria}\n"
            f"Descrição: {descricao}\nMétodo: {metodo_pagamento}\n"
            f"Secretaria: {secretaria_id}\nGuincho: {guincho_id}\nMotorista: {motorista_id}\nStatus: {status}"
        )
        # Gera o ZIP com um nome único (usando, por exemplo, 'anexo_transacao' como base)
        arquivo_zip = criar_attachment(conteudo, "anexo_transacao", i, secretaria_id)
        anexo = Anexo(operacao_id=i, file_name=arquivo_zip, tipo="nota_fiscal", usuario_id=secretaria_id)
        anexo.salvar(banco, google)
        print(f"Anexo para transação {i} criado.")
    
    # --- Simulação de Serviços de Guincho ---
    for i in range(1, 11):
        data_solicitacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        guincho_id = guinchos[i % len(guinchos)].placa
        tipo_solicitacao = ["Particular", "Seguradora"][i % 2]
        protocolo = f"PROTOCOLO_{i}"
        origem = f"Origem {i}"
        destino = f"Destino {i}"
        status = ["Em andamento", "Finalizado", "Cancelado"][i % 3]
        
        servico = ServicoGuincho(data_solicitacao, guincho_id, tipo_solicitacao,
                                 protocolo, origem, destino, status)
        servico.salvar(banco, google)
        print(f"Serviço de guincho {i} cadastrado.")
        
        # Cria anexo para serviço
        conteudo = (
        f"Serviço de Guincho {i}:\n"
        f"Data Solicitação: {data_solicitacao}\nGuincho: {guincho_id}\n"
        f"Tipo: {tipo_solicitacao}\nProtocolo: {protocolo}\n"
        f"Origem: {origem}\nDestino: {destino}\nStatus: {status}"
        )
        arquivo_zip = criar_attachment(conteudo, "Serviços de Guincho", i, secretaria_id)
        anexo = Anexo(operacao_id=i, file_name=arquivo_zip, tipo="nota_fiscal", usuario_id=secretaria_id)
        anexo.salvar(banco, google)
        
        print(f"Anexo para serviço de guincho {i} criado.")
    
    # Zipa e faz upload dos anexos
    zip_filename = zipar_anexos()
    try:
        google.upload_anexo(zip_filename)
        print(f"Anexos zipados e enviados para o Google Drive: {zip_filename}")
    except Exception as e:
        print(f"Erro ao enviar anexos zipados: {e}")
    
    # --- Testes de Leitura (ler) ---
    print_sheet_data(google, "usuarios")
    print_sheet_data(google, "transacoes")
    print_sheet_data(google, "guinchos")
    print_sheet_data(google, "servicos_guincho")
    print_sheet_data(google, "anexos")
    
    # --- Teste de Atualização (update) ---
    # Atualizar o email de "Secretaria 3" – supondo que, pela ordem de inserção, seu registro seja o de ID 4
    novo_email = "nova_secretaria3@example.com"
    admin = Administrador(nome="Admin", email="admin@example.com", senha="admin123",
                          cnh="000", celular="1111111111")
    admin.atualizar_registro("usuarios", 4, {"email": novo_email}, banco, google)
    print("\nApós atualização de Secretaria 3:")
    print_sheet_data(google, "usuarios")
    
    # --- Teste de Deleção (delete) com Cascade ---
    # 1. Excluir "Secretaria 3" (ID 4) – dados vinculados em transações e guinchos devem ser removidos
    admin.deletar_registro("usuarios", 4, banco, google)
    print("\nApós deleção de Secretaria 3 na planilha 'usuarios':")
    print_sheet_data(google, "usuarios")
    # Cascade delete nas planilhas:
    delete_rows_by_condition(google, "transacoes", 6, "Secretaria 3")  # coluna 6 = secretaria_id em transações
    delete_rows_by_condition(google, "guinchos", 4, "Secretaria 3")      # coluna 4 = secretaria_id em guinchos
    
    # 2. Excluir "Motorista 5" – supondo que seu registro seja o de ID 11; referências em transações e guinchos devem ser atualizadas para vazio
    admin.deletar_registro("usuarios", 11, banco, google)
    print("\nApós deleção de Motorista 5 na planilha 'usuarios':")
    print_sheet_data(google, "usuarios")
    update_cells_by_condition(google, "transacoes", 8, "Motorista 5", "")
    update_cells_by_condition(google, "guinchos", 3, "Motorista 5", "")
    
    # 3. Excluir a Transação 1 – o anexo vinculado também deve ser removido
    admin.deletar_registro("transacoes", 1, banco, google)
    print("\nApós deleção da Transação 1 na planilha 'transacoes':")
    print_sheet_data(google, "transacoes")
    delete_rows_by_condition(google, "anexos", 1, "1")  # coluna 1 = operacao_id (supondo que esteja salvo como "1")
    print("\nApós deleção em cascata do Anexo da Transação 1 na planilha 'anexos':")
    print_sheet_data(google, "anexos")
    
    print("\nSimulação completa. Dados salvos localmente e atualizados online, com operações de leitura, atualização e deleção (e cascade).")

if __name__ == "__main__":
    main()
