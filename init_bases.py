"""
Inicializa bases de dados necessarias para o script principal.
Executado antes do main.py quando o cache esta vazio (primeira execucao).
"""
import os
import json

os.makedirs('bases', exist_ok=True)

if not os.path.exists('dadosPrevision.json'):
    json.dump(dict(), open('dadosPrevision.json', 'w'))
    print('dadosPrevision.json inicializado vazio')

if not os.path.exists('dadosEvoObra.json'):
    json.dump(dict(), open('dadosEvoObra.json', 'w'))
    print('dadosEvoObra.json inicializado vazio')

if not os.path.exists('bases/baseContratosItens.json'):
    print('Cache vazio - gerando bases do Sienge (primeira execucao)...')
    from atualizacaoBasesSienge import atualizaContratos
    atualizaContratos()
    print('Bases geradas com sucesso.')

if not os.path.exists('baseOrc.json'):
    print('Gerando baseOrc.json...')
    from formaBaseOrc import formaOuAtBase
    dados = formaOuAtBase()
    json.dump(dados, open('baseOrc.json', 'w', encoding='utf-8'))
    print('baseOrc.json gerado.')

print('Inicializacao concluida.')
