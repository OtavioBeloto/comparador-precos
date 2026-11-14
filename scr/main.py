from scr.scraper import TerabyteScraper
from scr.gui import AppComparador
import tkinter as tk


def main():
    root = tk.Tk()
    app = AppComparador(root)
    root.mainloop()

if __name__ == "__main__":
    main()
