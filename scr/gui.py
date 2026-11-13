import tkinter as tk
from tkinter import messagebox

class AppComparador:
    def __init__(self, root):
        self.root = root
        self.root.title("Comparador de Preços")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="Cole a URL do produto:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(pady=5)

        self.button = tk.Button(root, text="Buscar Preço", command=self.buscar_preco)
        self.button.pack(pady=10)

    def buscar_preco(self):
        url = self.entry.get()
        if url:
            messagebox.showinfo("Resultado", f"URL inserida: {url}")
        else:
            messagebox.showwarning("Aviso", "Por favor, insira uma URL primeiro.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppComparador(root)
    root.mainloop()
