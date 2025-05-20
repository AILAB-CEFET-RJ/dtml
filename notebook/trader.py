from TradingSimulator import TradingSimulator
import TradingRelatorio
import pandas as pd
trade_df = pd.read_csv('stock_action_data.csv')
trade_df['Fdate'] = pd.to_datetime(trade_df['Fdate'])

simulator = TradingSimulator(capital_inicial=0)
loan_amount = 10000
fazer_emprestimo = True

def executar_decisoes(simulator, rows):
    for _, row in day_trades.iterrows():
        acao = row['Action']
        preco = row['Current Price']
        data = row['Fdate']
        quantidade = 20

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
TradingRelatorio.obter_pnl_diario(simulator)
