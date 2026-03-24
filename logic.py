
from datetime import datetime

#Objetivo: Calcular XP, niveles y validar datos antes de guardar.

"""
Módulo de Lógica de Negocio - Controlador
Calcula XP, niveles, rachas
"""

class GameLogic:
    """Clase con la lógica de gamificación"""
    
    XP_PER_HABIT = 10
    XP_PER_LEVEL = 100
    
    @staticmethod
    def calculate_xp(current_xp, habits_completed):
        """
        Calcula XP total después de completar hábitos
        Parámetros: current_xp, habits_completed
        Retorna: nuevo total de XP
        """
        gained = habits_completed * GameLogic.XP_PER_HABIT
        return current_xp + gained
    
    @staticmethod
    def calculate_level(xp):
        """
        Calcula el nivel basado en XP acumulada
        Fórmula: Nivel = (XP / 100) + 1
        Retorna: nivel actual
        """
        return (xp // GameLogic.XP_PER_LEVEL) + 1
    
    @staticmethod
    def calculate_progress_to_next_level(xp):
        """
        Calcula porcentaje de progreso al siguiente nivel
        Retorna: porcentaje (0-100)
        """
        level = GameLogic.calculate_level(xp)
        xp_for_current_level = (level - 1) * GameLogic.XP_PER_LEVEL
        xp_in_current_level = xp - xp_for_current_level
        percentage = (xp_in_current_level / GameLogic.XP_PER_LEVEL) * 100
        return min(percentage, 100)
    
    @staticmethod
    def check_streak(dates_list):
        """
        Calcula racha de días consecutivos
        Parámetro: lista de fechas en formato 'YYYY-MM-DD'
        Retorna: número de días de racha
        """
        if not dates_list or len(dates_list) == 0:
            return 0
        
        # Convertir strings a objetos datetime y ordenar
        try:
            sorted_dates = sorted([
                datetime.strptime(d, '%Y-%m-%d').date() 
                for d in dates_list
            ])
        except ValueError:
            return 0
        
        streak = 1
        today = datetime.now().date()
        
        # Verificar si hay actividad hoy o ayer
        if sorted_dates[-1] < today - timedelta(days=1):
            return 0  # Racha rota
        
        # Contar días consecutivos
        for i in range(len(sorted_dates) - 1, 0, -1):
            diff = (sorted_dates[i] - sorted_dates[i-1]).days
            if diff == 1:
                streak += 1
            elif diff > 1:
                break
        
        return streak
    
    @staticmethod
    def get_habit_completion_rate(completed, total):
        """
        Calcula porcentaje de completitud de hábitos
        Retorna: porcentaje (0-100)
        """
        if total == 0:
            return 0
        return (completed / total) * 100