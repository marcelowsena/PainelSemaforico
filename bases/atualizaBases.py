import json

def itensContratos(dados):
    arquivo = open('bases/baseContratosItens.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Contratos e Itens - Atualizada')

def contratos(dados):
    arquivo = open('bases/baseInContratosPreco.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Contratos - Atualizada')

def credor(dados):
    arquivo = open('bases/baseInCredor.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Credores - Atualizada')

def NFEs(dados):
    arquivo = open('bases/nfBase.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - NFEs - Atualizada')

def NFEsComEmitPgt(dados):
    arquivo = open('bases/baseInNf.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - NFEs Emit e Pgt - Atualizada')  

def pedidosCompra(dados):
    arquivo = open('bases/basePedidos.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Pedido de Compra - Atualizada')

def titulosContasAPagar(dados):
    arquivo = open('bases/titBase.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Titulos - Atualizada')

def bulkTitulos(dados):
    arquivo = open('bases/bulkTitulos.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Titulos Bulk - Atualizada')

def obras(dados):
    arquivo = open('bases/enterprises.json', mode='w', encoding='utf-8')
    json.dump(dados, arquivo)
    print('Base - Obras - Atualizada')