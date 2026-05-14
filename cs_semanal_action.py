# -*- coding: utf-8 -*-
import requests
import json
import os
import sys
from datetime import datetime, timedelta

# Tokens vem das variaveis de ambiente (GitHub Secrets)
CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
META_TOKEN = os.environ.get("META_TOKEN", "")
CLICKUP_LIST_ID = "901325426193"
PIX_SEMANAL = 300.0

if not CLICKUP_TOKEN or not META_TOKEN:
    print("ERRO: Tokens nao configurados. Configure CLICKUP_TOKEN e META_TOKEN nos GitHub Secrets.")
    sys.exit(1)

CAMPOS = {
    "cliente":    "b9892282-cac2-41f8-8e39-59bb0ee89c53",
    "plataforma": "1e2811d8-af23-455b-92eb-0bc995d8b664",
    "meta_cpl":   "4149e4ca-b01f-426b-b6bd-16c9c4add0c3",
    "cpl_7d":     "5407a9f2-247d-461f-add3-ad0e1ff9dbf6",
    "leads_7d":   "ae4741ba-ed7b-422b-99e2-71dfb6b9599f",
    "pgto_ca":    "6644e4a1-e68c-4015-80dc-28f4d0785847",
    "link_grupo": "99e9eded-f032-4554-b500-2df1a8b1ab02",
    "gargalo":    "ea72efed-ab12-4396-8c71-dcd7530b72e5",
    "ultima_atualizacao": "875e9007-605a-4cc1-afc0-4127e4fef483",
}

MAPA = {
    "Juliana Couto":                "981821890966321",
    "Rogério":                      "1426016344887799",
    "Jessíca Machado":              "2104277963310752",
    "Débora e Dilson":              "161254036978153",
    "Grasielli e Amanda":           "957299715350643",
    "Kaüe/Cristian":                "1092853728175420",
    "Jozi":                         "876814367940864",
    "Matheus":                      "987188046671152",
    "Rafael Gentine - Limeira/SP":  "1269260778582752",
    "Rafael Gentine - Macapá/AP":   "352322129822164",
    "Rafael Gonzaga - Santarém/PR": "1226501099425856",
    "Ademir":                       "570493612230387",
    "Tendência Planejados":         "1451590226264346",
    "Torre Estruturas":             "956582003798132",
    "Mamuh Steakhouse":             "892974669033947",
}


def get_clientes():
    url = "https://api.clickup.com/api/v2/list/{}/task".format(CLICKUP_LIST_ID)
    headers = {"Authorization": CLICKUP_TOKEN}
    params = {"include_closed": "false", "limit": 100}
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
    url = "https://api.clickup.com/api/v2/task/{}".format(task_id)
    headers = {"Authorization": CLICKUP_TOKEN, "Content-Type": "application/json"}
    payload = {"custom_fields": [{"id": campo_id, "value": valor}]}
    try:
        requests.put(url, headers=headers, json=payload)
    except Exception:
        pass


def get_meta(account_id):
    hoje = datetime.now()
    fim = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")
    inicio = (hoje - timedelta(days=7)).strftime("%Y-%m-%d")
    url = "https://graph.facebook.com/v19.0/act_{}/insights".format(account_id)
    params = {
        "access_token": META_TOKEN,
        "fields": "spend,actions,cost_per_action_type",
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


def extrair_leads(ins):
    if not ins:
        return 0
    for a in ins.get("actions", []):
        if a.get("action_type") in ["lead", "onsite_conversion.lead_grouped"]:
            return int(a.get("value", 0))
    return 0


def extrair_cpl(ins):
    if not ins:
        return None
    for a in ins.get("cost_per_action_type", []):
        if a.get("action_type") in ["lead", "onsite_conversion.lead_grouped"]:
            v = float(a.get("value", 0))
            return round(v, 2) if v > 0 else None
    sp = float(ins.get("spend", 0))
    l = extrair_leads(ins)
    return round(sp / l, 2) if l > 0 else None


def extrair_investimento(ins):
    if not ins:
        return 0
    return round(float(ins.get("spend", 0)), 2)


# ---- INICIO ----
linhas = []

def log(txt=""):
    print(txt)
    linhas.append(txt)

log("=" * 60)
log("CS SEMANAL AUTOMATIZADO")
log("Data: {}".format(datetime.now().strftime("%d/%m/%Y %H:%M")))
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

for t in tasks:
    nome = t.get("name", "")
    empresa = get_campo(t, CAMPOS["cliente"])
    plat = get_campo(t, CAMPOS["plataforma"])
    pgto = get_campo(t, CAMPOS["pgto_ca"])
    meta_cpl_val = get_campo(t, CAMPOS["meta_cpl"])
    leads_7d = get_campo(t, CAMPOS["leads_7d"]) or 0
    cpl_7d = get_campo(t, CAMPOS["cpl_7d"])
    gargalo = get_campo(t, CAMPOS["gargalo"])
    link = get_campo(t, CAMPOS["link_grupo"])

    usa_meta = plat in ["Meta Ads", "Face + Google"]
    inv = 0

    mapa_key = None
    if nome in MAPA:
        mapa_key = nome
    else:
        for k in MAPA:
            if k.lower() in nome.lower() or nome.lower() in k.lower():
                mapa_key = k
                break

    if usa_meta and mapa_key:
        ins = get_meta(MAPA[mapa_key])
        if ins:
            cpl_7d = extrair_cpl(ins)
            leads_7d = extrair_leads(ins)
            inv = extrair_investimento(ins)
            # Atualiza ClickUp automaticamente
            hoje_str = datetime.now().strftime("%Y-%m-%d")
            if cpl_7d:
                atualizar_campo(t["id"], CAMPOS["cpl_7d"], cpl_7d)
            atualizar_campo(t["id"], CAMPOS["leads_7d"], str(leads_7d))
            atualizar_campo(t["id"], CAMPOS["ultima_atualizacao"], hoje_str)
            log("[OK] {}: CPL R${} | {} leads | R${} investido".format(nome, cpl_7d, leads_7d, inv))
        else:
            log("[--] {}: sem dados Meta esta semana".format(nome))
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
        if dev > 0.25:
            saude = "Em Risco"
        elif dev > 0.10:
            saude = "Atencao"
        else:
            saude = "Dentro da Meta"
    else:
        saude = "Dentro da Meta"

    l7 = int(leads_7d) if leads_7d else 0
    display = empresa or nome

    if saude == "Dentro da Meta":
        msg = "Ola! Update da semana.\n\n*{}*\n{} leads".format(display, l7)
        if c7:
            msg += " | CPL R${:.2f}".format(c7)
        if mc:
            msg += "\nMeta: R${:.2f}".format(mc)
        msg += "\n\nPerformando bem! Qualquer duvida, estou aqui."
        dentro_meta.append(display)
    elif saude == "Atencao":
        msg = "Ola! Alinhamento da semana.\n\n*{}*\n{} leads".format(display, l7)
        if c7 and mc:
            msg += " | CPL R${:.2f} (meta: R${:.2f})".format(c7, mc)
        msg += "\n\nLevemente acima — ajustes em andamento."
    else:
        msg = "Ola! Transparencia sobre essa semana.\n\n*{}*\n{} leads".format(display, l7)
        if c7 and mc:
            msg += " | CPL R${:.2f} (meta: R${:.2f})".format(c7, mc)
        msg += "\n\nIdentifiquei o gargalo ({}) e ja estou corrigindo.".format(
            gargalo or "estrutura")
        em_risco.append(display)

    mensagens.append({"nome": display, "saude": saude, "link": link, "msg": msg})

# ---- RESUMO EXECUTIVO ----
log("\n" + "=" * 60)
log("RESUMO EXECUTIVO")
log("=" * 60)
log("Total de clientes: {}".format(len(tasks)))
log("Dentro da Meta: {}".format(len(dentro_meta)))
log("Em Risco / Atencao: {}".format(len(em_risco)))
if em_risco:
    log("  Atencao para: {}".format(", ".join(em_risco)))
log("Pix a enviar: {} clientes | R${:.2f}".format(len(boleto), len(boleto) * PIX_SEMANAL))

# ---- MENSAGENS ----
log("\n" + "=" * 60)
log("MENSAGENS DE CS — copie e mande no WhatsApp")
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

# Salva o output em arquivo para o GitHub Actions disponibilizar
with open("output_cs.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(linhas))
