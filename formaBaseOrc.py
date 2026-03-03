from consultas.API import origem
import json

def formaOuAtBase():
    consultaObras = origem.consultaObras()

    #consultaOrc = origem.consultaOrcItens(203, 1)
    dicGeral = {}

    for obra in consultaObras:

        print('consultando Obra', obra['name'])
        consultaOrc = origem.consultaOrcItens(obra['id'], 1)
        if 'status' in consultaOrc:
            print('Plan Não encontrada')
            continue
        totalObra = 0
        dicEAP = {}
        dicEapKeys = []

        for item in consultaOrc:
            totalItem = 0
            catItem = item['wbsCode']
            for categoria in item['pricesByCategory']:
                totalItem += categoria['totalPrice']
            if catItem.count('.') == 0:
                totalObra += totalItem
            dicEapKeys.append(catItem)
            dicEAP[catItem] = {
                'total': totalItem,
                'peso': 0,
            }

        for key in dicEapKeys:
            try:
                dicEAP[key]['peso'] = dicEAP[key]['total']/round(totalObra, 2)
            except ZeroDivisionError:
                pass
        
        dicGeral[obra['id']] = dicEAP

    json.dump(dicGeral, open('baseOrc.json', mode='w', encoding='utf-8-sig'))

def verificaEAP(codEap, obra):

    base = json.load(open('baseOrc.json', encoding='utf-8-sig'))

    eapObra = base[obra]

    valorEAP = round(eapObra[codEap]['total'], 2)
    check = 0

    keysObra = list(base[obra].keys())

    for key in keysObra:
        if key != codEap and key[0:len(codEap)] == codEap and key.count('.') == codEap.count('.')+1:
            check += round(eapObra[key]['total'], 2)
    
    print('Check da obra', obra, 'e EAP', codEap)
    print(valorEAP, round(check, 2))

#verificaEAP('02', '905')
formaOuAtBase()