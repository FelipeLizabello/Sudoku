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


def gerar_tabuleiro():
    graph = _construir_grafo()
    cores = list(range(1, 10))
    cont = 0
    for _ in range(1000):
        tabuleiro = [[0 for _ in range(9)] for _ in range(9)]
        posicoes = random.sample([(i, j) for i in range(9) for j in range(9)], 17)
        preset = {}
        falhou = False
        cont += 1

        for i, j in posicoes:
            candidatos = cores[:]
            random.shuffle(candidatos)
            for valor in candidatos:
                if _valor_valido(tabuleiro, i, j, valor):
                    tabuleiro[i][j] = valor
                    preset[(i, j)] = valor
                    break
            else:
                falhou = True
                break

        if falhou:
            continue

        coloracao = graph.saturBFS(cores, preset)
        if coloracao:
            return graph._graph, tabuleiro, coloracao, cont

    return None, None, None


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