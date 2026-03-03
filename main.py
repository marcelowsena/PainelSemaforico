from atualizacaoBasesSienge import atualizaContratos
from formaRelatorioCSV import linhasFinais
from prevision import agrPrev_V5 as prv
import csv
import json
from datetime import datetime

hoje = datetime.today()
dia_semana = hoje.weekday()  # Segunda = 0, Terça = 1, ..., Domingo = 6
dia_mes = hoje.day

orcObras = json.load(open('baseOrc.json', encoding='utf-8-sig'))

#freq At Prevision
if dia_semana == 1 or dia_mes == 1: #Atualiza terça-feira ou dia primeiros
    atualizaContratos()
    dadosPrev = prv.novoloop()
    json.dump(dadosPrev, open('dadosPrevision.json', mode='w', encoding='utf-8-sig'))
    evoProjetos = prv.trazDadosEvol()
    json.dump(evoProjetos, open('dadosEvoObra.json', mode='w', encoding='utf-8-sig'))
else:
    atualizaContratos()
    dadosPrev = json.load(open('dadosPrevision.json', mode='r', encoding='utf-8-sig'))
    evoProjetos = json.load(open('dadosEvoObra.json', mode='r', encoding='utf-8-sig'))

#bloco para arrumar os 06.06 no prevision
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

outputCSV = csv.writer(open('semaforico.csv', encoding='utf-8-sig', newline='', mode='w'), delimiter=';')
cabecalho = list(linhasFinais[0].keys())[0:-1]
outputCSV.writerow(cabecalho)

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
        
        # Etapa 1: tenta buscar a chave diretamente
        valor = dados.get(chave)
        if valor is not None and valor != 0:
            return {chave: valor}

        # Etapa 2: descer para filhos DIRETOS apenas
        filhos = filhos_diretos(chave)
        nao_zero = {k: v for k, v in filhos.items() if v != 0}
        if nao_zero:
            return nao_zero

        # Etapa 3: subir para os pais
        pai = subir_nivel(chave)
        while pai:
            valor = dados.get(pai)
            if valor is not None and valor != 0:
                return {pai: valor}
            pai = subir_nivel(pai)

        return {chave: 0}  # Nada encontrado
    
    return(buscar_valor(dadosEAPObra, codEAP))

def calculaEf(obra, dicEap):

    pesoTotal = 0
    evolucao = 0

    for k in list(dicEap.keys()):
        pesoTotal += orcObras[obra][k]['peso']
    
    for k in list(dicEap.keys()):
        evolucao += round((orcObras[obra][k]['peso']/pesoTotal)*dicEap[k], 4)
    
    return(round(evolucao, 4))

def balancim(obra, dadosPrev):
    '''
    coloca os cods de obra e dados do prevision e traz o % 
    aprop  Naut - 04.003.002
    '''
    evolucaoBal = 0

    if obra == '2024':
        
        dadosEvObra = dadosPrev[obra]
        match = '19.0'
        totalEv = 0
        count = 0
        for ev in dadosEvObra:
            if ev[0:4] == match and len(ev) == 6:
                count += 1
                totalEv += dadosEvObra[ev]
        evolucaoBal = (totalEv/count)

    return(round(evolucaoBal, 4))  

def grua(obra, dadosPrev):
    '''
    coloca os cods de obra e dados do prevision e traz o % 
    soma os itens 09.0xx e traz a media para o item - Naut
    aprop grua no Naut - 04.003.004
    '''
    evolucaoGrua = 0

    if obra == '2024':
        
        dadosEvObra = dadosPrev[obra]
        match = '09.0'
        totalEv = 0
        count = 0
        for ev in dadosEvObra:
            if ev[0:4] == match and len(ev) == 6:
                count += 1
                totalEv += dadosEvObra[ev]
        evolucaoGrua = (totalEv/count)

    return(round(evolucaoGrua, 4))    

def cremalheira(obra, dadosPrev):
    '''
    coloca os cods de obra e dados do prevision e traz o % 
    soma os itens 09.0xx e traz a media para o item - Naut
    aprop grua no Naut - 04.003.003
    '''
    evolucaoCrem = 0
    
    if obra == '2024':
        
        dadosEvObra = dadosPrev[obra]
        totalEv = dadosEvObra['10.001'] + dadosEvObra['17.001']
        count = 2
        evolucaoCrem = (totalEv/count)

    return(round(evolucaoCrem, 4))    

def fundInfraSupra(obra, dadosPrev):
    '''
    nova versão da função
    '''
   
    if obra == '2024':
        #codigos de referencia
        codigosEapEquivalentes = [
            '07',
            '08',
            '09',
        ]

    else:
        #codigos de referencia
        codigosEapEquivalentes = [
            '06',
            '07',
            '08',
            '09',
        ]

    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)

        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return(calculaEf(obra, dicGeralDeEvolucao))

def srvFachada(obra, dadosPrev):
    '''
    nova versão da função
    '''
   
    if obra == '2024':
        #codigos de referencia
        codigosEapEquivalentes = [
            '19.001',
            '19.002',
            '19.003',
        ]

    else:
        #codigos de referencia
        codigosEapEquivalentes = [
            '19.001',
            '19.002',
            '19.006',
        ]

    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)

        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return(calculaEf(obra, dicGeralDeEvolucao))

def supraRevExt(obra, dadosPrev):
    '''
    nova versão da função
    '''
   
    if obra == '2024':
        #codigos de referencia
        codigosEapEquivalentes = [
            '19.001',
            '19.002',
            '19.003',
            '09',
        ]

    else:
        #codigos de referencia
        codigosEapEquivalentes = [
            '19.001',
            '19.002',
            '19.006',
            '09',
        ]

    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)

        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return(calculaEf(obra, dicGeralDeEvolucao))

def supraRebExt(obra, dadosPrev):
    '''
    nova versão da função
    '''
    
    codigosEapEquivalentes = [
        '19.001',
        '09',
        ]

    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)

        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return(calculaEf(obra, dicGeralDeEvolucao))

def supra(obra, dadosPrev):
    '''
    nova versão da função
    '''
   
    codigosEapEquivalentes = [
            '09',
        ]

    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)

        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return(calculaEf(obra, dicGeralDeEvolucao))

def supraVed(obra, dadosPrev):
    '''
    nova versão da função
    '''
   
    codigosEapEquivalentes = [
            '09',
            '10'
        ]

    dicGeralDeEvolucao = {}

    for c in codigosEapEquivalentes:
        chaves = buscaEF(obra, c)

        for k in list(chaves.keys()):
            dicGeralDeEvolucao[k] = chaves[k]

    return(calculaEf(obra, dicGeralDeEvolucao))

def montaEFGeral(efPrev, orcSienge):

    def subir_eap(eap):
        partes = eap.split('.')
        if len(partes) == 1:
            return None
        return '.'.join(partes[:-1])

    def buscar_peso(orcamento, eap):
        atual = eap
        while atual:
            item = orcamento.get(atual)
            if item and item.get('peso', 0) != 0:
                return item['peso']
            atual = subir_eap(atual)
        return 0

    def calcular_evolucao_ponderada(evolucao, orcamento):
        total_ponderado = 0
        for eap, evolucao_fisica in evolucao.items():
            peso = buscar_peso(orcamento, eap)
            total_ponderado += evolucao_fisica * peso
        return total_ponderado  # sem divisão, respeitando o peso
    
    return calcular_evolucao_ponderada(efPrev, orcSienge)

filtroApropriacoesNaut = {
    '02.002.009': fundInfraSupra, #topografia
    '04.003.002': balancim,
    '04.003.003': cremalheira,
    '04.003.004': grua,
    '03.005.015': supra, #MO GRUA 
    '02.002.009': fundInfraSupra, #topografia
    '02.003.001': fundInfraSupra, #controle tec
    '02.003.002': fundInfraSupra, 
    '02.003.003': fundInfraSupra, 
    '02.003.004': fundInfraSupra,
    '02.003.005': fundInfraSupra,
    '02.003.006': fundInfraSupra,
    '02.003.007': fundInfraSupra,
    '02.003.008': fundInfraSupra,
    '03.002.003': fundInfraSupra, #container
    '04.003.001': srvFachada, #andaime fachadeiro
    '04.004.001': srvFachada,
    '04.003.002': srvFachada, #balancim
    '03.004.006': supraRevExt, #tela fachadeira
    '03.004.005': supraRebExt, #bandeija
    '03.004.008': supra, #tela fachadeira
    '04.003.008': supra, #escoramento    
}

filtroApropriacoes = {
    '02.002.003.001': fundInfraSupra, #topografia
    '02.003.001.001': fundInfraSupra, #controle tec
    '02.003.001.002': fundInfraSupra, 
    '02.003.001.003': fundInfraSupra, 
    '02.003.001.004': fundInfraSupra,
    '02.003.001.005': fundInfraSupra,
    '02.003.001.006': fundInfraSupra,
    '03.002.003.001': fundInfraSupra, #container
    '03.002.003.002': fundInfraSupra,
    '04.005.001.001': srvFachada, #andaime fachadeiro
    '04.002.001.001': supra, #grua
    '04.002.001.002': supra, # MO grua
    '04.002.001.002': supra, # MO grua
    '04.004.001.001': supra, # cremalheiras
    '04.004.001.002': supra, # MO cremalheiras
    '04.006.001.001': srvFachada, #balancim
    '03.004.001.001': supraRevExt, #tela fachadeira
    '03.004.001.002': supraRevExt, #tela fachadeira
    '03.004.001.003': supraRevExt, #tela fachadeira
    '03.004.001.004': supraRevExt, #tela fachadeira
    '03.004.006.001': supraRebExt, #bandeija
    '03.004.006.005': supraRebExt, #bandeija
    '03.004.002.001': supra, #tela fachadeira
    '03.004.002.002': supra, #tela fachadeira
    '04.007.002.001': supra, #escoramento
}

for linha in linhasFinais:  
    evolucao = 0
    codObra = str(linha['buildingId']) 
    if codObra in dadosPrev:
        kAprops = list(linha['pesoAprops'].keys())
        for k in kAprops:
            if str(codObra) == '2024':
                apFiltros = list(filtroApropriacoesNaut.keys())
                filtroAp = filtroApropriacoesNaut
            else:
                apFiltros = list(filtroApropriacoes.keys())
                filtroAp = filtroApropriacoes
            if k in apFiltros:
                evoSubs = filtroAp[k](codObra, dadosPrev)
                evolucao += (evoSubs * linha['pesoAprops'][k])
                #print(evolucao)
                #print(linha)
                continue
            qtdNiveis = k.count('.')
            apropExp = k.split('.')
            consultas = []
            for nv in range(qtdNiveis):
                consultas.append('.'.join(apropExp[0:nv+1]))
            consultas.append(k)
            consultas.reverse()
            for c in consultas:
                try:
                    evolucao += (dadosPrev[codObra][c] * linha['pesoAprops'][k])
                except KeyError:
                    evolucao += 0
    
    valorTotalContrato = float(linha['totalContrato'].replace(',', '.'))

    if evolucao == 0:
        try:
            evolucao = round(evoProjetos[str(codObra)], 4)
        except:
            pass

    difEvols = linha['evolucaoFinanceira'] - evolucao
    
    if difEvols > 0:
        if evolucao >= 1:
            difProjetado = 0
        else:
            difProjetado = round(difEvols*valorTotalContrato, 2)
    else:
        difProjetado = 0

    #difProjetado = round(estipuladoGastos - valorTotalContrato, 2)

    #if difProjetado < 0:
    #    difProjetado = 0

    if linha['autorizado'] == "Sim":
        if linha['statusContrato'] == "Parcialmente Medido" or linha['statusContrato'] == "Pendente":
            linha['projeção'] = str(difProjetado).replace('.', ',')
    else:
        linha['projeção'] = 0
    linha['evolucaoFinanceira'] = str(round(linha['evolucaoFinanceira'], 4)).replace('.', ',')
    linha['evolucaoFIsica'] = str(round(evolucao, 4)).replace('.', ',')
    dadoslinha = list(linha.values())[0:-1]
    outputCSV.writerow(dadoslinha)

from crudSP import main as sharepoint

sharepoint.upload_arquivo_sharepoint(sharepoint.token, 'semaforico.csv')