"""ma trận cho 0 chạy random theo các hướng nhưng không đi lại vị trí đã đi qua, nếu đạt đích thì dừng, nếu không đạt đích sau 10 bước thì dừng"""
"""Luật :
Nếu 0 không ở biên trên → được đi lên.
Nếu 0 không ở biên dưới → được đi xuống.
Nếu 0 không ở biên trái → được đi trái.
Nếu 0 không ở biên phải → được đi phải.
Không đi lại trạng thái đã xuất hiện trong visited.
Nếu đạt ma trận đích → dừng.
Nếu đi đủ 10 bước mà chưa đạt đích → dừng.
PEAS:
P – Performance
Đưa ma trận về trạng thái đích trong ≤ 10 bước.
E – Environment
Ma trận 3×3 của trò chơi 8-puzzle.
A – Actuators
Di chuyển 0 lên, xuống, trái, phải.
S – Sensors
Quan sát vị trí 0 và trạng thái ma trận
Thuật toán:
B1: Kiểm tra nếu ma trận hiện tại là ma trận đích thì dừng.

B2: Sinh các trạng thái mới bằng cách di chuyển số 0 theo 4 hướng
    nhưng không được trùng trạng thái đã đi.

B3: Chọn ngẫu nhiên một trạng thái mới và cập nhật ma trận hiện tại.

B4: Lặp lại cho đến khi đạt đích hoặc đủ 10 bước thì dừng.
    """
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