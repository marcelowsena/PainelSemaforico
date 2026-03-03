from .consultaapi import consultaAPI
import datetime

# 1 - Administrativo - ex. 107 - Adm Opera
# 2 - Obra
# 3 - Marketing
# 4 - 

def formataData(datetimeObj):
    ano = str(datetimeObj.year)
    mes = str(datetimeObj.month)
    dia = str(datetimeObj.day)

    if len(mes) == 1:
        mes = '0'+mes
    if len(dia) == 1:
        dia = '0'+dia

    return('-'.join([ano, mes, dia]))

def consultaPedidos():

    apiPedidosPendentes = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/purchase-orders?",
        #"startDate=": 0,
        #"&endDate=": 0,
        "status=": "PENDING",
        "&limit=": "200",
        "&offset=": 0
    }

    apiPedidosParcial = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/purchase-orders?",
        #"startDate=": 0,
        #"&endDate=": 0,
        "status=": "PARTIALLY_DELIVERED",
        "&limit=": "200",
        "&offset=": 0
    }

    pedidospendentes = consultaAPI(apiPedidosPendentes)
    pedidosparciais = consultaAPI(apiPedidosParcial)

    pedidosDic = {}
    for pp in pedidospendentes:
        if pp['buildingId'] not in pedidosDic:
            pedidosDic[pp['buildingId']] = [pp]
        else:
            pedidosDic[pp['buildingId']].append(pp)
    
    for pp in pedidosparciais:
        if pp['buildingId'] not in pedidosDic:
            pedidosDic[pp['buildingId']] = [pp]
        else:
            pedidosDic[pp['buildingId']].append(pp)
    
    return(pedidosDic)

def consultaItemPedido(pedido):
    apiItens = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/purchase-orders/",
        "": pedido,
        "/items?": '',
        "&limit=": "200",
        "&offset=": 0
    }

    itens = consultaAPI(apiItens)

    return(itens)

def consultaTodosPedidos():

    apiPedidosPendentes = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/purchase-orders?",
        #"startDate=": 0,
        #"&endDate=": 0,
        "&limit=": "200",
        "&offset=": 0
    }

    pedidos = consultaAPI(apiPedidosPendentes)

    pedidosDic = {}
    for pp in pedidos:
        if pp['buildingId'] not in pedidosDic:
            pedidosDic[pp['buildingId']] = [pp]
        else:
            pedidosDic[pp['buildingId']].append(pp)
    
    return(pedidosDic)

def consultaContratos(basedepreco=False):

    apiContratos = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1//supply-contracts/all?",
        "contractStartDate=": 0,
        "&contractEndDate=": 0,
        #"&statusApproval=": "A",
        #"&authorization=": "A",        
        "&limit=": "200",
        "&offset=": 0
    }

    apiContratos["contractStartDate="] = "2007-01-01"
    apiContratos["&contractEndDate="] = "2040-12-31"

    contratos = consultaAPI(apiContratos)

    dadosfinais = []
    
    for c in contratos:
        if basedepreco == False:
            if c['status'] != "COMPLETED" and c['status'] != "RESCINDED":
                dadosfinais.append(c)
        else:
            dadosfinais.append(c)
    
    return(dadosfinais)

def consultaItensContratos(contrato, bUID):

    apiContratos = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/supply-contracts/items?",
        "documentId=": contrato['documentId'],
        "&contractNumber=": contrato['contractNumber'],
        "&buildingId=": contrato['buildings'][0]['buildingId'],
        "&buildingUnitId=": str(bUID),   
        "&limit=": "200",
        "&offset=": 0
    }

    itensContrato = consultaAPI(apiContratos)
    
    return(itensContrato)

def consultaCaucao(contrato):
    
    apiContratos = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/supply-contracts?",
        "documentId=": contrato['documentId'],
        "&contractNumber=": contrato['contractNumber'],
    }

    try:
        detalhesCaucao = consultaAPI(apiContratos)['securityDeposit']
    except KeyError:
        detalhesCaucao = { 
    "securityDepositPercentage": '',
    "dueDate": '',
    "documentId": '',
    "indexerId": '',
    "billIssueDate": '',
    "incidenceOver": '',
    "hasTaxWithhold": '',
    "hasDirectBillingDiscount": '',
    "considerContractItemPaymentCategories": '',
    "paymentCategoryId": '',
    "securityDepositBalance": ''
        }
    return(detalhesCaucao)

apiBuildingID = {
    "raiz": "https://api.sienge.com.br/trust/public/api/v1/enterprises/",
    "": 0
}
apiBuildingID[""] = 31
#print = consultaAPI(apiBuildingID)

def bulktitulos():

    apiLink = {
        'raiz': 'https://api.sienge.com.br/trust/public/api/bulk-data/v1/outcome?',
        'startDate=': "2007-01-01",
        '&endDate=':"2040-12-31",
        '&selectionType=':'I',
        '&correctionIndexerId=':0,
        '&correctionDate=':formataData(datetime.datetime.today()),
        '&withBankMovements=': 'false',
    }

    dadosConsulta = consultaAPI(apiLink)

    return(dadosConsulta)

def consultaObradoTitulo(link):
    apiLink = {
        'raiz': link
    }
    dadosConsulta = consultaAPI(apiLink)

    return(dadosConsulta['0'])

def consultaEAP(obra, aloc):

    apiEap = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/building-cost-estimations/",
        "": obra,
        "/sheets/": aloc,
        "/items?": "",
        "&limit=": "200",
        "&offset=": 0
    }

    dadosConsulta = consultaAPI(apiEap)

    return(dadosConsulta)

def consultaObras():

    apiEap = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/enterprises?",
        "limit=": "200",
        "&offset=": 0,
        "&onlyBuildingsEnabledForIntegration=false": ''
    }

    dadosConsulta = consultaAPI(apiEap)

    return(dadosConsulta)

def consultaOrcamentos(codObra):

    apiEap = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/building-cost-estimations/",
        '': codObra,
        "/sheets?limit=": "200",
        "&offset=": 0,
    }

    dadosConsulta = consultaAPI(apiEap)

    return(dadosConsulta)

def consultaOrcItens(codObra, buiId):

    apiEap = {
        "raiz": "https://api.sienge.com.br/trust/public/api/v1/building-cost-estimations/",
        '': codObra,
        "/sheets/": buiId, 
        "/items?limit=": "200",
        "&offset=": 0,
    }

    dadosConsulta = consultaAPI(apiEap)

    return(dadosConsulta)