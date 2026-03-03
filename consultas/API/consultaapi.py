import requests, json, os
from requests.auth import HTTPDigestAuth, HTTPBasicAuth


user = os.environ.get('SIENGE_USER', 'trust-francisco')
pw = os.environ.get('SIENGE_PASSWORD', 'vSMeJeliJNfpkrXv7lDvrR6v2aLaynnZ')


def formalink(linkdic):
    raizlink = linkdic["raiz"]
    for var in list(linkdic.keys()):
        if var != "raiz":
            raizlink+= var+str(linkdic[var])
    return(raizlink)

def puxaDados(link):
    response = requests.get(link, auth=HTTPBasicAuth(user, pw)).text
    retornos = json.loads(response)
    return(retornos)

def consultaAPI(diclink):

    linkfinal = formalink(diclink)
    dados = puxaDados(linkfinal)
    if 'results' in dados:
        dadosfinais = list(dados['results'])
        lenconsulta = len(dadosfinais)
        consultas = 1
        while lenconsulta == 200:
            diclink["&offset="] += 200
            linkfinal = formalink(diclink)
            dados = puxaDados(linkfinal)['results']
            lenconsulta = len(dados)
            for d in dados:
                dadosfinais.append(d)
            consultas += 1
        
        return(dadosfinais)
    else:
        return(dados)