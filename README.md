📊 Sistema de Monitoramento e Análise de Relatórios — Usina Santa Adélia

Sistema desktop desenvolvido em Python com interface gráfica moderna (CustomTkinter) para automatizar a captura de telas e relatórios operacionais, realizar análises inteligentes utilizando a Inteligência Artificial do Google (Gemini) e enviar os resultados e imagens diretamente para um canal ou chat no Telegram.

🚀 Funcionalidades

Captura Automatizada ou Manual: Permite capturar a tela inteira ou uma região personalizada da tela em intervalos regulares configuráveis.

Análise Inteligente (IA): Utiliza o modelo Gemini para interpretar o relatório na imagem, destacando métricas principais e alertando sobre anomalias ou desvios operacionais.

Envio via Telegram: Dispara automaticamente a imagem capturada e o resumo gerado pela IA para o chat configurado.

Alertas Antecipados: Conta com contadores regressivos na tela e pop-ups flutuantes avisando quando uma nova captura está prestes a acontecer (5, 2 e 1 minuto antes).

Logs de Execução: Registra todas as atividades e eventos em tempo real tanto na interface gráfica quanto em um arquivo de log local (historico_execucao.log).

📂 Estrutura do Projeto

monitoramento-usina/
├── main.py                # Ponto de entrada do programa e controle do loop de tempo
├── interface.py           # Interface gráfica construída com CustomTkinter
├── capture.py             # Módulo responsável pela captura de tela (PyAutoGUI)
├── ai_analyzer.py         # Módulo de integração com a API da IA Gemini
├── telegram_bot.py        # Módulo de envio de mensagens e imagens para o Telegram
├── config_manager.py      # Gerenciador de leitura e escrita do arquivo config.json
├── main.spec              # Arquivo de configuração para compilação com PyInstaller
├── logo.png               # Logotipo da aplicação exibido na interface
└── README.md              # Documentação oficial do projeto


🛠️ Tecnologias Utilizadas

Python 3.x

CustomTkinter (Interface Gráfica)

PyAutoGUI (Captura de tela)

Google GenAI SDK (google-genai / Gemini Flash)

Pillow (PIL) (Manipulação de imagens)

PyInstaller (Empacotamento para executável .exe)

⚙️ Configuração e Instalação

Clone o repositório ou baixe os arquivos para o seu computador:

git clone https://github.com/SEU-USUARIO/monitoramento-usina-santa-adelia.git


Instale as dependências necessárias via terminal:

pip install customtkinter pillow pyautogui google-genai


Configure as suas credenciais diretamente na interface gráfica do aplicativo (Aba Telegram & IA) ou criando um arquivo config.json:

Token do Bot do Telegram

Chat ID do Telegram

Chave da API do Gemini (gemini_api_key)

Execute o sistema:

python main.py


📦 Como Gerar o Executável (.exe)

Se desejar gerar um aplicativo executável independente para rodar no Windows sem precisar do interpretador Python instalado:

pyinstaller main.spec


(O executável será gerado dentro da pasta dist/).
