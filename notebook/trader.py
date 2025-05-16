from TradingSimulator import TradingSimulator
import pandas as pd
trade_df = pd.read_csv('stock_action_data.csv', parse_dates=['Fdate'])

# Inicializar com $10,000 de capital inicial
simulator = TradingSimulator(capital_inicial=10000)

# Processar decisões
for idx, row in trade_df.iterrows():
    acao = row['Action']
    preco = row['Current Price']
    data = row['Fdate']
    quantidade = 5  # 5 ações por transação

    simulator.executar_decisao(
        decisao=acao,
        quantidade=quantidade,
        preco=preco,
        data=data
    )

# Obter resumo final
resumo = simulator.obter_relatorio(trade_df['Current Price'].iloc[-1])
print(simulator.obter_pnl_diario())
print(resumo)
