from scr.scrapper import TerabyteScraper

def testar():
    print("Inicializando o scraper da Terabyte...")
    scraper = TerabyteScraper()

    # Escolha um produto real que você sabe que tem na Terabyte
    termo = "RTX 4060"

    print(f"Buscando por: '{termo}'...")
    produtos = scraper.buscar(termo)

    print(f"\n--- RESULTADOS ENCONTRADOS ({len(produtos)}) ---")
    if not produtos:
        print("N deu boa, arrumar seletores.")

    for i, p in enumerate(produtos, 1):
        print(f"\n[{i}] Produto: {p['nome']}")
        print(f"    Preço: R$ {p['preco']:.2f}")
        print(f"    Site: {p['site']}")
        print(f"    Link: {p['link']}")

if __name__ == "__main__":
    testar()