import time
import winsound
from datetime import datetime

# Import do módulo de interface (atualizado de gui para interface)
from interface import App

# Imports dos demais módulos do projeto
from capture import tirar_foto
from ai_analyzer import analisar_imagem
from telegram_bot import enviar_telegram

# Variável global para controlar o estado do monitoramento
monitoramento_ativo = False


def executar_ciclo(config=None, app_gui=None, teste_imediato=False):
    """
    Executa o ciclo de captura, análise e envio.
    Se teste_imediato for True, roda apenas 1 vez.
    Se for False, entra em loop continuo respeitando o intervalo configurado.
    """
    global monitoramento_ativo

    if teste_imediato:
        monitoramento_ativo = False
    else:
        monitoramento_ativo = True

    # ---- CONTAGEM REGRESSIVA INICIAL (Apenas ao clicar em Iniciar) ----
    if monitoramento_ativo and not teste_imediato:
        if app_gui:
            app_gui.adicionar_log("⏳ Preparando primeira captura em 3 segundos...")
            time.sleep(1)
            if not monitoramento_ativo: return
            app_gui.adicionar_log("⏳ 2...")
            time.sleep(1)
            if not monitoramento_ativo: return
            app_gui.adicionar_log("⏳ 1...")
            time.sleep(1)
            if not monitoramento_ativo: return

    while monitoramento_ativo or teste_imediato:
        print("\n--- Iniciando ciclo de captura, análise e envio ---")
        
        if app_gui:
            app_gui.adicionar_log("Iniciando captura de tela...")
            app_gui.lbl_estado.configure(text="Rodando", text_color="#10B981")

        try:
            if not config:
                config = {}

            tipo = config.get("tipo_captura", "inteira")
            regiao = None
            if tipo == "personalizada":
                regiao = (
                    config.get("regiao_x", 0),
                    config.get("regiao_y", 0),
                    config.get("regiao_largura", 800),
                    config.get("regiao_altura", 600),
                )

            # 1. Tira a foto da tela ou da região selecionada
            caminho = tirar_foto(tipo_captura=tipo, regiao=regiao)
            print(f"[+] Foto capturada: {caminho}")
            if app_gui:
                app_gui.adicionar_log(f"Foto capturada: {caminho}")
                app_gui.lbl_ultimo.configure(text=f"{datetime.now():%H:%M:%S}", text_color="#10B981")

            # 2. Analisa o relatório com a IA Gemini (se a API key estiver configurada)
            if config.get("gemini_api_key"):
                if app_gui:
                    app_gui.adicionar_log("Processando imagem com Gemini IA...")
                analise = analisar_imagem(caminho, config["gemini_api_key"])
            else:
                analise = "Captura realizada com sucesso (Modo sem IA)."

            # 3. Envia o relatório e o print para o Telegram
            if config.get("telegram_token") and config.get("telegram_chat_id"):
                if app_gui:
                    app_gui.adicionar_log("Enviando para o Telegram...")
                enviar_telegram(
                    caminho, 
                    analise, 
                    config["telegram_token"], 
                    config["telegram_chat_id"]
                )
                if app_gui:
                    app_gui.adicionar_log("Envio para o Telegram concluído!")

            if app_gui:
                app_gui.adicionar_log("Ciclo concluído com sucesso!")
            print("[✔] Ciclo concluído com sucesso!")

        except Exception as e:
            erro_msg = f"Erro na execução: {e}"
            print(f"[✘] {erro_msg}")
            if app_gui:
                app_gui.adicionar_log(erro_msg)
                app_gui.lbl_estado.configure(text="Erro", text_color="#EF4444")

        # Se for um teste manual imediato, interrompe o loop aqui
        if teste_imediato:
            break

        # --- LÓGICA DE ESPERA E CRONÔMETRO REVISADA ---
        minutos_espera = config.get("intervalo_minutos", 60)
        segundos_espera = minutos_espera * 60
        
        if app_gui:
            app_gui.adicionar_log(f"Aguardando {minutos_espera} minutos para o próximo ciclo...")
            
        avisou_5min = False
        avisou_2min = False
        avisou_1min = False

        for segundo_restante in range(segundos_espera, 0, -1):
            if not monitoramento_ativo:
                break
                
            if app_gui:
                # Cálculo exato de horas, minutos e segundos para exibição
                h = segundo_restante // 3600
                m = (segundo_restante % 3600) // 60
                s = segundo_restante % 60
                texto_tempo = f"{h:02d}:{m:02d}:{s:02d}"
                
                # Atualiza o relógio na interface a cada 1 segundo
                app_gui.lbl_proxima.configure(text=texto_tempo, text_color="#3B82F6")

                # ---- DISPARO DE AVISOS E POP-UPS ----
                if segundo_restante == 300 and not avisou_5min:
                    msg = "Faltam 5 minutos para a próxima captura de tela!"
                    app_gui.adicionar_log(f"⏰ AVISO: {msg}")
                    app_gui.after(0, lambda: app_gui.exibir_aviso_pop_up(msg, tempo_auto_fechar=6))
                    avisou_5min = True
                
                if segundo_restante == 120 and not avisou_2min:
                    msg = "Faltam 2 minutos para a próxima captura de tela!"
                    app_gui.adicionar_log(f"⏰ AVISO: {msg}")
                    app_gui.after(0, lambda: app_gui.exibir_aviso_pop_up(msg, tempo_auto_fechar=6))
                    avisou_2min = True

                if segundo_restante == 60 and not avisou_1min:
                    msg = "Falta apenas 1 MINUTO! Organize o relatório na tela."
                    app_gui.adicionar_log(f"🚨 AVISO: {msg}")
                    app_gui.after(0, lambda: app_gui.exibir_aviso_pop_up(msg, tempo_auto_fechar=8))
                    avisou_1min = True
                    if winsound:
                        try:
                            winsound.Beep(1000, 500)
                        except:
                            pass
            
            time.sleep(1)

    # Se o loop terminar (quando o usuário clica em parar), reseta os textos de status
    if app_gui and not teste_imediato:
        app_gui.lbl_estado.configure(text="Parado", text_color="#EF4444")
        app_gui.lbl_proxima.configure(text="Nenhuma", text_color="#9CA3AF")


# ------------------------------------------------------------------
# PONTO DE ENTRADA PRINCIPAL DA APLICAÇÃO
# ------------------------------------------------------------------
if __name__ == "__main__":
    import threading

    # Inicializa a interface gráfica
    app = App()

    def callback_iniciar_ciclo(config):
        threading.Thread(target=executar_ciclo, args=(config, app, False), daemon=True).start()

    def callback_teste_imediato(config):
        threading.Thread(target=executar_ciclo, args=(config, app, True), daemon=True).start()

    app.callback_executar_ciclo = callback_iniciar_ciclo
    app.callback_teste_imediato = callback_teste_imediato

    app.mainloop()