# agentes.py

import random
import heapq # Necessário para o AStarKraken
import math

# Importa todas as constantes do arquivo config.py
from config import * # --- AGENTE PREDADOR (KRAKEN) - Busca Determinística A* ---

class AStarKraken:
    """Implementa A* para o Kraken (Busca Determinística no mapa REAL)."""
    
    @staticmethod
    def heuristic(a, b):
        """Distância Manhattan (heurística admissível)."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, env, start, goal):
        """Encontra o caminho mais curto, evitando redemoinhos."""
        
        # O A* precisa de uma verificação inicial de validade do objetivo/início.
        if not env.is_valid_kraken_move(goal) or not env.is_valid_kraken_move(start):
            return []

        priority_queue = []
        heapq.heappush(priority_queue, (0, start))
        
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while priority_queue:
            _, current = heapq.heappop(priority_queue)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # O Kraken evita redemoinhos.
                if env.is_valid_kraken_move(neighbor):
                    new_cost = cost_so_far[current] + 1
                    
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        priority = new_cost + self.heuristic(neighbor, goal)
                        heapq.heappush(priority_queue, (priority, neighbor))
                        came_from[neighbor] = current
        
        return []

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            if current:
                path.append(current)
            else:
                break
        path.reverse()
        return path[1:]

# --- AMBIENTE E AGENTE PROBABILÍSTICO (IA DE PESCA) ---

class AmbienteProbabilistico:
    """
    Controla o mapa, a IA de Pesca (probabilística) e o Kraken (predador).
    """
    def __init__(self, w, h):
        self.w = w
        self.h = h
        # MAPAS (Mundo da IA)
        self.real_grid = {}     
        self.known_grid = {}    
        self.visit_count = {}   
        
        # ESTADO
        self.barco_pos = (0, 0)
        self.score = 0
        self.game_over = False
        self.kraken_pos = (self.w - 1, self.h - 1)
        self.kraken_target = None
        self.kraken_path = []
        
        self._gerar_mapa_oculto()
        self._inicializar_memoria_ia()

    # Métodos do Ambiente (Gerar e Validar)
    def _gerar_mapa_oculto(self):
        # Gera o mapa real com peixes e perigos aleatórios
        for x in range(self.w):
            for y in range(self.h):
                self.real_grid[(x, y)] = 'MAR'
        
        for _ in range(int(self.w * self.h * 0.08)): # 8% de chance Redemoinho
            rx, ry = random.randint(1, self.w-1), random.randint(1, self.h-1)
            if (rx, ry) != (0, 0) and self.real_grid[(rx, ry)] == 'MAR':
                self.real_grid[(rx, ry)] = 'REDEMOINHO'

        count = 0
        while count < MAX_FISH_GOAL: # Posiciona Peixes
            px, py = random.randint(0, self.w-1), random.randint(0, self.h-1)
            if self.real_grid[(px, py)] == 'MAR' and (px, py) != (0, 0):
                self.real_grid[(px, py)] = 'PEIXE'
                count += 1
    
    def _inicializar_memoria_ia(self):
        # A IA começa sem saber nada (Névoa)
        for x in range(self.w):
            for y in range(self.h):
                self.visit_count[(x, y)] = 0 
                self.known_grid[(x, y)] = {
                    "visual": 'NEVOA',
                    "prob_peixe": PROB_INICIAL,
                    "prob_perigo": PROB_INICIAL,
                    "visitado": False
                }

    def is_valid_kraken_move(self, pos):
        """Verifica se o Kraken pode se mover para esta célula (evitando redemoinho)."""
        x, y = pos
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.real_grid[pos] != 'REDEMOINHO'
        return False
    
    def get_vizinhos(self, pos):
        """Retorna coordenadas vizinhas válidas (dentro do grid)."""
        x, y = pos
        vizinhos = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.w and 0 <= ny < self.h:
                vizinhos.append((nx, ny))
        return vizinhos
    
    # Métodos da IA de Pesca (Decisão Probabilística)
    def sentir_ambiente(self):
        """Sensores e Atualização de Crença."""
        x, y = self.barco_pos
        self.visit_count[(x, y)] += 1
        
        vizinhos = self.get_vizinhos((x, y))
        sentiu_tremor = False
        sentiu_vento = False
        
        for vx, vy in vizinhos: # Detecção de sinais no mapa REAL
            conteudo = self.real_grid[(vx, vy)]
            if conteudo == 'PEIXE': sentiu_tremor = True
            elif conteudo == 'REDEMOINHO': sentiu_vento = True
        
        cell_info = self.known_grid[(x, y)]
        cell_info["visitado"] = True
        cell_info["prob_peixe"] = 0.0  
        cell_info["prob_perigo"] = 0.0
        
        if cell_info["visual"] not in ['PESCADO', 'AFOGADO']:
            if sentiu_tremor and sentiu_vento: cell_info["visual"] = 'AMBOS'
            elif sentiu_tremor: cell_info["visual"] = 'TREMOR'
            elif sentiu_vento: cell_info["visual"] = 'VENTO'
            else: cell_info["visual"] = 'VAZIO'

        for vx, vy in vizinhos: # Propaga as probabilidades (Inferência)
            viz_info = self.known_grid[(vx, vy)]
            if not viz_info["visitado"]:
                if sentiu_tremor: viz_info["prob_peixe"] = max(viz_info["prob_peixe"], IMPACTO_DICA_POS)
                else: viz_info["prob_peixe"] = 0.05 
                
                if sentiu_vento: viz_info["prob_perigo"] = max(viz_info["prob_perigo"], IMPACTO_DICA_NEG)
                else: viz_info["prob_perigo"] = 0.0

    def decidir_movimento(self):
        """Cálculo de Utilidade: Risco vs Recompensa vs Tédio."""
        melhor_move = None
        maior_utilidade = -float('inf') 
        vizinhos = self.get_vizinhos(self.barco_pos)
        
        if self._kraken_is_near(): # Fuga!
            return self._decidir_fuga()

        for pos in vizinhos:
            info = self.known_grid[pos]
            
            recompensa = info["prob_peixe"] * PESO_RECOMPENSA
            risco = info["prob_perigo"] * PESO_RISCO
            exploracao = BONUS_EXPLORAR if not info["visitado"] else 0
            tedio = self.visit_count[pos] * PENALIDADE_TEDIO
            
            utilidade = recompensa - risco + exploracao - tedio

            if utilidade > maior_utilidade:
                maior_utilidade = utilidade
                melhor_move = pos
            elif utilidade == maior_utilidade and random.random() > 0.5:
                melhor_move = pos
                
        return melhor_move

    def _kraken_is_near(self):
        """Verifica se o Kraken está a uma distância perigosa (raio de 2 células)."""
        kx, ky = self.kraken_pos
        bx, by = self.barco_pos
        distance = abs(kx - bx) + abs(ky - by)
        return distance <= 2

    def _decidir_fuga(self):
        """Calcula o movimento que maximiza a distância do Kraken."""
        melhor_move = self.barco_pos
        max_dist_increase = -float('inf')
        kx, ky = self.kraken_pos
        
        for pos in self.get_vizinhos(self.barco_pos):
            nx, ny = pos
            current_dist = abs(self.barco_pos[0] - kx) + abs(self.barco_pos[1] - ky)
            new_dist = abs(nx - kx) + abs(ny - ky)
            dist_increase = new_dist - current_dist
            
            # Penalidade por fugir para o redemoinho
            if self.real_grid.get(pos) == 'REDEMOINHO':
                 dist_increase -= 100 

            if dist_increase > max_dist_increase:
                max_dist_increase = dist_increase
                melhor_move = pos
        
        return melhor_move