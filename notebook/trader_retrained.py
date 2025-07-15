from io import StringIO
from TradingSimulator import TradingSimulator
import TradingRelatorio
import pandas as pd
from pprint import pprint
import warnings
import pickle
import numpy as np
warnings.filterwarnings("ignore")

def predict_values(df, xgb_model):
    df_features = df[features].copy()
    preds = xgb_model.predict(df_features)
    if preds.ndim == 2 and preds.shape[1] == len(target_variables):
        for i, col in enumerate(target_variables):
            df[f'{col}'] = preds[:, i]
    else:
        print('Unexpected prediction shape:', preds.shape)
    return df, features, target_variables

def calculate_vwap(df, price_columns, volume_columns, vwap_col_name):
    vwap_result = pd.DataFrame()
    for p, v in zip(price_columns, volume_columns):
        vwap_result[f'{p}_{v}'] = df[p] * df[v]
    total_value = vwap_result.sum(axis=1)
    total_volume = df[volume_columns].sum(axis=1)
    df[vwap_col_name] = total_value / total_volume
    return df

def retrain_xgboost_model(X_train, y_train, previous_model, params=None, num_boost_round=30):
    import xgboost as xgb
    if params is None:
        params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'mae',
            'tree_method': 'auto',
            'verbosity': 1,
            'alpha': 1.8727005942368125,
            'colsample_bytree': 0.9753571532049581,
            'gamma': 2.1959818254342154,
            'reg_lambda': 2.993292420985183,
            'learning_rate': 0.039643541684062936,
            'max_depth': 5,
            'min_child_weight': 7,
            'subsample': 0.7296244459829335,
            'random_state': 42
        }
    model = xgb.XGBRegressor(**params, n_estimators=num_boost_round)
    model.fit(X_train, y_train, xgb_model=previous_model.get_booster())
    return model

# Prepare for daily retraining and trading

df_test = pd.read_csv('df_20_dados_fdate_test.csv', parse_dates=["Fdate"], index_col="Fdate")
df_test['Fdate_date'] = df_test.index.to_series().dt.date
unique_dates = sorted(df_test['Fdate_date'].unique())

with open('xgboost_model.pkl', 'rb') as f:
    xgb_model = pickle.load(f)

results = pd.read_csv('results_xb.csv', index_col=0)
price_columns = [idx for idx in results.index if ('Pa_' in idx or 'Pb_' in idx)]
avg_mae_price = results.loc[price_columns].mean()["MAE"]
threshold = 0.005

simulator = TradingSimulator(capital_inicial=0)
loan_amount = 10000
fazer_emprestimo_inicial = True

if fazer_emprestimo_inicial:
    first_trade_date = df_test.index.min()
    last_trade_date = df_test.index.max()
    simulator.registrar_posicao(first_trade_date, 0)
    simulator.tomar_emprestimo(loan_amount, first_trade_date)

for i in range(len(unique_dates)):
    previous_day = unique_dates[i-1]
    current_day = unique_dates[i]

    train_data = df_test[df_test['Fdate_date'] == previous_day]
    test_data = df_test[df_test['Fdate_date'] == current_day]
    if len(test_data) == 0 or len(train_data) == 0:
        print("!!!!!!!!!!")
        continue

    target_variables = [col for col in train_data.columns if len(col) == 4]
    features = [col for col in train_data.columns if col not in target_variables and col != 'Fdate_date']
    X_train = train_data[features]
    y_train = train_data[target_variables]

    xgb_model = retrain_xgboost_model(X_train, y_train, xgb_model)
    test_data, _, _ = predict_values(test_data, xgb_model)

    feature_price_columns = [c for c in features if 'Pa_' in c] + [c for c in features if 'Pb_' in c]
    feature_volume_columns = [c for c in features if 'Sa_' in c] + [c for c in features if 'Sb_' in c]
    target_price_columns = [c for c in target_variables if 'Pa_' in c] + [c for c in target_variables if 'Pb_' in c]

    calculate_vwap(test_data, feature_price_columns, feature_volume_columns, 'VWAP_features')
    if target_price_columns:
        test_data['VWAP_targets'] = test_data[target_price_columns].mean(axis=1)
    else:
        test_data['VWAP_targets'] = None

    test_data['Action'] = 'manter'
    if 'VWAP_targets' in test_data.columns and test_data['VWAP_targets'].notna().any():
        vwap_diff = (test_data['VWAP_targets'] - test_data['VWAP_features'])
        threshold_value = (threshold * test_data['VWAP_features']) + avg_mae_price
        test_data.loc[vwap_diff > threshold_value, 'Action'] = 'compra'
        test_data.loc[vwap_diff < -threshold_value, 'Action'] = 'venda'

    test_data['Quantidade'] = None
    for _, row in test_data.iterrows():
        acao = row['Action']
        preco = row['VWAP_features']
        data = row.name
        if acao == 'compra':
            orcamento_atual = simulator.montante
            quantidade = int((orcamento_atual * 0.80) // preco)
            if quantidade < 1:
                quantidade = 5
        elif acao == 'venda':
            quantidade = simulator.quantidade_acoes
        else:
            quantidade = row['Quantidade'] if pd.notna(row['Quantidade']) else 10
        simulator.executar_decisao(
            decisao=acao,
            quantidade=quantidade,
            preco=preco,
            data=data
        )
    simulator.atualizar_juros_emprestimos(pd.Timestamp(row.name))

simulator.pagar_emprestimo(last_trade_date)
simulator.atualizar_posicao()
simulator.registrar_posicao(
    simulator.posicoes[-1]['data'],
    simulator.posicoes[-1]['preco']
)
TradingRelatorio.obter_relatorio(simulator)
df = TradingRelatorio.obter_pnl_diario(simulator)
fig = TradingRelatorio.gerar_grafico(df)

# #######################

total_emprestimos = sum(e['valor'] for e in simulator.emprestimos)
num_emprestimos = len(simulator.emprestimos)
valor_medio_emprestimo = total_emprestimos / num_emprestimos if num_emprestimos > 0 else 0

print(f"Total emprestado: {total_emprestimos}")
print(f"Número de empréstimos: {num_emprestimos}")
print(f"Valor médio dos empréstimos: {valor_medio_emprestimo}")

# # Additional detailed analysis for retraining
# print("\n=== DETAILED RETRAINING ANALYSIS ===")

# # Show examples of buy decisions
# buy_decisions = trade_df[trade_df['Action'] == 'compra']
# if len(buy_decisions) > 0:
#     print(f"\nBUY DECISIONS ({len(buy_decisions)} total):")
#     print(buy_decisions[['Fdate', 'Current Price', 'Predicted Price', 'Price Change %']].head())
#     print(f"Average expected gain from buy decisions: {buy_decisions['Price Change %'].mean():.4f}%")

# # Show examples of sell decisions
# sell_decisions = trade_df[trade_df['Action'] == 'venda']
# if len(sell_decisions) > 0:
#     print(f"\nSELL DECISIONS ({len(sell_decisions)} total):")
#     print(sell_decisions[['Fdate', 'Current Price', 'Predicted Price', 'Price Change %']].head())
#     print(f"Average expected change from sell decisions: {sell_decisions['Price Change %'].mean():.4f}%")

# # Performance metrics
# print(f"\nRetraining algorithm configuration:")
# print(f"- Model used: xgboost_model.pkl")
# print(f"- Test dataset: df_20_dados_fdate_test.csv ({len(df_test)} records)")
# print(f"- Threshold applied: {threshold} ({threshold*100}%)")
# print(f"- Average MAE from training: {avg_mae_price:.6f}")
# print(f"- Actions generated: {len(trade_df)}")
# print(f"- Date range: {trade_df['Fdate'].min()} to {trade_df['Fdate'].max()}")

# print(f"\nFinal trading results saved to: pnl_diario.csv")
# print(f"Action decisions saved to: {output_filename}")
