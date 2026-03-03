import json
from bases import carregabases
import csv
from datetime import datetime

# Configuração do arquivo de log
log_file = open(f'debug_hpb_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w', encoding='utf-8')

def write_log(mensagem, nivel=0):
    indent = "  " * nivel
    linha = f"{indent}{mensagem}"
    print(linha)  # Ainda mostra no console
    log_file.write(linha + "\n")
    log_file.flush()  # Força escrita imediata

write_log("=" * 80)
write_log("DEBUG OBRA HPB - ANÁLISE DETALHADA")
write_log(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
write_log("=" * 80)

# Carrega bases existentes (evita consultas desnecessárias)
baseItens = carregabases.itensContratos()
dadosPrev = json.load(open('dadosPrevision.json', mode='r', encoding='utf-8-sig'))
evoProjetos = json.load(open('dadosEvoObra.json', mode='r', encoding='utf-8-sig'))
orcObras = json.load(open('baseOrc.json', encoding='utf-8-sig'))

# Ajuste dos códigos 06.06 para 06.006
codAjustados = {}
for obra in list(dadosPrev.keys()):
    dicApropNovo = {}
    dicAprAntigo = dadosPrev[obra]
    for codAConferir in list(dicAprAntigo.keys()):
        valorCorreto = dicAprAntigo[codAConferir]
        if codAConferir[0:5] == '06.06':
            codAConferir = '06.006'+codAConferir[6:]
        dicApropNovo[codAConferir] = valorCorreto
    codAjustados[obra] = dicApropNovo

dadosPrev = dict(codAjustados)

def log_detalhado(mensagem, nivel=0):
    write_log(mensagem, nivel)

def buscaEF(obra, codEAP):
    dadosEAPObra = dadosPrev[obra]

    def buscar_valor(dados, chave):
        def filhos_diretos(chave_base):
            prefixo = chave_base + '.'
            return {
                k: v for k, v in dados.items()
                if k.startswith(prefixo) and k.count('.') == chave_base.count('.') + 1
            }

        def subir_nivel(chave):
            partes = chave.split('.')
            if len(partes) == 1:
                return None
            return '.'.join(partes[:-1])
        
        # Etapa 1: busca direta
        valor = dados.get(chave)
        if valor is not None and valor != 0:
            log_detalhado(f"Encontrado valor direto para {chave}: {valor}", 2)
            return {chave: valor}

        # Etapa 2: busca filhos diretos
        filhos = filhos_diretos(chave)
        nao_zero = {k: v for k, v in filhos.items() if v != 0}
        if nao_zero:
            log_detalhado(f"Encontrados filhos para {chave}: {nao_zero}", 2)
            return nao_zero

        # Etapa 3: sobe para pais
        pai = subir_nivel(chave)
        while pai:
            valor = dados.get(pai)
            if valor is not None and valor != 0:
                log_detalhado(f"Encontrado valor no pai {pai} para {chave}: {valor}", 2)
                return {pai: valor}
            pai = subir_nivel(pai)

        log_detalhado(f"Nenhum valor encontrado para {chave}, retornando 0", 2)
        return {chave: 0}
    
    return buscar_valor(dadosEAPObra, codEAP)

def calculaEf(obra, dicEap):
    log_detalhado(f"Calculando EF para obra {obra} com EAPs: {list(dicEap.keys())}", 1)
    
    pesoTotal = 0
    evolucao = 0

    for k in list(dicEap.keys()):
        try:
            peso = orcObras[obra][k]['peso']
            pesoTotal += peso
            log_detalhado(f"EAP {k}: peso={peso}", 2)
        except KeyError:
            log_detalhado(f"EAP {k} não encontrado no orçamento", 2)
    
    for k in list(dicEap.keys()):
        try:
            peso = orcObras[obra][k]['peso']
            peso_ponderado = (peso/pesoTotal) * dicEap[k]
            evolucao += peso_ponderado
            log_detalhado(f"EAP {k}: evolucao={dicEap[k]}, peso={peso}, contribuicao={peso_ponderado}", 2)
        except (KeyError, ZeroDivisionError):
            log_detalhado(f"Erro no cálculo para EAP {k}", 2)
    
    resultado = round(evolucao, 4)
    log_detalhado(f"Resultado final EF: {resultado}", 1)
    return resultado

# Funções de cálculo específicas
def fundInfraSupra(obra, dadosPrev):
    log_detalhado(f"Calculando fundInfraSupra para obra {obra}", 1)
    
    codigosEapEquivalentes = ['06', '07', '08', '09']
    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)
        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]
            log_detalhado(f"Adicionado {k}: {chaves[k]}", 2)

    return calculaEf(obra, dicGeralDeEvolucao)

def srvFachada(obra, dadosPrev):
    log_detalhado(f"Calculando srvFachada para obra {obra}", 1)
    
    codigosEapEquivalentes = ['19.001', '19.002', '19.006']
    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)
        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return calculaEf(obra, dicGeralDeEvolucao)

def supra(obra, dadosPrev):
    log_detalhado(f"Calculando supra para obra {obra}", 1)
    
    codigosEapEquivalentes = ['09']
    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)
        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return calculaEf(obra, dicGeralDeEvolucao)

# Filtros de apropriações
filtroApropriacoes = {
    '02.002.003.001': fundInfraSupra,
    '02.003.001.001': fundInfraSupra,
    '02.003.001.002': fundInfraSupra,
    '02.003.001.003': fundInfraSupra,
    '02.003.001.004': fundInfraSupra,
    '02.003.001.005': fundInfraSupra,
    '02.003.001.006': fundInfraSupra,
    '03.002.003.001': fundInfraSupra,
    '03.002.003.002': fundInfraSupra,
    '04.005.001.001': srvFachada,
    '04.002.001.001': supra,
    '04.002.001.002': supra,
}

# Busca contratos da obra HPB
contratos_hpb = []
for cont in baseItens:
    if len(cont['buildings']) == 0:
        continue
    
    buildingId = cont['buildings'][0]['buildingId']
    buildingName = cont['buildings'][0]['name']
    
    # Identifica HPB pelos possíveis IDs ou nomes
    if 'HPB' in buildingName.upper() or buildingId in [905, '905']:  # Ajuste conforme necessário
        contratos_hpb.append(cont)

if not contratos_hpb:
    write_log("ERRO: Nenhum contrato encontrado para HPB")
    write_log("Obras disponíveis:")
    obras_encontradas = set()
    for cont in baseItens:
        if len(cont['buildings']) > 0:
            obra_info = f"ID: {cont['buildings'][0]['buildingId']}, Nome: {cont['buildings'][0]['name']}"
            if obra_info not in obras_encontradas:
                write_log(f"  - {obra_info}")
                obras_encontradas.add(obra_info)
    log_file.close()
    exit()

write_log(f"Encontrados {len(contratos_hpb)} contratos para HPB")

# Debug detalhado por contrato
for cont in contratos_hpb:
    buildingId = cont['buildings'][0]['buildingId']
    buildingName = cont['buildings'][0]['name']
    numCont = cont['documentId'] + '/' + cont['contractNumber']
    nomeFornecedor = cont['supplierName']
    
    write_log(f"\n{'='*60}")
    write_log(f"CONTRATO: {numCont} - {nomeFornecedor}")
    write_log(f"OBRA: {buildingName} (ID: {buildingId})")
    write_log(f"{'='*60}")
    
    # Cálculo evolução financeira
    valorTotalContrato = round(cont['totalLaborValue'] + cont['totalMaterialValue'], 2)
    evolucaoFinanceira = 0
    totalMedido = 0
    dicApropriacoes = {}
    valorApropriadoPorEAP = {}
    
    write_log(f"Valor Total Contrato: R$ {valorTotalContrato:,.2f}")
    
    listaBuid = list(cont['itens'].keys())
    
    if "1" in listaBuid:
        dicItem = cont['itens']["1"]
        
        for i, item in enumerate(dicItem):
            itemQtd = item['quantity'] if item['quantity'] is not None else 0
            valorMaterial = item['materialPrice'] if item['materialPrice'] is not None else 0
            valorMO = item['laborPrice'] if item['laborPrice'] is not None else 0
            valorUnitario = valorMO + valorMaterial
            valorTotalItem = round(itemQtd * valorUnitario, 2)
            
            try:
                percRepItem = round(valorTotalItem / valorTotalContrato, 3)
            except ZeroDivisionError:
                percRepItem = 0
            
            # Apropriações do item
            apropriacoesItem = item['buildingAppropriations']
            totalApropriadoItem = 0
            
            write_log(f"\n  Item {i+1}: Qtd={itemQtd}, VlrUnit=R${valorUnitario:.2f}, VlrTotal=R${valorTotalItem:.2f}")
            write_log(f"    Participação no contrato: {percRepItem:.3f}")
            
            for aprop in apropriacoesItem:
                totalApropriadoItem += aprop['measuredQuantity']
                try:
                    valorApropriadoPorEAP[aprop['wbsCode']] += round(aprop['quantity'] * valorUnitario, 2)
                except KeyError:
                    valorApropriadoPorEAP[aprop['wbsCode']] = round(aprop['quantity'] * valorUnitario, 2)
                
                write_log(f"    Apropriação EAP {aprop['wbsCode']}: Qtd={aprop['quantity']}, Medido={aprop['measuredQuantity']}")
            
            totalMedido += round(totalApropriadoItem * valorUnitario)
            
            try:
                percMedidoItem = round(totalApropriadoItem / itemQtd, 3)
            except ZeroDivisionError:
                percMedidoItem = 0
            
            evolucaoFinanceira += round(percRepItem * percMedidoItem, 3)
            
            write_log(f"    Total apropriado: {totalApropriadoItem}, % Medido: {percMedidoItem:.3f}")
    
    # Calcula peso das apropriações
    write_log(f"\nTOTAL MEDIDO: R$ {totalMedido:,.2f}")
    write_log(f"EVOLUÇÃO FINANCEIRA: {evolucaoFinanceira:.4f}")
    
    for k in list(valorApropriadoPorEAP.keys()):
        try:
            dicApropriacoes[k] = round(valorApropriadoPorEAP[k] / valorTotalContrato, 4)
        except ZeroDivisionError:
            dicApropriacoes[k] = 0
    
    write_log(f"\nAPROPRIAÇÕES POR EAP:")
    for eap, peso in dicApropriacoes.items():
        valor = valorApropriadoPorEAP[eap]
        write_log(f"  {eap}: R$ {valor:,.2f} ({peso:.4f})")
    
    # Cálculo evolução física
    codObra = str(buildingId)
    evolucao = 0
    
    write_log(f"\nCÁLCULO EVOLUÇÃO FÍSICA para obra {codObra}:")
    
    if codObra in dadosPrev:
        write_log(f"Dados Prevision encontrados para obra {codObra}")
        write_log(f"Códigos EAP disponíveis no Prevision: {len(dadosPrev[codObra])} códigos")
        
        # Mostra alguns códigos disponíveis
        codigos_sample = list(dadosPrev[codObra].keys())[:10]
        write_log(f"Amostra de códigos: {codigos_sample}")
        
        kAprops = list(dicApropriacoes.keys())
        
        for k in kAprops:
            write_log(f"\n  Processando apropriação {k} (peso: {dicApropriacoes[k]:.4f}):")
            
            # Verifica se está nos filtros
            if k in filtroApropriacoes:
                log_detalhado(f"Usando filtro especial para {k}", 1)
                evoSubs = filtroApropriacoes[k](codObra, dadosPrev)
                contribuicao = evoSubs * dicApropriacoes[k]
                evolucao += contribuicao
                write_log(f"    Filtro especial: {evoSubs:.4f} x {dicApropriacoes[k]:.4f} = {contribuicao:.4f}")
                continue
            
            # Busca hierárquica padrão
            qtdNiveis = k.count('.')
            apropExp = k.split('.')
            consultas = []
            for nv in range(qtdNiveis):
                consultas.append('.'.join(apropExp[0:nv+1]))
            consultas.append(k)
            consultas.reverse()
            
            write_log(f"    Busca hierárquica: {consultas}")
            
            encontrado = False
            for c in consultas:
                try:
                    valor_prev = dadosPrev[codObra][c]
                    contribuicao = valor_prev * dicApropriacoes[k]
                    evolucao += contribuicao
                    write_log(f"    Encontrado {c}: {valor_prev:.4f} x {dicApropriacoes[k]:.4f} = {contribuicao:.4f}")
                    encontrado = True
                    break
                except KeyError:
                    write_log(f"    Não encontrado: {c}")
            
            if not encontrado:
                write_log(f"    Nenhum valor encontrado para {k}")
    else:
        write_log(f"ERRO: Obra {codObra} não encontrada nos dados do Prevision")
        write_log(f"Obras disponíveis: {list(dadosPrev.keys())}")
    
    # Fallback para evolução geral da obra
    if evolucao == 0:
        try:
            evolucao = round(evoProjetos[str(codObra)], 4)
            write_log(f"Usando evolução geral da obra: {evolucao:.4f}")
        except KeyError:
            write_log(f"Evolução geral não encontrada para obra {codObra}")
    
    write_log(f"\nRESULTADO FINAL:")
    write_log(f"  Evolução Financeira: {evolucaoFinanceira:.4f}")
    write_log(f"  Evolução Física: {evolucao:.4f}")
    write_log(f"  Diferença: {evolucaoFinanceira - evolucao:.4f}")
    
    # Cálculo de projeção
    difEvols = evolucaoFinanceira - evolucao
    
    if difEvols > 0:
        if evolucao >= 1:
            difProjetado = 0
        else:
            difProjetado = round(difEvols * valorTotalContrato, 2)
    else:
        difProjetado = 0
    
    write_log(f"  Projeção: R$ {difProjetado:,.2f}")

write_log(f"\n{'='*80}")
write_log("FIM DO DEBUG HPB")
write_log(f"{'='*80}")

# Fecha o arquivo de log
log_file.close()
write_log(f"\nArquivo de debug salvo como: debug_hpb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")