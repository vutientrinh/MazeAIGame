import sys
import pygame
import random
import operator
import time
import copy
sys.setrecursionlimit(3000)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGRAY = (169, 169, 169)
YELLOW = (222, 178, 0)
PINK = (225, 96, 253)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
ORANGE = (255, 99, 71)
GRAY = (119, 136, 153)
LIGHTORANGE = (255, 176, 56)
INTERMEDIARYORANGE = (255, 154, 0) 
LIGHTBLUE = (60, 170, 255)
DARKBLUE = (0, 101, 178)
BEIGE = (178, 168, 152)
BORDER_THICKNESS = 1.0

HEIGHT_TOTAL = 680
WIDTH = 600
HEIGHT = 600
SCREEN_SIZE = (WIDTH + 300, HEIGHT_TOTAL + 80)

FONTSIZE_START = 50
FONTSIZE_COMMANDS_INTIAL = 25
FONTSIZE_MAZE = 20

SIZE = 50
NUM_SCORE_POINTS = HEIGHT_TOTAL // SIZE // 2

SCORE_MODE = True


def text(background, message, color, size, coordinate_x, coordinate_y):
    font = pygame.font.SysFont(None, size)
    text = font.render(message, True, color)
    background.blit(text, [coordinate_x, coordinate_y])

class NodeBorder():
    def __init__(self, pos_x, pos_y, width, height):
        self.color = BLACK
        self.thickness = BORDER_THICKNESS
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])


class Node():
    def __init__(self, pos_x, pos_y):
        self.color = DARKGRAY

        self.visited = False
        self.explored = False

        self.matrix_pos_x = 0
        self.matrix_pos_y = 0

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = SIZE
        self.height = SIZE

        self.top_border = NodeBorder(self.pos_x, self.pos_y, SIZE, BORDER_THICKNESS)
        self.bottom_border = NodeBorder(self.pos_x, self.pos_y + SIZE - BORDER_THICKNESS, SIZE, BORDER_THICKNESS)
        self.right_border = NodeBorder(self.pos_x + SIZE - BORDER_THICKNESS, self.pos_y, BORDER_THICKNESS, SIZE)
        self.left_border = NodeBorder(self.pos_x, self.pos_y, BORDER_THICKNESS, SIZE)

        self.neighbors = []
        self.neighbors_connected = []
        self.parent = None
        
        self.score_point = None
    
    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])

        self.top_border.render(background)
        self.bottom_border.render(background)
        self.right_border.render(background)
        self.left_border.render(background)

class ScorePoint():
    def __init__(self, pos_x, pos_y, value, color):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.collected = False
        #modified
        self.value = value
        self.color = color
        
    def render(self, background):
        if not self.collected:
            pygame.draw.circle(background, self.color, (self.pos_x*SIZE + SIZE//2, self.pos_y*SIZE + SIZE//2), SIZE // 3)

class Player():
    def __init__(self, initial_x, initial_y):
        self.pos_x = initial_x * SIZE + BORDER_THICKNESS
        self.pos_y = initial_y * SIZE + BORDER_THICKNESS
        self.matrix_pos_x = initial_x
        self.matrix_pos_y = initial_y
        self.width = SIZE - 2 * BORDER_THICKNESS
        self.height = SIZE - 2 * BORDER_THICKNESS
        self.color = RED
        self.score = HEIGHT // SIZE * 3

    def update(self, maze, events, score_points):
            for event in events:
                if self.score > 0 or not SCORE_MODE:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT and self.pos_x > BORDER_THICKNESS and (maze[self.matrix_pos_x][self.matrix_pos_y].left_border.color != BLACK):
                            self.pos_x -= SIZE
                            self.matrix_pos_x -= 1
                            if SCORE_MODE:
                                self.score -= 1
                        if event.key == pygame.K_RIGHT and self.pos_x + BORDER_THICKNESS < WIDTH - SIZE and (maze[self.matrix_pos_x][self.matrix_pos_y].right_border.color != BLACK):
                            self.pos_x += SIZE
                            self.matrix_pos_x += 1
                            if SCORE_MODE:
                                self.score -= 1
                        if event.key == pygame.K_UP and self.pos_y > BORDER_THICKNESS and (maze[self.matrix_pos_x][self.matrix_pos_y].top_border.color != BLACK): 
                            self.pos_y -= SIZE
                            self.matrix_pos_y -= 1
                            if SCORE_MODE:
                                self.score -= 1
                        if event.key == pygame.K_DOWN and self.pos_y + BORDER_THICKNESS < HEIGHT - SIZE and (maze[self.matrix_pos_x][self.matrix_pos_y].bottom_border.color != BLACK):
                            self.pos_y += SIZE
                            self.matrix_pos_y += 1
                            if SCORE_MODE:
                                self.score -= 1
            for point in score_points:
                if self.matrix_pos_x == point.pos_x and self.matrix_pos_y == point.pos_y and not point.collected:
                    if SCORE_MODE:
                        self.score += point.value
                    point.collected = True

    def render(self, background):
        pygame.draw.rect(background, self.color, [self.pos_x, self.pos_y, self.width, self.height])

class Maze():
    def __init__(self, background, initial_x, initial_y, final_x, final_y):
        self.maze = []
        self.total_nodes = 0
        self.maze_created = False
        self.initial_coordinate_x = initial_x
        self.initial_coordinate_y = initial_y
        self.final_coordinate_x = final_x
        self.final_coordinate_y = final_y
        values = [25, 50, 75, 100]
        colors = [WHITE, BLACK, RED, GREEN]
        self.score_points = [ScorePoint(random.randint(0, WIDTH // SIZE - 1), random.randint(0, HEIGHT // SIZE - 1), values[rand], colors[rand]) for rand in [random.randint(0, len(values)-1) for _ in range(NUM_SCORE_POINTS)]]
        x = 0
        y = 0
        for i in range(0, WIDTH, SIZE):
            self.maze.append([])
            for j in range(0, HEIGHT, SIZE):
                self.maze[x].append(Node(i , j))
                self.total_nodes += 1
                y += 1
            x += 1

        self.define_neighbors()
        
        for point in self.score_points:
            self.maze[point.pos_x][point.pos_y].score_point = point

    def add_edge(self, node, neighbor):
        neighbor.neighbors_connected.append(node)
        node.neighbors_connected.append(neighbor)

    def remove_neighbors_visited(self, node):
        node.neighbors = [x for x in node.neighbors if not x.visited]
        
    def render(self, background):
        for i in range(0, int(HEIGHT / SIZE)):
            for j in range(0, int(WIDTH / SIZE)):
                self.maze[i][j].render(background)
        if self.maze_created:
            self.maze[self.initial_coordinate_x][self.initial_coordinate_y].color = BEIGE
            self.maze[self.final_coordinate_x][self.final_coordinate_y].color = LIGHTBLUE
        if SCORE_MODE:
            for sp in self.score_points:
                sp.render(background)
    
    def define_neighbors(self):
        for i in range(0, int(HEIGHT / SIZE)):
            for j in range(0, int(WIDTH / SIZE)):
                self.maze[i][j].matrix_pos_x = i
                self.maze[i][j].matrix_pos_y = j
                if i > 0 and j > 0 and i < int(HEIGHT / SIZE) - 1 and j < int(HEIGHT / SIZE) - 1:
                    self.maze[i][j].neighbors.append(self.maze[i + 1][j]) # bot
                    self.maze[i][j].neighbors.append(self.maze[i - 1][j]) # top
                    self.maze[i][j].neighbors.append(self.maze[i][j + 1]) # right
                    self.maze[i][j].neighbors.append(self.maze[i][j - 1]) # left
                elif i == 0 and j == 0:
                    self.maze[i][j].neighbors.append(self.maze[i][j + 1]) # right
                    self.maze[i][j].neighbors.append(self.maze[i + 1][j]) # bot
                elif i == int(HEIGHT / SIZE) - 1 and j == 0:
                    self.maze[i][j].neighbors.append(self.maze[i - 1][j]) # top
                    self.maze[i][j].neighbors.append(self.maze[i][j + 1]) # right
                elif i == 0 and j == int(WIDTH / SIZE) - 1:
                    self.maze[i][j].neighbors.append(self.maze[i][j - 1]) # left
                    self.maze[i][j].neighbors.append(self.maze[i + 1][j]) # bot
                elif i == int(HEIGHT / SIZE) - 1 and j == int(WIDTH / SIZE) - 1:
                    self.maze[i][j].neighbors.append(self.maze[i][j - 1]) # left
                    self.maze[i][j].neighbors.append(self.maze[i - 1][j]) # top
                elif j == 0:
                    self.maze[i][j].neighbors.append(self.maze[i - 1][j]) # top
                    self.maze[i][j].neighbors.append(self.maze[i][j + 1]) # right
                    self.maze[i][j].neighbors.append(self.maze[i + 1][j]) # bot
                elif i == 0:
                    self.maze[i][j].neighbors.append(self.maze[i + 1][j]) # bot
                    self.maze[i][j].neighbors.append(self.maze[i][j + 1]) # right
                    self.maze[i][j].neighbors.append(self.maze[i][j - 1]) # left
                elif i == int(HEIGHT / SIZE) - 1:
                    self.maze[i][j].neighbors.append(self.maze[i - 1][j]) # top
                    self.maze[i][j].neighbors.append(self.maze[i][j + 1]) # right
                    self.maze[i][j].neighbors.append(self.maze[i][j - 1]) # left
                elif j == int(WIDTH / SIZE) - 1:
                    self.maze[i][j].neighbors.append(self.maze[i + 1][j]) # bot
                    self.maze[i][j].neighbors.append(self.maze[i - 1][j]) # top
                    self.maze[i][j].neighbors.append(self.maze[i][j - 1]) # left

    def break_border(self, node, neightbor, color):
        # right
        if (neightbor.matrix_pos_x == node.matrix_pos_x + 1) and (neightbor.matrix_pos_y == node.matrix_pos_y):
            node.right_border.color = color
            neightbor.left_border.color = color
        # left
        elif (neightbor.matrix_pos_x == node.matrix_pos_x - 1) and (neightbor.matrix_pos_y == node.matrix_pos_y):
            node.left_border.color = color
            neightbor.right_border.color = color
        # bot
        elif (neightbor.matrix_pos_x == node.matrix_pos_x) and (neightbor.matrix_pos_y == node.matrix_pos_y + 1):
            node.bottom_border.color = color
            neightbor.top_border.color = color
        # top
        elif (neightbor.matrix_pos_x == node.matrix_pos_x) and (neightbor.matrix_pos_y == node.matrix_pos_y - 1):
            node.top_border.color = color
            neightbor.bottom_border.color = color

    def manhattan_distance(self, node):
        return abs(node.matrix_pos_x - self.final_coordinate_x) + abs(node.matrix_pos_y - self.final_coordinate_y)
    
    #Map generating
    def dfs(self, background):
        current_cell = random.choice(random.choice(self.maze))
        current_cell.visited = True
        current_cell.color = GREEN
        stack = [current_cell]
        visited_cells = 1
        
        while visited_cells != self.total_nodes or len(stack) != 0:
            self.remove_neighbors_visited(current_cell)
            if len(current_cell.neighbors) > 0:
                random_neighbor = random.choice(current_cell.neighbors)

                self.break_border(current_cell, random_neighbor, GREEN)

                self.add_edge(current_cell, random_neighbor)
                current_cell = random_neighbor
                stack.append(current_cell)
                current_cell.visited = True
                current_cell.color = GREEN
                visited_cells += 1
            else:
                current_cell.color = YELLOW

                if current_cell.top_border.color == GREEN:
                    current_cell.top_border.color = YELLOW
                if current_cell.bottom_border.color == GREEN:
                    current_cell.bottom_border.color = YELLOW
                if current_cell.right_border.color == GREEN:
                    current_cell.right_border.color = YELLOW
                if current_cell.left_border.color == GREEN:
                    current_cell.left_border.color = YELLOW
                    
                if len(stack) == 1:
                    stack.pop()
                else:
                    stack.pop()
                    current_cell = stack[-1]
            self.render(background)
            text(background, "GENERATING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 215, 620)
            pygame.display.update()
        self.maze_created = True

    #Breadth first search
    def bfs(self, background, player, slow):
        total = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(initial_node, 0)]
        while len(queue) > 0 and not find:
            current_node, depth = queue.pop(0)
            if depth > player.score:
                continue
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK

            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    if i.score_point is not None and not i.score_point.collected:
                        queue.append((i, depth + 1 - i.score_point.value))
                    else:
                        queue.append((i, depth + 1))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
        
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        if current.parent is None:
            print("No solution")
            return (False, depth - 1)
        else: 
            total = 0
            while (current.parent).parent != None:
                current = current.parent
                current.color = ORANGE
                if current.score_point is not None and not current.score_point.collected:
                    player.score += current.score_point.value
                    total += current.score_point.value

                if current.top_border.color == PINK:
                    current.top_border.color = ORANGE
                if current.bottom_border.color == PINK:
                    current.bottom_border.color = ORANGE
                if current.right_border.color == PINK:
                    current.right_border.color = ORANGE
                if current.left_border.color == PINK:
                    current.left_border.color = ORANGE
                #render the path-to-end step
                self.render(background)
                player.render(background)
                pygame.display.update()
            return (True, depth + total + 1)

    #Depth-limited search
    def dls(self, background, player, slow):
        total = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        stack = [(initial_node, 0)]

        while len(stack) > 0 and not find:
            current_node, depth = stack.pop()
            if depth > player.score:
                continue
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK

            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    if i.score_point is not None and not i.score_point.collected:
                        stack.append((i, depth + 1 - i.score_point.value))  # Decrease the depth by the value of the score point
                    else:
                        stack.append((i, depth + 1))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
        
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        if current.parent is None:
            print("No solution")
            return (False, depth - 1)
        else: 
            total = 0
            while (current.parent).parent != None:
                current = current.parent
                current.color = ORANGE
                if current.score_point is not None and not current.score_point.collected:
                    player.score += current.score_point.value
                    total += current.score_point.value

                if current.top_border.color == PINK:
                    current.top_border.color = ORANGE
                if current.bottom_border.color == PINK:
                    current.bottom_border.color = ORANGE
                if current.right_border.color == PINK:
                    current.right_border.color = ORANGE
                if current.left_border.color == PINK:
                    current.left_border.color = ORANGE

                self.render(background)
                player.render(background)
                pygame.display.update()
            return (True, depth + total + 1)

    #Uniform cost search
    def ucs(self, background, player, slow):
        total = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(0, initial_node)]
        while len(queue) > 0 and not find:
            queue.sort(key=operator.itemgetter(0), reverse = True)  # Sort in descending order
            cost, current_node = queue.pop()
            if cost > player.score:
                continue
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK

            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    if i.score_point is not None and not i.score_point.collected:
                        queue.append((cost + 1 - i.score_point.value, i))  # Decrease the cost by the value of the score point
                    else:
                        queue.append((cost + 1, i))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
        
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        if current.parent is None:
            print("No solution")
            return (False, cost - 1)
        else: 
            while (current.parent).parent != None:
                current = current.parent
                current.color = ORANGE
                if current.score_point is not None and not current.score_point.collected:
                    player.score += current.score_point.value
                    total += current.score_point.value

                if current.top_border.color == PINK:
                    current.top_border.color = ORANGE
                if current.bottom_border.color == PINK:
                    current.bottom_border.color = ORANGE
                if current.right_border.color == PINK:
                    current.right_border.color = ORANGE
                if current.left_border.color == PINK:
                    current.left_border.color = ORANGE

                self.render(background)
                player.render(background)
                pygame.display.update()
            return (True, cost + total + 1)

    #Greedy Search
    def greedy(self, background, player, slow):
        total = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(0 + self.manhattan_distance(initial_node), 0, initial_node)]
        while len(queue) > 0 and not find:
            queue.sort(key=operator.itemgetter(0), reverse = True)
            total_cost, path_cost, current_node = queue.pop()  # Pop the node with the smallest total cost
            if path_cost > player.score:
                continue
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK

            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    if i.score_point is not None and not i.score_point.collected:
                        queue.append((path_cost + 1 - i.score_point.value , path_cost + 1 - i.score_point.value, i))  # Decrease the path cost by the value of the score point
                    else:
                        queue.append((path_cost + 1 , path_cost + 1, i))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()

        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        if current.parent is None:
            print("No solution")
            return (False, path_cost - 1)
        else: 
            while (current.parent).parent != None:
                current = current.parent
                current.color = ORANGE
                if current.score_point is not None and not current.score_point.collected:
                    player.score += current.score_point.value
                    total += current.score_point.value

                if current.top_border.color == PINK:
                    current.top_border.color = ORANGE
                if current.bottom_border.color == PINK:
                    current.bottom_border.color = ORANGE
                if current.right_border.color == PINK:
                    current.right_border.color = ORANGE
                if current.left_border.color == PINK:
                    current.left_border.color = ORANGE

                self.render(background)
                player.render(background)
                pygame.display.update()
            return (True, path_cost + total + 1)

    #A-Star Search
    def astar(self, background, player, slow):
        total = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(0 + self.manhattan_distance(initial_node), 0, initial_node)]
        while len(queue) > 0 and not find:
            queue.sort(key=operator.itemgetter(0), reverse = True)
            total_cost, path_cost, current_node = queue.pop()  # Pop the node with the smallest total cost
            if path_cost > player.score:
                continue
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK

            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    if i.score_point is not None and not i.score_point.collected:
                        queue.append((path_cost + 1 - i.score_point.value + self.manhattan_distance(i), path_cost + 1 - i.score_point.value, i))  # Decrease the path cost by the value of the score point
                    else:
                        queue.append((path_cost + 1 + self.manhattan_distance(i), path_cost + 1, i))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()

        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        if current.parent is None:
            print("No solution")
            return (False, path_cost - 1)
        else: 
            while (current.parent).parent != None:
                current = current.parent
                current.color = ORANGE
                if current.score_point is not None and not current.score_point.collected:
                    player.score += current.score_point.value
                    total += current.score_point.value

                if current.top_border.color == PINK:
                    current.top_border.color = ORANGE
                if current.bottom_border.color == PINK:
                    current.bottom_border.color = ORANGE
                if current.right_border.color == PINK:
                    current.right_border.color = ORANGE
                if current.left_border.color == PINK:
                    current.left_border.color = ORANGE

                self.render(background)
                player.render(background)
                pygame.display.update()
            return (True, path_cost + total + 1)


    #Infinite BFS Search
    def n_bfs(self, background, player, slow):
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [initial_node]
        while len(queue) > 0 and not find:
            queue[0].color = PINK
            if queue[0].top_border.color == YELLOW:
                queue[0].top_border.color = PINK
            if queue[0].bottom_border.color == YELLOW:
                queue[0].bottom_border.color = PINK
            if queue[0].right_border.color == YELLOW:
                queue[0].right_border.color = PINK
            if queue[0].left_border.color == YELLOW:
                queue[0].left_border.color = PINK

            u = queue.pop(0)
            for i in u.neighbors_connected:
                if i.explored == False:
                    i.parent = u
                    i.explored = True
                    queue.append(i)
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
        
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        steps = 0
        while (current.parent).parent != None:
            steps += 1
            current = current.parent
            current.color = ORANGE

            if current.top_border.color == PINK:
                current.top_border.color = ORANGE
            if current.bottom_border.color == PINK:
                current.bottom_border.color = ORANGE
            if current.right_border.color == PINK:
                current.right_border.color = ORANGE
            if current.left_border.color == PINK:
                current.left_border.color = ORANGE

            self.render(background)
            player.render(background)
            pygame.display.update()
        return (find, steps + 1)

    #Infinite DFS Search 
    def n_dfs(self, background, player, slow):
        steps = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        stack = [initial_node]
        while len(stack) > 0 and not find:
            current_node = stack.pop()
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK

            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    stack.append(i)
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
            
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        while (current.parent).parent != None:
            steps += 1
            current = current.parent
            current.color = ORANGE

            if current.top_border.color == PINK:
                current.top_border.color = ORANGE
            if current.bottom_border.color == PINK:
                current.bottom_border.color = ORANGE
            if current.right_border.color == PINK:
                current.right_border.color = ORANGE
            if current.left_border.color == PINK:
                current.left_border.color = ORANGE

            self.render(background)
            player.render(background)
            pygame.display.update()
        return (find, steps + 1)

    #Infinite UCS Search
    def n_ucs(self, background, player, slow):
        steps = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(0, initial_node)]
        while len(queue) > 0 and not find:
            queue.sort(key=operator.itemgetter(0), reverse = True)
            cost, current_node = queue.pop()
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK
                    
            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    queue.append((cost + 1, i))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
            
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        while (current.parent).parent != None:
            steps += 1
            current = current.parent
            current.color = ORANGE

            if current.top_border.color == PINK:
                current.top_border.color = ORANGE
            if current.bottom_border.color == PINK:
                current.bottom_border.color = ORANGE
            if current.right_border.color == PINK:
                current.right_border.color = ORANGE
            if current.left_border.color == PINK:
                current.left_border.color = ORANGE

            self.render(background)
            player.render(background)
            pygame.display.update()
        return (find, steps + 1) 

    #Infinite Greedy Search
    def n_greedy(self, background, player, slow):
        steps = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(self.manhattan_distance(initial_node), initial_node)]
        while len(queue) > 0 and not find:
            queue.sort(key=operator.itemgetter(0), reverse = True)
            heuristic, current_node = queue.pop()
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK
                    
            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    queue.append((self.manhattan_distance(i), i))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
            
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        while (current.parent).parent != None:
            steps += 1
            current = current.parent
            current.color = ORANGE

            if current.top_border.color == PINK:
                current.top_border.color = ORANGE
            if current.bottom_border.color == PINK:
                current.bottom_border.color = ORANGE
            if current.right_border.color == PINK:
                current.right_border.color = ORANGE
            if current.left_border.color == PINK:
                current.left_border.color = ORANGE

            self.render(background)
            player.render(background)
            pygame.display.update()
        return (find, steps + 1)

    #Infinite A-Star Search
    def n_astar(self, background, player, slow):
        steps = 0
        initial_node = self.maze[player.matrix_pos_x][player.matrix_pos_y]
        initial_node.explored = True
        find = False
        queue = [(0 + self.manhattan_distance(initial_node), 0, initial_node)]
        while len(queue) > 0 and not find:
            queue.sort(key=operator.itemgetter(0), reverse = True)
            total_cost, path_cost, current_node = queue.pop()
            current_node.color = PINK
            if current_node.top_border.color == YELLOW:
                current_node.top_border.color = PINK
            if current_node.bottom_border.color == YELLOW:
                current_node.bottom_border.color = PINK
            if current_node.right_border.color == YELLOW:
                current_node.right_border.color = PINK
            if current_node.left_border.color == YELLOW:
                current_node.left_border.color = PINK
                    
            for i in current_node.neighbors_connected:
                if i.explored == False:
                    i.parent = current_node
                    i.explored = True
                    queue.append((path_cost + 1 + self.manhattan_distance(i), path_cost + 1, i))
                    if i.matrix_pos_x == self.final_coordinate_x and i.matrix_pos_y == self.final_coordinate_y:
                        find = True
            self.render(background)
            if (slow):
                time.sleep(0.1)
            text(background, "SOLVING MAZE", WHITE, FONTSIZE_COMMANDS_INTIAL, 218, 620)
            player.render(background)
            pygame.display.update()
            
        current = self.maze[self.final_coordinate_x][self.final_coordinate_y]
        while (current.parent).parent != None:
            steps += 1
            current = current.parent
            current.color = ORANGE

            if current.top_border.color == PINK:
                current.top_border.color = ORANGE
            if current.bottom_border.color == PINK:
                current.bottom_border.color = ORANGE
            if current.right_border.color == PINK:
                current.right_border.color = ORANGE
            if current.left_border.color == PINK:
                current.left_border.color = ORANGE

            self.render(background)
            player.render(background)
            pygame.display.update()
        return (find, steps + 1)


class Game():
    def __init__(self):
        try:
            pygame.init()
        except:
            print('The pygame module did not start successfully')

        self.score_algorithms = ['bfs', 'dls', 'ucs', 'greedy', 'astar']
        self.no_score_algorithms = ['n_bfs', 'n_dfs', 'n_ucs', 'n_greedy', 'n_astar']
        self.current_algorithm_index = 0

        self.sizes = [50, 40, 30, 20]
        self.size_index = 0

        self.initial_coordinate_x = 0
        self.initial_coordinate_y = 0
        self.final_coordinate_x = 0
        self.final_coordinate_y = 0
        
        self.tempstart_x = 0
        self.tempstart_y = 0
        self.tempfinal_x = 0
        self.tempfinal_y = 0
        
        self.start = False
        self.solved = False
        self.winner = False
        self.exit = False
        self.aiwin = False
        self.total = 0
        self.isSlow = False
        self.activerefresh = False
    #here
    def end_of_game(self):
        if SCORE_MODE:
            current_algorithm = self.score_algorithms[self.current_algorithm_index]
        else:
            current_algorithm = self.no_score_algorithms[self.current_algorithm_index]
        # Call the algorithm
        (self.aiwin, self.total) = getattr(self.maze, current_algorithm)(self.background, self.player, self.isSlow)

    def update(self, event):
        if not self.solved and not self.winner:
            self.player.update(self.maze.maze, event, self.score_points)
        if self.player.matrix_pos_x == self.final_coordinate_x and self.player.matrix_pos_y == self.final_coordinate_y:
            self.winner = True

    def load(self):
        self.background = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption('Maze Game')
        self.initial_coordinate_x = random.randint(0, int(HEIGHT / SIZE) - 1)
        self.initial_coordinate_y = random.randint(0, int(WIDTH / SIZE) - 1)
        self.final_coordinate_x = random.randint(0, int(HEIGHT / SIZE) - 1)
        self.final_coordinate_y = random.randint(0, int(WIDTH / SIZE) - 1)
        while self.final_coordinate_x == self.initial_coordinate_x or self.final_coordinate_y == self.initial_coordinate_y:
            self.final_coordinate_x = random.randint(0, int(HEIGHT / SIZE) - 1)
            self.final_coordinate_y = random.randint(0, int(WIDTH / SIZE) - 1)
        self.maze = Maze(self.background, self.initial_coordinate_x, self.initial_coordinate_y, self.final_coordinate_x, self.final_coordinate_y)
        self.player = Player(self.initial_coordinate_x, self.initial_coordinate_y)
        self.score_points = self.maze.score_points
        
        if not self.activerefresh:
            self.tempstart_x = self.initial_coordinate_x
            self.tempstart_y = self.initial_coordinate_y
            self.tempfinal_x = self.final_coordinate_x
            self.tempfinal_y = self.final_coordinate_y

        

    def initial_game(self):
        self.background.fill(DARKBLUE)
        pygame.draw.rect(self.background, BEIGE, [40, 40, 530, 580])
        pygame.draw.rect(self.background, LIGHTBLUE, [40, 100, 530, 450])
        pygame.draw.rect(self.background, BLACK, [110, 150, 380, 350])
        pygame.draw.rect(self.background, DARKBLUE, [110, 150, 380, 100])

        text(self.background, "GROUP MEMBER", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL + 5, 650, 20)
        text(self.background, "Le Quang Dung - 21110761", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL + 5, 600, 60)
        text(self.background, "Pham Quang Duy - 21110760", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL + 5, 600, 90)
        text(self.background, "Vu Tien Trinh - 21110806", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL + 5, 600, 120)


        text(self.background, "MAZE ADVENTURES", LIGHTORANGE, FONTSIZE_START, 125, 185)
        text(self.background, "PRESS (ESC) TO CLOSE GAME", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL + 5, 150, 375)
        pygame.display.update()
        pygame.time.wait(180)

        text(self.background, "PRESS (S) TO START GAME", INTERMEDIARYORANGE, FONTSIZE_COMMANDS_INTIAL + 5, 160, 350)
        pygame.display.update()
        pygame.time.wait(180)



    def render(self):##############################################################################

        if SCORE_MODE:
            current_algorithm = self.score_algorithms[self.current_algorithm_index]
        else:
            current_algorithm = self.no_score_algorithms[self.current_algorithm_index]
        self.background.fill(BLACK)
        
        self.maze.render(self.background)

        self.player.render(self.background)

        pygame.draw.rect(self.background, GRAY, [600, 0, 300, 900])

        text(self.background, "GROUP MEMBER", WHITE, FONTSIZE_COMMANDS_INTIAL + 5, 660, 20)
        text(self.background, "Le Quang Dung - 21110761", WHITE, FONTSIZE_COMMANDS_INTIAL + 5, 610, 60)
        text(self.background, "Pham Quang Duy - 21110760", WHITE, FONTSIZE_COMMANDS_INTIAL + 5, 610, 90)
        text(self.background, "Vu Tien Trinh - 21110806", WHITE, FONTSIZE_COMMANDS_INTIAL + 5, 610, 120)

        pygame.draw.rect(self.background, DARKGRAY, [600, 150, 300, 5])

        if SCORE_MODE == True:
            text(self.background, "CURRENTLY CONSUMING STEPS", DARKBLUE, FONTSIZE_COMMANDS_INTIAL, 615, 165)
        else: 
            text(self.background, "CURRENTLY NOT CONSUMING STEPS", DARKBLUE, FONTSIZE_COMMANDS_INTIAL, 600, 165)
        
        text(self.background, f"ALGORITHM: {current_algorithm.upper()}", WHITE, FONTSIZE_COMMANDS_INTIAL, 670, 190)
        text(self.background, f"STEPS TAKEN: {self.total}",  DARKBLUE, FONTSIZE_COMMANDS_INTIAL , 675, 215)


        # Draw the button
        pygame.draw.rect(self.background, DARKBLUE, [650, 270, 95, 50])
        text(self.background, "SOLVE", WHITE, FONTSIZE_COMMANDS_INTIAL, 670, 285)

        pygame.draw.rect(self.background, DARKBLUE, [755, 270, 95, 50])
        if SIZE == 50:
            text(self.background, "EASY", WHITE, FONTSIZE_COMMANDS_INTIAL, 780, 285)
        elif SIZE == 40:
            text(self.background, "NORMAL", WHITE, FONTSIZE_COMMANDS_INTIAL, 765, 285)
        elif SIZE == 30:
            text(self.background, "HARD", WHITE, FONTSIZE_COMMANDS_INTIAL, 779, 285)
        elif SIZE == 20:
            text(self.background, ":))", WHITE, FONTSIZE_COMMANDS_INTIAL, 790, 285)

        pygame.draw.rect(self.background, INTERMEDIARYORANGE, [650, 330, 200, 50])
        text(self.background, "CHANGE ALGORITHM", DARKBLUE, FONTSIZE_COMMANDS_INTIAL, 655, 345)

        pygame.draw.rect(self.background, INTERMEDIARYORANGE, [650, 390, 200, 50])
        text(self.background, "TOGGLE SCORE MODE", DARKBLUE, FONTSIZE_COMMANDS_INTIAL, 655, 405)

        pygame.draw.rect(self.background, DARKBLUE, [650, 450, 95, 50])
        text(self.background, "REFRESH", WHITE, FONTSIZE_COMMANDS_INTIAL, 657, 465)

        pygame.draw.rect(self.background, DARKBLUE, [755, 450, 95, 50])
        text(self.background, "NEW", WHITE, FONTSIZE_COMMANDS_INTIAL, 782, 465)

        pygame.draw.rect(self.background, INTERMEDIARYORANGE, [650, 510, 200, 50])
        if self.isSlow:
            text(self.background, "SLOW MODE", DARKBLUE, FONTSIZE_COMMANDS_INTIAL, 700, 525)
        else: text(self.background, "FAST MODE", DARKBLUE, FONTSIZE_COMMANDS_INTIAL, 700, 525)




        if not self.solved:
            if not self.winner:
                pygame.draw.rect(self.background, RED, [0, 601, SIZE, SIZE])
                text(self.background, "- PLAYER", WHITE, FONTSIZE_MAZE, 0 + SIZE + 3, 601 + 6)
                pygame.draw.rect(self.background, BEIGE, [0, 601 + SIZE + 1, SIZE, SIZE])
                text(self.background, "- STARTING POINT", WHITE, FONTSIZE_MAZE, 0 + SIZE + 3, 601 + SIZE + 1 + 6)
                pygame.draw.rect(self.background, LIGHTBLUE, [0, 601 + 2 * SIZE + 2, SIZE, SIZE])
                text(self.background, "- GOAL", WHITE, FONTSIZE_MAZE, 0 + SIZE + 3, 601 + 2 * SIZE + 1 + 6)

                text(self.background, "PRESS (R) TO RETRY GAME", WHITE, FONTSIZE_MAZE, 220, 610)
                text(self.background, "PRESS (Q) TO GIVE UP", WHITE, FONTSIZE_MAZE, 230, 630)
                text(self.background, "PRESS (ESC) TO CLOSE GAME", WHITE, FONTSIZE_MAZE, 212, 650)

                if self.player.score <= 0:
                    pygame.draw.rect(self.background, BLACK, [220, 600, 300, 150])
                    text(self.background, "PLAYER RAN OUT OF STEPS", RED, FONTSIZE_MAZE + 3, 220, 610)
                    text(self.background, "PRESS (R) TO RETRY GAME", WHITE, FONTSIZE_MAZE, 220, 630)
                    text(self.background, "PRESS (ESC) TO CLOSE GAME", WHITE, FONTSIZE_MAZE, 212, 650)
            else:

                text(self.background, "PLAYER WIN", BLUE, FONTSIZE_MAZE + 3, 270, 610)
                text(self.background, "PRESS (R) TO RETRY GAME", WHITE, FONTSIZE_MAZE, 220, 630)
                text(self.background, "PRESS (ESC) TO CLOSE GAME", WHITE, FONTSIZE_MAZE, 212, 650)
        else:
            if not self.aiwin:
                pygame.draw.rect(self.background, BLACK, [220, 600, 300, 150])
                text(self.background, "AI RAN OUT OF STEPS", RED, FONTSIZE_MAZE + 3, 220, 610)
                text(self.background, "PRESS (R) TO RETRY GAME", WHITE, FONTSIZE_MAZE, 220, 630)
                text(self.background, "PRESS (ESC) TO CLOSE GAME", WHITE, FONTSIZE_MAZE, 212, 650) 
                      
            else:
                text(self.background, "AI WIN", YELLOW, FONTSIZE_MAZE + 3, 285, 610)
                text(self.background, "PRESS (R) TO RETRY GAME", WHITE, FONTSIZE_MAZE, 220, 630)
                text(self.background, "PRESS (ESC) TO CLOSE GAME", WHITE, FONTSIZE_MAZE, 212, 650)

        if SCORE_MODE:
            text(self.background, f"SCORE: {self.player.score}", WHITE, FONTSIZE_COMMANDS_INTIAL, 705, 240)  # Moved and changed font size
        pygame.display.update()

    def refresh_map(self):
        initial_start = (self.tempstart_x, self.tempstart_y)
        initial_goal = (self.tempfinal_x, self.tempfinal_y)
        initial_score_points = [(point.pos_x, point.pos_y, point.value, point.color) for point in self.score_points]

        self.solved = False
        self.winner = False
        self.total = 0
        self.maze = None
        self.player = None

        # Restore the maze to its initial state
        self.maze = copy.deepcopy(self.maze_copy)

        # Reset the player's starting point
        self.player = Player(self.tempstart_x, self.tempstart_y)
        self.player.matrix_pos_x, self.player.matrix_pos_y = initial_start

        # Reset the goal point
        self.final_coordinate_x, self.final_coordinate_y = initial_goal

        # Reset the score points
        for i, point in enumerate(self.score_points):
            point.pos_x, point.pos_y, point.value, point.color = initial_score_points[i]

        self.background.fill(BLACK)
        self.maze.render(self.background)


    def run(self):
        self.load()
        global SCORE_MODE
        global SIZE
        global NUM_SCORE_POINTS
        while not self.start:
            self.initial_game()
            pygame.display.update()
            if pygame.event.get(pygame.QUIT) or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit(0)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    self.start = True
        pygame.display.update()

        self.background.fill(BLACK)
        self.maze.dfs(self.background)
        self.maze_copy = copy.deepcopy(self.maze)

        while not self.exit:
            if pygame.event.get(pygame.QUIT) or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.exit = True
            e = pygame.event.get()
            if self.winner:
                self.background.fill(BLACK)
            for event in e:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.solved = False
                        self.winner = False
                        self.activerefresh = False
                        self.total = 0
                        self.run()
                    if not self.solved and event.key == pygame.K_q and not self.winner:
                        self.background.fill(BLACK)
                        self.end_of_game()
                        self.solved = True


                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()

                    if pygame.Rect(650, 270, 95, 50).collidepoint(x, y):  
                        if not self.solved and not self.winner: 
                            self.background.fill(BLACK)
                            self.end_of_game()
                            self.solved = True

                    elif pygame.Rect(755, 270, 95, 50).collidepoint(x, y): 
                        SIZE = self.sizes[self.size_index]
                        NUM_SCORE_POINTS = HEIGHT_TOTAL // SIZE // 2
                        self.size_index = (self.size_index + 1) % len(self.sizes)
                        self.solved = False
                        self.winner = False
                        self.activerefresh = False
                        self.total = 0
                        print(f"Current SIZE: {SIZE}, Current index: {self.size_index}")
                        self.run()

                    elif pygame.Rect(650, 330, 200, 50).collidepoint(x, y): 
                        self.current_algorithm_index = (self.current_algorithm_index + 1) % len(self.score_algorithms if SCORE_MODE else self.no_score_algorithms)
                        print(f"Current algorithm: {self.score_algorithms[self.current_algorithm_index] if SCORE_MODE else self.no_score_algorithms[self.current_algorithm_index]}")
                        self.activerefresh = True
                        self.refresh_map()

                    elif pygame.Rect(650, 390, 200, 50).collidepoint(x, y): 
                        SCORE_MODE = not SCORE_MODE

                    elif pygame.Rect(650, 450, 95, 50).collidepoint(x, y):   
                        self.activerefresh = True
                        self.refresh_map()         

                    elif pygame.Rect(755, 450, 95, 50).collidepoint(x, y): 
                        self.solved = False
                        self.winner = False
                        self.activerefresh = False
                        self.total = 0
                        self.run()

                    elif pygame.Rect(650, 510, 200, 50).collidepoint(x, y): 
                        self.isSlow = not self.isSlow

            self.update(e)
            self.render()

        pygame.quit()
        sys.exit(0)
        
def main():
    mygame = Game()
    mygame.run()

if __name__ == '__main__':
    main()