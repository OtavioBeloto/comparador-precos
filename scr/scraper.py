import os
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
import undetected_chromedriver as uc

class BaseScraper(ABC):
    
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

    def _formatar_preco(self, preco_str):
                preco_limpo = preco_str.replace("\xa0", " ").replace("R$", "").replace(".", "").replace(",", ".").strip()
                return float(preco_limpo)
    
    @abstractmethod
    def buscar(self, termo: str):
        pass

    

class TerabyteScraper(BaseScraper):
    def buscar(self, termo: str):
        chrome_options = Options()
        chrome_options.binary_location = self.brave_path
        chrome_options.add_argument("--headless")

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


class PichauScraper(BaseScraper):
    SELETOR = "a[data-cy='list-product']"
    def buscar(self, termo: str):
        options = uc.ChromeOptions()
        options.binary_location = self.brave_path
        options.add_argument("--headless=new")
        
        #chrome_options.add_argument("--headless") # Descomente depois que estiver tudo funcionando

        driver = uc.Chrome(options=options, browser_executable_path=self.brave_path)

        resultados = []
        try:
            termo_formatado = termo.replace(" ", "+")
            url = f"https://www.pichau.com.br/search?q={termo_formatado}"

            driver.get(url)
            wait = WebDriverWait(driver, 10)

           # Pega os cards REAIS (o elemento que tem o data-tss-price)
            cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[data-cy="list-product"]'))
            )

            print(f"\n[DEBUG] Encontrou {len(cards)} cards na tela!")

            for card in cards[:10]:
                try:
                    link = urljoin("https://www.pichau.com.br", card.get_attribute("href"))

                    try:
                        nome = card.find_element(By.CSS_SELECTOR, '[class*="product_info_title"]').text
                    except Exception:
                        nome = card.find_element(By.TAG_NAME, "h2").text

                    # Preço: atributo do próprio card
                    preco_str = card.find_element(By.CSS_SELECTOR, '[class*="price_vista"]').text
                    preco = self._formatar_preco(preco_str)

                    if not any(d["link"] == link for d in resultados):
                        resultados.append({
                            "nome": nome,
                            "preco": preco,
                            "site": "Pichau",
                            "link": link,
                        })
                except Exception as ex:
                    print(f"[DEBUG] Erro ao processar card: {ex}")
                    continue

            return resultados

        except Exception as e:
            print(f"Erro na busca da Pichau: {e}")
            return []
        finally:
            driver.quit()

class KabumScraper(BaseScraper):
    SELETOR = 'a[href^="/produto/"]'

    def buscar(self, termo: str):
        chrome_options = Options()
        chrome_options.binary_location = self.brave_path

        chrome_options.add_argument("--disable-blink-features=AutomationControlled") #desativa a flag de automatizaçao
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])#esconde o cabeçalho do robo
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        #pichau reconhece que é automatizado
        chrome_options.add_argument("--headless") # Descomente depois que estiver tudo funcionando


        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # COMANDO MÁGICO: Injeta o script ANTES de qualquer página carregar!
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        resultados = []
        try:
            termo_formatado = termo.replace(" ", "-")
            url = f"https://www.kabum.com.br/busca/{termo_formatado}"

            driver.get(url)
            wait = WebDriverWait(driver, 10)

           # Pega os cards REAIS (o elemento que tem o data-tss-price)
            cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.SELETOR))
            )

            print(f"\n[DEBUG] Encontrou {len(cards)} cards na tela!")

            for card in cards[:10]:
                try:
                    link = urljoin("https://www.kabum.com.br", card.get_attribute("href"))

                    nome = card.find_element(By.CSS_SELECTOR, 'span[class*="line-clamp-2"]').text

                    # Preço: atributo do próprio card
                    valor_str = card.find_element(By.XPATH, './/span[normalize-space()="R$"]/following-sibling::span[1]').get_attribute("textContent")
                    preco = self._formatar_preco(valor_str)

                    if not any(d["link"] == link for d in resultados):
                        resultados.append({
                            "nome": nome,
                            "preco": preco,
                            "site": "Kabum",
                            "link": link,
                        })
                except Exception as ex:
                    print(f"[DEBUG] Erro ao processar card: {ex}")
                    continue

            return resultados

        except Exception as e:
            print(f"Erro na busca da Pichau: {e}")
            return []
        finally:
            driver.quit()