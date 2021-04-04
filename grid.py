import constants as c
import pygame
import random


class Cell:
    """
    Class for 1 cell of the grid
    """

    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = c.WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.path = False

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == c.RED

    def is_open(self):
        return self.color == c.GREEN

    def is_barrier(self):
        return self.color == c.BLACK

    def is_start(self):
        return self.color == c.ORANGE

    def is_end(self):
        return self.color == c.TURQUOISE

    def is_path(self):
        return self.path

    def is_slow(self):
        return self.color == c.YELLOW

    def is_empty(self):
        return self.color == c.WHITE

    def make_closed(self):
        self.color = c.RED

    def make_open(self):
        self.color = c.GREEN

    def make_barrier(self):
        self.path = False
        self.color = c.BLACK

    def make_start(self):
        self.path = False
        self.color = c.ORANGE

    def make_end(self):
        self.path = False
        self.color = c.TURQUOISE

    def make_path(self):
        self.path = True

    def make_slow(self):

        self.color = c.YELLOW

    def reset(self):
        self.path = False
        self.color = c.WHITE

    def draw(self, scr):
        pygame.draw.rect(scr, self.color, (self.x, self.y, self.width, self.width))

    def draw_path(self, scr):
        pygame.draw.rect(scr, c.PURPLE,
                         (self.x + c.OFFSET / 2, self.y + c.OFFSET / 2,
                          self.width - c.OFFSET, self.width - c.OFFSET))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

    def g_cost(self):
        if self.is_slow():
            return c.G_SCORE_SLOW
        else:
            return c.G_SCORE


class Grid:
    def __init__(self, rows, width):
        self.grid = []
        self.rows = rows
        self.start = None
        self.end = None
        self.width = width
        self.gap = width // rows
        for i in range(rows):
            self.grid.append([])
            for j in range(rows):
                cell = Cell(i, j, self.gap, self.rows)
                self.grid[i].append(cell)

    def draw(self, scr):
        for i in range(self.rows):
            pygame.draw.line(scr, c.GREY, (0, i * self.gap), (self.width, i * self.gap))
            for j in range(self.rows):
                pygame.draw.line(scr, c.GREY, (j * self.gap, 0), (j * self.gap, self.width))

    def set_barriers(self):
        for col in range(self.rows):
            self.grid[col][0].make_barrier()  # top barrier
            self.grid[col][self.rows - 1].make_barrier()  # bottom barrier
            self.grid[0][col].make_barrier()  # left barrier
            self.grid[self.rows - 1][col].make_barrier()  # right barrier

    def set_random_cells(self):
        """
        Stupid method, just for fun.
        """
        colors = {0: c.GREY, 1: c.GREEN, 2: c.RED, 3: c.BLACK}

        for row in self.grid:
            for cell in row:
                key = random.randint(0, 3)
                cell.color = colors[key]

    def set_random_map(self, prob):
        prob = prob * 100
        for ii in range(1, self.rows - 1):
            for jj in range(1, self.rows - 1):
                key = random.randrange(0, 100)
                if key < prob // 2:
                    self.grid[ii][jj].make_slow()
                elif key < prob:
                    self.grid[ii][jj].make_barrier()

    def get_cell(self, i, j):
        return self.grid[i][j]

    def __len__(self):
        return len(self.grid)
