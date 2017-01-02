import random
import sys
import heapq
import operator
import math

direction = {(-1, 0): "up",
             (0, 1): "right",
             (1, 0): "down",
             (0, -1): "left"}


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Bot:

    def __init__(self):
        self.game = None
        self.path_stack = Stack()
        self.goal = None
        self.trace = []
        self.path = []

    def setup(self, game):
        self.game = game

    def do_turn(self):
        self.search()

        if self.path_stack.size() == 0:
            self.game.issue_order_pass()
        elif self.game.my_player().is_paralyzed:
            self.game.issue_order_pass()
        else:
            move = self.path_stack.pop()
            (_, chosen) = move
            self.game.issue_order(chosen)


    ## Added changes
    def search(self):
        goals = self.game.field.get_goals()
        bugs = self.game.field.get_bugs()
        other_position = self.other_player_position()
        player_position = self.player_position()

        if len(goals) != 0:
            min = 1000
            for goal_t in goals:
                [trace, cost] = self.a_star_search(player_position, goal_t)
                try:
                    attraction = self.game.field.attraction_count(goal_t)
                    int(math.floor(attraction*2.5))
                    cost = cost - attraction * 2.5
                except:
                    cost = cost

                    if len(bugs) != 0:
                        for bug in bugs:
                            if bug in trace:
                                cost = cost + 3
                                break

                    if other_position in trace:
                       cost = cost + 2

                if cost <= min:
                    min = cost
                    goal = goal_t
                    self.trace = trace


            self.goal = goal
            self.path_stack.items = []
            self.path = []

            path = []
            traverse = goal
            while traverse != player_position:
                prev = traverse
                traverse = self.trace[traverse]
                move = tuple(map(operator.sub, prev, traverse))
                path.append(traverse)
                self.path_stack.push((move, direction[move]))

            path.reverse()
            self.path = path

    def player_position(self):
        pos_x = self.game.my_player().row
        pos_y = self.game.my_player().col
        return (pos_x, pos_y)

    def other_player_position(self):
        other = self.game.players[self.game.other_botid]
        pos_x = other.row
        pos_y = other.col
        return (pos_x, pos_y)

    def a_star_search(self, start, goal):
        board = self.game.field
        bugs = self.game.field.get_bugs()
        other_pos = self.other_player_position()
        has_weapon = self.game.my_player().has_weapon
        other_has_weapon = self.game.players[self.game.other_botid].has_weapon
        other_code = self.game.players[self.game.other_botid].snippets
        code = self.game.my_player().snippets

        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            moves = board.legal_moves(current)

            for next_move in moves:
                next = tuple(map(operator.add, next_move[0], current))

                if len(bugs) != 0:
                    for bug in bugs:
                        if next == bug:
                            if has_weapon:
                                new_cost = cost_so_far[current] + 2
                            else:
                                new_cost = cost_so_far[current] + 10
                            break
                        else:
                            new_cost = cost_so_far[current] + 1
                else:
                    new_cost = cost_so_far[current] + 1

                if next == other_pos:
                    if has_weapon:
                        if other_code > code:
                            new_cost = cost_so_far[current] - 8
                        else:
                            new_cost = cost_so_far[current] - 1
                    elif other_has_weapon:
                        new_cost = cost_so_far[current] + 10
                    else:
                        new_cost = cost_so_far[current] + 2


                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(next, goal)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far[goal]


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)