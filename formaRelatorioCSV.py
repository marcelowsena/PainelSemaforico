from bases import carregabases
import csv

baseItens = carregabases.itensContratos()

linhasFinais = []

for cont in baseItens:

    #bloco BuldingId
    if len(cont['buildings']) == 0:
        continue
    buildingId = cont['buildings'][0]['buildingId']

    filtroNotBuildingId = [
        101,
    ]

    if buildingId in filtroNotBuildingId:
        continue

    #bloco BuldingId
    buildingName = cont['buildings'][0]['name']    

    #bloco numContrato
    numCont = cont['documentId'] + '/' + cont['contractNumber']

    #bloco evolucaoFinanceira - media ponderada
    valorTotalContrato = round(cont['totalLaborValue'] + cont['totalMaterialValue'], 2)

    evolucaoFinanceira = 0
    totalMedido = 0

    dicApropriacoes = {}
    valorApropriadoPorEAP = {}

    listaBuid = list(cont['itens'].keys())

    #Alterado para pegar só das Buid 1
    try:
        if "1" in listaBuid:

            dicItem = cont['itens']["1"]

            for item in dicItem:
                if item['quantity'] != None:
                    itemQtd = item['quantity']
                else:
                    itemQtd = 0
                valorMaterial = 0
                valorMO = 0
                if item['laborPrice'] != None:
                    valorMO = item['laborPrice']
                if item['materialPrice'] != None:
                    valorMaterial = item['materialPrice']
                valorUnitario = valorMO + valorMaterial
                valorTotalItem = round(itemQtd*valorUnitario, 2)
                try:
                    percRepItem = round(valorTotalItem/valorTotalContrato, 3)
                except ZeroDivisionError:
                    percRepItem = 0             

                #bloco medicoes
                log = False

                #if numCont == 'CT/1012':
                #    log = True 
                
                #bloco Apropriações
                apropriacoesItem = item['buildingAppropriations']
                totalApropriadoItem = 0
                for aprop in apropriacoesItem:
                    totalApropriadoItem += aprop['measuredQuantity']
                    try:
                        valorApropriadoPorEAP[aprop['wbsCode']] += round(aprop['quantity']*valorUnitario, 2)
                    except KeyError:
                        valorApropriadoPorEAP[aprop['wbsCode']] = round(aprop['quantity']*valorUnitario, 2)
                

                totalMedido += round(totalApropriadoItem*valorUnitario)
                if log:
                    print('ApropItem', totalMedido, valorUnitario)
                try:
                    percMedidoItem = round(totalApropriadoItem/itemQtd, 3)
                except ZeroDivisionError:
                    percMedidoItem = 0
                evolucaoFinanceira += round(percRepItem*percMedidoItem, 3)

        else:
            continue
    except TypeError:
        continue

    #ajuste % de ApropPor Contrato
    for k in list(valorApropriadoPorEAP.keys()):
        try:
            dicApropriacoes[k] = round(valorApropriadoPorEAP[k]/valorTotalContrato, 4)
        except ZeroDivisionError:
            dicApropriacoes[k] = 0
    
    #blocoNomeFornecedor
    nomeFornecedor = cont['supplierName']

    #objeto do contrato
    objetoContrato = cont['object']

    #bloco autorizado    
    autorizacao = 'Não'
    if cont['isAuthorized']:
        autorizacao = 'Sim'
    
    #bloco status

    traducao = {
        'PARTIALLY_MEASURED': 'Parcialmente Medido',
        "FULLY_MEASURED": 'Totalmente Medido',
        "RESCINDED": 'Rescindido',
        "PENDING": 'Pendente',
        "COMPLETED": 'Concluído',
    }
    statusContrato = traducao[cont['status']]

    #bloco inicio e fim contrato
    def formataDataPadraoExc(dataStr):
        dataDividida = dataStr.split('-')
        return('/'.join([dataDividida[2], dataDividida[1], dataDividida[0]]))
    
    inicioCont= formataDataPadraoExc(cont['startDate'])
    fimCont = formataDataPadraoExc(cont['endDate'])

    #bloco Mix de Apropriações


    linha = {
        'buildingId': buildingId,
        'buildingName': buildingName,
        'numContrato': numCont,
        'evolucaoFinanceira': evolucaoFinanceira,
        'evolucaoFIsica': 0,
        'projeção': 0,
        'difEvolucao': 0,
        'nomeFornecedor': nomeFornecedor,
        'objetoContrato': objetoContrato,
        'totalContrato': str(valorTotalContrato).replace('.', ','),
        'totalMedido': str(totalMedido).replace('.', ','),
        'totalSaldo': str(round(valorTotalContrato - totalMedido, 2)).replace('.', ','),
        'catContrato': 0,
        'autorizado': autorizacao,
        'statusContrato': statusContrato,
        'inicioContrato': inicioCont,
        'fimContrato': fimCont,
        'pesoAprops': dicApropriacoes
    }

    linhasFinais.append(linha)
