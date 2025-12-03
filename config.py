# config.py

import pygame

# --- 1. CONFIGURAÇÕES GERAIS E CONSTANTES ---

# Cores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WATER = (0, 100, 150)
SHALLOW = (0, 150, 200)
DANGER_ZONE = (150, 0, 0)
PATH_COLOR = (255, 255, 102)

# Dimensões da Tela e Grid
GRID_SIZE = 10
TILE_SIZE = 60
WIDTH = TILE_SIZE * GRID_SIZE
HEIGHT = TILE_SIZE * GRID_SIZE
DASHBOARD_WIDTH = 300
TOTAL_WIDTH = WIDTH + DASHBOARD_WIDTH
TOTAL_HEIGHT = HEIGHT

# Constantes do Jogo
MAX_FISH_GOAL = 5
KRAKEN_SPEED_DIVISOR = 3 # Kraken se move 1 vez a cada 3 turnos do barco

# Configurações de Probabilidade e Utilidade
PROB_INICIAL = 0.1
IMPACTO_DICA_POS = 0.8
IMPACTO_DICA_NEG = 0.9

# Pesos da Decisão (A Personalidade da IA de Pesca)
PESO_RECOMPENSA = 100
PESO_RISCO = 500
BONUS_EXPLORAR = 50
PENALIDADE_TEDIO = 70

# Mapeamento de strings para os ícones (Usado no GameController)
ICON_MAP = {
            'TREMOR': "🌊", 'VENTO': "💨", 'AMBOS': "⛈️", 'PESCADO': "🎣", 
            'AFOGADO': "☠️", 'BARCO': "🚢", 'KRAKEN': "🐙", 'MORTE': "💀"
}