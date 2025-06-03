from io import StringIO
from TradingSimulator import TradingSimulator
import TradingRelatorio
import pandas as pd
from pprint import pprint

# test_data = '''
# Fdate,Current Price,Action,Quantidade
# 2025-05-22 09:30:00,20.00,compra,5
# 2025-05-23 09:35:00,30.00,venda,3
# 2025-05-24 09:40:00,30.00,manter,NaN
# '''

# trade_df = pd.read_csv(StringIO(test_data), parse_dates=['Fdate'])
trade_df = pd.read_csv('stock_action_data.csv', parse_dates=['Fdate'])
trade_df['Quantidade'] = None

simulator = TradingSimulator(capital_inicial=0)
loan_amount = 1000
fazer_emprestimo = True

def executar_decisoes(simulator, rows):
    for _, row in day_trades.iterrows():
        acao = row['Action']
        preco = row['Current Price']
        data = row['Fdate']
        quantidade = row['Quantidade'] if pd.notna(row['Quantidade']) else 10

        simulator.executar_decisao(
            decisao=acao,
            quantidade=quantidade,
            preco=preco,
            data=data
        )


if fazer_emprestimo:
    first_trade_date = trade_df['Fdate'].min()
    last_trade_date = trade_df['Fdate'].max()
    simulator.registrar_posicao(first_trade_date, 0)
    simulator.tomar_emprestimo(loan_amount, first_trade_date)
    for date, day_trades in trade_df.groupby(trade_df['Fdate'].dt.date):
        executar_decisoes(simulator, day_trades)
    simulator.atualizar_juros_emprestimos(pd.Timestamp(date))
    simulator.pagar_emprestimo(last_trade_date)
    simulator.atualizar_posicao()
else:
    for date, day_trades in trade_df.groupby(trade_df['Fdate'].dt.date):
        executar_decisoes(simulator, day_trades)

simulator.registrar_posicao(
    simulator.posicoes[-1]['data'],
    simulator.posicoes[-1]['preco']
)

# Obter resumo final
TradingRelatorio.obter_relatorio(simulator)

df = TradingRelatorio.obter_pnl_diario(simulator)
fig = TradingRelatorio.gerar_grafico(df)
