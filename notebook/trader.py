from TradingSimulator import TradingSimulator
import TradingRelatorio
import pandas as pd
trade_df = pd.read_csv('stock_action_data.csv', parse_dates=['Fdate'])

simulator = TradingSimulator(capital_inicial=10000)
loan_amount = 10000
fazer_emprestimo = False

def executar_decisoes(simulator, rows):
    for _, row in day_trades.iterrows():
        acao = row['Action']
        preco = row['Current Price']
        data = row['Fdate']
        quantidade = 5

        simulator.executar_decisao(
            decisao=acao,
            quantidade=quantidade,
            preco=preco,
            data=data
        )

def executar_decisao_nula(simulator, preco):
    simulator.executar_decisao(
        decisao='manter',
        quantidade=0,
        preco=preco,
        data=None
    )


if fazer_emprestimo:
    for date, day_trades in trade_df.groupby(trade_df['Fdate'].dt.date):
        simulator.tomar_emprestimo(loan_amount, date)
        executar_decisoes(simulator, day_trades)
        simulator.pagar_emprestimo(date)
else:
    for date, day_trades in trade_df.groupby(trade_df['Fdate'].dt.date):
        executar_decisoes(simulator, day_trades)

executar_decisao_nula(simulator, trade_df['Current Price'].iloc[-1])

# Obter resumo final
resumo = TradingRelatorio.obter_relatorio(simulator)
print(TradingRelatorio.obter_pnl_diario(simulator))
print(resumo)
