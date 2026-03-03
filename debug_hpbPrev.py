import requests
import json
from datetime import datetime

# Configuração do arquivo de log
log_file = open(f'debug_prevision_2028_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w', encoding='utf-8')

def write_log(mensagem, nivel=0):
    indent = "  " * nivel
    linha = f"{indent}{mensagem}"
    print(linha)
    log_file.write(linha + "\n")
    log_file.flush()

# Configuração da API Prevision
token = "6r6LVwYARqrBuibv3ZB366LT"
url = "https://api.prevision.com.br/graphql"
headers = {
    "Accept": "application/json",
    "UserAuthorization": f"token {token}",
    "Content-Type": "application/json"
}

write_log("=" * 100)
write_log("DEBUG DETALHADO PREVISION - OBRA 2028")
write_log(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
write_log("=" * 100)

def executar_query(query, variables, nome_query):
    """Executa uma query GraphQL e loga detalhadamente"""
    write_log(f"\n{'='*80}")
    write_log(f"EXECUTANDO QUERY: {nome_query}")
    write_log(f"{'='*80}")
    
    write_log("QUERY:")
    for i, linha in enumerate(query.strip().split('\n'), 1):
        write_log(f"{i:3d}: {linha}")
    
    write_log(f"\nVARIABLES:")
    write_log(json.dumps(variables, indent=2, ensure_ascii=False))
    
    write_log(f"\nENVIANDO REQUEST...")
    
    try:
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=30
        )
        
        write_log(f"STATUS CODE: {response.status_code}")
        write_log(f"HEADERS RESPONSE: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            
            write_log(f"\nRESPOSTA RECEBIDA:")
            write_log(f"Tamanho da resposta: {len(response.text)} caracteres")
            
            if "errors" in data:
                write_log(f"\n❌ ERROS NA RESPOSTA:")
                for i, erro in enumerate(data["errors"], 1):
                    write_log(f"  Erro {i}: {erro}")
                return None
            
            write_log(f"\n✅ SUCESSO - Processando dados...")
            
            # Salva resposta completa em arquivo separado para análise
            with open(f'response_{nome_query.lower().replace(" ", "_")}_{datetime.now().strftime("%H%M%S")}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return data
            
        else:
            write_log(f"\n❌ ERRO HTTP: {response.status_code}")
            write_log(f"TEXTO RESPOSTA: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        write_log(f"\n❌ TIMEOUT na requisição")
        return None
    except Exception as e:
        write_log(f"\n❌ ERRO INESPERADO: {str(e)}")
        return None

# STEP 1: Buscar todos os projetos para encontrar o projeto 2028
write_log("\nSTEP 1: BUSCANDO TODOS OS PROJETOS")
write_log("-" * 50)

query_projetos = """
query {
  me {
    projectsPage(first: 100) {
      nodes {
        id
        name
      }
    }
  }
}
"""

projetos_data = executar_query(query_projetos, {}, "BUSCAR PROJETOS")

projeto_2028 = None
if projetos_data:
    projetos = projetos_data.get("data", {}).get("me", {}).get("projectsPage", {}).get("nodes", [])
    write_log(f"\nPROJETOS ENCONTRADOS: {len(projetos)}")
    
    for projeto in projetos:
        write_log(f"  ID: {projeto['id']} | Nome: '{projeto['name']}'")
        
        # Procura por 2028 no nome ou ID
        if '2028' in projeto['name'] or projeto['id'] == '2028':
            projeto_2028 = projeto
            write_log(f"  >>> PROJETO 2028 IDENTIFICADO! <<<")

if not projeto_2028:
    write_log(f"\n❌ PROJETO 2028 NÃO ENCONTRADO!")
    write_log("Verifique se o projeto existe ou se o nome/ID está correto")
    log_file.close()
    exit()

projeto_id = projeto_2028['id']
projeto_nome = projeto_2028['name']

write_log(f"\n✅ PROJETO ENCONTRADO:")
write_log(f"  ID: {projeto_id}")
write_log(f"  Nome: {projeto_nome}")

# STEP 2: Buscar Budget Reports do projeto
write_log(f"\nSTEP 2: BUSCANDO BUDGET REPORTS DO PROJETO {projeto_id}")
write_log("-" * 50)

query_budget_reports = """
query BudgetReports($projectId: ID!) {
  me {
    project(id: $projectId) {
      budgetReports {
        id
        name
        sienge {
          id
          siengeProjectId
          constructionUnitId
          contractWhitelisted
        }
      }
    }
  }
}
"""

budget_reports_data = executar_query(
    query_budget_reports, 
    {"projectId": projeto_id}, 
    "BUDGET REPORTS"
)

budget_reports = []
if budget_reports_data:
    reports = budget_reports_data.get("data", {}).get("me", {}).get("project", {}).get("budgetReports", [])
    write_log(f"\nBUDGET REPORTS ENCONTRADOS: {len(reports)}")
    
    for i, report in enumerate(reports, 1):
        write_log(f"\n  Report {i}:")
        write_log(f"    ID: {report['id']}")
        write_log(f"    Nome: '{report['name']}'")
        if report.get('sienge'):
            sienge_info = report['sienge']
            write_log(f"    Sienge ID: {sienge_info.get('siengeProjectId')}")
            write_log(f"    Construction Unit ID: {sienge_info.get('constructionUnitId')}")
            write_log(f"    Contract Whitelisted: {sienge_info.get('contractWhitelisted')}")
        
        # Filtra reports que não sejam COMU
        if "COMU" not in report['name']:
            budget_reports.append(report)

if not budget_reports:
    write_log(f"\n❌ NENHUM BUDGET REPORT VÁLIDO ENCONTRADO!")
    log_file.close()
    exit()

# STEP 3: Para cada Budget Report, buscar dados detalhados
for report in budget_reports:
    budget_report_id = report['id']
    budget_report_name = report['name']
    
    write_log(f"\nSTEP 3: PROCESSANDO BUDGET REPORT '{budget_report_name}'")
    write_log("-" * 80)
    
    # STEP 3A: Buscar CFF Table
    write_log(f"\nSTEP 3A: BUSCANDO CFF TABLE")
    write_log("-" * 40)
    
    query_cff_table = """
    query CffTableQuery($projectId: ID!, $budgetReportId: ID!) {
      me {
        project(id: $projectId) {
          budgetReport(id: $budgetReportId) {
            name
            cffTable {
              dates
              rows {
                budgetItem {
                  totalCost
                  budgetWeights {
                    jobBudgetWeights {
                      job {
                        name
                        part
                        activityId
                      }
                      percentage
                    }
                    percentage
                    activity {
                      id
                      service {
                        name
                      }
                      floor {
                        name
                      }
                    }
                  }
                  groupType
                  code
                  description
                  materialCost
                  laborCost
                  totalCost
                }
                startAt
                endAt
                basePoints {
                  x
                  y
                }
                expectedPoints {
                  x
                  y
                }
                realizedPoints {
                  x
                  y
                }
              }
            }
          }
        }
      }
    }
    """
    
    cff_data = executar_query(
        query_cff_table,
        {"projectId": projeto_id, "budgetReportId": budget_report_id},
        f"CFF TABLE - {budget_report_name}"
    )
    
    if cff_data:
        cff_table = cff_data.get("data", {}).get("me", {}).get("project", {}).get("budgetReport", {}).get("cffTable", {})
        
        if cff_table:
            rows = cff_table.get("rows", [])
            write_log(f"\n✅ CFF TABLE OBTIDA: {len(rows)} linhas")
            
            write_log(f"\nANÁLISE DOS CÓDIGOS EAP NA CFF TABLE:")
            codigos_eap_encontrados = {}
            
            for i, row in enumerate(rows[:10]):  # Analisa primeiras 10 linhas
                budget_item = row.get("budgetItem", {})
                code = budget_item.get("code", "")
                description = budget_item.get("description", "")
                budget_weights = budget_item.get("budgetWeights", [])
                
                write_log(f"\n  Linha {i+1}:")
                write_log(f"    Código EAP: '{code}'")
                write_log(f"    Descrição: '{description}'")
                write_log(f"    Budget Weights: {len(budget_weights)} itens")
                
                if code:
                    if code not in codigos_eap_encontrados:
                        codigos_eap_encontrados[code] = []
                    
                    # Analisa budget weights
                    for j, weight in enumerate(budget_weights[:3]):  # Primeiros 3
                        activity = weight.get("activity", {})
                        activity_id = activity.get("id", "")
                        service_name = activity.get("service", {}).get("name", "")
                        floor_name = activity.get("floor", {}).get("name", "")
                        percentage = weight.get("percentage", 0)
                        
                        write_log(f"      Weight {j+1}:")
                        write_log(f"        Activity ID: {activity_id}")
                        write_log(f"        Service: '{service_name}'")
                        write_log(f"        Floor: '{floor_name}'")
                        write_log(f"        Percentage: {percentage}")
                        
                        codigos_eap_encontrados[code].append({
                            'activity_id': activity_id,
                            'service': service_name,
                            'floor': floor_name,
                            'percentage': percentage
                        })
            
            if len(rows) > 10:
                write_log(f"\n  ... e mais {len(rows) - 10} linhas na CFF Table")
            
            # Resumo dos códigos EAP
            write_log(f"\nRESUMO DOS CÓDIGOS EAP ENCONTRADOS:")
            for code in sorted(codigos_eap_encontrados.keys())[:20]:
                qtd_weights = len(codigos_eap_encontrados[code])
                write_log(f"  {code}: {qtd_weights} budget weights")
        
        else:
            write_log(f"\n❌ CFF TABLE VAZIA OU INEXISTENTE")
    
    # STEP 3B: Buscar Activities
    write_log(f"\nSTEP 3B: BUSCANDO ACTIVITIES")
    write_log("-" * 40)
    
    query_activities = """
    query Activities($projectId: ID!, $jobsWithDates: Boolean) {
      me {
        project(id: $projectId) {
          name
          floorsPage {
            nodes {
              id
              name
              activitiesPage {
                nodes {
                  id
                  part
                  wbsCode
                  percentageCompleted
                  expectedPercentageCompleted
                  startAt
                  endAt
                  duration: workDuration
                  service {
                    name
                  }
                  floor {
                    name
                  }
                  jobs(withDates: $jobsWithDates) {
                    id
                    name
                    wbsCode
                    percentageCompleted
                    expectedPercentageCompleted
                    startAt
                    endAt
                    duration
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    
    activities_data = executar_query(
        query_activities,
        {"projectId": projeto_id, "jobsWithDates": False},
        f"ACTIVITIES - {budget_report_name}"
    )
    
    if activities_data:
        project_data = activities_data.get("data", {}).get("me", {}).get("project", {})
        floors = project_data.get("floorsPage", {}).get("nodes", [])
        
        write_log(f"\n✅ ACTIVITIES OBTIDAS: {len(floors)} andares")
        
        total_activities = 0
        activities_com_percentual = 0
        percentuais_exemplo = []
        
        for floor in floors[:5]:  # Analisa primeiros 5 andares
            floor_name = floor.get("name", "")
            activities = floor.get("activitiesPage", {}).get("nodes", [])
            
            write_log(f"\n  Andar: '{floor_name}' - {len(activities)} atividades")
            
            for activity in activities[:3]:  # Primeiras 3 atividades por andar
                activity_id = activity.get("id", "")
                wbs_code = activity.get("wbsCode", "")
                percentage = activity.get("percentageCompleted")
                service_name = activity.get("service", {}).get("name", "")
                
                write_log(f"    Activity ID: {activity_id}")
                write_log(f"      WBS Code: '{wbs_code}'")
                write_log(f"      Service: '{service_name}'")
                write_log(f"      Percentage: {percentage}")
                
                total_activities += 1
                if percentage is not None:
                    activities_com_percentual += 1
                    percentuais_exemplo.append(percentage)
        
        write_log(f"\nESTATÍSTICAS DAS ACTIVITIES:")
        write_log(f"  Total analisado: {total_activities} atividades")
        write_log(f"  Com percentual: {activities_com_percentual} atividades")
        if percentuais_exemplo:
            write_log(f"  Percentuais exemplo: {percentuais_exemplo[:10]}")

# STEP 4: Buscar Dashboard Data (evolução geral)
write_log(f"\nSTEP 4: BUSCANDO DASHBOARD DATA")
write_log("-" * 50)

query_dashboard = """
query DefaultDashboardProjectData($projectId: ID!) {
  me {
    project(id: $projectId) {
      detailedDashboard {
        generalInfo
      }
    }
  }
}
"""

dashboard_data = executar_query(
    query_dashboard,
    {"projectId": projeto_id},
    "DASHBOARD DATA"
)

if dashboard_data:
    general_info = dashboard_data.get("data", {}).get("me", {}).get("project", {}).get("detailedDashboard", {}).get("generalInfo", {})
    
    if general_info:
        write_log(f"\n✅ DASHBOARD DATA OBTIDA:")
        write_log(f"General Info keys: {list(general_info.keys())}")
        
        # Busca especificamente por dados de evolução
        for key, value in general_info.items():
            if isinstance(value, (int, float)):
                write_log(f"  {key}: {value}")
            elif isinstance(value, str):
                write_log(f"  {key}: '{value}'")
            else:
                write_log(f"  {key}: {type(value)} - {str(value)[:100]}...")

write_log(f"\n{'='*100}")
write_log("RESUMO FINAL DO DEBUG")
write_log(f"{'='*100}")

write_log(f"Projeto analisado: {projeto_nome} (ID: {projeto_id})")
write_log(f"Budget Reports processados: {len(budget_reports)}")
write_log("Dados coletados com sucesso:")
write_log("  ✓ Lista de projetos")
write_log("  ✓ Budget Reports")
write_log("  ✓ CFF Tables")
write_log("  ✓ Activities")
write_log("  ✓ Dashboard Data")

write_log(f"\nArquivos JSON gerados com respostas detalhadas:")
write_log("  - response_buscar_projetos_*.json")
write_log("  - response_budget_reports_*.json")
write_log("  - response_cff_table_*.json")
write_log("  - response_activities_*.json")
write_log("  - response_dashboard_data_*.json")

write_log(f"\n{'='*100}")
write_log("FIM DO DEBUG DETALHADO")
write_log(f"{'='*100}")

log_file.close()
print(f"\nArquivo de debug salvo: debug_prevision_2028_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
print("Arquivos JSON com respostas completas também foram salvos para análise detalhada.")