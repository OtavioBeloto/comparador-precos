import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scr.scraper import TerabyteScraper
import webbrowser

class AppComparador:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Preços")
        self.root.geometry("400x200")

        # filtros
        self.frame_filtros = tk.Frame(root, pady=5)
        self.frame_filtros.pack(fill=tk.X, padx=10)

        tk.Label(self.frame_filtros, text="ordenar por:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)

        self.btn_menor_preco = tk.Button(self.frame_filtros, text="Menor Preço", command=lambda: self.ordenar_tabela("preco", reverso=False))
        self.btn_menor_preco.pack(side=tk.LEFT, padx=2)

        self.btn_maior_preco = tk.Button(self.frame_filtros, text="Maior Preço", command=lambda: self.ordenar_tabela("preco", reverso=True))
        self.btn_maior_preco.pack(side=tk.LEFT, padx=2)

        self.btn_loja_abc = tk.Button(self.frame_filtros, text="Loja A-Z", command=lambda: self.ordenar_tabela("site", reverso=False))
        self.btn_loja_abc.pack(side=tk.LEFT, padx=2)

        # Busca
        self.frame_busca = tk.Frame(root, pady=10)
        self.frame_busca.pack(fill=tk.X, padx=20) #tk.X para preencher horizontalmente

        self.label = tk.Label(self.frame_busca, width=40, text="Produto:", font=("Arial", 11))
        self.label.pack(side=tk.LEFT, pady=5)

        self.entry_termo = tk.Entry(self.frame_busca, width=40, font=("Arial", 11))
        self.entry_termo.pack(side=tk.LEFT, padx=5)

        #deixa apertar enter para buscar
        self.entry_termo.bind("<Return>", lambda event: self.buscar_preco())

        self.btn_buscar = tk.Button(self.frame_busca, text="Buscar Preços", command=self.buscar_preco, font=("Arial", 11))
        self.btn_buscar.pack(side=tk.LEFT, padx=5)

        #Label do status
        self.label_status = tk.Label(root, text="", font=("Arial", 10, "italic"))
        self.label_status.pack(pady=12)

        #colunas da tabela
        colunas = ("nome", "preco", "site")
        self.tabela = ttk.Treeview(root, columns=colunas, show="headings")
        self.tabela.heading("nome", text="Nome do Produto")
        self.tabela.heading("preco", text="Preço (R$)")
        self.tabela.heading("site", text="Site")
        self.tabela.tag_configure("link", font=("Arial", 10, "underline"))
        self.tabela.bind("<Button-1>", self.clicar)
        self.tabela.bind("<Motion>", self.ao_passar_mouse)

        self.tabela.column("nome", width=500, anchor=tk.W)
        self.tabela.column("preco", width=120, anchor=tk.CENTER)
        self.tabela.column("site", width=120, anchor=tk.CENTER)

        #scrollbar da tabela
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)

        self.tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    
        
    def buscar_preco(self):
        termo = self.entry_termo.get().strip()
        if not termo:
            messagebox.showwarning("Aviso", "Por favor, insira um termo de busca.")
            return

        # Limpa a tabela antes de buscar
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        self.btn_buscar.config(state=tk.DISABLED)  # Desabilita o botão durante a busca
        self.label_status.config(text="Buscando preços...")  # Atualiza o status

        # Roda em thread separada para o Tkinter não travar
        threading.Thread(target=self.executar_scraping, args=(termo,), daemon=True).start()


    def executar_scraping(self, termo):
        resultados_totais = []

        try:
            self.label_status.config(text="Buscando na Terabyte...")
            teranbyte = TerabyteScraper()
            produtos_terabyte = teranbyte.buscar(termo)
            resultados_totais.extend(produtos_terabyte)

            self.root.after(0, lambda: self.atualizar_tabela(resultados_totais))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro durante a busca: {e}"))
            self.root.after(0, lambda: self.label_status.config(text="Erro na busca."))
        finally:
            self.root.after(0, lambda: self.btn_buscar.config(state=tk.NORMAL))  # Reabilita o botão após a busca

    def atualizar_tabela(self, produtos):
        if not produtos:
            self.label_status.config(text="Nenhum produto encontrado.")
            return
        for pr in produtos:
            preco_formatado = f"R$ {pr['preco']:.2f}".replace(".", ",")
            self.tabela.insert("", tk.END, values=(pr["nome"], preco_formatado, pr["site"]), tags=(pr["link"],))
        self.label_status.config(text=f"Busca concluída. {len(produtos)} produtos encontrados.")



    def clicar(self, event):
            item_id = self.tabela.identify_row(event.y)
            coluna = self.tabela.identify_column(event.x)
    
            if coluna == "#1" and item_id:
                tags = self.tabela.item(item_id, "tags")
                if tags:
                    link = tags[0]  # O link está na primeira tag do item
                    webbrowser.open(link)  #abre o link no navegador
                
    
    # maozinha ao passar o mouse
    def ao_passar_mouse(self, event):
        coluna = self.tabela.identify_column(event.x)
        regiao = self.tabela.identify("region", event.x, event.y)

        if regiao == "cell" and coluna == "#1":
            self.tabela.config(cursor="hand2")
        else:
            self.tabela.config(cursor="")

    def ordenar_tabela(self, criterio, reverso):
        dados = []
        for child in self.tabela.get_children():
            valores = self.tabela.item(child, "values")
            tags = self.tabela.item(child, "tags")
            dados.append((valores, tags))

        if not dados:
            return

        # Define qual coluna usar para ordenar
        if criterio == "preco":
            # Converte "R$ 1.500,50" para float (1500.50)
            def converter_preco(item):
                preco_str = item[0][1].replace("R$", "").replace(".", "").replace(",", ".").strip()
                try:
                    return float(preco_str)
                except ValueError:
                    return 0.0

            dados.sort(key=converter_preco, reverse=reverso)

        elif criterio == "site":
            # Ordena pelo nome do site (Coluna 2)
            dados.sort(key=lambda item: item[0][2].lower(), reverse=reverso)

        # Limpa a tabela atual
        for child in self.tabela.get_children():
            self.tabela.delete(child)

        # Reinsere os dados ordenados na tabela (mantendo as tags com os links!)
        for valores, tags in dados:
            self.tabela.insert("", tk.END, values=valores, tags=tags)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = AppComparador(root)
    root.mainloop()
