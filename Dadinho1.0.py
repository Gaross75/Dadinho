import tkinter as tk
from tkinter import messagebox
import threading
import time
import requests
import json
import os  # <-- NOVA IMPORTAÇÃO NECESSÁRIA

# Novas importações para resolver o login e a API oficial do Gemini
import undetected_chromedriver as uc
from google import genai
import io
from PIL import Image
import base64

# Novas importações para automação de navegador
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class YouTubeAIBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Espectador de Live com IA (Selenium)")
        self.root.geometry("550x500")

        self.is_running = False
        self.driver = None  # Guardará a instância do navegador

        # --- INTERFACE TINKER ---
        tk.Label(root, text="URL da Live no YouTube:", font=("Arial", 12)).pack(pady=10)

        self.url_entry = tk.Entry(root, width=50, font=("Arial", 12))
        self.url_entry.pack(pady=5)

        tk.Label(root, text="Modo de Inteligência Artificial:", font=("Arial", 12)).pack(pady=10)

        self.ai_mode = tk.StringVar(value="local")

        tk.Radiobutton(root, text="IA Local (Ollama - LLaVA)", variable=self.ai_mode, value="local", font=("Arial", 10),
                       command=self.toggle_api_field).pack()
        tk.Radiobutton(root, text="IA via API (Google Gemini)", variable=self.ai_mode, value="api", font=("Arial", 10),
                       command=self.toggle_api_field).pack()

        tk.Label(root, text="Chave de API (Apenas para modo API):", font=("Arial", 12)).pack(pady=10)

        self.api_key_entry = tk.Entry(root, width=50, font=("Arial", 12), show="*")
        self.api_key_entry.pack(pady=5)
        self.api_key_entry.config(state=tk.DISABLED)

        self.start_btn = tk.Button(root, text="Iniciar Bot", command=self.toggle_bot, bg="green", fg="white",
                                   font=("Arial", 12, "bold"))
        self.start_btn.pack(pady=20)

        self.log_text = tk.Text(root, height=7, width=60, state=tk.DISABLED)
        self.log_text.pack(pady=5)

    def toggle_api_field(self):
        """Ativa ou desativa o campo de API Key baseado no Radiobutton selecionado"""
        if self.ai_mode.get() == "api":
            self.api_key_entry.config(state=tk.NORMAL)
        else:
            self.api_key_entry.config(state=tk.DISABLED)

    def log(self, message):
        """Adiciona mensagens ao log na interface gráfica"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def toggle_bot(self):
        if not self.is_running:
            url = self.url_entry.get()
            if not url or "youtube.com" not in url:
                messagebox.showerror("Erro", "Por favor, insira um link válido do YouTube.")
                return

            if self.ai_mode.get() == "api" and not self.api_key_entry.get().strip():
                messagebox.showerror("Erro", "Você selecionou o modo API. Insira sua Chave de API do Google Gemini.")
                return

            self.is_running = True
            self.start_btn.config(text="Parar Bot", bg="red")
            self.log("Iniciando navegador...")

            # Inicia o processo do Selenium em uma thread separada
            threading.Thread(target=self.watch_live, args=(url,), daemon=True).start()
        else:
            self.is_running = False
            self.start_btn.config(text="Iniciar Bot", bg="green")
            self.log("Parando o bot e fechando navegador...")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def watch_live(self, youtube_url):
        try:
            self.log("Preparando navegador indetectável...")

            # Substituímos o webdriver comum pelo undetected_chromedriver
            options = uc.ChromeOptions()
            options.add_argument("--disable-notifications")
            # options.add_argument("--mute-audio")

            # --- CONFIGURAÇÃO DE PERFIL ---
            profile_path = os.path.join(os.getcwd(), "PerfilBotChrome")
            options.add_argument(f"--user-data-dir={profile_path}")

            # --- NOVA BUSCA DE CAMINHO DO CHROME ---
            # O Windows as vezes esconde o caminho do Chrome da biblioteca.
            # Vamos forçar a busca nos locais padrões de instalação.
            chrome_path = None
            possiveis_caminhos = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe")
            ]

            for path in possiveis_caminhos:
                if os.path.exists(path):
                    chrome_path = path
                    break

            # Inicia o Chrome passando o caminho exato se o encontrou
            # ADICIONAMOS O version_main=150 PARA CORRIGIR O ERRO DE VERSÃO
            if chrome_path:
                self.driver = uc.Chrome(options=options, browser_executable_path=chrome_path, version_main=150)
            else:
                self.driver = uc.Chrome(options=options, version_main=150)

            self.driver.get(youtube_url)

            self.log("Live aberta! ATENÇÃO: Faça login no YouTube agora se quiser comentar.")
            self.log("Aguardando 15 segundos para carregar os anúncios/página...")
            time.sleep(15)

            # Loop principal de observação e comentário
            while self.is_running:
                self.log("Capturando visão do navegador...")

                # Tira print da tela do navegador em formato base64
                # É assim que pegamos a imagem sem precisar de OpenCV
                base64_image = self.driver.get_screenshot_as_base64()

                mode = self.ai_mode.get()
                if mode == "local":
                    comment = self.analyze_with_local_ai(base64_image)
                else:
                    comment = self.analyze_with_api(base64_image)

                if comment:
                    self.post_comment_to_youtube(comment)

                self.log("Aguardando 30 segundos para a próxima análise...")
                for _ in range(30):
                    if not self.is_running: break
                    time.sleep(1)

        except Exception as e:
            self.log(f"Erro no navegador: {str(e)}")
        finally:
            self.is_running = False
            self.start_btn.config(text="Iniciar Bot", bg="green")
            if self.driver:
                self.driver.quit()

    def analyze_with_local_ai(self, base64_image):
        """Envia o screenshot para o Ollama rodando localmente (modelo LLaVA)"""
        self.log("Analisando cena com IA Local (Ollama/LLaVA)...")
        try:
            # O LLaVA pode demorar um pouco dependendo da placa de vídeo/processador.
            # Adicionamos um timeout de 60 segundos para não travar o bot indefinidamente.
            response = requests.post('http://localhost:11434/api/generate', json={
                "model": "llava",
                "prompt": "Você é um espectador de uma live stream. Baseado nesta imagem da tela da live, escreva UMA frase curta, informal e natural (em português do Brasil) para mandar no chat ao vivo. Não use aspas.",
                "images": [base64_image],
                "stream": False
            }, timeout=60)

            if response.status_code == 200:
                return response.json().get('response', '').strip()
            else:
                self.log(f"Ollama retornou um erro: {response.status_code}")
                return None

        except requests.exceptions.ConnectionError:
            self.log("❌ ERRO: O Ollama não está rodando no seu computador!")
            self.log("Abra o terminal do seu Windows e digite: ollama run llava")
            return None
        except Exception as e:
            self.log(f"Erro na IA local: {str(e)}")
            return None

    def analyze_with_api(self, base64_image):
        """Envia o screenshot usando a NOVA biblioteca OFICIAL do Google Gemini"""
        api_key = self.api_key_entry.get().strip()
        self.log("Analisando cena com IA via API (Gemini)...")

        try:
            # Inicializa o cliente usando o novo padrão do pacote google.genai
            client = genai.Client(api_key=api_key)

            # Convertemos o base64 para imagem do Pillow para facilitar a leitura da IA
            image_data = base64.b64decode(base64_image)
            image = Image.open(io.BytesIO(image_data))

            prompt = "Você é um espectador em uma live stream. Com base no que está acontecendo nesta imagem da tela, crie UMA frase curta, em português do Brasil, informal e engajadora para enviar no chat ao vivo. Não use aspas."

            # ATUALIZADO: Colocamos os modelos PRO no topo da lista de prioridade!
            modelos = [
                'gemini-2.5-pro',  # O mais inteligente atual (se disponível na sua cota)
                'gemini-1.5-pro',  # O cérebro pesado e consolidado
                'gemini-2.5-flash',  # Alternativa rápida
                'gemini-2.0-flash',
                'gemini-1.5-flash-latest'
            ]

            response = None
            ultimo_erro = ""

            for modelo in modelos:
                try:
                    self.log(f"Testando permissão no modelo: {modelo}...")
                    response = client.models.generate_content(
                        model=modelo,
                        contents=[prompt, image]
                    )
                    self.log(f"✅ Conectado com sucesso ao {modelo}!")
                    break  # Se funcionou, sai do loop de tentativas
                except Exception as e:
                    ultimo_erro = str(e)
                    # Se for erro 404 (não encontrado), ele tenta o próximo da lista
                    if "404" in ultimo_erro or "not found" in ultimo_erro.lower():
                        continue
                    else:
                        raise e  # Se for erro de cota ou chave inválida, ele interrompe

            if response:
                return response.text.strip()
            else:
                self.log(f"Nenhum modelo compatível na sua chave. Erro: {ultimo_erro}")
                return None

        except Exception as e:
            self.log(f"Erro na API do Gemini: {str(e)}")
            return None

    def post_comment_to_youtube(self, comment):
        """Usa o Selenium para encontrar o chat e digitar a mensagem de verdade"""
        self.log(f"IA gerou: {comment}")
        self.log("Tentando postar no chat...")

        try:
            self.driver.switch_to.default_content()

            # Espera até o iframe do chat aparecer (max 15 segundos)
            wait = WebDriverWait(self.driver, 15)
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#chatframe")))
            self.driver.switch_to.frame(iframe)

            # Espera a caixa de texto estar presente no HTML do chat
            chat_box = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#input.yt-live-chat-text-input-field-renderer")))

            # Força o clique e o foco usando Javascript (ignora banners na frente)
            self.driver.execute_script("arguments[0].click();", chat_box)
            self.driver.execute_script("arguments[0].focus();", chat_box)
            time.sleep(1)  # Pausa humana pro YouTube registrar o foco

            # Envia o texto da mensagem
            chat_box.send_keys(comment)
            time.sleep(1)

            # Aperta ENTER na caixa de texto
            chat_box.send_keys(Keys.RETURN)

            # PLANO B: Se o ENTER não for suficiente, forçamos o clique no botão de enviar
            try:
                send_btn = self.driver.find_element(By.CSS_SELECTOR, "#send-button button")
                self.driver.execute_script("arguments[0].click();", send_btn)
            except:
                pass

            self.log("✅ Comentário enviado com sucesso!")

        except Exception as e:
            # Captura a primeira linha do erro real para sabermos o motivo exato se falhar
            erro_curto = str(e).split('\n')[0][:80]
            self.log(f"❌ Falha ao comentar. Erro técnico: {erro_curto}")

        finally:
            # Sempre retorna ao contexto principal da página para não quebrar a captura de tela
            try:
                self.driver.switch_to.default_content()
            except:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeAIBot(root)
    root.mainloop()