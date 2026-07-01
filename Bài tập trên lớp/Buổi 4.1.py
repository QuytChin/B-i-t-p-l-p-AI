import random

# Bước 1: Khai báo ma trận ban đầu và ma trận đích
mt = [[1,5,3],
      [7,0,6],
      [4,2,8]]

goal = [[1,2,3],
        [4,5,6],
        [7,8,0]]


# Bước 2: Hàm in ma trận
def print_matrix(mt):
    for row in mt:
        print(row)
    print()


# Bước 3: Kiểm tra đạt đích chưa
def is_goal(mt):
    return mt == goal


# Bước 4: Tìm vị trí số 0
def find_zero(mt):
    for i in range(3):
        for j in range(3):
            if mt[i][j] == 0:
                return i, j


# Bước 5: Hàm đổi chỗ
def swap(mt, x1, y1, x2, y2):
    new_mt = [row[:] for row in mt]

    new_mt[x1][y1], new_mt[x2][y2] = \
    new_mt[x2][y2], new_mt[x1][y1]

    return new_mt


# Bước 6: Các hướng di chuyển
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


# Bước 7: Lưu trạng thái đã đi
visited = set()

visited.add(tuple(tuple(row) for row in mt))


# Bước 8: In ma trận ban đầu
print("Bước 0:")
print_matrix(mt)


# Bước 9: Cho chạy tối đa 10 bước
step = 0

while step < 10 and not is_goal(mt):

    moves = []

    # Sinh các trạng thái mới
    for move in [move_up, move_down,
                 move_left, move_right]:

        new_mt = move(mt)

        if new_mt is not None:

            state = tuple(tuple(row) for row in new_mt)

            # Nếu trạng thái đã tồn tại
            if state in visited:

                print("Không được đi vì quay lại trạng thái cũ:")
                print_matrix(new_mt)

            else:
                moves.append(new_mt)

    # Nếu không còn đường đi
    if not moves:
        break

    # Chọn random 1 trạng thái
    mt = random.choice(moves)

    visited.add(tuple(tuple(row) for row in mt))

    step += 1

    print("Bước", step)
    print_matrix(mt)