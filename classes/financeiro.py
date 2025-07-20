# financeiro.py
import datetime
from classes.bancodados import BancoDados
import pandas as pd
from datetime import datetime

class Financeiro:
    def __init__(self, banco_dados):
        self.db = banco_dados

    def calcular_metricas(self, data_inicio: str, data_fim: str):
        transacoes = self.db.ler("transacoes")
        mask = (pd.to_datetime(transacoes['data']) >= pd.to_datetime(data_inicio)) & \
               (pd.to_datetime(transacoes['data']) <= pd.to_datetime(data_fim))
        
        transacoes_filtradas = transacoes[mask]
        
        entradas = transacoes_filtradas[transacoes_filtradas['categoria'] == 'Entrada']['valor'].sum()
        despesas_fixas = transacoes_filtradas[transacoes_filtradas['categoria'] == 'Despesas fixa']['valor'].sum()
        despesas_variaveis = transacoes_filtradas[transacoes_filtradas['categoria'] == 'Despesas variáveis']['valor'].sum()
        
        return {
            'receita': entradas - (despesas_fixas + despesas_variaveis),
            'entradas': entradas,
            'saidas': despesas_fixas + despesas_variaveis,
            'despesas_fixas': despesas_fixas,
            'despesas_variaveis': despesas_variaveis,
            'total_transacoes': len(transacoes_filtradas),
            'total_servicos': len(self.db.ler("servicos_guincho"))
        }

def get_bar_chart_data(data_inicio=None, data_fim=None):
    """
    Agrega os dados financeiros por data (formato YYYY-MM-DD) e calcula:
      - Entrada: soma das transações com categoria 'investimento' ou 'entrada'
      - Saída: soma das demais transações (custos)
      - Transações: quantidade de registros
      - Serviços de Guincho: contagem dos serviços com status 'Finalizado'
      - Despesas Fixas: soma das transações com categoria 'despesa fixa'
      - Despesas Variáveis: soma das transações com categoria 'despesa variavel'
      - Receita: Entrada - Saída
    """
    banco = BancoDados()
    transacoes = banco.ler("transacoes", {})
    servicos = banco.ler("servicos_guincho", {})

    data_inicio_dt = datetime.datetime.strptime(data_inicio, "%Y-%m-%d") if data_inicio else None
    data_fim_dt = datetime.datetime.strptime(data_fim, "%Y-%m-%d") if data_fim else None

    bar_data = {}
    categorias = ["Receita", "Entrada", "Saída", "Transações", "Serviços de Guincho", "Despesas Fixas", "Despesas Variáveis"]

    def init_date_entry(date_str):
        if date_str not in bar_data:
            bar_data[date_str] = {cat: 0 for cat in categorias}

    # Processa transações
    for t in transacoes:
        # t = (id, data, valor, categoria, descricao, metodo_pagamento, secretaria_id, guincho_id, motorista_id, status)
        try:
            t_date = datetime.datetime.strptime(t[1], "%Y-%m-%d")
        except Exception:
            continue

        if data_inicio_dt and t_date < data_inicio_dt:
            continue
        if data_fim_dt and t_date > data_fim_dt:
            continue

        date_str = t_date.strftime("%Y-%m-%d")
        init_date_entry(date_str)
        valor = t[2]
        cat = t[3].lower()
        if cat in ["investimento", "entrada"]:
            bar_data[date_str]["Entrada"] += valor
        else:
            bar_data[date_str]["Saída"] += valor
            if cat == "despesa fixa":
                bar_data[date_str]["Despesas Fixas"] += valor
            elif cat == "despesa variavel":
                bar_data[date_str]["Despesas Variáveis"] += valor
        bar_data[date_str]["Transações"] += 1

    # Processa os serviços de guincho
    for s in servicos:
        # s = (id, data_solicitacao, guincho_id, tipo_solicitacao, protocolo, origem, destino, status)
        try:
            try:
                s_date = datetime.datetime.strptime(s[1], "%Y-%m-%dT%H:%M")
            except:
                s_date = datetime.datetime.strptime(s[1], "%Y-%m-%d")
        except Exception:
            continue

        if data_inicio_dt and s_date < data_inicio_dt:
            continue
        if data_fim_dt and s_date > data_fim_dt:
            continue

        date_str = s_date.strftime("%Y-%m-%d")
        init_date_entry(date_str)
        if s[7].lower() == "finalizado":
            bar_data[date_str]["Serviços de Guincho"] += 1

    for date_str, dados in bar_data.items():
        dados["Receita"] = dados["Entrada"] - dados["Saída"]

    sorted_dates = sorted(bar_data.keys())
    datasets = {cat: [] for cat in categorias}
    for date in sorted_dates:
        for cat in categorias:
            datasets[cat].append(bar_data[date][cat])

    return {
        "labels": sorted_dates,
        "datasets": [{"label": cat, "data": datasets[cat]} for cat in categorias]
    }

def get_pie_chart_data():
    """
    Agrega a distribuição dos funcionários (usuários) por categoria:
      - Administrador, Secretaria, Motorista.
    """
    banco = BancoDados()
    usuarios = banco.ler("usuarios", {})
    counts = {"Administrador": 0, "Secretaria": 0, "Motorista": 0}
    for _, u in usuarios.iterrows():
        tipo = u['tipo']  # Acessa o campo 'tipo' pelo nome da coluna
        if tipo in counts:
            counts[tipo] += 1
    return {
        "labels": list(counts.keys()),
        "data": list(counts.values())
    }
