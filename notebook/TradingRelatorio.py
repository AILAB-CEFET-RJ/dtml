import numpy as np
import pandas as pd
from pprint import pprint

def obter_relatorio(simulador):
    valor_portfolio = simulador.montante + \
        simulador.quantidade_acoes * simulador.posicoes[-1]['preco']
    lucro_ou_prejuizo = valor_portfolio - simulador.capital_inicial
    total_juros_emprestimos = simulador.calcular_juros_totais()

    relatorio = {
        'capital_inicial': simulador.capital_inicial,
        'final_valor_portfolio': valor_portfolio,
        'valor_portfolio_s_impostos': valor_portfolio + simulador.total_impostos,
        'valor_portfolio_s_impostos_taxas': valor_portfolio + simulador.total_impostos + simulador.total_taxas,
        'quantidade_acoes_restantes': simulador.quantidade_acoes,
        'montante_restante': simulador.montante,
        'lucro_ou_prejuizo': lucro_ou_prejuizo,
        'retorno_percentual': (lucro_ou_prejuizo / simulador.capital_inicial) * 100 if simulador.capital_inicial > 0 else 0,
        'total_corretagem': simulador.total_corretagem,
        'total_taxas': simulador.total_taxas,
        'total_impostos': simulador.total_impostos,
        'total_emprestimos': total_juros_emprestimos,
        'total_juros_emprestimos': total_juros_emprestimos,
        'custo_corretagem_taxas_imposto': simulador.total_corretagem + simulador.total_taxas + simulador.total_impostos,
        'custo_operacional_total': simulador.total_corretagem + simulador.total_taxas + simulador.total_impostos + total_juros_emprestimos,
    }

    pprint(relatorio)

def obter_pnl_diario(simulador):
    df = pd.DataFrame(simulador.posicoes)
    if df.empty:
        return pd.DataFrame()
    df['valor_portfolio_bruto'] = df['valor_portfolio'] + \
        df['despesas_totais']
    df['valor_pos_emp'] = df['valor_portfolio'] - df['montante_devido']

    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')

    daily = df.groupby(df['data'].dt.date,
                       as_index=False).last().reset_index()
    daily.rename(
        columns={'data': 'dia', 'valor_portfolio': 'valor', 'valor_portfolio_bruto': 'valor_b'}, inplace=True)

    daily['pnl'] = daily['valor_pos_emp'].diff().fillna(
        daily['valor_pos_emp'] - simulador.capital_inicial
    )

    daily['pnl_b'] = daily['valor_b'].diff().fillna(
        daily['valor_b'] - simulador.capital_inicial
    )

    # daily['pnl%'] = daily['pnl'] / daily['valor'].shift(1)
    # daily['pnl%'] = daily['pnl%'].fillna(0) * 100

    # daily['dia'] = daily['dia'].dt.date

    print(daily[['dia', 'valor_b', 'valor', 'valor_pos_emp', 'pnl', 'pnl_b']])
