# main_game.py

import pygame
import os
import time
# É necessário importar heapq aqui, pois ele é usado pelo AStarKraken indiretamente
import heapq 

# Importa todas as constantes, classes e lógica
from config import *
from agentes import AStarKraken, AmbienteProbabilistico 

class GameController:
    """Gerencia o loop principal, a renderização e a interação entre Agentes."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
        pygame.display.set_caption("IA Probabilística vs Kraken")
        self.clock = pygame.time.Clock()
        
        # Carregamento de Fontes
        self.font = pygame.font.SysFont('Arial', 18)
        self.emoji_font = pygame.font.SysFont('Segoe UI Symbol', 40)
        if not self.emoji_font:
            self.emoji_font = pygame.font.SysFont(pygame.font.get_default_font(), 40) 

        # Instancia o ambiente e os agentes
        self.env = AmbienteProbabilistico(GRID_SIZE, GRID_SIZE)
        self.kraken_brain = AStarKraken()
        
        self.running = True
        self.turn = 0
        self.last_utility_log = ""
        self.kraken_chase_mode = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.env.game_over or self.env.score >= MAX_FISH_GOAL:
            return

        self.turn += 1
        
        # --- AÇÃO DA IA DE PESCA ---
        self.env.sentir_ambiente()
        new_pos = self.env.decidir_movimento()
        
        self.last_utility_log = self._capture_utility_log(new_pos)
        self.env.barco_pos = new_pos
        
        self._check_interaction(self.env.barco_pos)

        # --- AÇÃO DO KRAKEN (Movimento mais lento) ---
        if self.turn % KRAKEN_SPEED_DIVISOR == 0:
            self._update_kraken_logic()
        
        # Verifica colisão Barco vs Kraken
        if self.env.barco_pos == self.env.kraken_pos:
            self._handle_kraken_capture()

    def _capture_utility_log(self, chosen_pos):
        # Captura o log (reconstroi o cálculo para o dashboard)
        info = self.env.known_grid.get(chosen_pos, {})
        if info:
            recompensa = info.get("prob_peixe", 0) * PESO_RECOMPENSA
            risco = info.get("prob_perigo", 0) * PESO_RISCO
            tedio = self.env.visit_count.get(chosen_pos, 0) * PENALIDADE_TEDIO
            exploracao = BONUS_EXPLORAR if not info.get("visitado", True) else 0
            
            utilidade = recompensa - risco + exploracao - tedio
            
            return f"Uti: {utilidade:.1f} | P(Risco): {info.get('prob_perigo', 0.0):.2f}"
        return f"Turno {self.turn}: Fuga/Erro"


    def _update_kraken_logic(self):
        """Lógica de Perseguição do Kraken: Checa distância e executa A*."""
        kx, ky = self.env.kraken_pos
        bx, by = self.env.barco_pos
        distance = abs(kx - bx) + abs(ky - by)
        
        VISUAL_RANGE = 3
        BREAK_CHASE_RANGE = 5
        
        if distance <= VISUAL_RANGE:
            self.kraken_chase_mode = True
            self.env.kraken_target = self.env.barco_pos
        
        elif distance > BREAK_CHASE_RANGE:
            self.kraken_chase_mode = False
            self.env.kraken_target = None 
            self.env.kraken_path = []

        if self.kraken_chase_mode and self.env.kraken_target:
            self.env.kraken_path = self.kraken_brain.find_path(self.env, self.env.kraken_pos, self.env.kraken_target)
            
            if self.env.kraken_path:
                next_pos = self.env.kraken_path.pop(0)
                self.env.kraken_pos = next_pos
            else:
                self.kraken_chase_mode = False

    def _check_interaction(self, pos):
        """Verifica se o barco coletou peixe ou caiu em redemoinho."""
        x, y = pos
        content = self.env.real_grid.get(pos)
        
        if content == 'PEIXE':
            self.env.score += 1
            self.env.real_grid[pos] = 'VAZIO'
            self.env.known_grid[pos]["visual"] = 'PESCADO'
            
        elif content == 'REDEMOINHO':
            self.env.game_over = True
            self.env.known_grid[pos]["visual"] = 'AFOGADO'

    def _handle_kraken_capture(self):
        """Lida com a captura pelo Kraken."""
        print("KRAKEN CAPTURA O BARCO!")
        self.env.score = 0
        self.env.barco_pos = (0, 0)
        self.kraken_chase_mode = False
        self.env.kraken_path = []
        self.env.kraken_pos = (self.env.w - 1, self.env.h - 1)
        
    def draw(self):
        self.screen.fill(WATER)

        # --- Mapeamento de Ícones (Usando o que foi importado de config) ---
        
        # --- A. Desenho do Grid (O que a IA Sabe) ---
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pos = (x, y)
                cell_info = self.env.known_grid[pos]
                
                # 1. Fundo baseado no conhecimento
                if cell_info["visual"] == 'NEVOA':
                    color = BLACK
                elif cell_info["prob_perigo"] > 0.5:
                    color = DANGER_ZONE
                else:
                    color = SHALLOW
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, BLACK, rect, 1)

                # 2. Símbolos de Dica (Memória Visual)
                visual_key = cell_info["visual"]
                
                if visual_key in ICON_MAP and visual_key != 'VAZIO':
                    text_surface = self.emoji_font.render(ICON_MAP[visual_key], True, WHITE)
                else:
                    text_surface = None
                
                if text_surface:
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)


        # --- B. Desenho dos Agentes (No topo) ---
        
        # Desenha a Rota do Kraken (A*) - Debug
        for px, py in self.env.kraken_path:
             rect = pygame.Rect(px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE)
             pygame.draw.rect(self.screen, PATH_COLOR, rect, 3)

        # 1. Barco
        bx, by = self.env.barco_pos
        boat_icon_str = ICON_MAP['MORTE'] if self.env.game_over else ICON_MAP['BARCO']
        boat_icon = self.emoji_font.render(boat_icon_str, True, WHITE)
        boat_rect = boat_icon.get_rect(center=(bx * TILE_SIZE + TILE_SIZE // 2, by * TILE_SIZE + TILE_SIZE // 2))
        self.screen.blit(boat_icon, boat_rect)
        
        # 2. Kraken (Sempre desenhado no mapa REAL)
        kx, ky = self.env.kraken_pos
        kraken_icon = self.emoji_font.render(ICON_MAP['KRAKEN'], True, (255, 0, 0))
        kraken_rect = kraken_icon.get_rect(center=(kx * TILE_SIZE + TILE_SIZE // 2, ky * TILE_SIZE + TILE_SIZE // 2))
        self.screen.blit(kraken_icon, kraken_rect)

        # --- C. Desenho do Dashboard ---
        self._draw_dashboard()

        pygame.display.flip()

    def _draw_dashboard(self):
        # Fundo do dashboard
        dashboard_rect = pygame.Rect(WIDTH, 0, DASHBOARD_WIDTH, TOTAL_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, dashboard_rect)

        y_offset = 20
        
        title_text = self.font.render("DASHBOARD IA", True, WHITE)
        self.screen.blit(title_text, (WIDTH + 10, y_offset))
        y_offset += 40

        metrics = [
            f"Turno: {self.turn}",
            f"Peixes Coletados: {self.env.score} / {MAX_FISH_GOAL}",
            f"Carga: 0 / 1 (Simples)",
            f"Estado da IA: {'Fuga!' if self.env._kraken_is_near() else 'Explorando'}",
        ]
        
        for text in metrics:
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (WIDTH + 10, y_offset))
            y_offset += 25
            
        y_offset += 20
        
        # Log de Utilidade (Raciocínio)
        text_surface = self.font.render("Última Decisão:", True, WHITE)
        self.screen.blit(text_surface, (WIDTH + 10, y_offset))
        y_offset += 25
        
        log_text = self.font.render(self.last_utility_log, True, (255, 255, 102))
        self.screen.blit(log_text, (WIDTH + 10, y_offset))
        y_offset += 40
        
        # Status do Kraken
        kraken_status = "Em Perseguição!" if self.kraken_chase_mode else "Em Patrulha."
        status_color = (255, 100, 100) if self.kraken_chase_mode else (100, 255, 100)
        
        kraken_text = self.font.render(f"Kraken: {kraken_status}", True, status_color)
        self.screen.blit(kraken_text, (WIDTH + 10, y_offset))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(5)

        pygame.quit()

# --- PONTO DE EXECUÇÃO ---

if __name__ == "__main__":
    game = GameController()
    game.run()