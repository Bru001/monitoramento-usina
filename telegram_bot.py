import requests

def enviar_telegram(caminho_imagem: str, texto_analise: str, token: str, chat_id: str):
    if not token or not chat_id:
        raise ValueError("Token ou Chat ID do Telegram não estão configurados. Configure no menu.")

    url_foto = f"https://api.telegram.org/bot{token}/sendPhoto"
    url_msg = f"https://api.telegram.org/bot{token}/sendMessage"

    # Prepara o texto limpo (remove caracteres markdown que quebram o Telegram se necessário)
    legenda = f"🤖 Análise da IA:\n\n{texto_analise}"
    
    # Se a legenda passar do limite de 1024 caracteres do Telegram para fotos, corta com segurança
    if len(legenda) > 1024:
        legenda = legenda[:1020] + "..."

    # 1. Tenta enviar a foto com a legenda (SEM parse_mode para o Telegram não tentar interpretar sintaxe)
    with open(caminho_imagem, "rb") as foto:
        resposta = requests.post(
            url_foto,
            data={
                "chat_id": chat_id,
                "caption": legenda
                # Nota: Nenhum parse_mode é enviado aqui para evitar o erro de entidades
            },
            files={"photo": foto}
        )
    
    # Se a foto falhar por algum motivo de tamanho da legenda, divide: envia a foto pura e depois o texto
    if not resposta.ok:
        with open(caminho_imagem, "rb") as foto:
            requests.post(url_foto, data={"chat_id": chat_id}, files={"photo": foto})
        
        # Envia o relatório completo em texto separado
        requests.post(
            url_msg, 
            json={
                "chat_id": chat_id, 
                "text": f"🤖 Análise da IA:\n\n{texto_analise}"
            }
        )