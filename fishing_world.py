import random
import os
import time
# FEITO EM PYTHON 3.14.0
# --- 1. CONFIGURAÇÕES VISUAIS E CONSTANTES ---

# O que existe de verdade (Escondido da IA)
REAL_PEIXE      = "🐟"
REAL_REDEMOINHO = "🌀"
REAL_VAZIO      = "🟦" 

# NOVOS ICONES PARA CÉLULAS JÁ INTERAGIDAS
REAL_PESCADO    = "🎣" # Onde tinha peixe e foi coletado
REAL_AFOGADO    = "☠️" # Onde tinha redemoinho e o barco afundou (Game Over)

# O que a IA vê/sente (Sensores e Memória)
DICA_TREMOR     = "🌊"  # Indica chance de peixe
DICA_VENTO      = "💨"  # Indica chance de perigo
DICA_AMBOS      = "⛈️"  # Vento + Tremor
VISAO_NEVOA     = "▒▒"   # Área não explorada (Fog of War)
BARCO           = "🚢"  # Agente
MORTE           = "💀"  # Icone para o barco afundado na posição final do barco

# Configurações de Probabilidade e Utilidade
PROB_INICIAL      = 0.1   # Chance base de ter algo em área desconhecida
IMPACTO_DICA_POS  = 0.8   # Se tremer, vizinhos têm 80% de chance de ser peixe
IMPACTO_DICA_NEG  = 0.9   # Se ventar, vizinhos têm 90% de chance de ser perigo

# Pesos da Decisão
PESO_RECOMPENSA = 100   # O quanto ela quer peixe
PESO_RISCO      = 1000  # O quanto o agente vai temer o game over (Redemoinho)
BONUS_EXPLORAR  = 20    # Incentivo para ir onde nunca foi
PENALIDADE_TEDIO = 60   # Pontos perdidos por voltar ao mesmo lugar (Anti-Loop)

# --- 2. CLASSE PRINCIPAL DO AMBIENTE E DO AGENTE ---
class AmbienteProbabilistico:
    """
    Controla o mapa (real e o conhecido pela IA) e o estado do jogo.
    Esta versão inclui a correção de bug para ícones permanentes.
    """
    def __init__(self, largura=10, altura=10):
        self.w = largura
        self.h = altura
        
        # Mapas
        self.real_grid = {}     
        self.known_grid = {}    
        self.visit_count = {}   
        
        # Estado do Agente
        self.barco_pos = (0, 0)
        self.score = 0
        self.game_over = False
        
        self._gerar_mapa_oculto()
        self._inicializar_memoria_ia()

    # (Métodos _gerar_mapa_oculto, _inicializar_memoria_ia e get_vizinhos permanecem iguais)
    def _gerar_mapa_oculto(self):
        for x in range(self.w):
            for y in range(self.h):
                self.real_grid[(x, y)] = REAL_VAZIO
        count = 0
        while count < 6:
            rx, ry = random.randint(1, self.w-1), random.randint(1, self.h-1)
            if (rx, ry) != (0, 0) and self.real_grid[(rx, ry)] == REAL_VAZIO:
                self.real_grid[(rx, ry)] = REAL_REDEMOINHO
                count += 1
        count = 0
        while count < 5:
            px, py = random.randint(0, self.w-1), random.randint(0, self.h-1)
            if self.real_grid[(px, py)] == REAL_VAZIO and (px, py) != (0, 0):
                self.real_grid[(px, py)] = REAL_PEIXE
                count += 1

    def _inicializar_memoria_ia(self):
        for x in range(self.w):
            for y in range(self.h):
                self.visit_count[(x, y)] = 0 
                self.known_grid[(x, y)] = {
                    "visual": VISAO_NEVOA,
                    "prob_peixe": PROB_INICIAL,
                    "prob_perigo": PROB_INICIAL,
                    "visitado": False
                }

    def get_vizinhos(self, pos):
        x, y = pos
        vizinhos = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.w and 0 <= ny < self.h:
                vizinhos.append((nx, ny))
        return vizinhos
    # Fim dos métodos inalterados

    def sentir_ambiente(self):
        x, y = self.barco_pos
        self.visit_count[(x, y)] += 1
        
        vizinhos = self.get_vizinhos((x, y))
        sentiu_tremor = False
        sentiu_vento = False
        
        # 2. Leitura dos Sensores (A IA 'sente' o que está REALMENTE ao redor)
        for vx, vy in vizinhos:
            conteudo = self.real_grid[(vx, vy)]
            if conteudo == REAL_PEIXE: sentiu_tremor = True
            elif conteudo == REAL_REDEMOINHO: sentiu_vento = True
        
        # 3. Atualiza a célula atual (o que o barco viu e sentiu ali)
        cell_info = self.known_grid[(x, y)]
        cell_info["visitado"] = True
        cell_info["prob_peixe"] = 0.0  
        cell_info["prob_perigo"] = 0.0
        
        # Evitando que a IA sobrescreva os emojis do peixes já pescados ou redemoinhos encontrados
        if cell_info["visual"] != REAL_PESCADO and cell_info["visual"] != REAL_AFOGADO:
            
            # Define o emoji da dica deixado na célula
            if sentiu_tremor and sentiu_vento:
                cell_info["visual"] = DICA_AMBOS
            elif sentiu_tremor:
                cell_info["visual"] = DICA_TREMOR
            elif sentiu_vento:
                cell_info["visual"] = DICA_VENTO
            else:
                cell_info["visual"] = REAL_VAZIO
                
        # 4. Propaga as probabilidades para os vizinhos (Inferência)
        for vx, vy in vizinhos:
            viz_info = self.known_grid[(vx, vy)]
            
            if not viz_info["visitado"]:
                if sentiu_tremor: viz_info["prob_peixe"] = max(viz_info["prob_peixe"], IMPACTO_DICA_POS)
                else: viz_info["prob_peixe"] = 0.05 
                
                if sentiu_vento: viz_info["prob_perigo"] = max(viz_info["prob_perigo"], IMPACTO_DICA_NEG)
                else: viz_info["prob_perigo"] = 0.0

    # 5. Lógica de utilidade da IA
    def decidir_movimento(self):
        melhor_move = None
        maior_utilidade = -float('inf') 
        vizinhos = self.get_vizinhos(self.barco_pos)
        
        print("\n🧠 Raciocínio da IA (Cálculo de Utilidade):")
        
        for pos in vizinhos:
            info = self.known_grid[pos]
            recompensa = info["prob_peixe"] * PESO_RECOMPENSA
            risco = info["prob_perigo"] * PESO_RISCO
            exploracao = BONUS_EXPLORAR if not info["visitado"] else 0
            tedio = self.visit_count[pos] * PENALIDADE_TEDIO
            
            utilidade = recompensa - risco + exploracao - tedio
            
            status_txt = "NOVO" if not info["visitado"] else f"VISITADO {self.visit_count[pos]}x"
            print(f"   -> Ir para {pos} [{status_txt}]:")
            print(f"      Utilidade: {utilidade:.1f} (Peixe:{recompensa:.0f} - Perigo:{risco:.0f} - Tédio:{tedio})")

            if utilidade > maior_utilidade:
                maior_utilidade = utilidade
                melhor_move = pos
            elif utilidade == maior_utilidade and random.random() > 0.5:
                melhor_move = pos
                
        return melhor_move

    def mover(self):
        self.sentir_ambiente()
        novo_pos = self.decidir_movimento()
        
        if novo_pos:
            self.barco_pos = novo_pos
            conteudo = self.real_grid[novo_pos]
            
            if conteudo == REAL_PEIXE:
                print(f"\n🎣 SUCESSO! Peixe capturado em {novo_pos}!")
                self.score += 1
                self.real_grid[novo_pos] = REAL_VAZIO
                # AQUI: Marca permanente na memória
                self.known_grid[novo_pos]["visual"] = REAL_PESCADO 
                time.sleep(1.5)
                
            elif conteudo == REAL_REDEMOINHO:
                print(f"\n💀 GAME OVER! O barco afundou em um redemoinho em {novo_pos}!")
                self.game_over = True
                # AQUI: Marca permanente na memória
                self.known_grid[novo_pos]["visual"] = REAL_AFOGADO 
                time.sleep(2)

    def desenhar(self):
        """Desenha a interface no console."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"--- 🤖 IA PROBABILÍSTICA DE PESCA 🤖 ---")
        print(f"Peixes Capturados: {self.score}/5")
        print(f"Legenda: {BARCO} Eu | {DICA_TREMOR} Treme | {DICA_VENTO} Vento | {VISAO_NEVOA} Névoa")
        print(f"            {REAL_PESCADO} Pescado | {REAL_AFOGADO} Perigo Fatal")
        print("-" * (self.w * 3 + 2))
        
        for y in range(self.h):
            linha = "|"
            for x in range(self.w):
                pos = (x, y)
                if pos == self.barco_pos:
                    if self.game_over:
                        linha += MORTE + " "
                    else:
                        linha += BARCO + " "
                else:
                    info = self.known_grid[pos]
                    # Desenha o visual guardado na memória da IA
                    if info["visitado"] or info["visual"] == REAL_PESCADO or info["visual"] == REAL_AFOGADO:
                         linha += info["visual"] + " "
                    else: 
                        linha += VISAO_NEVOA + " "
            print(linha + "|")
        print("-" * (self.w * 3 + 2))

# --- 3. EXECUÇÃO PRINCIPAL ---
def main():
    # Instancia o jogo (A simulação)
    jogo = AmbienteProbabilistico(largura=8, altura=8)
    
    print("Iniciando simulação...")
    time.sleep(1)
    
    turnos = 0
    MAX_TURNOS = 100 # Limite de turnos para evitar loops eternos
    
    while not jogo.game_over and turnos < MAX_TURNOS:
        turnos += 1
        
        jogo.desenhar() # Mostra o mapa
        jogo.mover()    # Executa a IA
        
        if jogo.score >= 5:
            jogo.desenhar()
            print("\n🏆 VITÓRIA! Todos os peixes foram coletados com segurança!")
            break
        
        # Pausa para dar tempo de ler os logs
        time.sleep(1.5) 
        
    if turnos >= MAX_TURNOS:
        print("\n⏳ Tempo esgotado (Combustível acabou).")
    
    print("Simulação encerrada.")

if __name__ == "__main__":
    # Garante que a função principal é chamada ao executar o script.
    main()