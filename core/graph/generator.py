import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.graph.Graph import classGraph

def _construir_grafo():
    graph = classGraph()
    for i in range(9):
        for j in range(9):
            graph._graph[(i, j)]
            for k in range(9):
                if k != j:
                    graph.add((i, j), (i, k))
                if k != i:
                    graph.add((i, j), (k, j))
            box_row, box_col = 3 * (i // 3), 3 * (j // 3)
            for br in range(box_row, box_row + 3):
                for bc in range(box_col, box_col + 3):
                    if (br, bc) != (i, j):
                        graph.add((i, j), (br, bc))
    return graph


def _valor_valido(tabuleiro, linha, coluna, valor):
    for k in range(9):
        if tabuleiro[linha][k] == valor or tabuleiro[k][coluna] == valor:
            return False
    box_row, box_col = 3 * (linha // 3), 3 * (coluna // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if tabuleiro[i][j] == valor:
                return False
    return True


def _encontrar_vazio(tabuleiro):
    for i in range(9):
        for j in range(9):
            if tabuleiro[i][j] == 0:
                return i, j
    return None

def _contar_solucoes(tabuleiro):
    vazio = _encontrar_vazio(tabuleiro)
    if vazio is None:
        return 1

    linha, coluna = vazio
    total = 0

    for valor in range(1, 10):
        if _valor_valido(tabuleiro, linha, coluna, valor):
            tabuleiro[linha][coluna] = valor
            total += _contar_solucoes(tabuleiro)
            tabuleiro[linha][coluna] = 0
            if total > 1:
                break
            

    return total


def gerar_tabuleiro_unico():
    graph = _construir_grafo()
    cores = list(range(1, 10))

    solucao = graph.satur_backtracking(cores)
    if not solucao:
        return None, None, None

    tabuleiro = [[solucao[(i, j)] for j in range(9)] for i in range(9)]
    celulas = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(celulas)

    for linha, coluna in celulas:
        backup = tabuleiro[linha][coluna]
        tabuleiro[linha][coluna] = 0

        if _contar_solucoes([fila[:] for fila in tabuleiro]) != 1:
            tabuleiro[linha][coluna] = backup

    return graph._graph, tabuleiro, solucao, 1


def gerar_tabuleiro():
    return gerar_tabuleiro_unico()


if __name__ == '__main__':
    connections, tabuleiro, solucao, cont = gerar_tabuleiro()
    if connections is None:
        print('Falha ao gerar Sudoku.')
    else:
        for linha in tabuleiro:
            print(linha)
        print('\nSolução completa:')
        for i in range(9):
            print([solucao[(i, j)] for j in range(9)])

    print(cont)