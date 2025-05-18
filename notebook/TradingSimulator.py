import pprint
import os

class TradingSimulator:
    def __init__(self, capital_inicial, imposto_curto=0.25,
                 corretagem_por_acao=0.00, taxa_sec_r=0.0000229,
                 taxa_taf_r=0.000145, limite_taf=7.27,
                 taxa_juros_diaria=0.001):
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
        self.taxa_juros_diaria = taxa_juros_diaria
        self.emprestimo_ativo = {}
        self.emprestimos_efetivados = []
        # garantir que logica de emprestimos seja consistente, ou seja, usar um unico atual ou uma lista deles
        # consertar logicas na hora de pagar o emprestimo e na hora de gerar o relatorio

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
            'valor_portfolio': self.montante + self.quantidade_acoes * preco,
            'despesas_totais': self.calcular_juros_totais() + self.total_impostos + self.total_taxas + self.total_corretagem,
            'despesas_emprestimos': self.calcular_juros_totais()
        })

    def _comprar(self, quantidade, preco, data):
        # Calcular custo total considerando comissões
        custo_total = quantidade * preco
        corretagem = quantidade * self.corretagem_por_acao

        # if custo_total + corretagem <= self.montante:

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
        # else:
        #     print(
        #         f'Não foi possível comprar {quantidade} ações a {preco} em {data}.')

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

    def tomar_emprestimo(self, valor, data):
        self.montante += valor
        self.emprestimo_ativo = {
            'valor': valor,
            'data': data
        }

    def pagar_emprestimo(self, data):
        emprestimo = self.emprestimo_ativo
        delta = data - emprestimo['data']
        # Um dia incompleto conta como um dia inteiro
        dias = max(1, int(delta.total_seconds() // 3600 // 24))
        juros = emprestimo['valor'] * self.taxa_juros_diaria * dias
        total_pagamento = emprestimo['valor'] + juros
        self._trocar_emprestivo_ativo(total_pagamento, juros)

    def _trocar_emprestivo_ativo(self, valor, juros):
        self.montante -= valor
        self.emprestimo_ativo['juros'] = juros
        self.emprestimos_efetivados.append(self.emprestimo_ativo)
        self.emprestimo_ativo = {}

    def calcular_juros_totais(self):
        return sum(e['juros']
                   for e in self.emprestimos_efetivados)
