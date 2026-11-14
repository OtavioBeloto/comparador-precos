import os
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BaseScraper(ABC):
    @abstractmethod
    def buscar(self, termo: str):
        """Deve retornar uma lista de dicionários com os produtos encontrados:
           [{'nome': '...', 'preco': 1500.0, 'site': '...', 'link': '...'}]
        """
        pass

class TerabyteScraper(BaseScraper):
    def __init__(self):
        #config brave
        caminho_padrao_64 = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        caminho_padrao_user = os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")

        if os.path.exists(caminho_padrao_64):
            self.brave_path = caminho_padrao_64
        elif os.path.exists(caminho_padrao_user):
            self.brave_path = caminho_padrao_user
        else:
            raise FileNotFoundError("Brave Browser não encontrado!")

    def buscar(self, termo: str):
        chrome_options = Options()
        chrome_options.binary_location = self.brave_path
        # chrome_options.add_argument("--headless") # Descomente depois que estiver tudo funcionando

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        resultados = []
        try:
            termo_formatado = termo.replace(" ", "+")
            url = f"https://www.terabyteshop.com.br/busca?str={termo_formatado}"

            driver.get(url)
            wait = WebDriverWait(driver, 10)

           # Pega os cards REAIS (o elemento que tem o data-tss-price)
            cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-item[data-tss-price]"))
            )

            print(f"\n[DEBUG] Encontrou {len(cards)} cards na tela!")

            for card in cards[:10]:
                try:
                    # Link e nome: o <a> com class product-item__name tem o title completo
                    link_elemento = card.find_element(By.CSS_SELECTOR, "a.product-item__name")
                    link = link_elemento.get_attribute("href")
                    nome = link_elemento.get_attribute("title")

                    # Preço: atributo do próprio card
                    preco_str = card.get_attribute("data-tss-price")
                    preco = float(preco_str) if preco_str else 0.0

                    if not any(d["link"] == link for d in resultados):
                        resultados.append({
                            "nome": nome,
                            "preco": preco,
                            "site": "Terabyte",
                            "link": link,
                        })
                except Exception as ex:
                    print(f"[DEBUG] Erro ao processar card: {ex}")
                    continue

            return resultados

        except Exception as e:
            print(f"Erro na busca da Terabyte: {e}")
            return []
        finally:
            driver.quit()

    def _formatar_preco(self, preco_str):
        preco_limpo = preco_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(preco_limpo)

    def abre_link(self, link):
        chrome_options = Options()
        chrome_options.binary_location = self.brave_path
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(link)