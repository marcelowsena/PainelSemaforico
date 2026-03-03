from bases import carregabases as cb
from bases import atualizaBases as ab
import datetime
import consultas
import consultas.API
import consultas.API.consultaapi
import consultas.API.origem
from progresso.logProgresso import monitoraProgresso

'''
Atualização otimizada de contratos - versão incremental
Só busca detalhes de contratos que tiveram alterações
'''

def precisaAtualizar(contratoAPI, baseLocal):
    """
    Verifica se o contrato precisa ser atualizado comparando com a base local.
    Retorna True se:
    - Contrato é novo (não existe na base)
    - Status mudou
    - Valor de mão de obra mudou
    - Valor de material mudou
    """
    if baseLocal is None:
        return True  # Contrato novo

    # Compara status
    if contratoAPI.get('status') != baseLocal.get('status'):
        return True

    # Compara valores (usando tolerância para float)
    if abs(contratoAPI.get('totalLaborValue', 0) - baseLocal.get('totalLaborValue', 0)) > 0.01:
        return True

    if abs(contratoAPI.get('totalMaterialValue', 0) - baseLocal.get('totalMaterialValue', 0)) > 0.01:
        return True

    return False

def criaIndiceBase(baseContratos):
    """
    Cria um índice para busca rápida de contratos na base local.
    Chave: (documentId, contractNumber)
    """
    indice = {}
    for c in baseContratos:
        chave = (c.get('documentId'), c.get('contractNumber'))
        indice[chave] = c
    return indice

def atualizaContratos():
    # Busca lista de contratos da API (só metadados, rápido)
    consultaContratos = consultas.API.origem.consultaContratos(True)
    ab.contratos(consultaContratos)

    # Carrega base local existente
    try:
        baseLocal = cb.itensContratos()
        indiceBase = criaIndiceBase(baseLocal)
        print(f'Base local carregada: {len(baseLocal)} contratos')
    except (FileNotFoundError, Exception) as e:
        print(f'Base local não encontrada ou erro ao carregar: {e}')
        print('Será feita atualização completa.')
        indiceBase = {}

    buildingUnitsId = list(range(1, 9))

    # Contadores para estatísticas
    total = len(consultaContratos)
    atualizados = 0
    pulados = 0
    sem_obra = 0

    inicio = datetime.datetime.now()
    contagem = 0

    for c in consultaContratos:
        contagem += 1

        # Pula contratos sem obra vinculada
        if len(c['buildings']) == 0:
            sem_obra += 1
            continue

        obra = c['buildings'][0]['buildingId']
        chave = (c.get('documentId'), c.get('contractNumber'))
        contratoLocal = indiceBase.get(chave)

        # Verifica se precisa atualizar
        if not precisaAtualizar(c, contratoLocal):
            # Mantém dados da base local (cache)
            c['caucao'] = contratoLocal.get('caucao', {})
            c['itens'] = contratoLocal.get('itens', {})
            pulados += 1
        else:
            # Busca dados atualizados da API
            caucao = consultas.API.origem.consultaCaucao(c)
            c['caucao'] = caucao
            c['itens'] = {}

            for buid in buildingUnitsId:
                consultaItens = consultas.API.origem.consultaItensContratos(c, buid)
                if 'status' not in consultaItens:
                    c['itens'][buid] = consultaItens
                    if obra != 2014:
                        break

            atualizados += 1

        monitoraProgresso(inicio, total, contagem, 20, 'Contratos')

    # Estatísticas finais
    print(f'\n--- Resumo da Atualização ---')
    print(f'Total de contratos: {total}')
    print(f'Atualizados (API): {atualizados}')
    print(f'Pulados (cache): {pulados}')
    print(f'Sem obra vinculada: {sem_obra}')
    print(f'Economia: {pulados}/{total} contratos não precisaram de chamadas à API')

    ab.itensContratos(consultaContratos)
