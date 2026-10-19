import os
import sys
import customtkinter as ctk
from PIL import Image, ImageGrab
import tkinter as tk
from datetime import datetime

from config_manager import carregar_config, salvar_config

# ------------------------------------------------------------------
# Configuração inicial (Forçado no modo escuro)
# ------------------------------------------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

# Paleta institucional (verde Usina Santa Adélia)
COR_VERDE       = "#1E4620"
COR_VERDE_HOVER = "#2D6A30"
COR_VERDE_CLARO = "#A5D6A7"


class App(ctk.CTk):

    def __init__(self, callback_executar_ciclo=None, callback_teste_imediato=None):
        super().__init__()

        self.callback_executar_ciclo = callback_executar_ciclo
        self.callback_teste_imediato = callback_teste_imediato

        self.title("Monitoramento — Usina Santa Adélia")
        self.geometry("950x650")
        self.resizable(False, False)

        # Carrega as configurações salvas no config.json
        self.config_atual = carregar_config()

        # Grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Variáveis de Controle
        self.rodando = False
        self.tipo_captura_var   = ctk.StringVar(value=self.config_atual.get("tipo_captura", "inteira"))
        
        # Recupera região personalizada se existir
        rx = self.config_atual.get("regiao_x", 0)
        ry = self.config_atual.get("regiao_y", 0)
        rw = self.config_atual.get("regiao_largura", 800)
        rh = self.config_atual.get("regiao_altura", 600)
        self.regiao_selecionada  = (rx, ry, rw, rh) if (rw > 0 and rh > 0) else None
        
        # Variáveis de Tempo
        intervalo_total = self.config_atual.get("intervalo_minutos", 60)
        self.freq_horas_var      = ctk.StringVar(value=str(intervalo_total // 60))
        self.freq_minutos_var    = ctk.StringVar(value=str(intervalo_total % 60))
        
        # Credenciais
        self.telegram_token_var   = ctk.StringVar(value=self.config_atual.get("telegram_token", ""))
        self.telegram_chat_id_var = ctk.StringVar(value=self.config_atual.get("telegram_chat_id", ""))
        self.gemini_key_var       = ctk.StringVar(value=self.config_atual.get("gemini_api_key", ""))

        # Construção da Interface
        self.setup_sidebar()
        self.setup_content_frames()

        self.mostrar_frame("painel")

    # ------------------------------------------------------------------
    # SIDEBAR (MENU LATERAL)
    # ------------------------------------------------------------------
    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # ---- Logo ----
        if hasattr(sys, '_MEIPASS'):
            logo_path = os.path.join(sys._MEIPASS, "logo.png")
        else:
            logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                largura = 150
                altura = int(img.height * (largura / img.width))
                logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(largura, altura))
                self.logo_label = ctk.CTkLabel(self.sidebar_frame, image=logo_img, text="")
                self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))
            except Exception as e:
                print(f"[interface] Falha ao carregar logo: {e}")
                self._logo_fallback()
        else:
            self._logo_fallback()

        ctk.CTkLabel(
            self.sidebar_frame, text="Monitoramento de Relatórios",
            font=ctk.CTkFont(size=11), text_color="gray60",
        ).grid(row=1, column=0, padx=20, pady=(0, 25))

        # ---- Botões de Navegação ----
        self.btn_painel = self._criar_botao_menu("📊  Painel Principal", 2, lambda: self.mostrar_frame("painel"))
        self.btn_telegram = self._criar_botao_menu("🤖  Telegram & IA", 3, lambda: self.mostrar_frame("telegram"))
        self.btn_config = self._criar_botao_menu("⚙️  Configurações", 4, lambda: self.mostrar_frame("config"))

        # ---- Rodapé ----
        rodape = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        rodape.grid(row=11, column=0, padx=15, pady=20, sticky="ew")
        self.lbl_status_rodape = ctk.CTkLabel(rodape, text="● Sistema pronto", font=ctk.CTkFont(size=11), text_color=COR_VERDE_CLARO)
        self.lbl_status_rodape.pack(anchor="w")
        ctk.CTkLabel(rodape, text="v1.0 • Santa Adélia", font=ctk.CTkFont(size=10), text_color="gray50").pack(anchor="w", pady=(4, 0))

    def _criar_botao_menu(self, texto, linha, comando):
        btn = ctk.CTkButton(
            self.sidebar_frame, text=texto, anchor="w", height=44, corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent",
            hover_color=("#D0E1D4", "#2A382B"), text_color=("gray10", "gray90"), command=comando,
        )
        btn.grid(row=linha, column=0, padx=15, pady=6, sticky="ew")
        return btn

    def _logo_fallback(self):
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="USINA\nSANTA ADÉLIA", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=(COR_VERDE, COR_VERDE_CLARO), justify="center",
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))

    # ------------------------------------------------------------------
    # ÁREA DE CONTEÚDO
    # ------------------------------------------------------------------
    def setup_content_frames(self):
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        self.frames = {
            "painel":   self.criar_tela_painel(self.content_area),
            "telegram": self.criar_tela_telegram(self.content_area),
            "config":   self.criar_tela_config(self.content_area),
        }
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, nome_frame):
        self.frames[nome_frame].tkraise()
        botoes = {"painel": self.btn_painel, "telegram": self.btn_telegram, "config": self.btn_config}
        for nome, btn in botoes.items():
            if nome == nome_frame:
                btn.configure(fg_color=COR_VERDE, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

    # ------------------------------------------------------------------
    # TELA 1 — PAINEL PRINCIPAL
    # ------------------------------------------------------------------
    def criar_tela_painel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Painel de Monitoramento", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))

        # ---- Botão Principal ----
        self.btn_iniciar = ctk.CTkButton(
            frame, text="▶  INICIAR MONITORAMENTO", 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER, height=50,
            command=self.alternar_monitoramento
        )
        self.btn_iniciar.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # ---- Card de controle (Frequência) ----
        control_card = ctk.CTkFrame(frame, corner_radius=10)
        control_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        control_card.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(control_card, text="Frequência:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=(20, 10), pady=18, sticky="w")

        frame_horas = ctk.CTkFrame(control_card, fg_color="transparent")
        frame_horas.grid(row=0, column=1, padx=(0, 10), pady=18, sticky="w")
        vcmd = (self.register(self._validar_numero), '%P')
        self.entry_horas = ctk.CTkEntry(frame_horas, width=60, textvariable=self.freq_horas_var, justify="center", validate="key", validatecommand=vcmd)
        self.entry_horas.pack(side="left")
        ctk.CTkLabel(frame_horas, text="h").pack(side="left", padx=(5, 0))

        frame_minutos = ctk.CTkFrame(control_card, fg_color="transparent")
        frame_minutos.grid(row=0, column=2, padx=(0, 20), pady=18, sticky="w")
        self.entry_minutos = ctk.CTkEntry(frame_minutos, width=60, textvariable=self.freq_minutos_var, justify="center", validate="key", validatecommand=vcmd)
        self.entry_minutos.pack(side="left")
        ctk.CTkLabel(frame_minutos, text="min").pack(side="left", padx=(5, 0))
        self.entry_minutos.bind("<FocusOut>", self._ajustar_minutos)

        ctk.CTkButton(control_card, text="📸  Testar Print Imediato", fg_color="#4B5563", hover_color="#374151", width=200, command=self.disparar_teste).grid(row=0, column=3, padx=20, pady=18, sticky="e")

        # ---- Card de status ----
        status_card = ctk.CTkFrame(frame, corner_radius=10)
        status_card.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        status_card.grid_columnconfigure((0, 1, 2), weight=1)

        self.lbl_estado = self._bloco_status(status_card, 0, "Estado", "Aguardando", "#9CA3AF")
        self.lbl_proxima = self._bloco_status(status_card, 1, "Próxima captura", "Nenhuma", "#9CA3AF")
        self.lbl_ultimo = self._bloco_status(status_card, 2, "Último envio", "Nenhum", "#9CA3AF")

        # ---- Logs ----
        logs_card = ctk.CTkFrame(frame, corner_radius=10)
        logs_card.grid(row=4, column=0, sticky="nsew")
        logs_card.grid_rowconfigure(1, weight=1)
        logs_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(logs_card, text="Histórico e Logs de Execução", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        self.txt_logs = ctk.CTkTextbox(logs_card, corner_radius=8, font=ctk.CTkFont(family="Consolas", size=12), fg_color="#1A1A1A", text_color="#E0E0E0", border_width=1, border_color="#333333")
        self.txt_logs.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.txt_logs.configure(state="disabled")
        self.adicionar_log("Sistema iniciado. Configurações carregadas.")

        return frame

    def _bloco_status(self, parent, coluna, titulo, valor_inicial, cor_valor):
        bloco = ctk.CTkFrame(parent, fg_color="transparent")
        bloco.grid(row=0, column=coluna, padx=15, pady=15, sticky="ew")
        
        ctk.CTkLabel(bloco, text=titulo.upper(), font=ctk.CTkFont(size=10, weight="bold"), text_color="gray55").pack(anchor="w", pady=(0, 4))
        
        badge = ctk.CTkFrame(bloco, fg_color="#2B2B2B", corner_radius=6) 
        badge.pack(anchor="w")
        
        lbl_valor = ctk.CTkLabel(badge, text=valor_inicial, font=ctk.CTkFont(size=13, weight="bold"), text_color=cor_valor, padx=10, pady=2)
        lbl_valor.pack()
        return lbl_valor

    def _validar_numero(self, texto):
        return texto.isdigit() or texto == ""

    def _ajustar_minutos(self, event=None):
        try:
            mins = int(self.freq_minutos_var.get() or 0)
            if mins >= 60:
                horas_atuais = int(self.freq_horas_var.get() or 0)
                self.freq_horas_var.set(str(horas_atuais + (mins // 60)))
                self.freq_minutos_var.set(str(mins % 60))
        except ValueError:
            self.freq_minutos_var.set("0")

    def obter_intervalo_minutos(self):
        try:
            horas = int(self.freq_horas_var.get() or 0)
            minutos = int(self.freq_minutos_var.get() or 0)
            total = (horas * 60) + minutos
            return total if total > 0 else 1
        except ValueError:
            return 60

    def alternar_monitoramento(self):
        if not self.rodando:
            self.rodando = True
            self.btn_iniciar.configure(text="⏹  PARAR MONITORAMENTO", fg_color="#B91C1C", hover_color="#991B1B")
            self.adicionar_log("Monitoramento INICIADO.")
            self.lbl_estado.configure(text="Rodando", text_color="#10B981")
            
            # Salva o intervalo atualizado no config
            intervalo = self.obter_intervalo_minutos()
            self.config_atual["intervalo_minutos"] = intervalo
            salvar_config(self.config_atual)

            if self.callback_executar_ciclo:
                config = {
                    "tipo_captura": self.tipo_captura_var.get(),
                    "intervalo_minutos": intervalo,
                    "telegram_token": self.entry_token.get(),
                    "telegram_chat_id": self.entry_chat.get(),
                    "gemini_api_key": self.entry_gemini.get(),
                    "regiao_x": self.regiao_selecionada[0] if self.regiao_selecionada else 0,
                    "regiao_y": self.regiao_selecionada[1] if self.regiao_selecionada else 0,
                    "regiao_largura": self.regiao_selecionada[2] if self.regiao_selecionada else 0,
                    "regiao_altura": self.regiao_selecionada[3] if self.regiao_selecionada else 0,
                }
                self.callback_executar_ciclo(config)
        else:
            self.rodando = False
            self.btn_iniciar.configure(text="▶  INICIAR MONITORAMENTO", fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER)
            self.adicionar_log("Monitoramento PARADO pelo usuário.")
            self.lbl_estado.configure(text="Parado", text_color="#EF4444")

    # ------------------------------------------------------------------
    # TELA 2 — TELEGRAM & IA
    # ------------------------------------------------------------------
    def criar_tela_telegram(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Telegram & Inteligência Artificial", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))

        tg_card = self._card_form(frame, "🤖  Bot do Telegram", 1)
        self.entry_token = self._campo(tg_card, 0, "Token do Bot:", "Ex: 123456789:ABCdef...", show="*", textvariable=self.telegram_token_var)
        self.entry_chat = self._campo(tg_card, 1, "Chat ID do Destino:", "Ex: -100123456789", textvariable=self.telegram_chat_id_var)

        ia_card = self._card_form(frame, "🧠  Inteligência Artificial (Gemini)", 2)
        self.entry_gemini = self._campo(ia_card, 0, "Chave API Gemini:", "Ex: AIzaSyD...", show="*", textvariable=self.gemini_key_var)

        ctk.CTkButton(frame, text="💾  Salvar Credenciais", fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER, width=220, height=40, command=self.salvar_credenciais).grid(row=3, column=0, sticky="e", pady=(10, 0))
        return frame

    # ------------------------------------------------------------------
    # TELA 3 — CONFIGURAÇÕES
    # ------------------------------------------------------------------
    def criar_tela_config(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Configurações do Sistema", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 15))

        cap_card = self._card_form(frame, "📷  Captura de Tela", 1)

        ctk.CTkLabel(cap_card, text="Tamanho da Imagem:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=(18, 8), sticky="nw")

        radio_frame = ctk.CTkFrame(cap_card, fg_color="transparent")
        radio_frame.grid(row=0, column=1, padx=20, pady=(18, 8), sticky="w")

        self.radio_inteira = ctk.CTkRadioButton(radio_frame, text="Padrão (Tela Inteira)", variable=self.tipo_captura_var, value="inteira", command=self.atualizar_estado_botao_area)
        self.radio_inteira.pack(anchor="w", pady=3)

        self.radio_personalizada = ctk.CTkRadioButton(radio_frame, text="Personalizada (Área Específica)", variable=self.tipo_captura_var, value="personalizada", command=self.atualizar_estado_botao_area)
        self.radio_personalizada.pack(anchor="w", pady=3)

        self.btn_selecionar_area = ctk.CTkButton(cap_card, text="🖱️ Selecionar Área com o Mouse", fg_color="#4B5563", hover_color="#374151", state="disabled", command=self.iniciar_selecao_area)
        self.btn_selecionar_area.grid(row=1, column=1, padx=20, pady=(0, 5), sticky="w")

        texto_area = "Nenhuma área personalizada selecionada."
        if self.regiao_selecionada:
            x, y, w, h = self.regiao_selecionada
            texto_area = f"Área salva: X:{x} Y:{y} | L:{w} A:{h}"

        self.lbl_info_area = ctk.CTkLabel(cap_card, text=texto_area, font=ctk.CTkFont(size=11, slant="italic"), text_color="gray55")
        self.lbl_info_area.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 18), sticky="w")

        self.atualizar_estado_botao_area()

        return frame

    def atualizar_estado_botao_area(self):
        if self.tipo_captura_var.get() == "personalizada":
            self.btn_selecionar_area.configure(state="normal", fg_color="#2E7D32")
        else:
            self.btn_selecionar_area.configure(state="disabled", fg_color="#4B5563")

    def iniciar_selecao_area(self):
        self.withdraw()
        self.tela_selecao = tk.Toplevel(self)
        self.tela_selecao.attributes("-fullscreen", True)
        self.tela_selecao.attributes("-alpha", 0.1)
        self.tela_selecao.attributes("-topmost", True)
        self.tela_selecao.config(cursor="cross")
        
        self.canvas_sel = tk.Canvas(self.tela_selecao, cursor="cross", bg="white", highlightthickness=0)
        self.canvas_sel.pack(fill="both", expand=True)
        
        self.canvas_sel.create_text(20, 20, anchor="nw", fill="black", text="Clique e arraste para selecionar a área. Solte para confirmar.\n(Pressione ESC para cancelar)", font=("Arial", 18, "bold"))
        
        self.canvas_sel.bind("<ButtonPress-1>", self._on_press)
        self.canvas_sel.bind("<B1-Motion>", self._on_drag)
        self.canvas_sel.bind("<ButtonRelease-1>", self._on_release)
        self.tela_selecao.bind("<Escape>", lambda e: self._fechar_selecao())

    def _on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if hasattr(self, 'retangulo_id') and self.retangulo_id:
            self.canvas_sel.delete(self.retangulo_id)
        self.retangulo_id = self.canvas_sel.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", width=3)

    def _on_drag(self, event):
        self.canvas_sel.coords(self.retangulo_id, self.start_x, self.start_y, event.x, event.y)

    def _on_release(self, event):
        x1, x2 = sorted([self.start_x, event.x])
        y1, y2 = sorted([self.start_y, event.y])
        largura = x2 - x1
        altura = y2 - y1
        
        if largura > 10 and altura > 10:
            self.regiao_selecionada = (x1, y1, largura, altura)
            self.lbl_info_area.configure(text=f"Área: X:{x1} Y:{y1} | L:{largura} A:{altura}", text_color="#A5D6A7")
            
            # Salva a nova região no json
            self.config_atual["tipo_captura"] = "personalizada"
            self.config_atual["regiao_x"] = x1
            self.config_atual["regiao_y"] = y1
            self.config_atual["regiao_largura"] = largura
            self.config_atual["regiao_altura"] = altura
            salvar_config(self.config_atual)

        self._fechar_selecao()

    def _fechar_selecao(self):
        self.tela_selecao.destroy()
        self.deiconify()

    # ------------------------------------------------------------------
    # POP-UP DE AVISO CENTRALIZADO
    # ------------------------------------------------------------------
    def exibir_aviso_pop_up(self, mensagem, tempo_auto_fechar=6):
        """Cria uma caixinha de aviso no centro da tela que fecha sozinha."""
        try:
            popup = ctk.CTkToplevel(self)
            popup.title("⏰ Aviso de Captura")
            popup.geometry("380x160")
            popup.attributes("-topmost", True)
            popup.resizable(False, False)

            # Centraliza na tela
            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            x = (screen_width // 2) - (380 // 2)
            y = (screen_height // 2) - (160 // 2)
            popup.geometry(f"380x160+{x}+{y}")

            # Conteúdo do Popup
            lbl_icone = ctk.CTkLabel(popup, text="🚨 AVISO DE MONITORAMENTO 🚨", font=ctk.CTkFont(size=14, weight="bold"), text_color="#F59E0B")
            lbl_icone.pack(pady=(15, 5))

            lbl_msg = ctk.CTkLabel(popup, text=mensagem, font=ctk.CTkFont(size=13), wraplength=340)
            lbl_msg.pack(pady=5)

            btn_ok = ctk.CTkButton(popup, text="Entendi (OK)", width=120, command=popup.destroy)
            btn_ok.pack(pady=(10, 10))

            popup.after(tempo_auto_fechar * 1000, lambda: popup.destroy() if popup.winfo_exists() else None)
        except Exception as e:
            print(f"Erro ao exibir popup: {e}")

    # ------------------------------------------------------------------
    # HELPERS DE FORMULÁRIO E AÇÕES
    # ------------------------------------------------------------------
    def _card_form(self, parent, titulo, linha):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=linha, column=0, sticky="ew", pady=(0, 12))
        card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
        
        sep = ctk.CTkFrame(card, height=1, fg_color="#333333")
        sep.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
        
        return card

    def _campo(self, card, indice, label, placeholder, show=None, textvariable=None):
        linha = indice + 2
        ctk.CTkLabel(card, text=label).grid(row=linha, column=0, padx=20, pady=10, sticky="w")
        entry = ctk.CTkEntry(card, placeholder_text=placeholder, show=show or "", height=36, textvariable=textvariable)
        entry.grid(row=linha, column=1, padx=20, pady=10, sticky="ew")
        return entry

    def adicionar_log(self, mensagem):
        # 1. Mostra na interface gráfica
        self.txt_logs.configure(state="normal")
        self.txt_logs.insert("end", f"> {mensagem}\n")
        self.txt_logs.see("end")
        self.txt_logs.configure(state="disabled")

        # 2. Salva automaticamente em arquivo de log
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("historico_execucao.log", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {mensagem}\n")
        except Exception as e:
            print(f"Erro ao gravar log em arquivo: {e}")

    def disparar_teste(self):
        self.adicionar_log("Disparando captura de teste imediato...")
        if self.callback_teste_imediato:
            config = {
                "tipo_captura": self.tipo_captura_var.get(),
                "telegram_token": self.entry_token.get(),
                "telegram_chat_id": self.entry_chat.get(),
                "gemini_api_key": self.entry_gemini.get(),
                "regiao_x": self.regiao_selecionada[0] if self.regiao_selecionada else 0,
                "regiao_y": self.regiao_selecionada[1] if self.regiao_selecionada else 0,
                "regiao_largura": self.regiao_selecionada[2] if self.regiao_selecionada else 0,
                "regiao_altura": self.regiao_selecionada[3] if self.regiao_selecionada else 0,
            }
            self.callback_teste_imediato(config)
        else:
            self.adicionar_log("Teste imediato concluído (Modo isolado).")

    def salvar_credenciais(self):
        self.config_atual["telegram_token"] = self.entry_token.get()
        self.config_atual["telegram_chat_id"] = self.entry_chat.get()
        self.config_atual["gemini_api_key"] = self.entry_gemini.get()
        self.config_atual["tipo_captura"] = self.tipo_captura_var.get()
        self.config_atual["intervalo_minutos"] = self.obter_intervalo_minutos()
        
        salvar_config(self.config_atual)
        self.adicionar_log("Credenciais e configurações salvas no config.json com sucesso!")


if __name__ == "__main__":
    app = App()
    app.mainloop()