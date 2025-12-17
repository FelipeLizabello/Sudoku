# Sudoku Neon

Uma experiência de Sudoku estilizada em neon construída com Python + Pygame, gerando tabuleiros válidos automaticamente e oferecendo modos de jogo e visualização da solução para demonstrar domínio de backtracking, heurísticas de coloração e UI animada.

## Visão geral

- **Geração garantida de Sudoku válido:** [`core.graph.generator.gerar_tabuleiro`](core/graph/generator.py) usa coloração DSATUR em [`core.graph.Graph.classGraph`](core/graph/Graph.py) para produzir soluções completas e depois remove pistas mantendo unicidade.
- **Interface animada em Pygame:** [`core.UI.board`](core/UI/board.py) desenha menu, jogo e efeitos (starfield, raios, animação de preenchimento).
- **CLI simples para contratação/demos:** [sudoku_main.py](sudoku_main.py) inicia menu interativo, troca entre “Jogar” e “Ver resolução” e conecta UI ao gerador.

## Arquitetura

| Camada | Responsabilidade | Arquivos |
| --- | --- | --- |
| Núcleo de grafos | Modela adjacências 9×9, aplica heurísticas de coloração, suporta presets | [`core/graph/Graph.py`](core/graph/Graph.py) |
| Geração de tabuleiros | Constrói grafo, preenche solução, remove pistas mantendo unicidade, expõe API | [`core/graph/generator.py`](core/graph/generator.py) |
| UI/Loop do jogo | Renderiza cena, captura input, valida movimentos, mostra animações/menus | [`core/UI/board.py`](core/UI/board.py) |
| Entrada principal | Menu inicial, carrega tabuleiro, propaga presets e modo para UI | [sudoku_main.py](sudoku_main.py) |

## Requisitos

- Python 3.10+
- `pygame>=2.5`
- Opcional: assets de fundo em `assets/background.(png|jpg)`

### Instalação rápida

```
pip install -r requirements.txt  # ou pip install pygame
```

## Como executar

```
python sudoku_main.py
```

1. Escolha **Jogar** para interagir com o tabuleiro.
2. Escolha **Ver resolução** para assistir à animação automática.
3. `Esc` retorna ao menu; `Enter` valida o tabuleiro.

## Controles principais

- Setas / WASD / clique: mover seleção.
- Dígitos (fila ou keypad): preencher célula (zeros limpam).
- `Ctrl + 0`: limpar todas as casas não fixas.
- `Enter`: valida o estado atual exibindo mensagem.

## Fluxo de geração

1. `_construir_grafo()` monta adjacências linha/coluna/box.
2. [`classGraph.satur_backtracking`](core/graph/Graph.py) colore nós com heurística DSATUR, garantindo solução consistente.
3. `_contar_solucoes()` remove pistas até o puzzle manter uma única solução.
4. `gerar_tabuleiro()` retorna conexões, puzzle parcial, solução e contador de tentativas.

## Próximos passos sugeridos

- Persistir melhores tempos/jogadores (ex.: SQLite ou JSON).
- Exportar/importar puzzles (`.sdk`).
- Ajustar dificuldade controlando quantidade mínima de pistas.
- Adicionar testes unitários para `validate_current_board` e `_valor_valido`.

## Licença e contato

Defina a licença neste arquivo e inclua informações de contato/portfólio para contratantes interessados.