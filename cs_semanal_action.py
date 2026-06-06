# -*- coding: utf-8 -*-
import requests
import json
import os
import sys
import unicodedata
from datetime import datetime, timedelta

CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
META_TOKEN = os.environ.get("META_TOKEN", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLICKUP_LIST_ID = "901325426193"
BASE_INTELIGENCIA_LIST_ID = "901327293866"
IA_MODEL = "claude-sonnet-4-6"
PIX_SEMANAL = 300.0

if not CLICKUP_TOKEN or not META_TOKEN:
    print("ERRO: Tokens nao configurados.")
    sys.exit(1)

CAMPOS = {
    "cliente":            "b9892282-cac2-41f8-8e39-59bb0ee89c53",
    "plataforma":         "1e2811d8-af23-455b-92eb-0bc995d8b664",
    "meta_cpl":           "4149e4ca-b01f-426b-b6bd-16c9c4add0c3",
    "cpl_7d":             "5407a9f2-247d-461f-add3-ad0e1ff9dbf6",
    "leads_7d":           "ae4741ba-ed7b-422b-99e2-71dfb6b9599f",
    "leads_14d":          "842ed666-ad6f-4999-821e-4a333f0fe605",
    "leads_21d":          "a1419879-438f-4b9f-a62a-629833040343",
    "leads_30d":          "45c4b282-23d3-479c-b29f-45c0194fec38",
    "pgto_ca":            "6644e4a1-e68c-4015-80dc-28f4d0785847",
    "link_grupo":         "99e9eded-f032-4554-b500-2df1a8b1ab02",
    "gargalo":            "ea72efed-ab12-4396-8c71-dcd7530b72e5",
    "ultima_atualizacao": "875e9007-605a-4cc1-afc0-4127e4fef483",
    "nicho":              "4b7323bc-de4e-43ab-970e-8a1ff3855c91",
    "saude_conta":        "52652d4c-250c-43ad-b6c7-fc15d2d4879a",
    "fase_campanha":      "592b5368-2199-4201-9de5-8c4544ec1e35",
    "orcamento_midia":    "ea84ccdd-414f-475d-81f3-51a45b6252f9",
    "status_financeiro":  "4712f853-fdf7-4ad1-8882-3c1fca98818e",
    "obs_semana":         "d0b56406-5562-46ae-a2b7-6a8f915b6895",
}

MAPA = {
    # ── Clientes com nome original ──────────────────────────────
    "Juliana Couto":                "981821890966321",
    "Rogério":                      "1426016344887799",
    "Débora e Dilson":              "161254036978153",
    "Mamuh Steakhouse":             "892974669033947",
    # ── Nomes antigos mantidos + nomes novos do ClickUp ────────
    "Jessíca Machado":              "2104277963310752",
    "Istituto Lopes Machado":       "2104277963310752",
    "Grasielli e Amanda":           "957299715350643",
    "Stillo":                       "957299715350643",
    "Kaüe/Cristian":                "1092853728175420",
    "Kaue/Cristian":                "1092853728175420",  # fallback sem acento
    "Athenas":                      "1092853728175420",
    "Jozi":                         "876814367940864",
    "Bom Boi":                      "876814367940864",
    "Matheus":                      "987188046671152",
    "Exclusive":                    "987188046671152",
    "Rafael Gentine - Limeira/SP":  "1269260778582752",
    "Rafael Gentine - Macapá/AP":   "352322129822164",
    "Rafael Gonzaga - Santarém/PR": "1226501099425856",
    "Ademir":                       "570493612230387",
    "Tendência Planejados":         "1451590226264346",
    "Tendências":                   "1451590226264346",
    "Patricía":                     "1451590226264346",  # mesmo que Tendências
    "Torre Estruturas":             "956582003798132",
    "Torre Estrutura":              "956582003798132",  # cobre "Torre Estrutura metálica"
    # ── Novos clientes ─────────────────────────────────────────
    "Mercado da Semijoias":         "226229720209425",
    "Rafael Breda":                 "226229720209425",  # mesmo que Mercado da Semijoias
    "Tulli":                        "1397248371252598",
    "Denise":                       "1397248371252598",  # mesmo que Tulli
    "Limer Modulos":                "1713522899816834",
    "Paulo e Bruna":                "1713522899816834",  # mesmo que Limer Modulos
}

ABERTURAS = {
    "estetica": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, vamos nessa. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de entrar no ritmo da semana, um olhar nos numeros da anterior. Relatorio de {ini} a {fim}."),
        ("parceria", "Oi pessoal, tudo bem? Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio da semana {ini} a {fim} abaixo. Bora ver como foi."),
        ("contexto", "Bom dia pessoal! Semana movimentada no digital — vamos ver o que os numeros mostram. Relatorio {ini} a {fim}."),
    ],
    "odontologia": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, agenda cheia. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de comecar a semana, um olhar nos resultados da anterior. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para deixar o relatorio da semana {ini} a {fim} e alinhar os proximos passos."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Vamos ver como ficaram as oportunidades da semana."),
        ("contexto", "Bom dia pessoal! Paciente decidido busca rapido — vamos ver o que a semana entregou. Relatorio {ini} a {fim}."),
    ],
    "moveis": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nNova semana, novos projetos. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Um olhar nos numeros antes de entrar no ritmo da semana. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados e o que vem por ai. Relatorio {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio da semana {ini} a {fim}. Vamos ver como ficaram as oportunidades."),
        ("contexto", "Bom dia pessoal! Moveis planejados tem ciclo longo — cada oportunidade conta. Relatorio {ini} a {fim}."),
    ],
    "atacado": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora crescer o volume. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de entrar no ritmo, um olhar nos numeros da semana passada. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Vamos ver como foi o volume de oportunidades."),
        ("contexto", "Bom dia pessoal! No atacado volume e consistencia andam juntos — vamos ver os numeros. Relatorio {ini} a {fim}."),
    ],
    "farmacia": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, vamos nessa. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Um olhar nos resultados antes de comecar a semana. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os numeros da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficaram as oportunidades da semana."),
        ("contexto", "Bom dia pessoal! Retorno rapido faz diferenca na farmacia — vamos ver o que a semana entregou. Relatorio {ini} a {fim}."),
    ],
    "vestuario": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora movimentar. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de entrar no ritmo da semana, um olhar nos numeros. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Vamos ver como ficou o movimento de oportunidades."),
        ("contexto", "Bom dia pessoal! Moda tem sazonalidade — vamos ver o que a semana entregou. Relatorio {ini} a {fim}."),
    ],
    "acougue": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora manter o movimento. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Um olhar nos numeros antes de comecar a semana. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para deixar o relatorio da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficaram as oportunidades da semana."),
        ("contexto", "Bom dia pessoal! Cliente de acougue e fiel quando bem atendido — vamos ver o que a semana entregou. Relatorio {ini} a {fim}."),
    ],
    "joias": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora brilhar. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de entrar no ritmo, um olhar nos numeros da semana passada. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Vamos ver como ficaram as oportunidades."),
        ("contexto", "Bom dia pessoal! Joia tem decisao emocional — criativo e atendimento fazem toda a diferenca. Relatorio {ini} a {fim}."),
    ],
    "seguro": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora fechar. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de comecar a semana, um olhar nos numeros da anterior. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficaram as oportunidades da semana."),
        ("contexto", "Bom dia pessoal! Seguro tem janela de decisao curta — cada hora conta no retorno. Relatorio {ini} a {fim}."),
    ],
    "modulos": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, novos projetos no horizonte. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Um olhar nos numeros antes de entrar no ritmo da semana. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Vamos ver como ficaram as oportunidades."),
        ("contexto", "Bom dia pessoal! Modulos e paineis tem decisao tecnica — qualificar bem a oportunidade e o caminho. Relatorio {ini} a {fim}."),
    ],
    "restaurante": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, mesa cheia. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de entrar no ritmo, um olhar nos numeros da semana passada. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficou o movimento de oportunidades."),
        ("contexto", "Bom dia pessoal! Restaurante e experiencia — cliente que vem uma vez volta se bem atendido. Relatorio {ini} a {fim}."),
    ],
    "otica": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora atender. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de comecar a semana, um olhar nos numeros. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficaram as oportunidades da semana."),
        ("contexto", "Bom dia pessoal! Otica tem decisao rapida — retorno no primeiro contato define o agendamento. Relatorio {ini} a {fim}."),
    ],
    "artesanato": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, bora produzir. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Um olhar nos numeros antes de entrar no ritmo. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficaram as oportunidades da semana."),
        ("contexto", "Bom dia pessoal! Artesanato tem nicho fiel — cliente que gosta volta e indica. Relatorio {ini} a {fim}."),
    ],
    "construcao": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, novos contratos no horizonte. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de entrar no ritmo da semana, um olhar nos numeros. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Como ficaram as oportunidades."),
        ("contexto", "Bom dia pessoal! Construcao tem ciclo longo — cada oportunidade bem trabalhada vale muito. Relatorio {ini} a {fim}."),
    ],
    "default": [
        ("energia", "Bom dia pessoal, tudo bom?\n\nSemana nova, vamos nessa. Segue o relatorio de {ini} a {fim}."),
        ("foco", "Bom dia! Antes de comecar a semana, um olhar nos numeros da anterior. Relatorio {ini} a {fim}."),
        ("parceria", "Oi pessoal! Passando para alinhar os resultados da semana {ini} a {fim}."),
        ("direto", "Bom dia! Relatorio {ini} a {fim}. Vamos ver como ficaram os numeros."),
        ("contexto", "Bom dia pessoal! Semana movimentada no digital — vamos ver o que os numeros mostram. Relatorio {ini} a {fim}."),
    ],
}

PERGUNTAS = {
    "estetica":    "Conseguiram dar retorno para todas as oportunidades essa semana?",
    "odontologia": "Como foi o atendimento essa semana? Algum perfil de paciente se destacou?",
    "moveis":      "Das oportunidades da semana passada, quantas evoluiram para visita ou orcamento?",
    "atacado":     "Como foi o volume de pedidos essa semana? Algum perfil novo se destacou?",
    "farmacia":    "Conseguiram dar retorno para todas as oportunidades essa semana?",
    "vestuario":   "Como foi o movimento essa semana? Alguma peca ou colecao se destacou nas vendas?",
    "acougue":     "Como foi o movimento essa semana? Algum produto se destacou?",
    "joias":       "Das oportunidades da semana passada, quantas evoluiram para compra?",
    "seguro":      "Conseguiram dar retorno para todas as oportunidades essa semana?",
    "modulos":     "Das oportunidades da semana passada, quantas evoluiram para visita tecnica ou orcamento?",
    "restaurante": "Como foi o movimento essa semana? Algum prato ou promocao se destacou?",
    "otica":       "Conseguiram dar retorno para todas as oportunidades essa semana?",
    "artesanato":  "Das oportunidades da semana passada, quantas evoluiram para compra?",
    "construcao":  "Das oportunidades da semana passada, quantas evoluiram para visita ou orcamento?",
    "default":     "Conseguiram dar retorno para todas as oportunidades essa semana?",
}

PROXIMOS = {
    "estetica":    {"ok": "Seguimos com as campanhas rodando. Vou monitorar o custo por oportunidade e ajusto se necessario.", "risco": "Vou revisar os criativos com foco em procedimentos de maior ticket. Do lado de voces, prioridade no retorno rapido para quem entrar."},
    "odontologia": {"ok": "Proxima semana vou testar criativos focados em procedimentos especificos para qualificar ainda mais as oportunidades.", "risco": "Vou ajustar a segmentacao e testar novos angulos de criativo. O retorno nas primeiras 2h aumenta muito a taxa de agendamento."},
    "moveis":      {"ok": "Campanha segue rodando. Vou monitorar o custo por oportunidade ao longo da semana.", "risco": "Vou expandir a segmentacao para reduzir o custo por oportunidade. O primeiro contato define quem fecha — prioridade no retorno rapido."},
    "atacado":     {"ok": "Campanhas seguem rodando com bom volume. Vou monitorar a qualidade das oportunidades ao longo da semana.", "risco": "Vou revisar publicos e criativos com foco no perfil de comprador com maior volume de pedido."},
    "farmacia":    {"ok": "Seguimos com as campanhas rodando. Vou monitorar e ajusto se necessario.", "risco": "Vou revisar a estrutura das campanhas. Cada oportunidade perdida tem custo alto nesse segmento."},
    "vestuario":   {"ok": "Campanhas seguem rodando. Vou acompanhar o desempenho dos criativos ao longo da semana.", "risco": "Vou testar novos criativos com foco nos produtos de maior saida. Retorno rapido no direct faz diferenca."},
    "acougue":     {"ok": "Seguimos com as campanhas rodando. Vou monitorar o custo por oportunidade.", "risco": "Vou revisar os criativos e segmentacao com foco em perfil de cliente recorrente."},
    "joias":       {"ok": "Campanhas seguem rodando. Vou monitorar e testar novos formatos ao longo da semana.", "risco": "Vou revisar criativos e segmentacao. Joias tem decisao emocional — criativo certo muda o custo por oportunidade."},
    "seguro":      {"ok": "Campanha segue rodando. Vou monitorar o custo por oportunidade e ajusto se necessario.", "risco": "Vou ajustar os termos de busca e segmentacao. Seguro tem margem curta — cada oportunidade perdida tem custo alto."},
    "modulos":     {"ok": "Campanha segue rodando. Vou acompanhar o custo por oportunidade ao longo da semana.", "risco": "Vou revisar criativos e segmentacao com foco em perfil com maior potencial de projeto."},
    "restaurante": {"ok": "Seguimos com as campanhas rodando. Vou monitorar e ajusto se necessario.", "risco": "Vou revisar criativos com foco em promocoes e diferenciais do cardapio."},
    "otica":       {"ok": "Campanhas seguem rodando. Vou monitorar e ajusto se necessario.", "risco": "Vou revisar segmentacao e criativos. Retorno rapido no primeiro contato define o agendamento."},
    "artesanato":  {"ok": "Campanhas seguem rodando com bom volume. Vou monitorar ao longo da semana.", "risco": "Vou testar novos criativos com foco nos produtos de maior procura."},
    "construcao":  {"ok": "Seguimos com as campanhas rodando. Vou monitorar o custo por oportunidade.", "risco": "Vou revisar segmentacao e criativos com foco em perfil de obra de maior ticket."},
    "default":     {"ok": "Seguimos com as campanhas rodando. Vou monitorar os resultados e ajusto se necessario.", "risco": "Vou revisar a estrutura das campanhas essa semana. Me avisa se precisar de ajuste de orcamento."},
}


def detectar_nicho(nicho_raw):
    if not nicho_raw:
        return "default"
    n = nicho_raw.lower()
    if any(x in n for x in ["estetica", "beleza", "sobrancelha", "depilacao", "nail"]):
        return "estetica"
    if any(x in n for x in ["odonto", "dent", "clinica", "saude", "medic", "doutor"]):
        return "odontologia"
    if any(x in n for x in ["movel", "planejado", "marcenaria", "tendencia"]):
        return "moveis"
    if any(x in n for x in ["atacado", "distribuicao", "saldao", "multimarca"]):
        return "atacado"
    if any(x in n for x in ["farmacia", "manipulado", "drogaria", "disk farma"]):
        return "farmacia"
    if any(x in n for x in ["moda", "roupa", "vestuario", "loja", "boutique", "vender"]):
        return "vestuario"
    if any(x in n for x in ["acougue", "carnes", "boi", "steakhouse", "churrasco"]):
        return "acougue"
    if any(x in n for x in ["joia", "semijoia", "folheado", "bijuteria", "ouro", "prata"]):
        return "joias"
    if any(x in n for x in ["seguro", "consorcio", "financ", "limer"]):
        return "seguro"
    if any(x in n for x in ["modulo", "painel", "eletronico"]):
        return "modulos"
    if any(x in n for x in ["restaurante", "lanchonete", "pizz", "hamburguer", "cafe", "mamuh"]):
        return "restaurante"
    if any(x in n for x in ["otica", "oculo", "lente", "optica"]):
        return "otica"
    if any(x in n for x in ["artesanato", "aviamento", "costura", "bordado", "tulli"]):
        return "artesanato"
    if any(x in n for x in ["constru", "estrutura", "reforma", "engenharia", "torre"]):
        return "construcao"
    return "default"


def periodo_semana():
    hoje = datetime.now()
    domingo = hoje - timedelta(days=hoje.weekday() + 1)
    segunda = domingo - timedelta(days=6)
    return segunda.strftime("%d/%m"), domingo.strftime("%d/%m")


def get_clientes():
    url = "https://api.clickup.com/api/v2/list/{}/task".format(CLICKUP_LIST_ID)
    headers = {"Authorization": CLICKUP_TOKEN}
    params = {
        "include_closed": "false",
        "limit": 100,
        "statuses[]": "clientes ativos"
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("tasks", [])


def get_campo(task, campo_id):
    for f in task.get("custom_fields", []):
        if f["id"] == campo_id:
            val = f.get("value")
            if f["type"] == "drop_down" and val is not None:
                opts = f.get("type_config", {}).get("options", [])
                for opt in opts:
                    if str(opt.get("orderindex")) == str(val):
                        return opt.get("name")
            return val
    return None


def atualizar_campo(task_id, campo_id, valor):
    url = "https://api.clickup.com/api/v2/task/{}/field/{}".format(task_id, campo_id)
    headers = {"Authorization": CLICKUP_TOKEN, "Content-Type": "application/json"}
    payload = {"value": valor}
    try:
        r = requests.post(url, headers=headers, json=payload)
        return r.status_code in [200, 201]
    except Exception:
        return False


def get_meta_periodo(account_id, inicio, fim):
    url = "https://graph.facebook.com/v19.0/act_{}/insights".format(account_id)
    params = {
        "access_token": META_TOKEN,
        "fields": "spend,actions,cost_per_action_type,clicks",
        "time_range": json.dumps({"since": inicio, "until": fim}),
        "level": "account"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return None
        d = r.json().get("data", [])
        return d[0] if d else None
    except Exception:
        return None


def get_spend_periodo(account_id, dias=3):
    """Gasto da conta nos ultimos N dias. Usado para detectar conta parada."""
    hoje = datetime.now()
    ini = (hoje - timedelta(days=dias)).strftime("%Y-%m-%d")
    fim = hoje.strftime("%Y-%m-%d")
    ins = get_meta_periodo(account_id, ini, fim)
    if not ins:
        return 0.0
    try:
        return float(ins.get("spend", 0) or 0)
    except Exception:
        return 0.0


def top_criativos(account_id, inicio, fim, limite=5):
    """Puxa os top criativos (ads) da conta por resultado no periodo. Retorna lista de dicts."""
    url = "https://graph.facebook.com/v19.0/act_{}/insights".format(account_id)
    params = {
        "access_token": META_TOKEN,
        "fields": "ad_name,actions,cost_per_action_type,spend,impressions",
        "time_range": json.dumps({"since": inicio, "until": fim}),
        "level": "ad",
        "sort": "spend_descending",
        "limit": limite,
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code != 200:
            return []
        dados = r.json().get("data", [])
        resultado = []
        for d in dados:
            nome = d.get("ad_name", "?")
            spend = float(d.get("spend", 0) or 0)
            impr = int(d.get("impressions", 0) or 0)
            # Extrair melhor metrica de resultado
            actions = d.get("actions", [])
            melhor_acao = ""
            melhor_qtd = 0
            for a in actions:
                tipo = a.get("action_type", "")
                qtd = int(a.get("value", 0) or 0)
                if qtd > melhor_qtd:
                    melhor_qtd = qtd
                    melhor_acao = tipo
            # CPL/custo por resultado
            cpa_list = d.get("cost_per_action_type", [])
            cpa = 0
            for c in cpa_list:
                if c.get("action_type") == melhor_acao:
                    cpa = float(c.get("value", 0) or 0)
                    break
            # Traduzir tipo de ação pra portugues simples
            tipo_label = {
                "onsite_conversion.messaging_conversation_started_7d": "conversas iniciadas",
                "lead": "leads",
                "link_click": "cliques no link",
                "landing_page_view": "visitas na pagina",
                "page_engagement": "engajamentos",
                "post_engagement": "engajamentos no post",
                "video_view": "visualizacoes de video",
                "comment": "comentarios",
                "like": "curtidas",
                "offsite_conversion.fb_pixel_lead": "leads (pixel)",
            }.get(melhor_acao, melhor_acao.replace("_", " ") if melhor_acao else "interacoes")
            if melhor_qtd > 0:
                resultado.append({
                    "nome": nome, "resultados": melhor_qtd, "tipo": tipo_label,
                    "cpr": cpa, "gasto": spend, "impressoes": impr,
                })
        return resultado
    except Exception as e:
        log("[META] erro top_criativos: {}".format(e))
        return []


def get_meta_todos_periodos(account_id):
    hoje = datetime.now()
    domingo_s1 = hoje - timedelta(days=hoje.weekday() + 1)
    segunda_s1 = domingo_s1 - timedelta(days=6)
    domingo_s2 = segunda_s1 - timedelta(days=1)
    segunda_s2 = domingo_s2 - timedelta(days=6)
    domingo_s3 = segunda_s2 - timedelta(days=1)
    segunda_s3 = domingo_s3 - timedelta(days=6)
    domingo_s4 = segunda_s3 - timedelta(days=1)
    segunda_s4 = domingo_s4 - timedelta(days=6)
    fmt = "%Y-%m-%d"
    ins_7d  = get_meta_periodo(account_id, segunda_s1.strftime(fmt), domingo_s1.strftime(fmt))
    ins_14d = get_meta_periodo(account_id, segunda_s2.strftime(fmt), domingo_s2.strftime(fmt))
    ins_21d = get_meta_periodo(account_id, segunda_s3.strftime(fmt), domingo_s3.strftime(fmt))
    ins_30d = get_meta_periodo(account_id, segunda_s4.strftime(fmt), domingo_s4.strftime(fmt))
    return ins_7d, ins_14d, ins_21d, ins_30d


TIPOS_LEAD = [
    "onsite_conversion.lead_grouped",          # lead form deduplucado
    "onsite_conversion.messaging_conversation_started_7d",  # conversa WPP iniciada
    "contact",                                 # clique em contato
    "omni_complete_registration",              # cadastro
    "schedule",                                # agendamento
]
# "lead" so entra se lead_grouped nao existir (evita dupla contagem)
TIPOS_LEAD_FALLBACK = ["lead"]


def extrair_leads(ins):
    if not ins:
        return 0
    actions = {a["action_type"]: int(a.get("value", 0))
               for a in ins.get("actions", [])}
    total = 0
    for t in TIPOS_LEAD:
        total += actions.get(t, 0)
    # soma "lead" apenas se lead_grouped nao veio (evita dupla contagem)
    if actions.get("onsite_conversion.lead_grouped", 0) == 0:
        total += actions.get("lead", 0)
    return total


def extrair_cpl(ins):
    if not ins:
        return None
    sp = float(ins.get("spend", 0))
    l = extrair_leads(ins)
    return round(sp / l, 2) if l > 0 else None


def gerar_mensagem(display, plat, nicho_key, saude, oportunidades,
                   cpl, meta_cpl, investimento, cliques, gargalo, ini, fim):

    # Rotacao por semana — nunca repete o mesmo angulo 2 semanas seguidas
    semana_num = datetime.now().isocalendar()[1]
    opcoes = ABERTURAS.get(nicho_key, ABERTURAS["default"])
    abertura_template = opcoes[semana_num % len(opcoes)][1]
    abertura = abertura_template.format(ini=ini, fim=fim)

    pergunta = PERGUNTAS.get(nicho_key, PERGUNTAS["default"])
    passo = PROXIMOS.get(nicho_key, PROXIMOS["default"])
    passo_txt = passo["risco"] if saude in ["Em Risco", "Atencao"] else passo["ok"]

    usa_meta = plat in ["Meta Ads", "Face + Google"]
    usa_google = plat in ["Google Ads", "Face + Google"]

    linhas = []
    linhas.append(abertura)

    if usa_meta:
        linhas.append("")
        linhas.append("*Meta Ads — {}*".format(display))
        linhas.append("")
        if oportunidades:
            linhas.append("{} oportunidades geradas no periodo".format(oportunidades))
        if cpl and meta_cpl:
            status = "dentro do esperado" if saude == "Dentro da Meta" else "acima da meta"
            linhas.append("Custo por oportunidade R${:.2f} com meta em R${:.2f} — {}".format(cpl, meta_cpl, status))
        elif cpl:
            linhas.append("Custo por oportunidade R${:.2f}".format(cpl))
        if investimento:
            linhas.append("Investimento da semana R${:.2f}".format(investimento))
        linhas.append("")
        if saude == "Dentro da Meta":
            linhas.append("Campanha entregando dentro do esperado.")
        elif saude == "Atencao":
            txt = "O custo por oportunidade esta levemente acima da meta."
            if gargalo and gargalo not in ["Nenhum", "Expectativa"]:
                txt += " Gargalo identificado: {}.".format(gargalo)
            linhas.append(txt)
        else:
            txt = "O custo por oportunidade esta acima da meta."
            if gargalo and gargalo not in ["Nenhum"]:
                txt += " Gargalo principal: {}.".format(gargalo)
            linhas.append(txt)

    if usa_google:
        linhas.append("")
        linhas.append("*Google Ads — {}*".format(display))
        linhas.append("")
        if cliques:
            linhas.append("{} cliques qualificados no periodo".format(cliques))
        linhas.append("Campanha ativa capturando intencao de busca direta")
        linhas.append("Perfil de contato com decisao mais avancada no funil")

    if usa_meta and usa_google:
        linhas.append("")
        linhas.append("*Panorama geral*")
        linhas.append("")
        panorama = "As duas plataformas cobrindo o funil: Meta gerando demanda e Google capturando quem ja esta buscando ativamente."
        if saude == "Dentro da Meta":
            panorama += " Custo por oportunidade consolidado dentro da meta, semana positiva."
        linhas.append(panorama)

    linhas.append("")
    linhas.append(passo_txt)
    linhas.append("")
    linhas.append(pergunta)

    return "\n".join(linhas)


# ---- INICIO ----
linhas_log = []

def log(txt=""):
    print(txt)
    linhas_log.append(txt)

def _norm(s):
    """Normaliza nome pra casar cliente operacional com card da Base de Inteligencia."""
    s = (s or "").replace("\U0001f9e0", " ").lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    out = []
    for ch in s:
        out.append(ch if (ch.isalnum() or ch == " ") else " ")
    return " ".join("".join(out).split())


def carregar_dossies():
    """Le os cards da Base de Inteligencia e devolve {nome_normalizado: texto_do_dossie}."""
    dossies = {}
    if not CLICKUP_TOKEN:
        return dossies
    url = "https://api.clickup.com/api/v2/list/{}/task".format(BASE_INTELIGENCIA_LIST_ID)
    headers = {"Authorization": CLICKUP_TOKEN}
    try:
        r = requests.get(url, headers=headers, params={"include_closed": "true"}, timeout=30)
        if r.status_code != 200:
            log("[IA] nao consegui ler a Base de Inteligencia: {}".format(r.status_code))
            return dossies
        for t in r.json().get("tasks", []):
            nome = t.get("name", "")
            if "TEMPLATE" in nome.upper():
                continue
            texto = (t.get("text_content") or t.get("description") or "").strip()
            if texto:
                dossies[_norm(nome)] = texto
        log("[IA] dossies carregados: {}".format(len(dossies)))
    except Exception as e:
        log("[IA] erro lendo Base de Inteligencia: {}".format(e))
    return dossies


def achar_dossie(display, dossies):
    """Casa o cliente operacional com o card dele na Base de Inteligencia."""
    alvo = _norm(display)
    if not alvo:
        return ""
    for chave, texto in dossies.items():
        if alvo in chave or chave in alvo:
            return texto
    # tentativa por palavras significativas (ignora nomes de pessoa antes do travessao)
    palavras = [p for p in alvo.split() if len(p) > 3]
    for chave, texto in dossies.items():
        if palavras and all(p in chave for p in palavras):
            return texto
    return ""


def _chamar_ia(sistema, usuario, max_tokens=700):
    """Chamada generica a Claude. Retorna texto ou ''."""
    if not ANTHROPIC_API_KEY:
        return ""
    body = {
        "model": IA_MODEL,
        "max_tokens": max_tokens,
        "system": sistema,
        "messages": [{"role": "user", "content": usuario}],
    }
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    try:
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=60)
        if r.status_code != 200:
            log("[IA] erro {}: {}".format(r.status_code, r.text[:200]))
            return ""
        partes = [b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text"]
        return "\n".join(partes).strip()
    except Exception as e:
        log("[IA] excecao: {}".format(e))
        return ""


REGRA_FORMATACAO = (
    "REGRA DE FORMATACAO OBRIGATORIA: nunca use travessao longo ou em-dash (caractere '\\u2014'). "
    "Use virgula, ponto, dois-pontos ou a palavra 'e' no lugar. "
    "Nunca use asteriscos para negrito (**texto**). Escreva texto corrido simples."
)

REGRA_BASE = (
    "Voce e o gestor de trafego da DD Mkt. Escreva SO a mensagem, pronta pra colar no WhatsApp, "
    "em portugues do Brasil. Adapte o TOM ao perfil do cliente descrito no dossie. "
    "VARIE a abertura e a estrutura toda semana. No maximo 1-2 emojis, e so se combinar. "
    + REGRA_FORMATACAO
)


def semana_do_mes():
    """Retorna 1, 2, 3 ou 4 baseado no dia do mes."""
    dia = datetime.now().day
    if dia <= 7:
        return 1
    elif dia <= 14:
        return 2
    elif dia <= 21:
        return 3
    return 4


ACOES_ROTATIVAS = {
    1: {
        "nome": "Engajar Instagram dos clientes",
        "instrucao": (
            "Gere uma orientacao curta para a pessoa de CS engajar o Instagram do cliente. "
            "Ex: curtir os 3 ultimos posts, comentar algo relevante, compartilhar no stories. "
            "Use o dossie pra saber o @ e o estilo do cliente. "
            "Se nao souber o @, oriente a pessoa de CS a procurar."
        ),
    },
    2: {
        "nome": "Insight de mercado do nicho",
        "instrucao": (
            "Gere uma mensagem curta com um insight de mercado relevante pro nicho do cliente. "
            "Pode ser uma tendencia, um dado, uma oportunidade que ele deveria conhecer. "
            "Tom consultivo, mostrando autoridade. A mensagem e pra enviar no grupo do cliente."
        ),
    },
    3: {
        "nome": "Disparar pesquisa NPS",
        "instrucao": (
            "Gere a mensagem de NPS pra enviar no grupo do cliente. Pergunte: "
            "'De 0 a 10, qual a chance de voce recomendar nosso trabalho pra alguem?' "
            "Adapte o tom ao perfil do cliente. Leve, sem pressao."
        ),
    },
    4: {
        "nome": "Relatorio mensal consolidado",
        "instrucao": (
            "Gere um resumo do mes do cliente: evolucao das ultimas 4 semanas, "
            "o que funcionou, o que ajustamos, e o plano pro proximo mes. "
            "Use os dados da semana como referencia (sao os mais recentes). "
            "Tom de fechamento de ciclo, positivo mas realista."
        ),
    },
}


def _montar_usuario(ctx, dossie, extra=""):
    """Monta o bloco de contexto do usuario pra qualquer prompt."""
    criativos_bloco = ctx.get("criativos", "")
    invest = ctx.get("invest", 0)
    return (
        "DADOS ({ini} a {fim}):\n"
        "- Cliente: {cliente}\n"
        "- Nicho: {nicho}\n"
        "- Plataforma: {plat}\n"
        "- Fase: {fase}\n"
        "- Gargalo: {gargalo}\n"
        "- Obs semana: {obs}\n"
        "- Leads/conversas totais: {leads} | CPL geral: {cpl} | Meta: {meta} | Investimento: {invest}\n\n"
        "{criativos}\n\n"
        "{extra}"
        "DOSSIE DO CLIENTE:\n{dossie}"
    ).format(
        ini=ctx.get("ini", ""), fim=ctx.get("fim", ""),
        cliente=ctx.get("cliente", ""), nicho=ctx.get("nicho", "") or "nao informado",
        plat=ctx.get("plat", "") or "nao informado", fase=ctx.get("fase", "") or "nao informada",
        gargalo=ctx.get("gargalo", "") or "Nenhum", obs=ctx.get("obs", "") or "(sem obs)",
        leads=ctx.get("leads", 0),
        cpl=("R$%.2f" % ctx["cpl"]) if ctx.get("cpl") else "sem dado",
        meta=("R$%.2f" % ctx["meta"]) if ctx.get("meta") else "nao definida",
        invest=("R$%.2f" % invest) if invest else "nao informado",
        criativos=criativos_bloco if criativos_bloco else "(sem breakdown de criativos)",
        extra=(extra + "\n\n") if extra else "",
        dossie=(dossie or "Sem dossie. Use o nicho para definir o tom.")[:4500],
    )


def gerar_relatorio_ia(ctx, dossie):
    """TERCA: relatorio de performance no tom do dossie, citando criativos."""
    sistema = (
        REGRA_BASE + "\n"
        "Esta e a mensagem de TERCA: relatorio de performance semanal com dados reais.\n\n"
        "ESTRUTURA OBRIGATORIA (adapte o tom ao dossie, mas siga esta estrutura):\n\n"
        "1. ABERTURA: cumprimento com o nome da pessoa de contato (do dossie). "
        "Mencione o periodo (ex: 'semana de 25 a 31/05').\n\n"
        "2. RESULTADOS: traduza os numeros em linguagem de empresario. "
        "Ex: '245 conversas iniciadas no WhatsApp', nao 'leads'. "
        "Mostre investimento, CPL e meta. Se CPL abaixo da meta, destaque a % (ex: '66% abaixo da meta'). "
        "Se acima, explique por que e o que vai fazer.\n\n"
        "3. DESTAQUES (criticos): se receber TOP CRIATIVOS, CITE OS NOMES dos 2-3 melhores. "
        "Ex: 'o criativo Tem tapete pra todo canto dominou, 223 dos 245 contatos a R$0,88'. "
        "Compare performance entre eles. Se um criativo novo entrou com CPL bom, destaque. "
        "NUNCA ignore os criativos quando eles estao nos dados.\n\n"
        "4. ANALISE: 1-2 frases interpretando os dados. "
        "O que explica o resultado? Campanha madura? Criativo novo? Sazonalidade?\n\n"
        "5. PROXIMOS PASSOS: acao concreta (testar variacao do criativo campeao, explorar novo angulo, "
        "ajustar publico). Seja especifico ao nicho.\n\n"
        "6. PERGUNTA DE ENGAJAMENTO: pergunte sobre a qualidade dos contatos, o retorno comercial, "
        "ou algo relevante ao negocio.\n\n"
        "REGRAS EXTRAS:\n"
        "- Se a plataforma for 'Face + Google' e o Meta tiver poucos leads, pode ser porque Meta faz "
        "conteudo/branding e Google faz lead gen. Explique isso naturalmente.\n"
        "- Use emojis pra separar secoes (tipo o exemplo). No maximo 4-5 emojis no total.\n"
        "- Tamanho: medio (8-15 linhas). Nem curto demais, nem texto enorme.\n"
        "- NUNCA invente dados. Se nao tem criativo, nao cite. Se nao tem CPL, diga.\n"
        "- Fale como o gestor de trafego que esta no detalhe, nao como um relatorio automatico."
    )
    return _chamar_ia(sistema, _montar_usuario(ctx, dossie))


def gerar_abertura_ia(ctx, dossie):
    """SEGUNDA: mensagem de abertura motivacional, sem numeros."""
    sistema = (
        REGRA_BASE + "\n"
        "Esta e a mensagem de SEGUNDA: abertura da semana.\n"
        "1. Motivacional, leve, humana. SEM numeros, SEM dados de performance.\n"
        "2. Pode mencionar algo do negocio do cliente (baseado no dossie) pra mostrar proximidade.\n"
        "3. Curta: 2-4 frases no maximo.\n"
        "4. Termine com energia positiva ou uma frase que mostre que voce esta ligado no negocio dele.\n"
        "5. NÃO mencione 'relatorio', 'dados', 'CPL', 'leads' ou qualquer metrica."
    )
    return _chamar_ia(sistema, _montar_usuario(ctx, dossie), max_tokens=300)


def gerar_fechamento_ia(ctx, dossie):
    """SEXTA: fechamento qualitativo, sem numeros, relacional."""
    sistema = (
        REGRA_BASE + "\n"
        "Esta e a mensagem de SEXTA: fechamento da semana.\n"
        "1. Qualitativa, relacional. SEM numeros, SEM dados de performance.\n"
        "2. Pergunte como foi a semana do lado DELES (vendas, movimento, feedback dos clientes).\n"
        "3. Mostre que voce esta presente e pensando no negocio.\n"
        "4. Curta: 2-4 frases.\n"
        "5. Tom de parceiro que se importa, nao de prestador de servico.\n"
        "6. NÃO repita a estrutura da mensagem de segunda. Varie."
    )
    return _chamar_ia(sistema, _montar_usuario(ctx, dossie), max_tokens=300)


def gerar_acao_rotativa(ctx, dossie, semana):
    """Gera a orientacao da acao rotativa da semana (1-4)."""
    acao = ACOES_ROTATIVAS.get(semana, ACOES_ROTATIVAS[1])
    sistema = (
        REGRA_BASE + "\n"
        "ACAO ROTATIVA DA SEMANA {}: {}\n".format(semana, acao["nome"]) +
        acao["instrucao"]
    )
    return _chamar_ia(sistema, _montar_usuario(ctx, dossie), max_tokens=400)


periodo_ini, periodo_fim = periodo_semana()

log("=" * 60)
log("CS SEMANAL AUTOMATIZADO")
log("Periodo: {} a {}".format(periodo_ini, periodo_fim))
log("Execucao: {}".format(datetime.now().strftime("%d/%m/%Y %H:%M")))
log("=" * 60)

log("\nBuscando clientes no ClickUp...")
try:
    tasks = get_clientes()
except Exception as e:
    log("ERRO ClickUp: {}".format(e))
    sys.exit(1)

log("{} clientes encontrados\n".format(len(tasks)))

boleto = []
mensagens = []
em_risco = []
dentro_meta = []

DOSSIES = carregar_dossies()

for t in tasks:
    nome = t.get("name", "")
    empresa = get_campo(t, CAMPOS["cliente"])
    plat = get_campo(t, CAMPOS["plataforma"])
    pgto = get_campo(t, CAMPOS["pgto_ca"])
    meta_cpl_val = get_campo(t, CAMPOS["meta_cpl"])
    leads_7d = get_campo(t, CAMPOS["leads_7d"]) or 0
    cpl_7d = get_campo(t, CAMPOS["cpl_7d"])
    gargalo = get_campo(t, CAMPOS["gargalo"])
    obs_sem = get_campo(t, CAMPOS["obs_semana"])
    link = get_campo(t, CAMPOS["link_grupo"])
    nicho_raw = get_campo(t, CAMPOS["nicho"])
    fase = get_campo(t, CAMPOS["fase_campanha"])
    status_fin = get_campo(t, CAMPOS["status_financeiro"])
    orcamento = get_campo(t, CAMPOS["orcamento_midia"])
    nicho_key = detectar_nicho(nicho_raw or nome)

    usa_meta = plat in ["Meta Ads", "Face + Google"]
    inv = 0
    cliques = 0

    mapa_key = None
    import unicodedata
    def norm(s):
        return ''.join(
            c for c in unicodedata.normalize("NFKD", s.lower())
            if not unicodedata.combining(c)
        )
    if nome in MAPA:
        mapa_key = nome
    else:
        for k in MAPA:
            if norm(k) in norm(nome) or norm(nome) in norm(k):
                mapa_key = k
                break

    leads_14d = 0
    leads_21d = 0
    leads_30d = 0
    cpl_medio_mensal = None

    if usa_meta and mapa_key:
        ins7, ins14, ins21, ins30 = get_meta_todos_periodos(MAPA[mapa_key])
        if ins7:
            cpl_7d = extrair_cpl(ins7)
            leads_7d = extrair_leads(ins7)
            inv = round(float(ins7.get("spend", 0)), 2)
            cliques = int(ins7.get("clicks", 0))
        if ins14:
            leads_14d = extrair_leads(ins14)
        if ins21:
            leads_21d = extrair_leads(ins21)
        if ins30:
            leads_30d = extrair_leads(ins30)

        # Volume acumulado
        vol_14d = int(leads_7d) + leads_14d
        vol_21d = vol_14d + leads_21d
        vol_30d = vol_21d + leads_30d

        # CPL medio mensal = investimento total / leads totais
        inv_total = inv
        for ins in [ins14, ins21, ins30]:
            if ins:
                inv_total += round(float(ins.get("spend", 0)), 2)
        if vol_30d > 0:
            cpl_medio_mensal = round(inv_total / vol_30d, 2)

        import time
        hoje_ts = int(time.time() * 1000)  # timestamp em ms para campo de data do ClickUp
        # Grava sempre — mesmo que semanas anteriores nao tenham dados
        if cpl_7d:
            atualizar_campo(t["id"], CAMPOS["cpl_7d"], cpl_7d)
        atualizar_campo(t["id"], CAMPOS["leads_7d"], str(int(leads_7d)))
        atualizar_campo(t["id"], CAMPOS["leads_14d"], str(int(vol_14d)))
        atualizar_campo(t["id"], CAMPOS["leads_21d"], str(int(vol_21d)))
        atualizar_campo(t["id"], CAMPOS["leads_30d"], str(int(vol_30d)))
        atualizar_campo(t["id"], CAMPOS["ultima_atualizacao"], hoje_ts)
        if ins7:
            log("[OK] {}: 7D={} | 14D={} | 21D={} | 30D={} | CPL-mes=R${} | R${} inv".format(
                nome, int(leads_7d), vol_14d, vol_21d, vol_30d, cpl_medio_mensal, inv))
        else:
            log("[--] {}: sem dados 7D | acumulado 14D={} 21D={} 30D={}".format(
                nome, vol_14d, vol_21d, vol_30d))
    elif not usa_meta:
        log("[GA] {}: Google Ads".format(nome))
    else:
        log("[??] {}: adicione em MAPA".format(nome))

    if pgto == "Boleto":
        boleto.append(empresa or nome)

    mc = float(meta_cpl_val) if meta_cpl_val else None
    c7 = float(cpl_7d) if cpl_7d else None

    if c7 and mc:
        dev = (c7 - mc) / mc
        saude = "Em Risco" if dev > 0.25 else "Atencao" if dev > 0.10 else "Dentro da Meta"
    else:
        saude = "Dentro da Meta"

    display = empresa or nome

    msg = gerar_mensagem(
        display=display, plat=plat or "Meta Ads", nicho_key=nicho_key,
        saude=saude, oportunidades=int(leads_7d) if leads_7d else 0,
        cpl=c7, meta_cpl=mc, investimento=inv, cliques=cliques,
        gargalo=gargalo, ini=periodo_ini, fim=periodo_fim
    )

    if saude == "Dentro da Meta":
        dentro_meta.append(display)
    else:
        em_risco.append(display)

    conta_parada = False
    # So detecta "conta parada" para clientes onde o Meta e o canal de leads (Meta Ads puro).
    # Clientes com Google (Google Ads / Face + Google) podem ter o Meta zerado sem estar parados
    # — o lead deles vem do Google, que este script nao enxerga. Evita falso positivo.
    if mapa_key and plat == "Meta Ads":
        spend_recente = get_spend_periodo(MAPA[mapa_key], 3)
        if spend_recente < 1.0 and (inv > 0 or int(leads_7d or 0) > 0):
            conta_parada = True
            log("[!!] {}: CONTA PARADA (Meta sem gasto nos ultimos 3 dias)".format(nome))

    pix_status = "pago" if status_fin == "Pago" else "pendente"

    # --- MENSAGENS IA (3 dias + acao rotativa) ---
    relatorio_ia = ""
    abertura_ia = ""
    fechamento_ia = ""
    acao_ia = ""
    SEMANA_MES = semana_do_mes()
    if not conta_parada and ANTHROPIC_API_KEY:
        # Top criativos da semana (só pra clientes com Meta)
        criativos = []
        if usa_meta and mapa_key:
            criativos = top_criativos(MAPA[mapa_key], periodo_ini, periodo_fim, limite=5)
        criativos_txt = ""
        if criativos:
            linhas = []
            for i, cr in enumerate(criativos, 1):
                linhas.append("  {}. \"{}\": {} {} a R${:.2f} cada (gasto R${:.2f})".format(
                    i, cr["nome"], cr["resultados"], cr["tipo"], cr["cpr"], cr["gasto"]))
            criativos_txt = "TOP CRIATIVOS DA SEMANA:\n" + "\n".join(linhas)
        ctx_ia = {
            "ini": periodo_ini, "fim": periodo_fim,
            "cliente": display, "nicho": nicho_raw,
            "plat": plat, "fase": fase, "gargalo": gargalo,
            "obs": obs_sem,
            "leads": int(leads_7d) if leads_7d else 0,
            "cpl": c7, "meta": mc,
            "criativos": criativos_txt,
            "invest": inv if 'inv' in dir() else 0,
        }
        dossie_txt = achar_dossie(display, DOSSIES)
        # Segunda: abertura motivacional
        abertura_ia = gerar_abertura_ia(ctx_ia, dossie_txt)
        # Terca: relatorio de performance
        relatorio_ia = gerar_relatorio_ia(ctx_ia, dossie_txt)
        # Sexta: fechamento qualitativo
        fechamento_ia = gerar_fechamento_ia(ctx_ia, dossie_txt)
        # Acao rotativa da semana
        acao_ia = gerar_acao_rotativa(ctx_ia, dossie_txt, SEMANA_MES)
        gerados = sum(1 for x in [abertura_ia, relatorio_ia, fechamento_ia, acao_ia] if x)
        log("[IA] {} - {}/4 mensagens geradas".format(display, gerados))

    mensagens.append({
        "nome": display, "saude": saude, "link": link, "msg": msg,
        "segmento": nicho_raw or "", "meta_cpl": mc or "",
        "leads": int(leads_7d) if leads_7d else 0, "cpl": c7 or "",
        "pix_valor": orcamento or "", "pix_status": pix_status,
        "conta_status": "parada" if conta_parada else "ativa",
        "relatorio_ia": relatorio_ia,
        "abertura_ia": abertura_ia,
        "fechamento_ia": fechamento_ia,
        "acao_ia": acao_ia,
    })

# ---- RESUMO ----
log("\n" + "=" * 60)
log("RESUMO EXECUTIVO")
log("=" * 60)
log("Total de clientes: {}".format(len(tasks)))
log("Dentro da Meta: {}".format(len(dentro_meta)))
log("Em Risco / Atencao: {}".format(len(em_risco)))
if em_risco:
    log("Atencao para: {}".format(", ".join(em_risco)))
log("Pix a enviar: {} clientes | R${:.2f}".format(len(boleto), len(boleto) * PIX_SEMANAL))

# ---- MENSAGENS ----
log("\n" + "=" * 60)
log("RELATORIOS DE PERFORMANCE — prontos para WhatsApp")
log("=" * 60)

for m in mensagens:
    log("\n" + "-" * 50)
    log("{} | {}".format(m["nome"], m["saude"]))
    if m.get("link"):
        log("Grupo: {}".format(m["link"]))
    log("")
    log(m["msg"])

# ---- PIX ----
if boleto:
    log("\n" + "=" * 60)
    log("PIX SEMANAL - {}".format(datetime.now().strftime("%d/%m/%Y")))
    log("=" * 60)
    total = 0
    for b in boleto:
        log("[ ] {} — R${:.2f}".format(b, PIX_SEMANAL))
        total += PIX_SEMANAL
    log("TOTAL: R${:.2f}".format(total))

log("\nConcluido!")

# Salva txt para artifact (fallback)
with open("output_cs.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(linhas_log))

# Gera HTML para GitHub Pages — acessivel em rainerlimaads.github.io/relat-rios/cs.html
import os
os.makedirs("docs", exist_ok=True)

def saude_cor(saude):
    if saude == "Em Risco":
        return "#e74c3c"
    elif saude == "Atencao":
        return "#f39c12"
    return "#27ae60"

cards_html = ""
for m in mensagens:
    cor = saude_cor(m["saude"])
    msg_html = m["msg"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    msg_html = msg_html.replace("*", "<strong>", 1)
    # bold simples: substitui *texto* por <strong>texto</strong>
    import re
    msg_formatada = re.sub(r'\*(.+?)\*', r'<strong>\1</strong>', m["msg"])
    msg_formatada = msg_formatada.replace("\n", "<br>")

    grupo_btn = ""
    if m.get("link") and m["link"] not in ["https://web.whatsapp.com/", None, ""]:
        grupo_btn = '<a href="{}" target="_blank" class="btn-grupo">Abrir grupo</a>'.format(m["link"])

    cards_html += """
    <div class="card">
        <div class="card-header">
            <span class="nome">{nome}</span>
            <span class="badge" style="background:{cor}">{saude}</span>
            {grupo_btn}
        </div>
        <div class="mensagem">{msg}</div>
        <button class="btn-copy" onclick="copiar(this)">Copiar mensagem</button>
        <textarea class="hidden-text">{msg_raw}</textarea>
    </div>
    """.format(
        nome=m["nome"],
        cor=cor,
        saude=m["saude"],
        grupo_btn=grupo_btn,
        msg=msg_formatada,
        msg_raw=m["msg"].replace("</", "<\\/")
    )

pix_html = ""
if boleto:
    pix_items = "".join(
        "<li>{} — R${:.2f}</li>".format(b, PIX_SEMANAL) for b in boleto
    )
    pix_html = """
    <div class="pix-section">
        <h2>Pix Semanal — {data}</h2>
        <ul>{items}</ul>
        <p class="total">Total: R${total:.2f}</p>
    </div>
    """.format(
        data=datetime.now().strftime("%d/%m/%Y"),
        items=pix_items,
        total=len(boleto) * PIX_SEMANAL
    )

html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CS Semanal {ini} a {fim}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; padding: 20px; color: #1a1a1a; }}
  h1 {{ font-size: 20px; font-weight: 700; margin-bottom: 6px; color: #1a1a1a; }}
  .meta {{ font-size: 13px; color: #666; margin-bottom: 24px; }}
  .resumo {{ background: #fff; border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; display: flex; gap: 24px; flex-wrap: wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .resumo-item {{ font-size: 13px; color: #444; }}
  .resumo-item strong {{ font-size: 22px; display: block; color: #1a1a1a; }}
  .card {{ background: #fff; border-radius: 12px; padding: 18px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }}
  .nome {{ font-size: 15px; font-weight: 600; flex: 1; }}
  .badge {{ font-size: 11px; font-weight: 600; color: #fff; padding: 3px 10px; border-radius: 20px; white-space: nowrap; }}
  .btn-grupo {{ font-size: 12px; color: #25d366; border: 1px solid #25d366; border-radius: 20px; padding: 3px 10px; text-decoration: none; white-space: nowrap; }}
  .mensagem {{ font-size: 14px; line-height: 1.7; color: #333; background: #f8f9fa; border-radius: 8px; padding: 14px; margin-bottom: 12px; white-space: pre-wrap; }}
  .btn-copy {{ font-size: 13px; background: #1a1a1a; color: #fff; border: none; border-radius: 8px; padding: 8px 16px; cursor: pointer; }}
  .btn-copy:hover {{ background: #333; }}
  .btn-copy.copiado {{ background: #27ae60; }}
  .hidden-text {{ display: none; }}
  .pix-section {{ background: #fff; border-radius: 12px; padding: 18px 20px; margin-top: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
  .pix-section h2 {{ font-size: 16px; margin-bottom: 12px; }}
  .pix-section ul {{ list-style: none; }}
  .pix-section li {{ padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
  .total {{ font-size: 16px; font-weight: 700; margin-top: 12px; }}
  @media (max-width: 600px) {{ body {{ padding: 12px; }} }}
</style>
</head>
<body>
<h1>Relatorios de Performance</h1>
<p class="meta">Semana {ini} a {fim} &nbsp;|&nbsp; Gerado em {gerado} &nbsp;|&nbsp; {total} clientes</p>
<div class="resumo">
  <div class="resumo-item"><strong>{n_meta}</strong>Dentro da Meta</div>
  <div class="resumo-item"><strong style="color:#e74c3c">{n_risco}</strong>Em Risco / Atencao</div>
  <div class="resumo-item"><strong>{n_pix}</strong>Pix a enviar</div>
  <div class="resumo-item"><strong>R${total_pix:.0f}</strong>Total Pix</div>
</div>
{cards}
{pix}
<script>
function copiar(btn) {{
  var txt = btn.nextElementSibling.value;
  navigator.clipboard.writeText(txt).then(function() {{
    btn.textContent = 'Copiado!';
    btn.classList.add('copiado');
    setTimeout(function() {{
      btn.textContent = 'Copiar mensagem';
      btn.classList.remove('copiado');
    }}, 2000);
  }});
}}
</script>
</body>
</html>""".format(
    ini=periodo_ini,
    fim=periodo_fim,
    gerado=datetime.now().strftime("%d/%m/%Y %H:%M"),
    total=len(mensagens),
    n_meta=len(dentro_meta),
    n_risco=len(em_risco),
    n_pix=len(boleto),
    total_pix=len(boleto) * PIX_SEMANAL,
    cards=cards_html,
    pix=pix_html
)

with open("docs/cs.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\nPagina gerada: https://rainerlimaads.github.io/relat-rios/cs.html")


# ---- CSV PARA O PAINEL NOVO (cs-painel.html le este arquivo) ----
import csv
with open("docs/cs-dados.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cliente","segmento","meta_cpl","leads","cpl","criativo","pix_valor","pix_status","link_grupo","conta_status"])
    for m in mensagens:
        w.writerow([
            m["nome"], m.get("segmento",""), m.get("meta_cpl",""),
            m.get("leads",""), m.get("cpl",""), "",
            m.get("pix_valor",""), m.get("pix_status","pendente"),
            m.get("link","") or "", m.get("conta_status","ativa"),
        ])
print("CSV do painel gerado: docs/cs-dados.csv")

# --- JSON com mensagens IA completas (3 dias + acao rotativa) ---
SEMANA_MES = semana_do_mes()
ACAO_NOME = ACOES_ROTATIVAS.get(SEMANA_MES, ACOES_ROTATIVAS[1])["nome"]
relatorios_ia = {"_meta": {"semana": SEMANA_MES, "acao_rotativa": ACAO_NOME, "periodo": "{} a {}".format(periodo_ini, periodo_fim)}}
for m in mensagens:
    dados_cliente = {}
    if m.get("abertura_ia"):
        dados_cliente["segunda"] = m["abertura_ia"]
    if m.get("relatorio_ia"):
        dados_cliente["terca"] = m["relatorio_ia"]
    if m.get("fechamento_ia"):
        dados_cliente["sexta"] = m["fechamento_ia"]
    if m.get("acao_ia"):
        dados_cliente["acao_rotativa"] = m["acao_ia"]
    if dados_cliente:
        relatorios_ia[m["nome"]] = dados_cliente
with open("docs/cs-relatorios.json", "w", encoding="utf-8") as f:
    json.dump(relatorios_ia, f, ensure_ascii=False, indent=1)
clientes_com_ia = len([k for k in relatorios_ia if k != "_meta"])
print("JSON de relatorios IA gerado: docs/cs-relatorios.json ({} clientes, semana {}, ~{} chamadas IA)".format(clientes_com_ia, SEMANA_MES, clientes_com_ia * 4))
