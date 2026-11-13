from abc import ABC, abstractmethod
# abc cria um molde que outras classes podem seguir

class BaseScrapper(ABC):
    @abstractmethod
    def Buscar_produto(self, url: str):
        pass

class TerabyteScrapper(BaseScrapper):
    def Buscar_produto(self, url: str):
        return {"nome": "Exemplo Terabyte", "preco": 100.00}