import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scr.scraper import TerabyteScraper

class AppComparador:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Preços")
        self.root.geometry("400x200")

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
            self.tabela.insert("", tk.END, values=(pr["nome"], preco_formatado, pr["site"]))
        self.label_status.config(text=f"Busca concluída. {len(produtos)} produtos encontrados.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppComparador(root)
    root.mainloop()
