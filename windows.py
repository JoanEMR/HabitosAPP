"""
Ventana Principal - Vista
Interfaz principal de la aplicación
"""

import sys
import os

# IMPORTANTE: Agregar ruta raíz al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import ImageTk, Image
from datetime import datetime, date

# Imports absolutos con ruta completa
from models.database import Database
from controllers.logic import GameLogic
from controllers.validators import Validator
from views.forms import RegistrationForm, HabitForm
from views.theme import ThemeManager
from utils.exporter import DataExporter
from utils.images import ImageHandler

class HabitApp:
    """Clase principal de la aplicación"""
    
    def __init__(self, root):
        """Inicializa la aplicación"""
        self.root = root
        self.db = Database()
        self.theme_manager = ThemeManager(root)
        self.current_user_id = 1
        
        self.setup_ui()
        self.load_user_stats()
        self.refresh_habits_list()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # === BARRA SUPERIOR ===
        self.top_frame = ttk.Frame(self.root, padding=10)
        self.top_frame.pack(fill=tk.X)
        
        # Stats del usuario
        self.stats_frame = ttk.Frame(self.top_frame)
        self.stats_frame.pack(side=tk.LEFT)
        
        self.lbl_level = ttk.Label(self.stats_frame, text="⚡ Nivel: 1", 
                                    font=("Arial", 14, "bold"))
        self.lbl_level.pack(side=tk.LEFT, padx=10)
        
        self.lbl_xp = ttk.Label(self.stats_frame, text="📊 XP: 0/100")
        self.lbl_xp.pack(side=tk.LEFT, padx=10)
        
        self.lbl_streak = ttk.Label(self.stats_frame, text="🔥 Racha: 0 días")
        self.lbl_streak.pack(side=tk.LEFT, padx=10)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(self.top_frame, length=200, mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=20)
        
        # Botón de tema
        self.btn_theme = ttk.Button(self.top_frame, text="🌓 Tema", 
                                    command=self.toggle_theme)
        self.btn_theme.pack(side=tk.RIGHT)
        
        # === ÁREA PRINCIPAL ===
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filtros
        filter_frame = ttk.Frame(self.main_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Filtrar por fecha:").pack(side=tk.LEFT)
        self.filter_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.filter_date.pack(side=tk.LEFT, padx=10)
        self.filter_date.set_date(date.today())
        
        ttk.Button(filter_frame, text="Aplicar Filtro", 
                    command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        # Lista de hábitos
        self.habits_container = ttk.Frame(self.main_frame)
        self.habits_container.pack(fill=tk.BOTH, expand=True)
        
        self.habits_list = []
        
        # === BARRA INFERIOR ===
        self.bottom_frame = ttk.Frame(self.root, padding=10)
        self.bottom_frame.pack(fill=tk.X)
        
        ttk.Button(self.bottom_frame, text="➕ Nuevo Hábito", 
                    command=self.open_habit_form).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.bottom_frame, text="👤 Registrar Usuario", 
                    command=self.open_registration).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.bottom_frame, text="📄 Exportar Excel", 
                    command=self.export_excel).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(self.bottom_frame, text="📕 Exportar PDF", 
                    command=self.export_pdf).pack(side=tk.RIGHT, padx=5)
    
    def load_user_stats(self):
        """Carga estadísticas del usuario"""
        user = self.db.fetch_one(
            "SELECT level, xp FROM users WHERE id=?", 
            (self.current_user_id,)
        )
        
        if user:
            level = user['level']
            xp = user['xp']
            
            self.lbl_level.config(text=f"⚡ Nivel: {level}")
            self.lbl_xp.config(text=f"📊 XP: {xp}/{GameLogic.XP_PER_LEVEL}")
            
            progress = GameLogic.calculate_progress_to_next_level(xp)
            self.progress['value'] = progress
            
            logs = self.db.fetch_all(
                """SELECT DISTINCT date FROM daily_logs 
                    WHERE habit_id IN (SELECT id FROM habits WHERE user_id=?) 
                    AND completed=1""",
                (self.current_user_id,)
            )
            dates = [log['date'] for log in logs]
            streak = GameLogic.check_streak(dates)
            self.lbl_streak.config(text=f"🔥 Racha: {streak} días")
    
    def refresh_habits_list(self):
        """Refresca la lista de hábitos"""
        for widget in self.habits_container.winfo_children():
            widget.destroy()
        self.habits_list.clear()
        
        habits = self.db.fetch_all(
            "SELECT * FROM habits WHERE user_id=?", 
            (self.current_user_id,)
        )
        
        if not habits:
            ttk.Label(self.habits_container, 
                        text="No hay hábitos registrados. ¡Crea uno nuevo!",
                        font=("Arial", 12)).pack(pady=20)
            return
        
        for habit in habits:
            self.create_habit_card(dict(habit))
    
    def create_habit_card(self, habit):
        """Crea una tarjeta visual para cada hábito"""
        card = ttk.Frame(self.habits_container, borderwidth=2, relief="groove")
        card.pack(fill=tk.X, pady=5, padx=10)
        
        if habit.get('icon_path'):
            try:
                img = Image.open(habit['icon_path']).resize((40, 40))
                photo = ImageTk.PhotoImage(img)
                lbl_img = ttk.Label(card, image=photo)
                lbl_img.image = photo
                lbl_img.pack(side=tk.LEFT, padx=10)
            except Exception as e:
                print(f"Error cargando imagen: {e}")
        
        info_frame = ttk.Frame(card)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        ttk.Label(info_frame, text=habit['name'], 
                    font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(info_frame, text=habit.get('category', ''), 
                    font=("Arial", 9)).pack(anchor=tk.W)
        
        today = date.today().strftime('%Y-%m-%d')
        
        existing = self.db.fetch_one(
            "SELECT * FROM daily_logs WHERE habit_id=? AND date=?",
            (habit['id'], today)
        )
        
        var = tk.BooleanVar(value=existing is not None)
        chk = ttk.Checkbutton(card, variable=var, 
                    command=lambda: self.toggle_habit(habit['id'], var, today))
        chk.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(card, text="✏️", width=3,
                    command=lambda: self.open_habit_form(habit)).pack(side=tk.RIGHT)
        
        ttk.Button(card, text="🗑️", width=3,
                    command=lambda: self.delete_habit(habit['id'])).pack(side=tk.RIGHT)
        
        self.habits_list.append(card)
    
    def toggle_habit(self, habit_id, var, today):
        """Marca/desmarca hábito como completado"""
        if var.get():
            self.db.execute_query(
                "INSERT INTO daily_logs (habit_id, date, completed, xp_earned) VALUES (?, ?, 1, 10)",
                (habit_id, today)
            )
            messagebox.showinfo("¡Excelente!", "✅ Hábito completado +10 XP")
        else:
            if messagebox.askyesno("Confirmar", "¿Deshacer completado?"):
                self.db.execute_query(
                    "DELETE FROM daily_logs WHERE habit_id=? AND date=?",
                    (habit_id, today)
                )
        
        self.load_user_stats()
    
    def delete_habit(self, habit_id):
        """Elimina un hábito con confirmación"""
        if messagebox.askyesno("⚠️  Confirmar", 
            "¿Estás seguro de eliminar este hábito? Esta acción no se puede deshacer."):
            self.db.execute_query("DELETE FROM habits WHERE id=?", (habit_id,))
            self.refresh_habits_list()
            self.load_user_stats()
    
    def open_habit_form(self, habit_data=None):
        """Abre formulario de hábitos"""
        HabitForm(self.root, self.db, self.current_user_id, 
                    habit_data, on_submit=self.refresh_habits_list)
    
    def open_registration(self):
        """Abre formulario de registro"""
        RegistrationForm(self.root, self.db, on_submit=self.load_user_stats)
    
    def apply_filter(self):
        """Aplica filtro por fecha"""
        selected_date = self.filter_date.get_date().strftime('%Y-%m-%d')
        messagebox.showinfo("Filtro", f"Filtrando por: {selected_date}")
    
    def toggle_theme(self):
        """Cambia el tema visual"""
        self.theme_manager.toggle_theme()
    
    def export_excel(self):
        """Exporta datos a Excel"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        
        if filename:
            data = self.db.fetch_all(
                """SELECT h.name, h.category, d.date, d.completed 
                    FROM habits h 
                    LEFT JOIN daily_logs d ON h.id = d.habit_id 
                    WHERE h.user_id=?""",
                (self.current_user_id,)
            )
            
            headers = ["Hábito", "Categoría", "Fecha", "Completado"]
            DataExporter.to_excel(data, filename, headers)
            messagebox.showinfo("Éxito", "Datos exportados a Excel")
    
    def export_pdf(self):
        """Exporta datos a PDF"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        
        if filename:
            data = self.db.fetch_all(
                """SELECT h.name, h.category, COUNT(d.id) as completados
                    FROM habits h 
                    LEFT JOIN daily_logs d ON h.id = d.habit_id 
                    WHERE h.user_id=? GROUP BY h.id""",
                (self.current_user_id,)
            )
            
            DataExporter.to_pdf(data, filename, "Reporte de Hábitos")
            messagebox.showinfo("Éxito", "Reporte exportado a PDF")
