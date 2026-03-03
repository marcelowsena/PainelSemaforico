import json
from bases import carregabases
from datetime import datetime

# Configuração do arquivo de log
log_file = open(f'investigacao_hpb_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w', encoding='utf-8')

def write_log(mensagem, nivel=0):
    indent = "  " * nivel
    linha = f"{indent}{mensagem}"
    print(linha)
    log_file.write(linha + "\n")
    log_file.flush()

write_log("=" * 80)
write_log("INVESTIGAÇÃO OBRA HPB - ORIGEM DO ID")
write_log(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
write_log("=" * 80)

# Carrega bases
baseItens = carregabases.itensContratos()
dadosPrev = json.load(open('dadosPrevision.json', mode='r', encoding='utf-8-sig'))
evoProjetos = json.load(open('dadosEvoObra.json', mode='r', encoding='utf-8-sig'))

write_log("\n1. BUSCANDO TODAS AS OBRAS DISPONÍVEIS:")
write_log("="*50)

obras_encontradas = {}
for cont in baseItens:
    if len(cont['buildings']) > 0:
        buildingId = cont['buildings'][0]['buildingId']
        buildingName = cont['buildings'][0]['name']
        
        if buildingId not in obras_encontradas:
            obras_encontradas[buildingId] = {
                'nome': buildingName,
                'contratos': 0
            }
        obras_encontradas[buildingId]['contratos'] += 1

write_log(f"Total de obras encontradas: {len(obras_encontradas)}")
write_log("\nLista completa de obras:")
for obra_id in sorted(obras_encontradas.keys()):
    info = obras_encontradas[obra_id]
    write_log(f"  ID: {obra_id} | Nome: '{info['nome']}' | Contratos: {info['contratos']}")

write_log("\n2. BUSCANDO ESPECIFICAMENTE 'HPB' NO NOME:")
write_log("="*50)

obras_hpb_candidatas = []
for obra_id, info in obras_encontradas.items():
    if 'HPB' in info['nome'].upper():
        obras_hpb_candidatas.append((obra_id, info))
        write_log(f"  ENCONTRADO - ID: {obra_id} | Nome: '{info['nome']}'")

if not obras_hpb_candidatas:
    write_log("  NENHUMA obra com 'HPB' no nome encontrada!")
    
    write_log("\n  Buscando nomes similares...")
    for obra_id, info in obras_encontradas.items():
        nome = info['nome'].upper()
        if any(termo in nome for termo in ['HP', 'HOTEL', 'PARK', 'BEACH']):
            write_log(f"    Possível candidata - ID: {obra_id} | Nome: '{info['nome']}'")

write_log("\n3. VERIFICANDO ID 905 (MENCIONADO NO CÓDIGO):")
write_log("="*50)

if 905 in obras_encontradas:
    info_905 = obras_encontradas[905]
    write_log(f"  ID 905 encontrado: '{info_905['nome']}' com {info_905['contratos']} contratos")
else:
    write_log("  ID 905 NÃO encontrado na base de dados")

write_log("\n4. VERIFICANDO DADOS PREVISION:")
write_log("="*50)

write_log(f"Obras disponíveis no Prevision: {len(dadosPrev)} obras")
write_log("IDs das obras no Prevision:")
for obra_id in sorted(dadosPrev.keys()):
    qtd_codigos = len(dadosPrev[obra_id])
    write_log(f"  {obra_id}: {qtd_codigos} códigos EAP")

write_log("\n5. VERIFICANDO EVOLUÇÃO DE PROJETOS:")
write_log("="*50)

write_log(f"Obras com evolução: {len(evoProjetos)} obras")
write_log("IDs das obras com evolução:")
for obra_id in sorted(evoProjetos.keys()):
    evolucao = evoProjetos[obra_id]
    write_log(f"  {obra_id}: {evolucao:.4f}")

write_log("\n6. ANÁLISE DETALHADA DOS CONTRATOS 'HPB':")
write_log("="*50)

contratos_hpb_detalhados = []
for cont in baseItens:
    if len(cont['buildings']) == 0:
        continue
    
    buildingName = cont['buildings'][0]['name']
    if 'HPB' in buildingName.upper():
        contratos_hpb_detalhados.append(cont)

write_log(f"Total de contratos com 'HPB': {len(contratos_hpb_detalhados)}")

for i, cont in enumerate(contratos_hpb_detalhados[:5]):  # Mostra primeiros 5
    buildingId = cont['buildings'][0]['buildingId']
    buildingName = cont['buildings'][0]['name']
    numCont = cont['documentId'] + '/' + cont['contractNumber']
    nomeFornecedor = cont['supplierName']
    status = cont['status']
    
    write_log(f"\n  Contrato {i+1}:")
    write_log(f"    Número: {numCont}")
    write_log(f"    Fornecedor: {nomeFornecedor}")
    write_log(f"    Building ID: {buildingId}")
    write_log(f"    Building Name: '{buildingName}'")
    write_log(f"    Status: {status}")
    
    # Verifica se tem itens
    if 'itens' in cont and cont['itens']:
        qtd_buid = len(cont['itens'])
        write_log(f"    Building Units: {list(cont['itens'].keys())} ({qtd_buid} unidades)")
        
        if "1" in cont['itens']:
            qtd_itens = len(cont['itens']["1"])
            write_log(f"    Itens na BUID 1: {qtd_itens} itens")

if len(contratos_hpb_detalhados) > 5:
    write_log(f"\n  ... e mais {len(contratos_hpb_detalhados) - 5} contratos")

write_log("\n7. CROSS-REFERENCE COM OUTRAS BASES:")
write_log("="*50)

# Verifica se o ID 3028 existe em outras bases
id_3028_existe = False

write_log("Verificando ID 3028 em diferentes bases:")

if '3028' in dadosPrev:
    write_log(f"  ✓ Prevision: ID 3028 encontrado com {len(dadosPrev['3028'])} códigos EAP")
    id_3028_existe = True
else:
    write_log(f"  ✗ Prevision: ID 3028 NÃO encontrado")

if '3028' in evoProjetos:
    write_log(f"  ✓ Evolução: ID 3028 encontrado com evolução {evoProjetos['3028']:.4f}")
    id_3028_existe = True
else:
    write_log(f"  ✗ Evolução: ID 3028 NÃO encontrado")

# Verifica se existe no orçamento
try:
    orcObras = json.load(open('baseOrc.json', encoding='utf-8-sig'))
    if 3028 in orcObras:
        write_log(f"  ✓ Orçamento: ID 3028 encontrado com {len(orcObras[3028])} códigos")
        id_3028_existe = True
    else:
        write_log(f"  ✗ Orçamento: ID 3028 NÃO encontrado")
except:
    write_log(f"  ? Orçamento: Erro ao carregar base")

write_log("\n8. CONCLUSÃO:")
write_log("="*50)

if id_3028_existe:
    write_log("O ID 3028 foi encontrado em pelo menos uma das bases complementares.")
    write_log("Isso sugere que é um ID válido, mesmo que não seja 905 como esperado.")
else:
    write_log("PROBLEMA: ID 3028 não foi encontrado nas bases Prevision/Evolução/Orçamento!")
    write_log("Isso pode indicar inconsistência entre as bases de dados.")

write_log("\nRECOMENDAÇÕES:")
write_log("1. Verificar se HPB realmente corresponde ao ID 3028")
write_log("2. Confirmar se existe mapeamento correto entre sistemas")
write_log("3. Considerar usar nome da obra em vez de ID para mapeamento")
write_log("4. Verificar se houve alteração de ID da obra recentemente")

write_log(f"\n{'='*80}")
write_log("FIM DA INVESTIGAÇÃO")
write_log(f"{'='*80}")

log_file.close()
print(f"\nArquivo de investigação salvo: investigacao_hpb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")