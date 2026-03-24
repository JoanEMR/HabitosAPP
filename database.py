#Este módulo se encarga de la conexión a SQLite y las operaciones CRUD. Usamos POO para encapsular la lógica.

#Lógica de datos y Base de Datos

#Objetivo: Gestionar la conexión a SQLite y las operaciones CRUD.

"""
Módulo de Base de Datos - Modelo
Gestiona todas las operaciones con SQLite
"""

import sqlite3
from datetime import datetime

class Database:
    """Clase para manejar la conexión y operaciones con SQLite"""
    
    def __init__(self, db_name="habitos.db"):
        """
        Inicializa la conexión a la base de datos
        Parámetro: db_name - Nombre del archivo .db
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establece conexión con SQLite"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        
        # Tabla de Usuarios
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                avatar_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de Hábitos
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                icon_path TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de Registro Diario (para rachas)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                xp_earned INTEGER DEFAULT 0,
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def execute_query(self, query, params=()):
        """
        Ejecuta una consulta SQL (INSERT, UPDATE, DELETE)
        Retorna: cursor o None si hay error
        """
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            print(f"❌ Error en BD: {e}")
            return None
    
    def fetch_all(self, query, params=()):
        """
        Ejecuta SELECT y retorna todos los resultados
        Retorna: lista de tuplas
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error en BD: {e}")
            return []
    
    def fetch_one(self, query, params=()):
        """
        Ejecuta SELECT y retorna un solo resultado
        Retorna: tupla o None
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error en BD: {e}")
            return None
    
    def get_last_id(self):
        """Retorna el último ID insertado"""
        return self.cursor.lastrowid
    
    def close(self):
        """Cierra la conexión a la BD"""
        if self.conn:
            self.conn.close()