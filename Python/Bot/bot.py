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

        m=4
        x = self.game.field.width

        if len(goals) != 0:
            min = 9999999
            for goal_t in goals:
                [trace, cost] = self.a_star_search(player_position, goal_t)
                [trash, cost_other] = self.a_star_search(other_position, goal_t)

                is_weapon = self.game.field.is_weapon(goal_t)
                if is_weapon:
                    cost = cost + 7
                    if has_weapon:
                        cost = cost + 1000

                path = []
                traverse_t = goal_t
                while traverse_t != player_position:
                    path.append(traverse_t)
                    traverse_t = trace[traverse_t]
                path.append(player_position)

                # If there are bugs on the trace, cost increases
                any_bug = False
                if len(bugs) != 0:
                    for bug in bugs:
                        if bug in trace:
                            [bug_t, bug_c] = self.a_star_search(player_position,bug)
                            any_bug = True
                            if has_weapon:
                                cost = cost + 8
                            else:
                                if (40-bug_c*1.5) > 0:
                                    cost = cost + (40 - bug_c*1.5)
                                else:
                                    cost = cost
                            break

                    if not any_bug:
                        if len(path) <= 5:
                            cost = cost - 40

                else:
                    if len(path) <= 5:
                        cost = cost - 40

                # If other player in your path, act as follows, bigger cost means likely take another path
                if other_position in path:
                    if has_weapon:
                        if other_code > code and code + 4 > other_code:
                            cost = cost - 10
                        else:
                            cost = cost - 25

                    elif other_has_weapon:
                        [o_t, o_c] = self.a_star_search(player_position,other_position)
                        if (40-1.5*o_c > 0):
                            cost = cost + (40 - o_c*1.5)
                        else:
                            cost = cost

                    if cost_other <= cost:
                        cost = cost + 90


                if cost_other <= cost:
                    cost = cost + 45

                # If there are many codes in some area, prioritize going that zone
                attraction = self.game.field.attraction_count(m,goal_t)
                multiplier = math.floor(attraction * (x - (x / m)))
                cost = cost - multiplier

                if cost <= min:
                    min = cost
                    goal = goal_t
                    self.trace = trace


            [kill_trace, cost_k] = self.a_star_search(player_position, other_position)
            if has_weapon and not other_has_weapon:
                if cost_k <= 4 and min > 5:
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
                                    new_cost = cost_so_far[current] + 5
                                else:
                                    if (60-heuristic(start,bug)*1.5 > 5):
                                        new_cost = cost_so_far[current] + (60 - heuristic(start,bug)*1.5)
                                    else:
                                        new_cost = cost_so_far[current] + 5
                                break

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