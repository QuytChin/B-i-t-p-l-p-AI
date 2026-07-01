import random

# Tạo ma trận 3x3 với giá trị 0 hoặc 1 ngẫu nhiên
# 1 = có bụi, 0 = sạch

def create_random_matrix(size=3):
    return [[random.choice([0, 1]) for _ in range(size)] for _ in range(size)]


# Chọn lệnh di chuyển ngẫu nhiên từ vị trí hiện tại
def get_action(pos, matrix):
    r, c = pos
    moves = []
    if r > 0:
        moves.append("UP")
    if r < len(matrix) - 1:
        moves.append("DOWN")
    if c > 0:
        moves.append("LEFT")
    if c < len(matrix) - 1:
        moves.append("RIGHT")
    return random.choice(moves)


# Thực hiện hành động di chuyển tới ô khác
def apply_action(pos, action, matrix):
    r, c = pos
    if action == "UP":
        return (r - 1, c)
    if action == "DOWN":
        return (r + 1, c)
    if action == "LEFT":
        return (r, c - 1)
    if action == "RIGHT":
        return (r, c + 1)
    return pos


# In ma trận và đánh dấu vị trí robot bằng chữ V phía trước giá trị
def print_matrix(matrix, pos):
    for r, row in enumerate(matrix):
        print(" ".join("V" + str(v) if (r, c) == pos else str(v) for c, v in enumerate(row)))
    print()


# Chạy robot hút bụi đến khi tất cả các ô sạch
def run_vacuum():
    matrix = create_random_matrix(3)
    pos = (random.randrange(3), random.randrange(3))
    print("Ma trận ban đầu:")
    print_matrix(matrix, pos)

    step = 0
    while True:
        step += 1
        if matrix[pos[0]][pos[1]] == 1:
            action = "SUCK"
            matrix[pos[0]][pos[1]] = 0
        else:
            action = get_action(pos, matrix)
            pos = apply_action(pos, action, matrix)
        print(f"Bước {step}: {pos} -> {action}")
        print_matrix(matrix, pos)
        if all(cell == 0 for row in matrix for cell in row):
            print("Đã sạch hết.")
            return

if __name__ == "__main__":
    run_vacuum()
