import numpy as np
import pandas as pd
import os

class TradingSimulator:
    def __init__(self, capital_inicial, imposto_curto=0,
                 corretagem_por_acao=0.00, taxa_sec_r=0.0000229,
                 taxa_taf_r=0.000145, limite_taf=7.27):
        self.capital_inicial = capital_inicial
        self.montante = capital_inicial
        self.quantidade_acoes = 0
        self.imposto_curto = imposto_curto
        self.corretagem_por_acao = corretagem_por_acao
        self.taxa_sec_r = taxa_sec_r
        self.taxa_taf_r = taxa_taf_r
        self.limite_taf = limite_taf
        self.transacoes = []
        self.posicoes = []
        self.total_corretagem = 0
        self.total_taxas = 0
        self.total_impostos = 0

    def executar_decisao(self, decisao, quantidade, preco, data):
        if decisao == 'compra':
            self._comprar(quantidade, preco, data)
        elif decisao == 'venda':
            self._vender(quantidade, preco, data)

        # Registrar estado atual
        self.posicoes.append({
            'data': data,
            'montante': self.montante,
            'quantidade_acoes': self.quantidade_acoes,
            'preco': preco,
            'valor_portfolio': self.montante + self.quantidade_acoes * preco
        })
        # print('.', sep='')

    def _comprar(self, quantidade, preco, data):
        # Calcular custo total considerando comissões
        custo_total = quantidade * preco
        corretagem = quantidade * self.corretagem_por_acao

        if custo_total + corretagem <= self.montante:

            self.montante -= (custo_total + corretagem)
            self.quantidade_acoes += quantidade
            self.total_corretagem += corretagem

            self.transacoes.append({
                'data': data,
                'tipo': 'compra',
                'quantidade': quantidade,
                'preco': preco,
                'corretagem': corretagem,
                'total': custo_total + corretagem
            })
        else:
            print(
                f'Não foi possível comprar {quantidade} ações a {preco} em {data}.')

    def _vender(self, quantidade, preco, data):
        if quantidade <= self.quantidade_acoes:
            # Calcular receita e taxas
            valor_venda = quantidade * preco
            corretagem = quantidade * self.corretagem_por_acao

            # Calcular taxas SEC e TAF
            taxa_sec_aplicada = valor_venda * self.taxa_sec_r
            taxa_taf_aplicada = min(
                quantidade * self.taxa_taf_r, self.limite_taf)

            # Simplificação para imposto (na prática precisaria rastrear cada lote)
            # Aqui consideramos que todos os ganhos são de curto prazo
            custo_base = self._calcular_custo_base(quantidade)
            base_calculo = valor_venda - custo_base
            imposto = max(0, base_calculo * self.imposto_curto)

            # Atualizar posição e caixa
            total_taxas = taxa_sec_aplicada + taxa_taf_aplicada
            receita_real = valor_venda - corretagem - total_taxas - imposto
            self.montante += receita_real
            self.quantidade_acoes -= quantidade

            # Atualizar totais
            self.total_corretagem += corretagem
            self.total_taxas += total_taxas
            self.total_impostos += imposto

            self.transacoes.append({
                'data': data,
                'tipo': 'venda',
                'quantidade': quantidade,
                'preco': preco,
                'corretagem': corretagem,
                'taxa_sec_aplicada': taxa_sec_aplicada,
                'taxa_taf_aplicada': taxa_taf_aplicada,
                'total_imposto': imposto,
                'receita_real': receita_real
            })

    def _calcular_custo_base(self, quantidade):
        # Método simplificado que retorna apenas o preço médio da compra por ação - na implementação real seria necessário
        # rastrear cada compra individualmente (FIFO, LIFO ou específica)
        # Aqui usamos um preço médio dos ativos em carteira
        if not self.transacoes:
            return 0

        compras = [t for t in self.transacoes if t['tipo'] == 'compra']
        if not compras:
            return 0

        custo_quantidade_acoes = sum(t['quantidade'] for t in compras)
        custo_total = sum(t['quantidade'] * t['preco'] for t in compras)

        avg_cost = custo_total / custo_quantidade_acoes if custo_quantidade_acoes > 0 else 0
        return quantidade * avg_cost

    def obter_relatorio(self, final_preco):
        valor_portfolio = self.montante + self.quantidade_acoes * final_preco
        lucro_ou_prejuizo = valor_portfolio - self.capital_inicial
        return {
            'capital_inicial': self.capital_inicial,
            'final_valor_portfolio': valor_portfolio,
            'valor_portfolio_s_impostos': valor_portfolio + self.total_impostos,
            'valor_portfolio_s_impostos_taxas': valor_portfolio + self.total_impostos + self.total_taxas,
            'quantidade_acoes_restantes': self.quantidade_acoes,
            'montante_restante': self.montante,
            'lucro_ou_prejuizo': lucro_ou_prejuizo,
            'retorno_percentual': (lucro_ou_prejuizo / self.capital_inicial) * 100 if self.capital_inicial > 0 else 0,
            'total_corretagem': self.total_corretagem,
            'total_taxas': self.total_taxas,
            'total_impostos': self.total_impostos,
            'custo_operacional_total': self.total_corretagem + self.total_taxas + self.total_impostos
        }

    def obter_pnl_diario(self):
        df = pd.DataFrame(self.posicoes)
        if df.empty:
            return pd.DataFrame(columns=['data', 'valor_portfolio', 'pnl', 'pnl_pct'])

        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')

        daily = df.groupby(df['data'].dt.date,
                           as_index=False).last().reset_index()
        daily.rename(
            columns={'data': 'dia', 'valor_portfolio': 'valor'}, inplace=True)

        daily['pnl'] = daily['valor'].diff().fillna(
            daily['valor'] - self.capital_inicial)
        daily['pnl_pct'] = (daily['pnl'] / self.capital_inicial) * 100

        return daily[['dia', 'valor', 'pnl', 'pnl_pct']]
