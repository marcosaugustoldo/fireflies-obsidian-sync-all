import os
import json
import requests
import re
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# ==========================================
# 1. CONFIGURAÇÕES E AMBIENTE
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

FF_API_KEY = os.getenv("FF_API_KEY")
OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT_PATH")

# O Livro-Caixa que impede duplicações e garante a extração de passivos
LEDGER_FILE = os.path.join(BASE_DIR, "synced_ledger.json")

# Fuso Horário cravado em Brasília (UTC-3)
BRT_TZ = timezone(timedelta(hours=-3))

if not FF_API_KEY or not OBSIDIAN_VAULT:
    print("ERRO CRÍTICO: .env incompleto. Verifique FF_API_KEY e OBSIDIAN_VAULT_PATH.")
    exit(1)

if not os.path.exists(OBSIDIAN_VAULT):
    print(f"ERRO CRÍTICO: O diretório do Obsidian não foi encontrado em: {OBSIDIAN_VAULT}")
    exit(1)

# ==========================================
# 2. CONTROLE DE ESTADO (DELTA SYNC)
# ==========================================
def load_ledger():
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            print("AVISO: Arquivo ledger corrompido. Iniciando um novo.")
            return set()
    return set()

def save_ledger(synced_ids):
    with open(LEDGER_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(synced_ids), f, indent=4)

# ==========================================
# 3. ENGENHARIA DE DADOS E API
# ==========================================
def sanitize_filename(name):
    # Remove caracteres que quebram o sistema de arquivos no Linux/Obsidian
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

def fetch_latest_transcripts():
    url = "https://api.fireflies.ai/graphql"
    headers = {
        "Authorization": f"Bearer {FF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # GraphQL cirúrgico exigindo a IA (summary) e as transcrições (sentences)
    query = """
    query {
      transcripts(limit: 50) {
        id
        title
        date
        duration
        summary {
          overview
          action_items
          shorthand_bullet
        }
        sentences {
          speaker_name
          text
        }
      }
    }
    """
    try:
        response = requests.post(url, headers=headers, json={"query": query})
        if response.status_code != 200:
            print(f"ERRO DE API: HTTP {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        return data.get("data", {}).get("transcripts", [])
    except Exception as e:
        print(f"ERRO DE CONEXÃO: Falha ao contatar a API do Fireflies -> {e}")
        return []

# ==========================================
# 4. MOTOR DE GERAÇÃO MARKDOWN (OBSIDIAN)
# ==========================================
def create_obsidian_note(transcript):
    t_id = transcript.get("id")
    title = transcript.get("title", "Reuniao_Sem_Titulo")
    date_ms = transcript.get("date")
    
    # Conversão de Timestamp Epoch para BRT
    if date_ms:
        dt_utc = datetime.fromtimestamp(int(date_ms) / 1000, tz=timezone.utc)
        dt_local = dt_utc.astimezone(BRT_TZ)
        date_str = dt_local.strftime("%Y-%m-%d")
        time_str = dt_local.strftime("%H:%M")
    else:
        date_str = datetime.now(BRT_TZ).strftime("%Y-%m-%d")
        time_str = "00:00"

    safe_title = sanitize_filename(f"{date_str} - {title}")
    filepath = os.path.join(OBSIDIAN_VAULT, f"{safe_title}.md")

    # Extração robusta dos metadados da IA (evita quebra se a IA falhar no Fireflies)
    summary_data = transcript.get("summary") or {}
    overview = summary_data.get("overview") or "Resumo não gerado pela IA."
    action_items = summary_data.get("action_items") or "Nenhum item de ação identificado."
    shorthand = summary_data.get("shorthand_bullet") or ""

    # Estruturação visual da nota com Frontmatter para Dataview
    content = f"""---
id: {t_id}
data: {date_str}
hora: {time_str}
duracao: {transcript.get('duration', 0)} min
tags: [fireflies, reuniao]
---

# {title}

## 🎯 Resumo da Reunião
{overview}

## ✅ Itens de Ação
{action_items}
"""
    if shorthand:
        content += f"\n## 📌 Pontos Chave\n{shorthand}\n"

    content += "\n## 📝 Transcrição\n"
    
    sentences = transcript.get("sentences", [])
    if not sentences:
        content += "\n*Nenhuma transcrição detalhada disponível para esta reunião.*\n"
    else:
        current_speaker = ""
        for sentence in sentences:
            speaker = sentence.get("speaker_name") or "Desconhecido"
            text = sentence.get("text", "").strip()
            
            # Agrupa as falas do mesmo palestrante
            if speaker != current_speaker:
                content += f"\n**{speaker}:**\n"
                current_speaker = speaker
            
            content += f"{text} "

    # Gravação no disco (I/O)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"SUCESSO: Nota rica criada -> {safe_title}.md")
        return True
    except Exception as e:
        print(f"FALHA: Não foi possível salvar {safe_title}.md no disco -> {e}")
        return False

# ==========================================
# 5. ORQUESTRADOR
# ==========================================
def main():
    print(f"[{datetime.now(BRT_TZ).strftime('%Y-%m-%d %H:%M:%S')}] Iniciando Delta Sync do Fireflies...")
    
    ledger = load_ledger()
    transcripts = fetch_latest_transcripts()
    
    if not transcripts:
        print("Nenhuma reunião retornada pela API ou erro na requisição.")
        return

    novas_reunioes = 0

    for t in transcripts:
        t_id = t.get("id")
        
        # Ignora se não houver ID válido ou se já estiver no Livro-Caixa
        if not t_id or t_id in ledger:
            continue 
        
        # Só carimba no Livro-Caixa se o Obsidian aceitar a gravação física no HD
        if create_obsidian_note(t):
            ledger.add(t_id)
            novas_reunioes += 1
            
    # Salva a memória de estado para a próxima execução
    save_ledger(ledger)
    print(f"Sincronização concluída. {novas_reunioes} novas reuniões extraídas com inteligência artificial.")

if __name__ == "__main__":
    main()
