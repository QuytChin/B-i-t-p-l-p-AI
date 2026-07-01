"""ma trận cho 0 chạy random theo các hướng nhưng không đi lại vị trí đã đi qua, nếu đạt đích thì dừng, nếu không đạt đích sau 10 bước thì dừng"""
mt = [[1,5,3],
      [7,0,6],
      [4,2,8]]

goal = [[1,2,3],
        [4,5,6],
        [7,8,0]]


# Kiểm tra ma trận đích
def is_matrix_kq(mt):
    return mt == goal


# Tìm vị trí số 0
def find_zero(mt):
    for i in range(3):
        for j in range(3):
            if mt[i][j] == 0:
                return i, j


# In ma trận
def print_matrix(mt):
    for row in mt:
        print(row)
    print()


# Hàm đổi chỗ
def swap(mt, x1, y1, x2, y2):
    new_mt = [row[:] for row in mt]
    new_mt[x1][y1], new_mt[x2][y2] = new_mt[x2][y2], new_mt[x1][y1]
    return new_mt


# Các hướng di chuyển
def move_up(mt):
    i, j = find_zero(mt)
    if i > 0:
        return swap(mt, i, j, i-1, j)
    return None


def move_down(mt):
    i, j = find_zero(mt)
    if i < 2:
        return swap(mt, i, j, i+1, j)
    return None


def move_left(mt):
    i, j = find_zero(mt)
    if j > 0:
        return swap(mt, i, j, i, j-1)
    return None


def move_right(mt):
    i, j = find_zero(mt)
    if j < 2:
        return swap(mt, i, j, i, j+1)
    return None


# Đếm khoảng cách Manhattan
def manhattan_distance(mt):
    distance = 0
    goal_positions = {goal[i][j]: (i, j) for i in range(3) for j in range(3)}
    for i in range(3):
        for j in range(3):
            if mt[i][j] != 0:
                gi, gj = goal_positions[mt[i][j]]
                distance += abs(i - gi) + abs(j - gj)
    return distance


# Thuật toán hill climbing với visited
import random

visited = set()
visited.add(tuple(tuple(row) for row in mt))

print("Bước 0: Ma trận ban đầu")
print_matrix(mt)

step = 0
while not is_matrix_kq(mt) and step < 10:
    moves = []
    for move in [move_up, move_down, move_left, move_right]:
        new_mt = move(mt)
        if new_mt is not None:
            state = tuple(tuple(row) for row in new_mt)
            if state not in visited:
                moves.append(new_mt)
    # Chọn ngẫu nhiên một nước đi
    if moves:
        mt = random.choice(moves)
        visited.add(tuple(tuple(row) for row in mt))
        step += 1
        print(f"Bước {step}:")
        print_matrix(mt)
    else:
        break  # Không có nước đi nào mới

if is_matrix_kq(mt):
    print("Đã đạt ma trận đích!")
else:
    print("Không đạt ma trận đích sau 10 bước.")