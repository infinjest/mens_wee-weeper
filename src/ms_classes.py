from random import randint, choice

# вместо кучи property
class Descr:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)
    
    def __set__(self, instance, value):
        setattr(instance, self.name, value)


class Cell:
    is_mine, number, is_open, is_tagged = Descr(), Descr(), Descr(), Descr()

    def __init__(self):
        self.is_mine = False
        self.number = 0  # число мин вокруг клетки (целое число от 0 до 8)
        self.is_open = False
        self.is_tagged = False

    def __bool__(self):
        return not self.is_open


class GameField:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, n: int, total_mines: int):
        self.n = n
        self.total_mines = total_mines
        self.closed = self.n ** 2
        self.tags = 0
        self.__field_cells = tuple([[Cell() for _ in range(self.n)] for _ in range(self.n)])

    @property
    def field(self):
        return self.__field_cells

    # инициализация начального состояния игрового поля
    def init_field(self):

        # расстановка мин
        cnt = 0
        while cnt < self.total_mines:
            rand_i, rand_j = randint(0, self.n - 1), randint(0, self.n - 1)
            cell = self.field[rand_i][rand_j]
            if not cell.is_mine:
                cell.is_mine = True
                cnt += 1

        # подсчет количества мин вокруг клеток без мин
        for i in range(self.n):
            for j in range(self.n):
                cell = self.field[i][j]
                if not cell.is_mine:
                    for ii in [i - 1, i, i + 1]:
                        for jj in [j - 1, j, j + 1]:
                            if self.are_indices_corr(ii, jj):
                                cell.number += self.field[ii][jj].is_mine

    # рекурсивное открытие всех ячеек области, включая границы (ячейки с cell.number != 0)
    def recurs_open(self, i, j):
        for ii in [i - 1, i, i + 1]:
            for jj in [j - 1, j, j + 1]:
                if (ii, jj) != (j, j) and self.are_indices_corr(ii, jj):
                    if self.field[ii][jj] and not self.field[ii][jj].is_mine:
                        self.field[ii][jj].is_open = True
                        self.closed -= 1
                        if self.field[ii][jj].number == 0:
                            self.recurs_open(ii, jj)

    # открытие ячейки с индексами (i, j) и области за ней, если cell.number = 0
    def open_cell(self, i, j):
        cell = self.field[i][j]
        if cell:
            cell.is_open = True
            self.closed -= 1
        if cell.number == 0:
            self.recurs_open(i, j)

    # проверка что не выходим за границы поля
    def are_indices_corr(self, i: int, j: int) -> bool:
        return (all([isinstance(x, int) for x in (i, j)]) and 0 <= i < self.n and 0 <= j < self.n)