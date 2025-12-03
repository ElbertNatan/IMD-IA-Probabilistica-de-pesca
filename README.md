# Fishing World

**Disciplina:** Introdução à Inteligência Artificial  
**Semestre:** 2025.2  
**Professor:** ANDRE LUIS FONSECA FAUSTINO
**Turma:** T03

## Integrantes do Grupo
ELBERT NATAN FERNANDES MORAIS - 20210052554

## Descrição do Projeto
O projeto consiste no desenvolvimento de um Agente Racional Probabilístico que simula o controle de um barco de pesca autônomo em um ambiente 2D com informações incertas. O objetivo principal é demonstrar a Tomada de Decisão sob Incerteza, onde o agente deve otimizar a coleta de recursos (peixes) enquanto gerencia o risco de fatalidade (redemoinhos). A IA não possui visibilidade total do mapa, dependendo exclusivamente de dicas sensoriais locais (🌊 e 💨) para construir um Mapa de Crença interno e calcular o próximo movimento.

A arquitetura tecnológica central é o Agente Baseado em Utilidade (Utility-Based Agent), implementado em Python. Utilizamos a Inferência Probabilística Heurística para atualizar as crenças do agente sobre o ambiente e uma Função de Utilidade ponderada para calcular o valor de cada ação. Crucialmente, para garantir a robustez e evitar loops ineficientes, implementamos um mecanismo de Penalidade de Tédio (anti-loop) que força o agente a explorar áreas de risco desconhecido, quebrando o comportamento míope de segurança

## Guia de Instalação e Execução
[Descreva os passos para instalacao e execucao do projeto. Inclua um passo-a-passo claro de como utilizar a proposta desenvolvida. Veja o exemplo abaixo.]

### 1. Instalação das Dependências
1. O projeto utiliza exclusivamente bibliotecas nativas do Python 3.x (random, os, time). Portanto, não há dependências externas a serem instaladas.

Certifique-se apenas de ter o Python 3.x configurado em seu ambiente.

# Instale a biblioteca Pygame
pip install pygame 
OU
pip install pygame-ce

2. Preparação do Código Fonte
Crie um novo arquivo de texto simples no seu computador.

Cole todo o código da IA de Pesca Probabilística dentro deste arquivo.

Salve o arquivo com o nome, por exemplo, pesca_ia_probabilistica.py.
### 2. Como Executar

Execute o comando abaixo no terminal para iniciar o servidor local:

```bash
python fishing_world.py
```

## Estrutura dos Arquivos
* config.py // Arquivo de configurações do jogo (quantidade de peixes, chance de redemoinho, etc...)
* agentes.py // Arquivo de inicialização do mapa e dos agentes (barco e kraken)
* fishing_world.py // Arquivo de execução do jogo, agentes, mapa e lógica

## Resultados e Demonstração

<img width="1000" height="600" alt="relatorio_final_ia" src="https://github.com/user-attachments/assets/57ff0009-6efc-4215-b21b-6f2f152775c5" />

<img width="1000" height="600" alt="relatorio_final_ia_2" src="https://github.com/user-attachments/assets/70fcc380-26b6-4c83-989b-42035b5cf1fb" />

## Referências
Playlist inicial utilizada para começar o projeto:
https://www.youtube.com/watch?v=BT2cjrxGpWo&list=PLJ8PYFcmwFOxtJS4EZTGEPxMEo4YdbxdQ&index=1

Palavras chaves de pesquisa:
* Pygame Básico	- pygame setup and main loop tutorial
* Renderização de Emojis - pygame render unicode emojis python
* Lógica do Kraken - python pygame astar pathfinding tutorial
* Agente Central	utility based agent python example
* Raciocínio Probabilístico	- bayesian inference simple python OU probabilistic agent belief update
* Anti-Loop (Tédio)	- local search algorithm hill climbing stagnation penalty

