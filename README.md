# [Nome do Projeto]

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

2. Preparação do Código Fonte
Crie um novo arquivo de texto simples no seu computador.

Cole todo o código da IA de Pesca Probabilística dentro deste arquivo.

Salve o arquivo com o nome, por exemplo, pesca_ia_probabilistica.py.
### 2. Como Executar

Execute o comando abaixo no terminal para iniciar o servidor local:

```bash
python pesca_ia.py
```

## Estrutura dos Arquivos

  * `src/`: Código-fonte da aplicação ou scripts de processamento.
  * `notebooks/`: Análises exploratórias, testes e prototipagem.
  * `data/`: Datasets utilizados (se o tamanho permitir o upload).
  * `assets/`: Imagens, logos ou gráficos de resultados.

## Resultados e Demonstração

[Adicione prints da aplicação em execução ou gráficos com os resultados do modelo/agente. Se for uma aplicação Web, coloque um print da interface.]

## Referências

  * [Link para o Dataset original]
  * [Artigo, Documentação ou Tutorial utilizado como base]
