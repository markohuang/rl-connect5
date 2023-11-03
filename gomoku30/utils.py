import copy

def mapping(board):  # Deprecated
    # piece_map is a dictionary with two keys 'o' and 'x'.
    # the value of each key holds a list of tuples containing
    # all piece positions of the key's type.
    piece_map = {'o': [], 'x': []}
    for i in range(len(board)):
        for j in range(len(board)):
            col = board[i][j]
            if col != ' ':
                piece_map[col].append((i, j))
    return piece_map


def blank_score(board):
    # score is a dictionary with all the board positions and their corresponding values
    score = {}
    for i in range(len(board)):
        for j in range(len(board)):
            score[(i, j)] = 0
    return score


def find_best_square(score):
    # returns the square with the highest evaluated score
    max_score = max(list(score.values()))
    for square in score:
        if score[square] == max_score:
            return square


def unpack_positions(position):
    # helper function for get_forced_plays_available
    pos1, pos2 = position
    dy, dx = (b - a for a, b in zip(pos1, pos2))
    if dy == 0:
        group = [(pos1[0], x + pos1[1]) for x in range(5)]
    elif dx == 0:
        group = [(y + pos1[0], pos1[1]) for y in range(5)]
    elif dx < 0:
        group = [(xy + pos1[0], pos1[1] - xy) for xy in range(5)]
    else:
        group = [(xy + pos1[0], xy + pos1[1]) for xy in range(5)]
    # e.g. ((1, 6) <-start, (5, 2) <- end) -->
    # group = [(1, 6), (2, 5), (3, 4), (4, 3), (5, 2)] <- expands into all positions
    #      ((3, 2), (3, 7)) -->
    # group = [(3, 2), (3, 3), (3, 4), (3, 5), (3, 6)]
    return group


class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0


def check_open_positions(board):
    # open is a dictionary with two keys 'o' and 'x'.
    # it contains information of all the open twos, threes, and fours on the board
    # by looking at all consecutive 5-in-a-row sequences on the board
    #
    # *0|1|2|3|4|5|6|7*
    # 0 | | | | | | | *
    # 1 |o| | | | | | *
    # 2 | |o| | | | | *
    # 3 | | |o| | | | *
    # 4 | | | | | | | *
    # 5 | | | | | | | *
    # 6 | | | | | | | *
    # 7 | | | | | | | *
    # *****************
    # open = {
    # 2: {'o': [((2, 2), (6, 6))], 'x': []},
    # 3: {'o': [((0, 0), (4, 4)), ((1, 1), (5, 5))], 'x': []},
    # 4: {'o': [], 'x': []}
    # }
    #
    # The first tuple is the starting position of the open position
    # and the second tuple is the end position

    open = {1: {'o': [], 'x': []}, 2: {'o': [], 'x': []},
            3: {'o': [], 'x': []}, 4: {'o': [], 'x': []}, 5: {'o': [], 'x': []}}
    for col in ['o', 'x']:
        for i in range(len(board)):
            for j in range(len(board)):
                for dy, dx in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    if i+4*dy not in range(len(board)) or j+4*dx not in range(len(board)):
                        continue
                    num_of_col = 0
                    valid = True
                    for count in range(5):
                        if board[i+dy*count][j+dx*count] == 'ox'.replace(col, ''):
                            valid = False
                            break
                        if board[i + dy * count][j + dx * count] == col:
                            num_of_col += 1
                    if num_of_col > 0 and valid:
                        end_pos = (i + 4 * dy, j + 4 * dx)  # end tuple of the free position
                        open[num_of_col][col].append(((i, j), end_pos))
    return open


def get_plays_available(board, positions):
    # helper function for forced_play
    # returns a list of tuples -
    # the first element of each tuple is a possible force play position
    # the second element of each tuple is a possible responsive play position
    # e.g. | |o|o|o| | --> |o|o|o|o|x| or |x|o|o|o|o|
    # 这个情况下possible_plays应该是x和o的位置，方便forced play放到板子上
    possible_plays = []
    free_moves = []
    for position in positions:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
                free_moves.append(square)
        possible_plays.extend([tuple(plays), tuple(plays[::-1])])
    return possible_plays, set(free_moves)


def forced_play(original_board, col):
    # returns a list containing the winning combination of moves (if there are any)
    # else returns False
    board = copy.deepcopy(original_board)
    open = check_open_positions(board)
    opp = 'ox'.replace(col, '')
    possible_plays, _ = get_plays_available(board, open[3][col])
    q = Queue()
    visited = [board]
    for play in possible_plays:
        pos1, pos2 = play
        next_board = copy.deepcopy(board)
        y1, x1 = pos1
        y2, x2 = pos2
        next_board[y1][x1] = col
        next_board[y2][x2] = opp
        open = check_open_positions(next_board)
        if open[4][opp] or open[5][opp]:
            continue
        q.push([(next_board, play)])
        visited += [next_board]
    while not q.isEmpty():
        state = q.pop()
        board = state[-1][0]
        open = check_open_positions(board)
        if open[4][col]:  # this is a winning forced playing position
            # print_board(board)
            # print('winning entry:', open[4][col])
            winning_play = []
            for item in state:
                play = item[1][0]
                winning_play.append(play)
            str = 'mate in {}'.format(len(winning_play))
            print(str)
            return winning_play
        possible_plays, _ = get_plays_available(board, open[3][col])
        for play in possible_plays:
            pos1, pos2 = play
            next_board = copy.deepcopy(board)
            y1, x1 = pos1
            y2, x2 = pos2
            next_board[y1][x1] = col
            next_board[y2][x2] = opp
            open = check_open_positions(next_board)
            if open[4][opp] or open[5][opp]:
                continue
            if next_board not in visited:
                path = state + [(next_board, play)]
                q.push(path)
                visited += [next_board]
    return False


# 这个function也是模仿你当时写的给板上每个格子算个分
def get_score(board, col, score):
    opp = 'ox'.replace(col, '')
    open = check_open_positions(board)
    for position in open[1][col]:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
        for play in plays:
            score[play] += 5
    for position in open[2][col]:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
        for play in plays:
            score[play] += 25
    for position in open[3][col]:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
        for play in plays:
            score[play] += 125

    for position in open[1][opp]:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
        for play in plays:
            score[play] += 4
    for position in open[2][opp]:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
        for play in plays:
            score[play] += 16
    for position in open[3][opp]:
        group = unpack_positions(position)
        plays = []
        for square in group:
            y, x = square
            if board[y][x] == ' ':
                plays.append(square)
        for play in plays:
            score[play] += 64
    return score