import json
from bases import carregabases
from datetime import datetime

# Configuração do arquivo de log
log_file = open(f'analise_eap_hpb_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w', encoding='utf-8')

def write_log(mensagem, nivel=0):
    indent = "  " * nivel
    linha = f"{indent}{mensagem}"
    print(linha)
    log_file.write(linha + "\n")
    log_file.flush()

write_log("=" * 80)
write_log("ANÁLISE MAPEAMENTO EAP - OBRA HPB")
write_log(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
write_log("=" * 80)

# Carrega bases
baseItens = carregabases.itensContratos()
dadosPrev = json.load(open('dadosPrevision.json', mode='r', encoding='utf-8-sig'))
orcObras = json.load(open('baseOrc.json', encoding='utf-8-sig'))

# Ajuste dos códigos 06.06 para 06.006
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

# Busca contratos HPB
contratos_hpb = []
for cont in baseItens:
    if len(cont['buildings']) == 0:
        continue
    
    buildingId = cont['buildings'][0]['buildingId']
    buildingName = cont['buildings'][0]['name']
    
    if 'HPB - Obra' in buildingName.upper() or buildingId in [2028, '2028']:
        contratos_hpb.append(cont)

if not contratos_hpb:
    write_log("ERRO: Obra HPB não encontrada")
    write_log("Obras disponíveis:")
    for cont in baseItens:
        if len(cont['buildings']) > 0:
            write_log(f"  ID: {cont['buildings'][0]['buildingId']}, Nome: {cont['buildings'][0]['name']}")
    log_file.close()
    exit()

# Identifica o ID da obra HPB
obra_hpb_id = str(contratos_hpb[0]['buildings'][0]['buildingId'])
write_log(f"Obra HPB identificada: ID {obra_hpb_id}")

# ANÁLISE 1: Códigos EAP no Sienge (apropriações)
write_log("\n" + "="*60)
write_log("1. CÓDIGOS EAP DO SIENGE (APROPRIAÇÕES)")
write_log("="*60)

codigos_sienge = set()
for cont in contratos_hpb:
    if "1" in cont['itens']:
        for item in cont['itens']["1"]:
            for aprop in item['buildingAppropriations']:
                codigos_sienge.add(aprop['wbsCode'])

codigos_sienge_ordenados = sorted(list(codigos_sienge))
write_log(f"Total de códigos EAP únicos no Sienge: {len(codigos_sienge_ordenados)}")
write_log("\nCódigos encontrados:")
for cod in codigos_sienge_ordenados:
    write_log(f"  {cod}")

# ANÁLISE 2: Códigos EAP no Prevision
write_log("\n" + "="*60)
write_log("2. CÓDIGOS EAP DO PREVISION")
write_log("="*60)

if obra_hpb_id in dadosPrev:
    codigos_prevision = list(dadosPrev[obra_hpb_id].keys())
    write_log(f"Total de códigos EAP no Prevision: {len(codigos_prevision)}")
    write_log("\nCódigos encontrados (primeiros 30):")
    for cod in sorted(codigos_prevision)[:30]:
        valor = dadosPrev[obra_hpb_id][cod]
        write_log(f"  {cod}: {valor:.4f}")
    
    if len(codigos_prevision) > 30:
        write_log(f"\n  ... e mais {len(codigos_prevision) - 30} códigos")
else:
    write_log(f"ERRO: Obra {obra_hpb_id} não encontrada no Prevision")
    write_log(f"Obras disponíveis no Prevision: {list(dadosPrev.keys())}")

# ANÁLISE 3: Códigos EAP no Orçamento Sienge
write_log("\n" + "="*60)
write_log("3. CÓDIGOS EAP DO ORÇAMENTO SIENGE")
write_log("="*60)

if obra_hpb_id in orcObras:
    codigos_orcamento = list(orcObras[obra_hpb_id].keys())
    write_log(f"Total de códigos EAP no orçamento: {len(codigos_orcamento)}")
    write_log("\nCódigos encontrados (primeiros 30):")
    for cod in sorted(codigos_orcamento)[:30]:
        peso = orcObras[obra_hpb_id][cod]['peso']
        total = orcObras[obra_hpb_id][cod]['total']
        write_log(f"  {cod}: peso={peso:.4f}, total=R${total:,.2f}")
    
    if len(codigos_orcamento) > 30:
        write_log(f"\n  ... e mais {len(codigos_orcamento) - 30} códigos")
else:
    write_log(f"ERRO: Obra {obra_hpb_id} não encontrada no orçamento")

# ANÁLISE 4: Padrões e estruturas
write_log("\n" + "="*60)
write_log("4. ANÁLISE DE PADRÕES")
write_log("="*60)

# Analisa níveis dos códigos Sienge
niveis_sienge = {}
for cod in codigos_sienge_ordenados:
    nivel = cod.count('.')
    if nivel not in niveis_sienge:
        niveis_sienge[nivel] = []
    niveis_sienge[nivel].append(cod)

write_log("Distribuição por níveis - SIENGE:")
for nivel in sorted(niveis_sienge.keys()):
    write_log(f"  {nivel} níveis: {len(niveis_sienge[nivel])} códigos")
    # Mostra alguns exemplos
    exemplos = niveis_sienge[nivel][:5]
    write_log(f"    Exemplos: {', '.join(exemplos)}")

# Analisa níveis dos códigos Prevision
if obra_hpb_id in dadosPrev:
    niveis_prevision = {}
    for cod in codigos_prevision:
        nivel = cod.count('.')
        if nivel not in niveis_prevision:
            niveis_prevision[nivel] = []
        niveis_prevision[nivel].append(cod)

    write_log("\nDistribuição por níveis - PREVISION:")
    for nivel in sorted(niveis_prevision.keys()):
        write_log(f"  {nivel} níveis: {len(niveis_prevision[nivel])} códigos")
        exemplos = niveis_prevision[nivel][:5]
        write_log(f"    Exemplos: {', '.join(exemplos)}")

# ANÁLISE 5: Tentativa de mapeamento
write_log("\n" + "="*60)
write_log("5. TENTATIVA DE MAPEAMENTO")
write_log("="*60)

def tentar_mapear_codigo(cod_sienge, codigos_prevision_dict):
    """Tenta mapear código do Sienge para Prevision"""
    partes = cod_sienge.split('.')
    
    # Tenta diferentes combinações
    tentativas = []
    
    # 1. Código completo
    tentativas.append(cod_sienge)
    
    # 2. Primeiros 2 níveis (ex: 06.002.001.001 -> 06.002)
    if len(partes) >= 2:
        tentativas.append('.'.join(partes[:2]))
    
    # 3. Primeiro nível (ex: 06.002.001.001 -> 06)
    tentativas.append(partes[0])
    
    # 4. Ajustar formato (ex: 06 -> 6, 02 -> 2)
    if partes[0].startswith('0'):
        tentativas.append(partes[0][1:])
    
    # 5. Diferentes combinações com zeros
    if len(partes) >= 2:
        p1 = partes[0][1:] if partes[0].startswith('0') else partes[0]
        p2 = partes[1][1:] if partes[1].startswith('0') else partes[1]
        tentativas.append(f"{p1}.{p2}")
    
    for tentativa in tentativas:
        if tentativa in codigos_prevision_dict:
            return tentativa, codigos_prevision_dict[tentativa]
    
    return None, 0

# Testa mapeamento para códigos problemáticos
codigos_teste = ['06.002.001.001', '06.002.001.002', '06.002.001.003', '06.002.001.004', '06.002.001.005']

if obra_hpb_id in dadosPrev:
    write_log("Testando mapeamento para códigos problemáticos:")
    for cod_teste in codigos_teste:
        if cod_teste in codigos_sienge_ordenados:
            resultado, valor = tentar_mapear_codigo(cod_teste, dadosPrev[obra_hpb_id])
            if resultado:
                write_log(f"  {cod_teste} -> {resultado}: {valor:.4f}")
            else:
                write_log(f"  {cod_teste} -> NÃO MAPEADO")

# ANÁLISE 6: Possíveis correspondências por padrão
write_log("\n" + "="*60)
write_log("6. POSSÍVEIS CORRESPONDÊNCIAS")
write_log("="*60)

if obra_hpb_id in dadosPrev:
    # Agrupa códigos Sienge por primeiro nível
    grupos_sienge = {}
    for cod in codigos_sienge_ordenados:
        primeiro = cod.split('.')[0]
        if primeiro not in grupos_sienge:
            grupos_sienge[primeiro] = []
        grupos_sienge[primeiro].append(cod)
    
    # Agrupa códigos Prevision por primeiro nível
    grupos_prevision = {}
    for cod in codigos_prevision:
        primeiro = cod.split('.')[0]
        if primeiro not in grupos_prevision:
            grupos_prevision[primeiro] = []
        grupos_prevision[primeiro].append(cod)
    
    write_log("Comparação por primeiro nível:")
    for nivel in sorted(set(list(grupos_sienge.keys()) + list(grupos_prevision.keys()))):
        sienge_count = len(grupos_sienge.get(nivel, []))
        prevision_count = len(grupos_prevision.get(nivel, []))
        write_log(f"  Nível {nivel}:")
        write_log(f"    Sienge: {sienge_count} códigos")
        write_log(f"    Prevision: {prevision_count} códigos")
        
        if nivel in grupos_prevision and prevision_count > 0:
            write_log(f"    Prevision exemplos: {', '.join(grupos_prevision[nivel][:3])}")

# ANÁLISE 7: Sugestões de correção
write_log("\n" + "="*60)
write_log("7. SUGESTÕES DE CORREÇÃO")
write_log("="*60)

write_log("Problemas identificados:")
write_log("1. Estrutura EAP incompatível entre Sienge (4 níveis) e Prevision (2-3 níveis)")
write_log("2. Códigos do tipo 06.002.001.xxx não encontram correspondência")
write_log("3. Possível diferença na numeração (06 vs 6)")

write_log("\nSoluções propostas:")
write_log("1. Implementar mapeamento automático de códigos")
write_log("2. Usar agregação por níveis superiores")
write_log("3. Verificar configuração EAP no Prevision")
write_log("4. Aplicar fallback para evolução geral da obra")

write_log(f"\n{'='*80}")
write_log("FIM DA ANÁLISE EAP HPB")
write_log(f"{'='*80}")

log_file.close()
print(f"\nArquivo de análise salvo: analise_eap_hpb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")