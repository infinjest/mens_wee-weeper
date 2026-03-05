from random import randint

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
        self.number = 0  # mines around the cell (int from 0 to 8)
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

    def init_field(self):

        # mines placement
        cnt = 0
        while cnt < self.total_mines:
            rand_i, rand_j = randint(0, self.n - 1), randint(0, self.n - 1)
            cell = self.field[rand_i][rand_j]
            if not cell.is_mine:
                cell.is_mine = True
                cnt += 1

        # mines counting
        for i in range(self.n):
            for j in range(self.n):
                cell = self.field[i][j]
                if not cell.is_mine:
                    for ii in [i - 1, i, i + 1]:
                        for jj in [j - 1, j, j + 1]:
                            if self.are_indices_corr(ii, jj):
                                cell.number += self.field[ii][jj].is_mine

    # recursive opening
    def recurs_open(self, i, j):
        for ii in [i - 1, i, i + 1]:
            for jj in [j - 1, j, j + 1]:
                if (ii, jj) != (j, j) and self.are_indices_corr(ii, jj):
                    if self.field[ii][jj] and not self.field[ii][jj].is_mine:
                        self.field[ii][jj].is_open = True
                        self.closed -= 1
                        if self.field[ii][jj].number == 0:
                            self.recurs_open(ii, jj)

    # opening the cell
    def open_cell(self, i, j):
        cell = self.field[i][j]
        if cell:
            cell.is_open = True
            self.closed -= 1
        if cell.number == 0:
            self.recurs_open(i, j)

    # are we within boundaries
    def are_indices_corr(self, i: int, j: int) -> bool:
        return (all([isinstance(x, int) for x in (i, j)]) and 0 <= i < self.n and 0 <= j < self.n)