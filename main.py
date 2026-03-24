"""
HabitRPG - Aplicación de Gamificación de Hábitos
"""

import sys
import os

# ✅ IMPORTANTE: Agregar ruta del proyecto al path de Python
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from tkinter import ttk, messagebox

# ✅ Imports absolutos
from views.windows import HabitApp
from views.theme import ThemeManager

def main():
    root = tk.Tk()
    root.title("HabitRPG - Gamifica tus Hábitos")
    root.geometry("900x700")
    root.minsize(800, 600)
    
    # Intentar cargar favicon
    try:
        root.iconbitmap("assets/icon.ico")
    except Exception:
        try:
            from PIL import ImageTk, Image
            img = Image.open("assets/icon.png")
            photo = ImageTk.PhotoImage(img)
            root.iconphoto(True, photo)
        except Exception:
            print("⚠️  No se encontró el favicon")
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Iniciar app
    app = HabitApp(root)
    
    # Manejo de cierre
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Estás seguro de que deseas salir?"):
            app.db.close()
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()