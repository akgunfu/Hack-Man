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
        self.futile_p = (9,10)
        self.trace = []
        self.path = []
        self.danger = False

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

        m = 2
        x = self.game.field.width

        if len(goals) != 0:
            min = 9999999
            goal_count = len(goals)
            futile_count = 0
            self.danger = False
            for goal_t in goals:
                [trace, cost_player] = self.a_star_search(player_position, goal_t)
                [trash, cost_other] = self.a_star_search(other_position, goal_t)

                cost = cost_player + cost_other*1.25

                if cost_player >= cost_other:
                    if cost_player == cost_other:
                        if other_has_weapon or not has_weapon:
                            cost = cost + 100
                            futile_count = futile_count + 1
                    else:
                        cost = cost + 100
                        futile_count = futile_count + 1

                is_weapon = self.game.field.is_weapon(goal_t)
                if is_weapon:
                    cost = cost + 6
                    if has_weapon:
                        cost = cost + 1000

                attraction = self.game.field.attraction_count(m,goal_t)
                multiplier = math.floor(attraction * (x - (x / m)))
                if multiplier > 15:
                    multiplier = 15
                cost = cost - multiplier

                if cost <= min:
                    min = cost
                    self.goal = goal_t
                    self.trace = trace

            if futile_count == goal_count or min > 100:
                [m_trace, m_cost] = self.a_star_search(player_position, self.futile_p)
                self.trace = m_trace
                self.goal = self.futile_p

            elif futile_count == 0 and heuristic(player_position, other_position) < 3:
                [kill_trace, cost_k] = self.a_star_search(player_position, other_position)
                if has_weapon and not other_has_weapon:
                    if cost_k <= 3:
                        self.goal = other_position
                        self.trace = kill_trace

        else:

            if player_position != self.futile_p:
                [m_trace, m_cost] = self.a_star_search(player_position, self.futile_p)
                self.trace = m_trace
                self.goal = self.futile_p

            else:
                [t1, c1] = self.a_star_search(player_position, (9,7))
                [t2, c2] = self.a_star_search(player_position, (9,12))

                if c1 == c2:
                    self.goal = self.futile_p

                else:
                    if c1 > c2:
                        self.goal = (9,12)
                        self.trace = t2
                    else:
                        self.goal = (9,7)
                        self.trace = t1


        path = []
        traverse = self.goal
        while traverse != player_position:
            path.append(traverse)
            prev = traverse
            traverse = self.trace[traverse]
            move = tuple(map(operator.sub, prev, traverse))
            self.path_stack.push((move, direction[move]))

        path.append(player_position)
        path.reverse()

        new_trace = []
        for p in path:
            if p != player_position:
                mo_p = self.game.field.legal_moves(p)
                for mo in mo_p:
                    new_p = tuple(map(operator.add, mo[0], p))
                    if not new_p in path:
                        new_trace.append(new_p)

        for nt in new_trace:
            path.append(nt)

        if len(bugs) != 0:
            for bug in bugs:
                if bug in path:
                    [b_t, b_c] = self.a_star_search(player_position, bug)
                    if b_c <= 2:
                        self.danger = True

        if other_position in path:
            if other_has_weapon:
                [ot_t, ot_c] = self.a_star_search(player_position, other_position)
                if ot_c <= 2:
                    self.danger = True


        if self.danger:
            back_move = tuple(map(operator.sub, player_position, path[1]))
            next_p = tuple(map(operator.add, back_move, player_position))
            if self.game.field.is_legal(next_p):
                self.path_stack.push((back_move, direction[back_move]))
            else:
                self.path_stack.push(((0, 0), "pass"))



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