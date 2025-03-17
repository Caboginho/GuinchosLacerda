# routes_financeiro.py
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from classes.administrador import Administrador
from classes.financeiro import get_bar_chart_data, get_pie_chart_data
import pandas as pd
from datetime import datetime

financeiro_bp = Blueprint('financeiro_bp', __name__)

@financeiro_bp.before_request
def verificar_permissao():
    if 'tipo' not in session or session['tipo'] != 'Administrador':
        return redirect(url_for('main_bp.login'))

@financeiro_bp.route('/dashboard')
def dashboard():
    try:
        admin = Administrador(
            id=session['usuario_id'],
            nome=session['nome'],
            email=session['email'],
            senha=None,
            cnh=session.get('cnh'),
            celular=session['celular'],
            justificativa=session['justificativa']
        )
        
        # Busca dados financeiros
        transacoes = admin.ler_registros('transacoes')
        servicos = admin.ler_registros('servicos_guincho')
        
        # Processa dados para o dashboard
        dados = {
            'transacoes': process_transacoes(transacoes) if not transacoes.empty else [],
            'servicos': process_servicos(servicos) if not servicos.empty else [],
            'total_receitas': 0,
            'total_servicos': 0,
            'grafico_mensal': get_dados_mensais(transacoes) if not transacoes.empty else [],
            'grafico_tipos': get_dados_tipos(servicos) if not servicos.empty else {'labels': [], 'data': []}
        }
        
        # Calcula totais
        if not transacoes.empty:
            dados['total_receitas'] = float(transacoes['valor'].sum())
        if not servicos.empty:
            dados['total_servicos'] = len(servicos)
        
        return render_template('financeiro.html', dados=dados)
        
    except Exception as e:
        print(f"Erro ao carregar dashboard financeiro: {e}")
        return render_template('financeiro.html', 
                             dados={'transacoes': [], 'servicos': [], 
                                   'total_receitas': 0, 'total_servicos': 0,
                                   'grafico_mensal': [], 'grafico_tipos': {'labels': [], 'data': []}},
                             erro="Erro ao carregar dados financeiros")

def process_transacoes(df):
    """Processa dados das transações"""
    if df.empty:
        return []
    return df.to_dict('records')

def process_servicos(df):
    """Processa dados dos serviços"""
    if df.empty:
        return []
    return df.to_dict('records')

def get_dados_mensais(df):
    """Agrupa dados por mês"""
    if df.empty:
        return []
    df['data'] = pd.to_datetime(df['data'])
    mensal = df.groupby(df['data'].dt.strftime('%Y-%m'))['valor'].sum()
    return [{'mes': mes, 'valor': float(valor)} for mes, valor in mensal.items()]

def get_dados_tipos(df):
    """Agrupa serviços por tipo"""
    if df.empty:
        return {'labels': [], 'data': []}
    tipos = df['tipo_solicitacao'].value_counts()
    return {
        'labels': tipos.index.tolist(),
        'data': tipos.values.tolist()
    }

@financeiro_bp.route('/financeiro_pg')
def financeiro():
    return render_template('financeiro.html')

@financeiro_bp.route('/financeiro/dados')
def financeiro_dados():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    barChart = get_bar_chart_data(data_inicio, data_fim)
    pieChart = get_pie_chart_data()
    return jsonify({"barChart": barChart, "pieChart": pieChart})
