"""
*Tập luật            
Agent di chuyển trong ma trận.
Agent chỉ được đi:lên,xuống,trái,phải,hút
Không được đi ra ngoài ma trận.
Khi agent đi vào ô có giá trị 1 thì ô đó được làm sạch thành 0.
Nếu ma trận còn ô 1 thì tiếp tục di chuyển.
Nếu toàn bộ ma trận đều là 0 thì dừng.

*PEAS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
P – Performance
Làm sạch toàn bộ ma trận.
E – Environment
Ma trận gồm:
1 = bụi
0 = sạch
A – Actuators
Di chuyển lên, xuống, trái, phải, hút.
S – Sensors
Quan sát vị trí hiện tại và trạng thái các ô trong ma trận.

*Thuật toán:
function CLEANING-AGENT(percept) returns action

    persistent: rules

    state ← INTERPRET-INPUT(percept)

    rule ← RULE-MATCH(state, rules)

    action ← rule.ACTION

    return action
    
*Các rule:  
if ô hiện tại có bụi (1)
    action ← CLEAN

else if đi lên được
    action ← MOVE-UP

else if đi xuống được
    action ← MOVE-DOWN

else if đi trái được
    action ← MOVE-LEFT

else if đi phải được
    action ← MOVE-RIGHT

else
    action ← STOP
"""

import random
import copy

# Tạo ma trận 3x3 với các giá trị ngẫu nhiên 0 hoặc 1
matrix = [[random.randint(0, 1) for _ in range(3)] for _ in range(3)]

# Chọn ngẫu nhiên vị trí bắt đầu cho agent và đặt là sạch (0)
start_i = random.randint(0, 2)
start_j = random.randint(0, 2)
matrix[start_i][start_j] = 0

# Vị trí hiện tại của agent
current_i, current_j = start_i, start_j

# Hàm in ma trận
def print_matrix(mat):
    for row in mat:
        print(row)
    print()

# Các hướng di chuyển: lên, xuống, trái, phải
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

print("Ma trận ban đầu:")
print_matrix(matrix)

step = 0
while any(1 in row for row in matrix):  # Tiếp tục nếu còn 1
    # Lấy các hướng hợp lệ
    valid_moves = []
    for di, dj in directions:
        ni, nj = current_i + di, current_j + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            valid_moves.append((ni, nj))

    if not valid_moves:
        break  # Không có nước đi, nhưng không nên xảy ra

    # Chọn ngẫu nhiên một hướng
    next_i, next_j = random.choice(valid_moves)

    # Di chuyển agent đến vị trí mới
    current_i, current_j = next_i, next_j

    # Làm sạch ô đó (biến 1 thành 0)
    matrix[current_i][current_j] = 0

    step += 1
    print(f"Bước {step}: Agent di chuyển đến ({current_i}, {current_j})")
    print_matrix(matrix)

print("Hoàn thành! Ma trận đã được làm sạch.")