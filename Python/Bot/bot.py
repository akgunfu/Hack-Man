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
        self.futile_p = None
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

    ## TODO Bug evasion

    def search(self):
        goals = self.game.field.get_goals()
        player_position = self.player_position()
        other_position = self.other_player_position()
        bugs = self.game.field.get_bugs()
        has_weapon=self.game.my_player().has_weapon
        other_has_weapon = self.game.players[self.game.other_botid].has_weapon
        other_code = self.game.players[self.game.other_botid].snippets
        code = self.game.my_player().snippets

        m = 3
        x = self.game.field.width

        if len(goals) != 0:
            min = 9999999
            goal_count = len(goals)
            futile_count = 0
            for goal_t in goals:
                [trace, cost_player] = self.a_star_search(player_position, goal_t)
                [trash, cost_other] = self.a_star_search(other_position, goal_t)

                cost = 0.75*cost_player + cost_other

                if cost_player >= cost_other:
                    cost = cost + 100
                    futile_count = futile_count + 1

                is_weapon = self.game.field.is_weapon(goal_t)
                if is_weapon:
                    cost = cost + 5
                    if has_weapon:
                        cost = cost + 1000

                attraction = self.game.field.attraction_count(m,goal_t)
                multiplier = math.floor(attraction * (x - (x / m)))
                if multiplier > 10:
                    multiplier = 10
                cost = cost - multiplier

                if cost <= min:
                    min = cost
                    goal = goal_t
                    self.trace = trace


            if futile_count == goal_count or min > 100:

                if self.futile_p is None:
                    midpoint = (9,10)
                else:
                    if self.futile_p == (9, 10):
                        midpoint = (5,10)
                    else:
                        midpoint = (9,10)

                [m_trace, m_cost] = self.a_star_search(player_position,midpoint)
                self.trace = m_trace
                self.futile_p = midpoint
                goal = midpoint

            elif futile_count == 0:
                [kill_trace, cost_k] = self.a_star_search(player_position, other_position)
                if has_weapon and not other_has_weapon:
                    if cost_k <= 3:
                        goal = other_position
                        self.trace = kill_trace

            self.goal = goal
            self.path_stack.items = []

            traverse = self.goal
            while traverse != player_position:
                prev = traverse
                traverse = self.trace[traverse]
                move = tuple(map(operator.sub, prev, traverse))
                self.path_stack.push((move, direction[move]))


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
        has_weapon = self.game.my_player().has_weapon
        other_has_weapon = self.game.players[self.game.other_botid].has_weapon
        other_position = self.other_player_position()
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        cost_so_far[goal] = 10000

        is_bug = False
        if goal in bugs:
            is_bug = True

        is_other = False
        if goal == other_position:
            is_other = True

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            moves = board.legal_moves(current)
            for next_move in moves:
                next = tuple(map(operator.add, next_move[0], current))
                new_cost = cost_so_far[current] + 1

                if not is_bug:
                    if len(bugs) != 0:
                        for bug in bugs:
                            if next == bug:
                                if has_weapon:
                                    new_cost = cost_so_far[current] + 2
                                else:
                                    if (35-heuristic(start,bug) > 2):
                                        new_cost = cost_so_far[current] + (35 - heuristic(start,bug))
                                    else:
                                        new_cost = cost_so_far[current] + 2
                                break

                if not is_other:
                    if next == other_position:
                        if has_weapon:
                            new_cost = cost_so_far[current] + 1
                        elif other_has_weapon:
                            if (35 - heuristic(start, other_position) > 2):
                                new_cost = cost_so_far[current] + (35 - heuristic(start, other_position))
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