## Visão Geral do Projeto

O sistema implementa três abordagens principais de trading:
1. **Abordagem Principal**: Treina modelo XGBoost uma vez e executa previsões
2. **Abordagem Random Forest**: Treina modelo Random Forest com processamento completo
3. **Abordagem Incremental**: Retreina o modelo diariamente com novos dados

## Licença

A licença deste projeto é Creative Commons Attribution-NonCommercial 4.0 International License. O uso autorizado pela licença exige o crédito aos respectivos autores. Não use para fins comerciais. O uso fora dos termos da licença pode resultar na terminação automática dos direitos concedidos por essa e sujeitar o infrator à responsabilização por violação de direitos autorais, incluindo possíveis ações legais e compensações por danos.

Ao compartilhar ou criar trabalhos derivativos deste, salvo em casos onde direitos autoriais não se aplicam, você deve dar os créditos ao autor e observar algumas exigências.

A licença é explicada em mais detalhes no arquivo LICENSE.md. Obtenha uma cópia em: https://creativecommons.org/licenses/by-nc/4.0/

## Pré-requisitos

Certifique-se de ter instalado:
- Python 3.8+
- Jupyter Notebook
- Bibliotecas necessárias: pandas, numpy, xgboost, scikit-learn, plotly, pickle

## Estrutura do Projeto

```
notebook/
├── data_featuring.ipynb           # Notebook principal de treinamento
├── data_featuring_actions_rf.ipynb # Treinamento Random Forest
├── data_featuring_actions_xb.ipynb # Execução com modelo pré-treinado
├── trader.py                      # Simulador principal
├── trader_retrained.py            # Simulador incremental
├── TradingSimulator.py            # Classe do simulador
├── TradingRelatorio.py            # Gerador de relatórios
└── df_final.parquet               # Arquivo de dados de mercado (entrada)
```

## Passo a Passo de Execução

### 1. Preparação dos Dados

Obtenha um arquivo `.parquet` no formato compatível contendo os dados de mercado que deseja utilizar. O arquivo deve conter:
- Dados históricos de preços das ações
- Volumes de negociação
- Timestamps das operações
- Dados de múltiplos timeframes

**Localização esperada**: Coloque o arquivo `.parquet` no diretório raiz do projeto.

### 2. Execução do Treinamento Principal

Execute o notebook `data_featuring.ipynb`. Este notebook contém:
- **Processamento de dados**: Limpeza e preparação dos dados de entrada
- **Feature engineering**: Criação de variáveis preditivas
- **Treinamento do modelo**: Treina o modelo XGBoost principal
- **Validação**: Avalia a performance do modelo

```bash
# Abra o Jupyter Notebook
jupyter notebook data_featuring.ipynb
```

**Saídas importantes**:
- `df_20_dados_fdate.csv`: Dados intermediários processados
- `xgboost_model.pkl`: Modelo XGBoost treinado
- Métricas de avaliação do modelo

### 3. Preparação dos Dados de Teste

O processo gera dois arquivos importantes:
- `df_20_dados_fdate.csv`: Arquivo intermediário no processo de preparação
- `df_20_dados_fdate_test.csv`: Dados completamente tratados e separados para testes (representa os últimos 10% dos dados)

### 4. Escolha da Estratégia de Trading

#### Opção A: Random Forest (Treinamento Completo)

Execute `data_featuring_actions_rf.ipynb`:
- **Funcionalidade**: Realiza tratamentos completos dos dados e treina um modelo Random Forest do zero
- **Processamento**: Feature engineering completo
- **Modelo**: Random Forest otimizado
- **Entrada**: Usa `df_20_dados_fdate.csv`
- **Saída**: `stock_action_data.csv` com decisões de trading

```bash
jupyter notebook data_featuring_actions_rf.ipynb
```

#### Opção B: XGBoost Pré-treinado (Recomendado)

Execute `data_featuring_actions_xb.ipynb`:
- **Funcionalidade**: Utiliza o modelo XGBoost já treinado em `data_featuring.ipynb`
- **Processamento**: Apenas previsões, sem novo treinamento
- **Entrada**: Usa `df_20_dados_fdate_test.csv`
- **Saída**: `stock_action_data.csv` com decisões de trading

```bash
jupyter notebook data_featuring_actions_xb.ipynb
```

**Nota importante**: Embora possa parecer contraditório treinar com todos os dias de uma vez, o modelo não é retreinado durante o processo de execução, apenas faz previsões. Isso é válido para backtesting.

### 5. Geração de Ações de Trading

Ambos os notebooks da etapa anterior geram o arquivo `stock_action_data.csv` contendo:
- **Ações**: Decisões de compra, venda ou manutenção
- **Preços**: Preços de execução das operações
- **Datas**: Timestamps das operações
- **Quantidades**: Número de ações para cada operação

O arquivo contém as movimentações calculadas para os últimos 10% dos dias do dataset (período de teste).

### 6. Simulação de Trading

#### Simulação Padrão

Execute `trader.py` para simular as estratégias principal ou simplificada:

```bash
python trader.py
```

**Características**:
- **Capital inicial**: Configurável (padrão: $0)
- **Sistema de empréstimo**: Permite alavancagem com $10,000 (também configurável)
- **Estratégia de compra/venda**: Compra 80% do capital disponível, vende toda a posição
- **Quantidade mínima**: Compra no mínimo 5 ações se o capital for insuficiente
- **Taxas**: Inclui corretagem, taxas SEC, TAF
- **Impostos**: Aplica imposto de 25% sobre ganhos de curto prazo
- **Juros**: Aplica juros diários de 0.2% sobre empréstimos
- **Relatórios**: Gera análise detalhada de P&L

**Configurações principais**:
```python
simulator = TradingSimulator(capital_inicial=0)
loan_amount = 10000
fazer_emprestimo = True  # Ativa sistema de empréstimo
```

#### Simulação Incremental

Execute `trader_retrained.py` para a abordagem incremental:

```bash
python trader_retrained.py
```

**Características**:
- **Retreinamento diário**: Modelo é atualizado diariamente
- **Dados crescentes**: Usa dados históricos acumulados
- **Maior realismo**: Simula condições reais de trading
- **Performance**: Mais lenta devido ao retreinamento

### 7. Análise dos Resultados

O sistema gera automaticamente:

#### Relatório Textual
- Resumo financeiro final
- Análise de transações (compras/vendas)
- Custos detalhados (corretagem, impostos, juros)
- Métricas de performance

#### Gráfico P&L Diário
- Visualização da evolução do portfolio
- Arquivo PNG salvo automaticamente
- Gráfico interativo com Plotly

#### Arquivo CSV de P&L
- `pnl_diario.csv`: Histórico detalhado diário
- Dados para análises adicionais

## Configuração Avançada

### TradingSimulator - Parâmetros

```python
simulator = TradingSimulator(
    capital_inicial=0,              # Capital inicial
    imposto_curto=0.25,            # Imposto sobre ganhos de curto prazo
    corretagem_por_acao=0.00,      # Taxa de corretagem por ação
    taxa_sec_r=0.0000229,          # Taxa SEC
    taxa_taf_r=0.000145,           # Taxa TAF
    limite_taf=7.27,               # Limite máximo TAF
    taxa_juros_diaria=0.002,       # Taxa de juros diária (0.2%)
    emprestimo_automatico=True,     # Empréstimo automático quando necessário
    limite_emprestimo=20000,        # Limite máximo de empréstimo
    log_transacoes=True            # Log detalhado de transações
)
```

### Estratégia de Empréstimo

O sistema permite alavancagem através de empréstimos:
- **Valor padrão**: $10,000
- **Taxa de juros**: 0.2% ao dia
- **Pagamento**: Automático ao final do período
- **Limite**: Configurável por instância

### Estratégia de Posicionamento

- **Compras**: Utiliza 80% do capital disponível
- **Vendas**: Vende toda a posição em ações
- **Manutenção**: Mantém posição atual
- **Quantidade mínima**: 5 ações quando capital insuficiente

### Análise de Performance

- **Total de Transações**: Número de operações executadas
- **Preço Médio de Compra/Venda**: Eficiência das operações
- **Evolução Diária**: Tendência do portfolio ao longo do tempo

## Solução de Problemas

### Erros Comuns

1. **Arquivo não encontrado**: Verifique se todos os arquivos CSV estão no diretório correto
2. **Modelo não carregado**: Execute `data_featuring.ipynb` primeiro
3. **Dados insuficientes**: Verifique se o arquivo `.parquet` tem dados suficientes
4. **Erro de dependências**: Instale todas as bibliotecas necessárias

## Extensões Possíveis

- **Múltiplos ativos**: Expandir para portfolio diversificado
- **Stop-loss**: Implementar limites de perda
- **Análise de risco**: Métricas de Sharpe, VaR, etc.

## Aviso

Este sistema foi desenvolvido para fins educacionais e de pesquisa. A negociação automática de ativos envolve riscos significativos. Consulte um profissional.

Feito por Gean de Magalhães de Souza <gean.souza@aluno.cefet-rj.br>

Orientador: Eduardo Bezerra <ebezerra@cefet-rj.br>