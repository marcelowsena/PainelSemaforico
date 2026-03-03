import json


def itensContratos():
    arquivo = open('bases/baseContratosItens.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def contratos():
    arquivo = open('bases/baseInContratosPreco.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def credor():
    arquivo = open('bases/baseInCredor.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def NFEs():
    arquivo = open('bases/nfBase.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def NFEsComEmitPgt():
    arquivo = open('bases/baseInNf.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def pedidosCompra():
    arquivo = open('bases/basePedidos.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def titulosContasAPagar():
    arquivo = open('bases/titBase.json', mode='r', encoding='utf-8')
    return(json.load(arquivo))

def titulosBulk():
    arquivo = open('bases/bulkTitulos.json', mode='r', encoding='utf-8-sig')
    return(json.load(arquivo))

def obras():
    arquivo = open('bases/enterprises.json', mode='r', encoding='utf-8-sig')
    return(json.load(arquivo))