import pprint
import os

class TradingSimulator:
    def __init__(self, capital_inicial, imposto_curto=0.25,
                 corretagem_por_acao=0.00, taxa_sec_r=0.0000229,
                 taxa_taf_r=0.000145, limite_taf=7.27,
                 taxa_juros_diaria=0.002, emprestimo_automatico=True,
                 permitir_montante_negativo=False, log_transacoes=True,
                 pagar_emprestimo_automaticamente=False,
                 limite_emprestimo=20000):
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
        self.emprestimo_ativo_idx = -1
        self.emprestimos = []
        self.emprestimo_automatico = emprestimo_automatico
        self.permitir_montante_negativo = permitir_montante_negativo
        self.log_transacoes = log_transacoes
        self.pagar_emprestimo_automaticamente = pagar_emprestimo_automaticamente
        self.limite_emprestimo = limite_emprestimo

        print("Configurações do TradingSimulator:")
        print(f"  capital_inicial: {self.capital_inicial}")
        print(f"  imposto_curto: {self.imposto_curto}")
        print(f"  corretagem_por_acao: {self.corretagem_por_acao}")
        print(f"  taxa_sec_r: {self.taxa_sec_r}")
        print(f"  taxa_taf_r: {self.taxa_taf_r}")
        print(f"  limite_taf: {self.limite_taf}")
        print(f"  taxa_juros_diaria: {self.taxa_juros_diaria}")
        print(f"  emprestimo_automatico: {self.emprestimo_automatico}")
        print(f"  permitir_montante_negativo: {self.permitir_montante_negativo}")
        print(f"  log_transacoes: {self.log_transacoes}")
        print(f"  pagar_emprestimo_automaticamente: {self.pagar_emprestimo_automaticamente}")
        print(f"  limite_emprestimo: {self.limite_emprestimo}")

    def executar_decisao(self, decisao, quantidade, preco, data):
        if decisao == 'compra':
            self._comprar(quantidade, preco, data)
        elif decisao == 'venda':
            self._vender(quantidade, preco, data)

        self.atualizar_juros_emprestimos(data)
        self.registrar_posicao(data, preco)

    def registrar_posicao(self, data, preco):
        despesas_totais = self.total_impostos + self.total_taxas + self.total_corretagem
        self.posicoes.append({
            'data': data,
            'montante_final': self.montante - despesas_totais,
            'montante_liquido': self.montante,
            'quantidade_acoes': self.quantidade_acoes,
            'preco': preco,
            'valor_portfolio': self.quantidade_acoes * preco,
            'despesas_totais': despesas_totais,
            'juros_emprestimos': self.calcular_juros_totais(),
            'juros_devidos': self.calcular_juros_devidos(),
            'montante_devido': self.calcular_montante_devido()
        })

    def atualizar_posicao(self):
        if not self.posicoes:
            return

        ultimo_preco = self.posicoes[-1]['preco']
        ultimo_data = self.posicoes[-1]['data']
        self.registrar_posicao(ultimo_data, ultimo_preco)

    def _comprar(self, quantidade, preco, data):
        # Calcular custo total considerando comissões
        custo_total = quantidade * preco
        corretagem = quantidade * self.corretagem_por_acao
        valor_necessario = custo_total + corretagem

        # Se não houver dinheiro suficiente, tomar empréstimo automaticamente se permitido
        if self.montante < valor_necessario:
            if self.permitir_montante_negativo:
                pass
            elif self.emprestimo_automatico:
                valor_emprestimo = valor_necessario - self.montante
                if valor_emprestimo <= 0:
                    # print(f'Compra cancelada: valor de empréstimo não é suficiente. ')
                    return
                if not self.tomar_emprestimo(valor_emprestimo, data):
                    # print(f'Compra cancelada: não foi possível obter empréstimo necessário.')
                    return
            else:
                print(f'Saldo insuficiente e empréstimo automático desativado. Necessário: {valor_necessario:.2f}, disponível: {self.montante:.2f}.')
                return

        self.montante -= custo_total
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
        if self.log_transacoes:
            print(f'Compra: {quantidade} ações a {preco:.2f} cada (total: {custo_total + corretagem:.2f}) em {data}.')

    def _vender(self, quantidade, preco, data):
        if quantidade == 0:
            # Ignorar transações de venda com quantidade zero
            return
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
            self.montante += valor_venda
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
                'total_imposto': imposto
            })
            if self.log_transacoes:
                print(f'Venda: {quantidade} ações a {preco:.2f} cada (total: {valor_venda - corretagem:.2f}) em {data}.')
            # Lógica para pagar empréstimo automaticamente
            if self.pagar_emprestimo_automaticamente:
                for emprestimo in self.emprestimos:
                    if not emprestimo['pago']:
                        self.atualizar_juros_emprestimos(data)
                        total_pagamento = emprestimo['valor'] + emprestimo.get('juros', 0)
                        if self.montante >= total_pagamento:
                            self.pagar_emprestimo(data)
                            break
        else:
            raise ValueError('Quantidade a vender é maior que a quantidade em carteira.')

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
        # Checa se o limite de empréstimo será ultrapassado
        if self.limite_emprestimo is not None:
            total_devido_apos = self.calcular_montante_devido() + self.calcular_juros_devidos() + valor
            if total_devido_apos > self.limite_emprestimo:
                print(f"Limite de empréstimo atingido. Não é possível tomar mais empréstimos. (Limite: {self.limite_emprestimo:.2f}, Devido após: {total_devido_apos:.2f})")
                return False
        self.montante += valor
        novo_emprestimo = {
            'id': os.urandom(8).hex(),
            'valor': valor,
            'data': data,
            'data_pgto': None,
            'pago': False
        }
        self.emprestimos.append(novo_emprestimo)
        self.emprestimo_ativo_idx = len(self.emprestimos) - 1
        print(f'Tomado empréstimo {novo_emprestimo["id"]} no valor de {valor:.2f} em {data}.')
        return True

    # def _encontrar_emprestimo(self, id):
        # for index, emprestimo in enumerate(self.emprestimos):
        #     if emprestimo['id'] == id:
        #         return emprestimo, index
        # raise ValueError(f"Empréstimo com id {id} não encontrado.")

    def atualizar_juros_emprestimos(self, data):
        for emprestimo in self.emprestimos:
            if not emprestimo['pago']:
                delta = data - emprestimo.get('data')
                # Um dia incompleto conta como um dia inteiro
                dias = max(1, int(delta.total_seconds() // 3600 // 24))
                # Juros compostos
                juros = emprestimo['valor'] * \
                    ((1 + self.taxa_juros_diaria) ** dias - 1)
                emprestimo['juros'] = juros

    def pagar_emprestimo(self, data):
        self.atualizar_juros_emprestimos(data)
        for idx, emprestimo in enumerate(self.emprestimos):
            if not emprestimo['pago']:
                juros = emprestimo.get('juros', 0)
                total_pagamento = emprestimo['valor'] + juros
                self.montante -= total_pagamento
                self.emprestimos[idx]['pago'] = True
                self.emprestimos[idx]['juros'] = juros
                self.emprestimos[idx]['data_pgto'] = data
                print(
                    f'Pago empréstimo {emprestimo["id"]} no valor de {total_pagamento:.2f} (juros pagos: {juros:.2f}) em {data}.')
        self.emprestimo_ativo_idx = -1

    def _trocar_emprestimo_ativo(self, juros, data):
        id = self.emprestimo_ativo_idx
        self.emprestimos[id]['pago'] = True
        self.emprestimos[id]['juros'] = juros
        self.emprestimos[id]['data_pgto'] = data
        self.emprestimo_ativo_id = -1

    def calcular_juros_totais(self):
        return sum(e['juros']
                   for e in self.emprestimos)

    def calcular_juros_devidos(self):
        return sum(e['juros']
                   for e in self.emprestimos if not e['pago'])

    def calcular_montante_devido(self):
        return sum(e['valor']
                   for e in self.emprestimos if not e['pago'])
