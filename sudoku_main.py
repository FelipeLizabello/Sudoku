
import sys

from core.UI import board
from core.graph.generator import gerar_tabuleiro


def main():
    while True:
        escolha = board.menu_loop()
        if escolha is None:
            sys.exit(0)

        connections, tab, sol, _ = gerar_tabuleiro()
        board.connections = connections
        board.tabuleiro = tab
        board.solucao = sol
        preset = set()
        first_empty = (0, 0)
        for i in range(9):
            for j in range(9):
                if tab[i][j] != 0:
                    preset.add((i, j))
                else:
                    if first_empty == (0, 0) and tab[0][0] != 0:
                        first_empty = (i, j)
                    elif first_empty == (0, 0) and tab[0][0] == 0:
                        first_empty = (0, 0)

        board.preset_positions = preset
        board.selected_cell = first_empty if any(tab[i][j] == 0 for i in range(9) for j in range(9)) else (0, 0)

        board.show_solution = True if escolha == 'solution' else False

        if escolha == 'solution':
            board.start_fill_animation(interval=0.04, random_order=False)
        else:
            board.stop_fill_animation()

        try:
            while True:
                res = board.game_loop()
                if res == 'menu':
                    break
        except SystemExit:
            raise
        except KeyboardInterrupt:
            print("Encerrando...")


if __name__ == '__main__':
    main()

