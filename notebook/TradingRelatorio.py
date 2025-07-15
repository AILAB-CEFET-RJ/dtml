import numpy as np
import pandas as pd
from pprint import pprint
import plotly.graph_objects as go

def obter_relatorio(simulador):
    valor_portfolio = simulador.quantidade_acoes * \
        simulador.posicoes[-1]['preco']

    preco_acao_final = simulador.posicoes[-1]['preco']
    custo_juros_emprestimos = simulador.calcular_juros_totais()

    custo_corretagem_taxas_impostos = simulador.total_corretagem + \
        simulador.total_taxas + simulador.total_impostos

    saldo_bruto_final = simulador.montante + valor_portfolio
    saldo_liquido_final = saldo_bruto_final - custo_corretagem_taxas_impostos

    lucro_ou_prejuizo_final = saldo_liquido_final - simulador.capital_inicial

    relatorio = {
        'capital_inicial': simulador.capital_inicial,
        'quantidade_acoes_restantes': simulador.quantidade_acoes,
        'preco_acao_final': preco_acao_final,
        'valor_portfolio': valor_portfolio,
        'custo_juros_emprestimos': custo_juros_emprestimos,
        'montante_restante': simulador.montante,
        '  saldo_bruto_final': saldo_bruto_final,
        'custo_corretagem': simulador.total_corretagem,
        'total_taxas': simulador.total_taxas,
        'total_impostos': simulador.total_impostos,
        'custo_corretagem_taxas_impostos': custo_corretagem_taxas_impostos,
        '  saldo_liquido_final': saldo_liquido_final,
        '  lucro_ou_prejuizo_final': lucro_ou_prejuizo_final,
    }

    pprint(relatorio, sort_dicts=False)


# precisa de refatoração
def obter_dados_indice(simulador):
    gspc = pd.read_csv('GSPC_historical_data.csv', parse_dates=['Date'])
    gspc.rename(
        columns={'Date': 'dia', "('Close', '^GSPC')": 'sp500'}, inplace=True)
    return gspc

def obter_pnl_diario(simulador):
    df = pd.DataFrame(simulador.posicoes)
    if df.empty:
        return pd.DataFrame()
    df['bruto'] = df['valor_portfolio'] + \
        df['montante_liquido'] - df['montante_devido']
    df['liquido'] = df['bruto'] - \
        df['despesas_totais'] - df['juros_devidos']

    df = df.sort_values('data')

    daily = df.groupby(df['data'].dt.date,
                       as_index=False).last().reset_index()

    daily['data'] = pd.to_datetime(daily['data']).dt.normalize()
    daily.rename(
        columns={'data': 'dia'}, inplace=True)

    daily['pnl'] = daily['liquido'].diff().fillna(
        daily['liquido'] - simulador.capital_inicial
    )

    daily['pnl%'] = (daily['pnl'] / daily['liquido'].shift(1)) * 100

    daily['pnl_b'] = daily['bruto'].diff().fillna(
        daily['bruto'] - simulador.capital_inicial
    )

    gspc = obter_dados_indice(simulador)
    daily = pd.merge(daily, gspc, on='dia', how='left')

    daily['pnl%'] = (daily['pnl'] / daily['liquido'].shift(1)) * 100
    sinal_anterior = np.sign(daily['liquido'].shift(1))
    sinal_atual = np.sign(daily['liquido'])
    mudanca_sinal = sinal_anterior != sinal_atual
    daily.loc[mudanca_sinal, 'pnl%'] = -1

    daily['sp500%'] = daily['sp500'].pct_change() * 100
    daily['sp500%'].fillna(0, inplace=True)

    df = daily[['dia', 'bruto', 'liquido', 'pnl',
                'pnl_b', 'pnl%', 'sp500', 'sp500%']].copy()
    pprint(df, sort_dicts=False)
    return df

def gerar_grafico(df):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['dia'], y=df['pnl%'],
        mode='lines+markers',
        name='pnl%',
        line=dict(color='#1FB8CD'),
        cliponaxis=False
    ))
    fig.add_trace(go.Scatter(
        x=df['dia'], y=df['sp500%'],
        mode='lines+markers',
        name='sp500%',
        line=dict(color='#FFC185'),
        cliponaxis=False
    ))

    fig.update_layout(
        title='pnl% vs sp500%',
        xaxis_title='Dia',
        yaxis_title='Valor.',
        legend=dict(orientation='h', yanchor='bottom',
                    y=1.05, xanchor='center', x=0.5)
    )
    fig.update_xaxes(tickvals=df['dia'], tickangle=0)
    fig.update_yaxes(tickformat='.2f')

    fig.write_image('pnl_sp500.png')
