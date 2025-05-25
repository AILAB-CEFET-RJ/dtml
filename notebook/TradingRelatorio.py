import numpy as np
import pandas as pd
from pprint import pprint

def obter_relatorio(simulador):
    valor_portfolio = simulador.quantidade_acoes * \
        simulador.posicoes[-1]['preco']

    preco_acao_final = simulador.posicoes[-1]['preco']
    custo_juros_emprestimos = simulador.calcular_juros_totais()

    custo_corretagem_taxas_impostos = simulador.total_corretagem + \
        simulador.total_taxas + simulador.total_impostos

    saldo_bruto_final = simulador.montante + valor_portfolio
    saldo_de_negociacoes = saldo_bruto_final + \
        custo_juros_emprestimos + custo_corretagem_taxas_impostos
    saldo_liquido_final = saldo_bruto_final - custo_corretagem_taxas_impostos

    lucro_ou_prejuizo_final = saldo_liquido_final - simulador.capital_inicial

    relatorio = {
        'capital_inicial': simulador.capital_inicial,
        'quantidade_acoes_restantes': simulador.quantidade_acoes,
        'preco_acao_final': preco_acao_final,
        'valor_portfolio': valor_portfolio,
        'custo_juros_emprestimos': custo_juros_emprestimos,
        'montante_restante': simulador.montante,
        '  saldo_de_negociacoes': saldo_de_negociacoes,
        '  saldo_bruto_final': saldo_bruto_final,
        'custo_corretagem': simulador.total_corretagem,
        'total_taxas': simulador.total_taxas,
        'total_impostos': simulador.total_impostos,
        'custo_corretagem_taxas_impostos': custo_corretagem_taxas_impostos,
        '  saldo_liquido_final': saldo_liquido_final,
        '  lucro_ou_prejuizo_final': lucro_ou_prejuizo_final,
    }

    pprint(relatorio, sort_dicts=False)

def obter_pnl_diario(simulador):
    df = pd.DataFrame(simulador.posicoes)
    if df.empty:
        return pd.DataFrame()
    df['saldo_bruto'] = df['valor_portfolio'] + \
        df['montante_liquido'] - df['montante_devido']
    df['saldo_liquido'] = df['saldo_bruto'] - \
        df['despesas_totais'] - df['juros_devidos']

    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')

    daily = df.groupby(df['data'].dt.date,
                       as_index=False).last().reset_index()
    daily.rename(
        columns={'data': 'dia'}, inplace=True)

    daily['pnl'] = daily['saldo_liquido'].diff().fillna(
        daily['saldo_liquido'] - simulador.capital_inicial
    )

    daily['pnl_b'] = daily['saldo_bruto'].diff().fillna(
        daily['saldo_bruto'] - simulador.capital_inicial
    )

    # daily['pnl%'] = daily['pnl'] / daily['valor'].shift(1)
    # daily['pnl%'] = daily['pnl%'].fillna(0) * 100

    # daily['dia'] = daily['dia'].dt.date

    print(daily[['dia', 'saldo_bruto', 'saldo_liquido', 'pnl', 'pnl_b']])
