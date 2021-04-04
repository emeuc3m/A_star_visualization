import pygame
import grid as g
from queue import PriorityQueue
import constants as c


class Main:
    """
    Main class for the visualization tool.

    Controls:
        Right Click: set start, end and barrier cells
        Central Click: set slow cells
        Left Click: erase cells
        E: erase cells modified by the algorithm
        R: erase all cells (set empty map)
        T: generate random map
    """
    def __init__(self, rows, width):
        self.rows = rows
        self.width = width
        self.screen = pygame.display.set_mode((self.width, self.width))
        self.grid = g.Grid(self.rows, self.width)

        pygame.display.set_caption("A*")
        self.update()

    def draw(self):
        """
        Draws the screen, the grid and the cells.
        """
        self.screen.fill(c.WHITE)

        for ii in range(self.rows):
            for jj in range(self.rows):
                cell = self.grid.get_cell(ii, jj)

                cell.draw(self.screen)
                if cell.is_path():
                    cell.draw_path(self.screen)

        self.grid.draw(self.screen)

        pygame.display.update()

    def update(self):

        run = True
        # main loop
        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                try:
                    # change the type of the cell at mouse's position

                    if pygame.mouse.get_pressed(3)[0]:  # left click pressed
                        cell = self.get_mouse_cell()

                        # if there's no start node, create it
                        if not self.grid.start:
                            self.grid.start = cell
                            self.grid.start.make_start()

                        # if there's no end node, create it
                        elif not self.grid.end and cell != self.grid.start:
                            self.grid.end = cell
                            self.grid.end.make_end()

                        # else, make a barrier
                        elif cell != self.grid.end and cell != self.grid.start:
                            cell.make_barrier()

                    elif pygame.mouse.get_pressed(3)[2]:    # right click pressed
                        cell = self.get_mouse_cell()

                        # reset start cell
                        if cell == self.grid.start:
                            self.grid.start = None
                            cell.reset()

                        # reset end cell
                        elif cell == self.grid.end:
                            self.grid.end = None
                            cell.reset()
                        # erase with stroke = 1 cell
                        elif self.grid.start is not None or self.grid.end is not None:
                            cell.reset()
                        # erase with stroke = 4 cells
                        else:
                            cell.reset()
                            self.delete_brush(cell)

                    elif pygame.mouse.get_pressed(3)[1]:    # wheel click pressed
                        cell = self.get_mouse_cell()

                        if cell != self.grid.start and cell != self.grid.end:
                            cell.make_slow()

                except IndexError:
                    pass

                # run A* algorithm
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and (self.grid.start and self.grid.end) is not None:
                        # update all cells' neighbors
                        grid = self.grid.grid
                        for row in grid:
                            for cell in row:
                                cell.update_neighbors(grid)
                        # call algorithm
                        self.a_star_alg()

                    elif event.key == pygame.K_e:
                        self.reset_map()

                    elif event.key == pygame.K_r:
                        self.reset_map(True)

                    elif event.key == pygame.K_t:
                        self.reset_map(True)
                        self.grid.set_barriers()
                        self.grid.set_random_map(c.PROB)

            self.draw()

        pygame.quit()

    def a_star_alg(self):
        grid = self.grid.grid
        start = self.grid.start
        end = self.grid.end

        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, start))
        expanded_nodes = {}  # list with the expanded nodes, used for backtracking

        # g and f costs:
        g_score = {cell: float("inf") for row in grid for cell in row}
        g_score[start] = 0
        f_score = {cell: float("inf") for row in grid for cell in row}
        f_score[start] = h(start.get_pos(), end.get_pos())

        # we need to hash all the open set nodes because PriorityQueue doesn't have a "in" method
        open_set_hash = {start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            # expand current node
            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == end:
                # we finished, make path.
                while current in expanded_nodes:
                    current = expanded_nodes[current]
                    if current != start:
                        current.make_path()
                    self.draw()

                end.make_end()
                return True

            for neighbor in current.neighbors:

                temp_g_score = g_score[current] + current.g_cost()

                # if a better path to the neighbor is found, update the path
                if temp_g_score < g_score[neighbor]:
                    expanded_nodes[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        if not neighbor.is_slow():
                            neighbor.make_open()

            self.draw()

            if current != start and current != end:
                if not current.is_slow():
                    current.make_closed()

        return False

    def get_mouse_pos(self, pos):
        gap = self.width // self.rows  # how big each cell is
        y, x = pos

        row = y // gap
        col = x // gap

        return row, col

    def get_mouse_cell(self):
        pos = pygame.mouse.get_pos()
        row, col = self.get_mouse_pos(pos)
        cell = self.grid.get_cell(row, col)
        return cell

    def delete_brush(self, cell):
        i, j = cell.get_pos()

        try:
            cell_up = self.grid.get_cell(i, j+1)
            cell_up.reset()
        except IndexError:
            pass
        try:
            cell_down = self.grid.get_cell(i, j-1)
            cell_down.reset()
        except IndexError:
            pass
        try:
            cell_left = self.grid.get_cell(i-1, j)
            cell_left.reset()
        except IndexError:
            pass
        try:
            cell_right = self.grid.get_cell(i+1, j)
            cell_right.reset()
        except IndexError:
            pass

    def reset_map(self, grid_reset=False):
        """
        Resets (sets to empty) the cells in the grid
        grid_reset (boolean):
            False = reset cells modified by the A* algorithm
            True = reset all cells in the grid

        """

        self.grid.start = None
        self.grid.end = None

        # reset non-map cells
        for row in self.grid.grid:
            for cell in row:
                if grid_reset:
                    cell.reset()

                elif not (cell.is_barrier() or cell.is_empty()):
                    if cell.is_slow():
                        cell.reset()
                        cell.make_slow()

                    else:
                        cell.reset()


def h(p1: tuple, p2: tuple):
    """
    Heuristic function using Manhattan Distance.
    """
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


if __name__ == "__main__":
    Main(c.ROWS, c.WIDTH)
