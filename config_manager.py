import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "telegram_token": "",
    "telegram_chat_id": "",
    "gemini_api_key": "",
    "intervalo_minutos": 60,
    "tipo_captura": "inteira",  # 'inteira' ou 'personalizada'
    "regiao_x": 0,
    "regiao_y": 0,
    "regiao_largura": 800,
    "regiao_altura": 600,
}


def carregar_config():
  if not os.path.exists(CONFIG_FILE):
    salvar_config(DEFAULT_CONFIG)
  with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    try:
      config = json.load(f)
      # Garante chaves novas se o arquivo for antigo
      for chave, valor in DEFAULT_CONFIG.items():
        if chave not in config:
          config[chave] = valor
      return config
    except json.JSONDecodeError:
      return DEFAULT_CONFIG


def salvar_config(config):
  with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)