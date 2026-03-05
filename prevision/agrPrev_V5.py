import requests
import csv
import os

# Query para listar projetos
query_projetos = """
query {
  me {
    projectsPage(first: 50) {
      nodes {
        id
        name
      }
    }
  }
}
"""

#Query para listar atividades e serviços de um projeto
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

# Query para listar budgetReports de um projeto
query_budget_reports = """
query BudgetReports($projectId: ID!) {
  me {
    project(id: $projectId) {
      budgetReports {
        id
        name
      }
    }
  }
}
"""

# Query para obter pesos dos orçamentos
query_pesos_orcamentos = """
query PesosOrcamentos($projectId: ID!, $budgetReportId: ID!, $budgetFilter: BudgetItemFilterInput!) {
  me {
    project(id: $projectId) {
      budgetReport(id: $budgetReportId) {
        budgetItemsPage(budgetFilter: $budgetFilter) {
          nodes {
            id
            code
            description
            totalCost
            weightLevel
            budgetWeights {
              id
              percentage
              activity {
                id
                percentageCompleted
                expectedPercentageCompleted
                service {
                  id
                  name
                }
                floor {
                  id
                  name
                }
              }
              jobBudgetWeights {
                id
                percentage
                job {
                  id
                  name
                  part
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

# Definindo a query GraphQL para CffTableQuery
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

# Definindo a query GraphQL para BudgetReportsWithSiengeWhitelist
query_budget_reports_with_sienge = """
query BudgetReportsWithSiengeWhitelist($projectId: ID!) {
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

# Função para buscar os orçamentos com informações do Sienge
def buscar_budget_reports_with_sienge(projeto_id):
    # Configurando as variáveis para a query
    variables = {"projectId": projeto_id}
    
    # Enviando a requisição POST para o endpoint da API GraphQL
    response = requests.post(
        url,  # Substitua 'url' pela URL real da sua API GraphQL
        json={"query": query_budget_reports_with_sienge, "variables": variables},
        headers=headers  # Substitua 'headers' pelos cabeçalhos necessários (ex.: autenticação)
    )
    
    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        
        # Verificando se há erros na resposta
        if "errors" in data:
            print(f"Erro ao buscar orçamentos com Sienge para o projeto {projeto_id}: {data['errors']}")
            return {}
        
        # Retornando os dados relevantes
        return data.get("data", {}).get("me", {}).get("project", {}).get("budgetReports", [])
    else:
        # Caso a requisição falhe, imprime o status code
        print(f"Erro ao buscar orçamentos com Sienge para o projeto {projeto_id}: {response.status_code}")
        return []

# Função pra trazer evolução da obra
query_default_dashboard = """
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

def buscar_dados_dashboard(projeto_id):
    # Configurando as variáveis para a query
    variables = {"projectId": projeto_id}
    
    response = requests.post(
        url,  # Substitua pela URL da sua API GraphQL
        json={"query": query_default_dashboard, "variables": variables},
        headers=headers  # Substitua pelos seus headers de autenticação
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if "errors" in data:
            print(f"Erro ao buscar dados do dashboard para o projeto {projeto_id}: {data['errors']}")
            return {}
        
        # Pegando a info do detailedDashboard > generalInfo
        return data.get("data", {}).get("me", {}).get("project", {}).get("detailedDashboard", {}).get("generalInfo", {})
    else:
        print(f"Erro ao buscar dados do dashboard para o projeto {projeto_id}: {response.status_code}")
        return {}

# Função para buscar os dados da tabela CFF de um orçamento específico
def buscar_cff_table(projeto_id, budget_report_id):
    # Configurando as variáveis para a query
    variables = {
        "projectId": projeto_id,
        "budgetReportId": budget_report_id
    }
    
    # Enviando a requisição POST para o endpoint da API GraphQL
    response = requests.post(
        url,  # Substitua 'url' pela URL real da sua API GraphQL
        json={"query": query_cff_table, "variables": variables},
        headers=headers  # Substitua 'headers' pelos cabeçalhos necessários (ex.: autenticação)
    )
    
    # Verificando se a requisição foi bem-sucedida
    if response.status_code == 200:
        data = response.json()
        
        # Verificando se há erros na resposta
        if "errors" in data:
            print(f"Erro ao buscar CFF Table para o projeto {projeto_id} e orçamento {budget_report_id}: {data['errors']}")
            return {}
        
        # Retornando os dados relevantes
        return data.get("data", {}).get("me", {}).get("project", {}).get("budgetReport", {})
    else:
        # Caso a requisição falhe, imprime o status code
        print(f"Erro ao buscar CFF Table para o projeto {projeto_id} e orçamento {budget_report_id}: {response.status_code}")
        return {}

# Função para buscar projetos
def buscar_projetos():
    response = requests.post(url, json={"query": query_projetos}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {}).get("me", {}).get("projectsPage", {}).get("nodes", [])
    else:
        print(f"Erro ao buscar projetos: {response.status_code}")
        return []

# Função para determinar o tipo de projeto com base em serviços e andares
def determinar_tipo_projeto(projeto_data):
    floors = projeto_data.get("floorsPage", {}).get("nodes", [])
    services = [activity.get("service", {}).get("name", "") for floor in floors for activity in floor.get("activitiesPage", {}).get("nodes", [])]
    incorporacao_keywords = ["licenciamento", "INC-", "comercial", "incorporação"]
    obra_keywords = ["fundação", "contenção", "obra", "fase"]
    if any(keyword in service.lower() for keyword in incorporacao_keywords for service in services):
        return "Incorporação"
    floor_names = [floor.get("name", "").lower() for floor in floors]
    if any(keyword in name for keyword in incorporacao_keywords for name in floor_names):
        return "Incorporação"
    return "Obra"

# Função para buscar budgetReports de um projeto
def buscar_budget_reports(projeto_id):
    variables = {"projectId": projeto_id}
    response = requests.post(url, json={"query": query_budget_reports, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"Erro ao buscar budgetReports para o projeto {projeto_id}: {data['errors']}")
            return []
        return data.get("data", {}).get("me", {}).get("project", {}).get("budgetReports", [])
    else:
        print(f"Erro ao buscar budgetReports para o projeto {projeto_id}: {response.status_code}")
        return []

# Função para buscar pesos dos orçamentos
def buscar_pesos_orcamentos(projeto_id, budget_report_id):
    variables = {
        "projectId": projeto_id,
        "budgetReportId": budget_report_id,
        "budgetFilter": {}
    }
    response = requests.post(url, json={"query": query_pesos_orcamentos, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"Erro na consulta GraphQL para o projeto {projeto_id} com budgetReportId {budget_report_id}: {data['errors']}")
            return {}
        return data.get("data", {}).get("me", {}).get("project", {})
    else:
        print(f"Erro ao buscar pesos para o projeto {projeto_id} com budgetReportId {budget_report_id}: {response.status_code}")
        return {}

# Função para extrair o agrupador do nome do serviço
def extrair_agrupador(nome_servico):
    # Extrai o prefixo antes do "-"
    if "-" in nome_servico:
        return nome_servico.split("-")[0].strip()
    return "Não especificado"

# Função para buscar atividades e serviços de um projeto
def buscar_activities(projeto_id):
    variables = {"projectId": projeto_id, "jobsWithDates": False}
    response = requests.post(url, json={"query": query_activities, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"Erro ao buscar activities para o projeto {projeto_id}: {data['errors']}")
            return {}
        return data.get("data", {}).get("me", {}).get("project", {})
    else:
        print(f"Erro ao buscar activities para o projeto {projeto_id}: {response.status_code}")
        return {}

def trazEvDaApropr(relCff, dicEvPorID):
  logging = False

  #if 'NAUT' in relCff['name']:
  #    logging = True
      
  vincEAPdic = {}
  dadosCFF = relCff['cffTable']['rows']

  for d in dadosCFF:

    dadosBudget = d['budgetItem']
    servicos = dadosBudget['budgetWeights']
    codEAP = dadosBudget['code']
    codEAPExp = codEAP.split('.')
    codEAPAJ = []
    for c in codEAPExp:
        coriginal = str(c)
        if c != codEAPExp[0]:
          if len(c) < 3:
              for dif in range(3 - len(c)):
                coriginal = '0'+coriginal
        else:
          if len(c) < 2:
              for dif in range(2 - len(c)):
                coriginal = '0'+coriginal
        codEAPAJ.append(coriginal)
    codEAPNova = '.'.join(codEAPAJ)

    if len(servicos) != 0:

      evoPonderada = 0

      for s in servicos:
          idServ = s['activity']['id']
          pesoServ = float(s['percentage'])
          try:
              evoPonderada += (dicEvPorID[idServ]* pesoServ)
          except KeyError:
              evoPonderada += 0
      
      vincEAPdic[codEAPNova] = round(evoPonderada, 4)

    else:
      evoPonderada = 0
      vincEAPdic[codEAPNova] = evoPonderada

    if logging:
      if '08' in codEAP:
          print(codEAP, servicos, evoPonderada)
      if '07' in codEAP:
          print(codEAP, servicos, evoPonderada)
  
  return(vincEAPdic)

def dicEvolAtividadePorId(dadosOrcamento):
    '''
    pega infos do orcamento do prevision e tras a evolução atual por id
    '''
    dicEvoSrv = {}
        
    #for d in dadosOrcamento['budgetReport']['budgetItemsPage']['nodes']:
    #    print(d, file=open('nodesTest.txt', mode='w'))
    
    itens = dadosOrcamento['budgetReport']['budgetItemsPage']['nodes']
    for i in itens:
        dadosAtiv = i['budgetWeights']
        if len(dadosAtiv) != 0:
            for ativ in dadosAtiv:
                percAvanc = ativ['activity']['percentageCompleted']
                if percAvanc == None:
                    percAvanc = 0
                dicEvoSrv[ativ['activity']['id']] = percAvanc
    
    return(dicEvoSrv)

def dicEvolAtividadePorId_atividade(dadosAtividade):
    '''
    pega infos de atividade do prevision e tras a evolução atual por id
    '''
    dicEvoSrv = {}
        
    #for d in dadosOrcamento['budgetReport']['budgetItemsPage']['nodes']:
    #    print(d, file=open('nodesTest.txt', mode='w'))
    
    andares = dadosAtividade['floorsPage']['nodes']
    for a in andares:
        dadosAtiv = a['activitiesPage']['nodes']
        if len(dadosAtiv) != 0:
            for ativ in dadosAtiv:
                percAvanc = ativ['percentageCompleted']
                if percAvanc == None:
                    percAvanc = 0
                dicEvoSrv[ativ['id']] = round(percAvanc/100, 4)
    
    return(dicEvoSrv)

# URL do endpoint GraphQL
token = os.environ.get('PREVISION_TOKEN')
url = "https://api.prevision.com.br/graphql"
headers = {
    "Accept": "application/json",
    "UserAuthorization": f"token {token}",
    "Content-Type": "application/json"
}

# Configuração do arquivo CSV
relatorio_servico = csv.writer(open('VersãoAgrupada.csv', mode='w', encoding='utf-8-sig', newline=''), delimiter=';')
cabecalho_rel_serv = [
    'ID do projeto',
    'Nome do projeto',
    'Tipo de projeto',
    'ID do andar',
    'Nome do andar',
    'Agrupador de Serviço',  # Nova coluna para agrupar serviços
    'ID do serviço',
    'Nome do serviço',
    'Evolução Real (%)',
    'Evolução Base (%)',
    'Evolução Esperada (%)',
    'Peso do serviço',  # Campo para peso do serviço
    'Peso da etapa',    # Campo para peso da etapa
    'Valor Orçado',     # Novo campo para o custo orçado
    'ID do contrato'
]
relatorio_servico.writerow(cabecalho_rel_serv)

# Processar todos os projetos
projetos = buscar_projetos()
if not projetos:
    print("Nenhum projeto encontrado!")
else:
    print(f"{len(projetos)} projeto(s) encontrado(s):")
    #for p in projetos:
    #    print(f" - {p['name']} (ID: {p['id']})")

#atividades_teste = buscar_activities(id_projeto_teste)
#novaconsulta = buscar_cff_table(id_projeto_teste, '41111')
#evolProjeto2 = dicEvolAtividadePorId_atividade(atividades_teste)
#dados = novaconsulta['cffTable']['rows']
#dadosEAP = trazEvDaApropr(novaconsulta, evolProjeto2)

logging = False
results = {}
filtrosProjeto = [
    'OCEAN VIEW',
    'VIVAPARK',
    'LEVEL',
    'LUME',
    'LEME',
    'Teste',
    'TESTE',
    '[Teste] - Gestão de Contratos',
]
filtroPositivo = [
    'NAUT - 2024'
]
tipoFiltro = False

evoProjetos = {}

def novoloop():
  prints = 0
  for projeto in projetos:
    projeto_id = projeto['id']
    projeto_nome = projeto['name']

    if tipoFiltro:
      if projeto_nome not in filtroPositivo:
        print(projeto_nome, 'no filtro de exclusão')
        continue
    else:
      if projeto_nome in filtrosProjeto:
        print(projeto_nome, 'no filtro de exclusão')
        continue
    # Buscar budgetReports do projeto
    budget_reports = buscar_budget_reports(projeto_id)
    if not budget_reports:
      print(f"Nenhum budgetReport encontrado para o projeto {projeto_nome}.")
      continue

    # Consultar pesos para cada budgetReport
    for budget_report in budget_reports:
      budget_report_id = budget_report.get("id", "")
      budget_report_name = budget_report.get("name", "")
      if "COMU" in budget_report_name:
          continue
      #print(f"Consultando pesos para {projeto_nome} usando budgetReport {budget_report_name}...")
        
      projeto_data = buscar_pesos_orcamentos(projeto_id, budget_report_id)
      if not projeto_data:
          print(f"Nenhum dado de peso retornado para o projeto {projeto_nome} com budgetReport {budget_report_name}.")
          continue

      # Determinar o tipo de projeto
      tipo_projeto = determinar_tipo_projeto(projeto_data)

      if tipo_projeto == "Obra":
        projetoCFF = buscar_cff_table(projeto_id, budget_report_id)
        print('Buscando cronograma do projeto com id', projeto_nome)
        atividadesProjeto = buscar_activities(projeto_id)
        print('Buscando atividades do projeto com id', projeto_nome)
        evolProjPorID = dicEvolAtividadePorId_atividade(atividadesProjeto)
        dadosEAP = trazEvDaApropr(projetoCFF, evolProjPorID)
        results[str(projeto_nome).split(' - ')[1]] = dadosEAP
        evoProjetos[str(projeto_nome).split(' - ')[1]] = buscar_dados_dashboard(projeto_id)['realized']
        if logging:
          if "NAUT" in projeto_nome:
              print(projetoCFF, file=open('nautCFF.txt', mode='w', encoding='utf-8-sig'))
              print(atividadesProjeto, file=open('nautAtiv.txt', mode='w', encoding='utf-8-sig'))
              print(evolProjPorID, file=open('nautEvol.txt', mode='w', encoding='utf-8-sig'))
              print(dadosEAP, file=open('nautdadosEAP.txt', mode='w', encoding='utf-8-sig'))
        if prints == 0:
            #print(dadosEAP)
            prints+=1

  return(results)

def trazDadosEvol():
   return(evoProjetos)