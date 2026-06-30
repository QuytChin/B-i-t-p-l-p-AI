'''
Đầu tiên chạy chương trình ra giao diện game sau đó bấm xáo trộn để tạo ra một trạng thái ngẫu nhiên. 
Sau đó chọn một trong các thuật toán (BFS, DFS, UCS, IDS) để giải đố.
BFS có 2 cách giải, DFS có 2 cách giải, và UCS là thuật toán tìm kiếm chi phí đồng nhất.
'''
from collections import deque
import heapq
import math
import random
import time
import tkinter as tk
from tkinter import messagebox, ttk
from copy import deepcopy

# ==================== CẤU HÌNH ====================
INITIAL_STATE = [[1, 2, 3],
                 [4, 0, 6],
                 [7, 5, 8]]

GOAL_STATE = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 0]]


# ==================== CÁC HÀM CƠ BẢN ====================
def print_matrix(mt):
    """In ma trận"""
    for row in mt:
        print(row)
    print()


def is_goal(mt):
    """Kiểm tra đạt đích chưa"""
    return mt == GOAL_STATE


def find_zero(mt):
    """Tìm vị trí số 0"""
    for i in range(3):
        for j in range(3):
            if mt[i][j] == 0:
                return i, j
    return None


def swap(mt, x1, y1, x2, y2):
    """Hàm đổi chỗ"""
    new_mt = [row[:] for row in mt]
    new_mt[x1][y1], new_mt[x2][y2] = new_mt[x2][y2], new_mt[x1][y1]
    return new_mt


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


def matrix_to_tuple(mt):
    """Chuyển ma trận thành tuple"""
    return tuple(tuple(row) for row in mt)


def get_neighbors(mt):
    """Lấy tất cả trạng thái kế tiếp"""
    neighbors = []
    for move in [move_up, move_down, move_left, move_right]:
        new_mt = move(mt)
        if new_mt is not None:
            neighbors.append(new_mt)
    return neighbors


FAILURE = "FAILURE"
CUTOFF = "CUTOFF"


class AndOrGraphProblem:
    """Bài toán AND-OR cho 8-puzzle xác định.

    Trong 8-puzzle chuẩn, mỗi hành động chỉ sinh đúng một kết quả. Vì vậy
    nút AND vẫn được vẽ theo đúng mẫu AND-OR, nhưng chỉ có một trạng thái con.
    Cấu trúc này giúp giao diện thể hiện đúng: OR chọn hành động, AND kiểm tra
    toàn bộ kết quả của hành động đó.
    """

    def __init__(self, initial_state):
        self.initial_state = matrix_to_tuple(initial_state)

    @staticmethod
    def _to_matrix(state):
        return [list(row) for row in state]

    def goal_test(self, state):
        return is_goal(self._to_matrix(state))

    def actions(self, state):
        matrix = self._to_matrix(state)
        candidates = []
        for name, func in (("U", move_up), ("D", move_down), ("L", move_left), ("R", move_right)):
            nxt = func(matrix)
            if nxt is not None:
                # Ưu tiên trạng thái gần đích để tránh duyệt sâu không cần thiết.
                candidates.append((misplaced_tiles(nxt), name))
        candidates.sort(key=lambda item: item[0])
        return [name for _, name in candidates]

    def results(self, state, action):
        matrix = self._to_matrix(state)
        move_map = {"U": move_up, "D": move_down, "L": move_left, "R": move_right}
        nxt = move_map[action](matrix)
        return [matrix_to_tuple(nxt)] if nxt is not None else []


def _and_or_or_search(state, problem, path, depth_left, stats):
    stats['goal_checks'] += 1
    if problem.goal_test(state):
        return {"type": "GOAL", "state": state}
    if state in path:
        stats['cycles_avoided'] += 1
        return FAILURE
    if depth_left == 0:
        return CUTOFF

    stats['nodes_expanded'] += 1
    actions = problem.actions(state)
    stats['frontier_max'] = max(stats['frontier_max'], len(actions))

    saw_cutoff = False
    for action in actions:
        stats['actions_tried'] += 1
        result_states = problem.results(state, action)
        stats['nodes_created'] += len(result_states)
        plan = _and_or_and_search(result_states, problem, path + [state], depth_left - 1, stats)
        if plan == CUTOFF:
            saw_cutoff = True
        elif plan != FAILURE:
            return {
                "type": "OR",
                "state": state,
                "action": action,
                "and": plan,
            }
    return CUTOFF if saw_cutoff else FAILURE


def _and_or_and_search(states, problem, path, depth_left, stats):
    outcomes = []
    saw_cutoff = False
    for state in states:
        child = _and_or_or_search(state, problem, path, depth_left, stats)
        if child == FAILURE:
            return FAILURE
        if child == CUTOFF:
            saw_cutoff = True
        outcomes.append({"state": state, "plan": child})
    if saw_cutoff:
        return CUTOFF
    return {"type": "AND", "outcomes": outcomes}


def AND_OR_GRAPH_SEARCH(problem, max_depth=40, stats=None):
    """Tìm kiếm AND-OR theo độ sâu tăng dần để tránh mắc kẹt ở nhánh dài."""
    if stats is None:
        stats = {}
    for depth in range(max_depth + 1):
        stats['iterations'] = depth + 1
        result = _and_or_or_search(problem.initial_state, problem, [], depth, stats)
        if result not in (FAILURE, CUTOFF):
            stats['depth_found'] = depth
            return result
        if result == FAILURE:
            return FAILURE
    return FAILURE


def and_or_graph_search_solver(start_state):
    """Trả về cây kế hoạch AND-OR và thống kê thực tế để hiển thị."""
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'solution_costs': [],
        'attempted_steps': 0,
        'goal_checks': 0,
        'actions_tried': 0,
        'cycles_avoided': 0,
        'iterations': 0,
        'depth_found': 0,
    }
    problem = AndOrGraphProblem(start_state)
    plan = AND_OR_GRAPH_SEARCH(problem, max_depth=40, stats=stats)
    stats['attempted_steps'] = stats.get('depth_found', 0)
    return plan, stats

def csp_backtracking_search(start_state, initial_domains=None, initial_logs=None, initial_stats=None):
    """Thuật toán CSP Backtracking theo mô hình điền số vào từng ô 3x3."""
    stats = initial_stats if initial_stats is not None else {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'goal_checks': 0,
        'constraint_violations': 0,
        'backtracks': 0,
        'csp_log': [],
        'solution_costs': [],
    }
    if initial_logs:
        stats['csp_log'].extend(initial_logs)

    variables = [(r, c) for r in range(3) for c in range(3)]
    domain_values = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    target_values = [1, 2, 3, 4, 5, 6, 7, 8, 0]

    domains = {}
    if initial_domains is not None:
        domains = {var: list(initial_domains.get(var, domain_values[:])) for var in variables}
    else:
        domains = {var: domain_values[:] for var in variables}

    assignment = {}

    def var_name(var_idx):
        return f"x{var_idx + 1}"

    def state_label(assignment_map):
        board = [[0 for _ in range(3)] for _ in range(3)]
        for (r, c), value in assignment_map.items():
            board[r][c] = value
        return "\n".join(" | ".join(str(v) for v in row) for row in board)

    def select_unassigned_variable(assign):
        for idx, var in enumerate(variables):
            if var not in assign:
                return idx, var
        return None, None

    def order_domain_values(var, assign):
        """Chọn giá trị từ miền đã được lọc trước đó để thử và quay lui."""
        used = set(assign.values())
        values = [value for value in domains[var] if value not in used]
        random.shuffle(values)
        return values

    def consistent(var, value, assign):
        idx = variables.index(var)
        expected = target_values[idx]

        if value in assign.values():
            stats['constraint_violations'] += 1
            stats['csp_log'].append(
                f"[RÀNG BUỘC] {var_name(idx)} = {value} bị từ chối vì số này đã được dùng ở ô khác."
            )
            return False

        if value != expected:
            stats['constraint_violations'] += 1
            stats['csp_log'].append(
                f"[RÀNG BUỘC] {var_name(idx)} = {value} bị từ chối vì không đúng cấu hình mục tiêu cần là {expected}."
            )
            stats['csp_log'].append(f"[QUAY LUI] Bỏ giá trị {value} của {var_name(idx)} và thử giá trị khác.")
            return False

        return True

    def backtrack(assign):
        stats['nodes_expanded'] += 1
        idx, var = select_unassigned_variable(assign)
        if idx is None:
            stats['csp_log'].append("[THÀNH CÔNG] Tìm thấy cấu hình hợp lệ cho bàn cờ CSP.")
            return assign

        for value in order_domain_values(var, assign):
            if not consistent(var, value, assign):
                continue

            assign[var] = value
            stats['nodes_created'] += 1
            stats['csp_log'].append(f"[Thử nghiệm] Gán {var_name(idx)} = {value} ... Hợp lệ.")
            stats['csp_log'].append("[Bàn cờ hiện tại]\n" + state_label(assign))

            result = backtrack(assign)
            if result is not None:
                return result

            del assign[var]
            stats['backtracks'] += 1
            stats['csp_log'].append(f"[QUAY LUI] Hủy bỏ {var_name(idx)} = {value}, quay lại ô trước.")

        stats['csp_log'].append(f"[Thử nghiệm] Không còn giá trị hợp lệ cho {var_name(idx)}.")
        return None

    solution = backtrack(assignment)
    if solution is None:
        stats['csp_log'].append("[KẾT THÚC] Không tìm được cấu hình CSP hợp lệ.")
        return None, stats

    board = [[0 for _ in range(3)] for _ in range(3)]
    for (r, c), value in solution.items():
        board[r][c] = value

    stats['solution_costs'] = [value for row in board for value in row]
    return board, stats


def min_conflicts_csp(start_state, max_steps=2000):
    """Giải CSP 8-puzzle bằng Min-Conflicts trên mô hình hoán vị 9 ô.

    Mỗi biến Xi là một vị trí trên bàn cờ. Giá trị của Xi là quân cờ đặt tại
    vị trí đó. Một xung đột xảy ra khi Xi khác giá trị mục tiêu tương ứng.
    Phép gán lại được thực hiện bằng cách tráo hai vị trí để luôn giữ ràng
    buộc AllDifferent (mỗi số 0..8 chỉ xuất hiện đúng một lần).

    Lưu ý: đây là lời giải CSP cho cấu hình đích, không phải chuỗi nước đi hợp
    lệ của ô trống. Vì vậy hàm trả về một bàn cờ kết quả, không trả về path.
    """
    flat_state = [value for row in start_state for value in row]
    goal_values = [value for row in GOAL_STATE for value in row]

    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'goal_checks': 0,
        'constraint_violations': 0,
        'backtracks': 0,
        'csp_log': [],
        'steps': 0,
        'max_steps': max_steps,
        'solution_costs': [],
        'initial_conflicts': 0,
        'final_conflicts': 0,
    }

    # Kiểm tra dữ liệu đầu vào để tránh lỗi random.choice([]) hoặc thiếu quân.
    if len(flat_state) != 9 or sorted(flat_state) != list(range(9)):
        stats['csp_log'].append(
            '❌ Trạng thái không hợp lệ: bàn cờ phải chứa đúng các số từ 0 đến 8.'
        )
        return None, stats

    def count_conflicts(current):
        return sum(current[i] != goal_values[i] for i in range(9))

    current = flat_state[:]
    current_errors = count_conflicts(current)
    stats['initial_conflicts'] = current_errors
    stats['constraint_violations'] = current_errors
    stats['csp_log'].append('[Khởi tạo] Gán tất cả Xi theo ma trận bắt đầu.')
    stats['csp_log'].append(
        f'[Trạng thái ban đầu] current = {current} -> số xung đột = {current_errors}.'
    )

    if current_errors == 0:
        board = [current[i:i + 3] for i in range(0, 9, 3)]
        stats['solution_costs'] = [0]
        stats['final_conflicts'] = 0
        stats['csp_log'].append('🎉 Trạng thái ban đầu đã là trạng thái đích.')
        return board, stats

    for step in range(1, max_steps + 1):
        stats['goal_checks'] += 1
        conflicted_vars = [i for i in range(9) if current[i] != goal_values[i]]
        if not conflicted_vars:
            break

        var = random.choice(conflicted_vars)
        before_value = current[var]
        stats['csp_log'].append(f'\n[Vòng lặp - Bước {step}]')
        stats['csp_log'].append(
            f'• Chọn ô x{var + 1} = {before_value}; mục tiêu của ô là {goal_values[var]}.'
        )

        # Thử tráo với TẤT CẢ vị trí khác. Việc chỉ thử các ô đang xung đột
        # có thể bỏ sót vị trí đang giữ quân cần thiết và làm thuật toán đứng yên.
        best_error = float('inf')
        best_swaps = []

        for other_var in range(9):
            if other_var == var:
                continue

            current[var], current[other_var] = current[other_var], current[var]
            errors = count_conflicts(current)
            stats['nodes_expanded'] += 1
            stats['csp_log'].append(
                f'   - Thử đổi x{var + 1} với x{other_var + 1}: {errors} xung đột.'
            )

            if errors < best_error:
                best_error = errors
                best_swaps = [other_var]
            elif errors == best_error:
                best_swaps.append(other_var)

            current[var], current[other_var] = current[other_var], current[var]

        if not best_swaps:
            stats['csp_log'].append('❌ Không tìm được phép tráo hợp lệ.')
            break

        # Chọn ngẫu nhiên trong các phép tráo tốt nhất để đúng tinh thần
        # Min-Conflicts và tránh thiên lệch do thứ tự duyệt.
        chosen = random.choice(best_swaps)
        current[var], current[chosen] = current[chosen], current[var]
        stats['nodes_created'] += 1
        stats['steps'] = step

        new_errors = count_conflicts(current)
        stats['constraint_violations'] += new_errors
        stats['csp_log'].append(
            f'• Chọn đổi x{var + 1} với x{chosen + 1} -> current = {current}, '
            f'còn {new_errors} xung đột.'
        )

        if new_errors == 0:
            board = [current[i:i + 3] for i in range(0, 9, 3)]
            stats['solution_costs'] = [stats['initial_conflicts'], 0]
            stats['final_conflicts'] = 0
            stats['csp_log'].append(f'🎉 Thành công tại bước {step}: đạt trạng thái đích.')
            return board, stats

    stats['final_conflicts'] = count_conflicts(current)
    stats['csp_log'].append(
        f'❌ Thất bại: đạt giới hạn {max_steps} bước, còn '
        f"{stats['final_conflicts']} xung đột."
    )
    return None, stats

def ac3_filter_blank_moves(start_state):
    flat_state = [value for row in start_state for value in row]
    blank_position = flat_state.index(0)

    neighbors = {
        0: {1, 3},
        1: {0, 2, 4},
        2: {1, 5},
        3: {0, 4, 6},
        4: {1, 3, 5, 7},
        5: {2, 4, 8},
        6: {3, 7},
        7: {4, 6, 8},
        8: {5, 7},
    }

    domains = {"blank": set(range(9))}
    queue = deque([("blank", "target")])
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'goal_checks': 0,
        'constraint_violations': 0,
        'backtracks': 0,
        'csp_log': [],
        'final_domains': {},
        'revisions': 0,
        'values_pruned': 0,
        'solution_costs': [],
        'average_domain_size': 0.0,
        'is_arc_consistent': False,
    }

    def is_consistent(blank_pos, target_pos):
        return target_pos in neighbors[blank_pos]

    def revise():
        removed = False
        original_domain = domains["blank"].copy()
        for target in original_domain:
            stats['nodes_expanded'] += 1
            if not is_consistent(blank_position, target):
                domains["blank"].remove(target)
                removed = True
                stats['values_pruned'] += 1
                stats['csp_log'].append(
                    f"[AC-3] Xóa vị trí {target} khỏi miền blank vì không phải hàng xóm của ô trống {blank_position}."
                )
        if removed:
            stats['revisions'] += 1
            stats['csp_log'].append(
                f"[AC-3] Miền blank thay đổi: {sorted(original_domain)} -> {sorted(domains['blank'])}"
            )
        return removed

    while queue:
        xi, xj = queue.popleft()
        if revise():
            if not domains["blank"]:
                stats['csp_log'].append(
                    f"[AC-3] Miền rỗng cho blank. Không còn nước đi hợp lệ."
                )
                stats['final_domains'] = {"blank": sorted(domains["blank"])}
                stats['average_domain_size'] = len(domains["blank"])
                stats['is_arc_consistent'] = False
                return domains, stats
            queue.append(("blank", "target"))

    stats['final_domains'] = {"blank": sorted(domains["blank"])}
    stats['average_domain_size'] = len(domains["blank"])
    stats['is_arc_consistent'] = True
    stats['csp_log'].append("[AC-3] Lọc miền hoàn thành.")
    stats['csp_log'].append(
        f"[AC-3] Vị trí hợp lệ cho ô trống: {sorted(domains['blank'])}."
    )
    return domains, stats


def csp_ac3_backtracking_search(start_state):
    domains, ac3_stats = ac3_filter_blank_moves(start_state)

    solution, stats = csp_backtracking_search(
        start_state,
        initial_logs=ac3_stats['csp_log'],
        initial_stats=ac3_stats,
    )
    return solution, stats


def ac3_csp(start_state):
    """Thuật toán AC-3 để lọc miền giá trị cho CSP 8-puzzle."""
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'goal_checks': 0,
        'constraint_violations': 0,
        'backtracks': 0,
        'csp_log': [],
        'final_domains': {},
        'revisions': 0,
        'values_pruned': 0,
        'solution_costs': [],
        'average_domain_size': 0.0,
        'is_arc_consistent': False,
    }

    variables = [(r, c) for r in range(3) for c in range(3)]
    domain_values = list(range(9))
    domains = {}
    for idx, var in enumerate(variables):
        r, c = var
        value = start_state[r][c]
        if value in domain_values:
            domains[var] = [value]
        else:
            domains[var] = domain_values[:]

    neighbors = {var: [other for other in variables if other != var] for var in variables}
    queue = deque((xi, xj) for xi in variables for xj in neighbors[xi])

    def var_name(var):
        return f"x{variables.index(var) + 1}"

    def constraint(xi, xj, value_i, value_j):
        return value_i != value_j

    def revise(xi, xj):
        removed = False
        original_domain = domains[xi][:]
        for value in original_domain:
            if not any(constraint(xi, xj, value, other_value) for other_value in domains[xj]):
                domains[xi].remove(value)
                removed = True
                stats['constraint_violations'] += 1
                stats['values_pruned'] += 1
                stats['csp_log'].append(
                    f"[AC-3] Xóa giá trị {value} khỏi miền {var_name(xi)} vì không có giá trị tương thích ở {var_name(xj)}."
                )
        if removed:
            stats['revisions'] += 1
            stats['csp_log'].append(
                f"[AC-3] Miền {var_name(xi)} thay đổi: {original_domain} -> {domains[xi]}"
            )
        return removed

    while queue:
        xi, xj = queue.popleft()
        if revise(xi, xj):
            if not domains[xi]:
                stats['csp_log'].append(
                    f"[AC-3] Miền rỗng cho {var_name(xi)}. CSP vô nghiệm."
                )
                stats['final_domains'] = {var_name(var): domains[var] for var in variables}
                stats['average_domain_size'] = sum(len(domains[var]) for var in variables) / len(variables)
                stats['is_arc_consistent'] = False
                return None, stats
            for xk in neighbors[xi]:
                if xk != xj:
                    queue.append((xk, xi))

    stats['final_domains'] = {var_name(var): sorted(domains[var]) for var in variables}
    stats['csp_log'].append("[AC-3] Lọc miền hoàn thành.")
    stats['average_domain_size'] = sum(len(domains[var]) for var in variables) / len(variables)
    stats['is_arc_consistent'] = True

    if all(len(domains[var]) == 1 for var in variables):
        board = [[0 for _ in range(3)] for _ in range(3)]
        for var, dom in domains.items():
            r, c = var
            board[r][c] = dom[0]
        stats['solution_costs'] = [value for row in board for value in row]
        stats['csp_log'].append("[AC-3] Tất cả miền là đơn trị, trả về bàn cờ kết quả.")
        return board, stats

    return None, stats


def _format_board_tuple(state, prefix=""):
    rows = []
    for row in state:
        rows.append(prefix + " ".join("_" if value == 0 else str(value) for value in row))
    return rows


def format_and_or_tree(plan):
    """Vẽ cây AND-OR dạng chữ giống mẫu: trạng thái OR → hành động → ○ AND."""
    if plan == FAILURE:
        return "FAILURE"

    lines = []

    def draw(node, indent=""):
        node_type = node.get("type") if isinstance(node, dict) else None
        if node_type == "GOAL":
            lines.append(indent + "G – GOAL")
            lines.extend(_format_board_tuple(node['state'], indent + "    "))
            return

        if node_type != "OR":
            lines.append(indent + str(node))
            return

        lines.append(indent + "OR – Trạng thái")
        lines.extend(_format_board_tuple(node['state'], indent + "    "))
        lines.append(indent + "    │")
        lines.append(indent + f"    └── {node['action']} ── ○ AND")

        outcomes = node['and'].get('outcomes', [])
        for index, outcome in enumerate(outcomes):
            last = index == len(outcomes) - 1
            connector = "└──" if last else "├──"
            child_indent = indent + ("        " if last else "│       ")
            lines.append(indent + f"        {connector} Kết quả {index + 1}")
            lines.extend(_format_board_tuple(outcome['state'], child_indent + "    "))
            plan_child = outcome['plan']
            if isinstance(plan_child, dict) and plan_child.get('type') == 'GOAL':
                lines.append(child_indent + "    ↓")
                lines.append(child_indent + "    GOAL")
            else:
                lines.append(child_indent + "    ↓")
                draw(plan_child, child_indent + "    ")

    draw(plan)
    return "\n".join(lines)

def generate_complex_start_states(base_state, count, steps=2):
    """Tạo danh sách trạng thái bắt đầu từ ma trận ban đầu của giao diện chính."""
    if count <= 0:
        return []

    states = []
    seen = {matrix_to_tuple(base_state)}
    attempts = 0

    while len(states) < count and attempts < 50:
        state = [row[:] for row in base_state]
        for _ in range(steps):
            neighbors = get_neighbors(state)
            if not neighbors:
                break
            state_h = misplaced_tiles(state)
            better = [n for n in neighbors if misplaced_tiles(n) <= state_h]
            state = random.choice(better) if better else random.choice(neighbors)
        state_tuple = matrix_to_tuple(state)
        if state_tuple not in seen:
            seen.add(state_tuple)
            states.append(state)
        attempts += 1

    while len(states) < count:
        neighbors = get_neighbors(base_state)
        if not neighbors:
            break
        state = random.choice(neighbors)
        state_tuple = matrix_to_tuple(state)
        if state_tuple not in seen:
            seen.add(state_tuple)
            states.append(state)

    return states


def generate_random_start_states(count, steps=2):
    """Tạo danh sách trạng thái bắt đầu gần đích."""
    if count <= 0:
        return []

    states = []
    seen = set()
    while len(states) < count:
        state = [row[:] for row in GOAL_STATE]
        for _ in range(steps):
            neighbors = get_neighbors(state)
            state = random.choice(neighbors)
        state_tuple = matrix_to_tuple(state)
        if state_tuple in seen:
            continue
        seen.add(state_tuple)
        states.append(state)
    return states


def random_walk_search(start_state, max_steps=200, max_trials=200):
    """Giải bằng cách đi bộ ngẫu nhiên, mô phỏng môi trường không quan sát."""
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'trials': 0,
        'attempted_steps': 0
    }

    if is_goal(start_state):
        stats['nodes_created'] = 1
        return [start_state], stats

    for trial in range(1, max_trials + 1):
        current = [row[:] for row in start_state]
        path = [current]
        stats['trials'] += 1
        stats['nodes_created'] += 1

        for _ in range(max_steps):
            neighbors = get_neighbors(current)
            stats['nodes_expanded'] += 1
            stats['attempted_steps'] += 1
            stats['frontier_max'] = max(stats['frontier_max'], len(neighbors))
            current = random.choice(neighbors)
            path.append(current)
            if is_goal(current):
                stats['solution_steps'] = len(path) - 1
                return path, stats

    return None, stats


def get_visible_cells(mask_type):
    """Trả về các ô được quan sát theo loại chế độ."""
    if mask_type == "row0":
        return {(0, 0), (0, 1), (0, 2)}
    if mask_type == "diag":
        return {(0, 0), (1, 1), (2, 2)}
    return {(0, 0), (0, 1), (0, 2), (1, 1), (2, 2)}


def partial_observation_heuristic(state, mask_type="default"):
    """Đánh giá chỉ dựa trên các ô quan sát được theo chế độ đã chọn."""
    visible_cells = get_visible_cells(mask_type)
    wrong = 0
    for i, j in visible_cells:
        if state[i][j] != 0 and state[i][j] != GOAL_STATE[i][j]:
            wrong += 1
    return wrong


def greedy_search_with_heuristic(start_state, heuristic_func, max_iterations=10000, fixed_cells=None):
    """Tìm kiếm Greedy với hàm heuristic tuỳ chỉnh."""
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'solution_costs': [],
        'attempted_steps': 0
    }

    if is_goal(start_state):
        stats['nodes_created'] = 1
        return [start_state], stats

    frontier = []
    heapq.heappush(frontier, (heuristic_func(start_state), 0, start_state, [start_state]))
    seen = {matrix_to_tuple(start_state)}
    stats['nodes_created'] = 1
    counter = 1

    while frontier and stats['nodes_expanded'] < max_iterations:
        stats['frontier_max'] = max(stats['frontier_max'], len(frontier))
        _, _, current_state, path = heapq.heappop(frontier)
        stats['nodes_expanded'] += 1
        stats['attempted_steps'] += 1

        if is_goal(current_state):
            return path, stats

        for neighbor in get_neighbors(current_state):
            # If there are fixed visible cells (from partial observation), disallow moves
            # that change those cells away from their goal values.
            if fixed_cells:
                violated = False
                for (fi, fj) in fixed_cells:
                    if neighbor[fi][fj] != GOAL_STATE[fi][fj]:
                        violated = True
                        break
                if violated:
                    continue
            neighbor_tuple = matrix_to_tuple(neighbor)
            if neighbor_tuple not in seen:
                seen.add(neighbor_tuple)
                heapq.heappush(frontier, (heuristic_func(neighbor), counter, neighbor, path + [neighbor]))
                counter += 1
                stats['nodes_created'] += 1

    return None, stats


def no_observation_environment(start_count, base_state):
    """Chạy nhiều trạng thái bắt đầu mô phỏng môi trường không quan sát bằng UCS."""
    states = generate_complex_start_states(base_state, start_count)
    total_stats = {
        'start_count': start_count,
        'solved_count': 0,
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'goal_checks': 0,
        'solutions': []
    }

    for idx, state in enumerate(states, start=1):
        if is_goal(state):
            solution = [state]
            stats = {
                'nodes_expanded': 0,
                'nodes_created': 1,
                'frontier_max': 0,
                'goal_checks': 0,
                'solution_costs': [0],
                'total_cost': 0
            }
            solved = True
        else:
            solution, stats = uniform_cost_search(state)
            solved = solution is not None

        total_stats['nodes_expanded'] += stats.get('nodes_expanded', 0)
        total_stats['nodes_created'] += stats.get('nodes_created', 0)
        total_stats['frontier_max'] = max(total_stats['frontier_max'], stats.get('frontier_max', 0))
        total_stats['goal_checks'] += stats.get('goal_checks', 0)

        if solved:
            total_stats['solved_count'] += 1

        total_stats['solutions'].append({
            'index': idx,
            'start_state': state,
            'solution': solution,
            'stats': stats,
            'solved': solved
        })

    return None, total_stats


def partial_observable_environment(start_count, base_state, mask_type="default"):
    """Chạy nhiều trạng thái bắt đầu mô phỏng môi trường quan sát một phần.
    Trả về tổng hợp thống kê và danh sách kết quả per-start để hiển thị song song.
    """
    states = generate_complex_start_states(base_state, start_count)
    total_stats = {
        'start_count': start_count,
        'solved_count': 0,
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'mask_type': mask_type,
        'solutions': []
    }

    for idx, state in enumerate(states, start=1):
        # Determine visible cells and which visible cells are already correct — these should be fixed
        visible = get_visible_cells(mask_type)
        fixed_cells = {(i, j) for (i, j) in visible if state[i][j] == GOAL_STATE[i][j]}

        # Use greedy with partial observation heuristic to try to solve under partial observability
        solution, stats = greedy_search_with_heuristic(
            state,
            lambda s: partial_observation_heuristic(s, mask_type),
            max_iterations=10000,
            fixed_cells=fixed_cells
        )

        solved = solution is not None
        if solved:
            total_stats['solved_count'] += 1

        total_stats['nodes_expanded'] += stats.get('nodes_expanded', 0)
        total_stats['nodes_created'] += stats.get('nodes_created', 0)
        total_stats['frontier_max'] = max(total_stats['frontier_max'], stats.get('frontier_max', 0))

        total_stats['solutions'].append({
            'index': idx,
            'start_state': state,
            'solution': solution,
            'stats': stats,
            'solved': solved
        })

    return None, total_stats


def get_move_name(prev, curr):
    """Lấy tên bước đi giữa hai trạng thái liên tiếp"""
    pi, pj = find_zero(prev)
    ci, cj = find_zero(curr)
    if ci == pi - 1 and cj == pj:
        return "Up"
    if ci == pi + 1 and cj == pj:
        return "Down"
    if ci == pi and cj == pj - 1:
        return "Left"
    if ci == pi and cj == pj + 1:
        return "Right"
    return ""


def format_solution_steps(path, costs=None, cost_label="Chi phí g(n)"):
    """Định dạng chuỗi trạng thái theo từng bước"""
    lines = []
    for idx, state in enumerate(path):
        lines.append(f"Bước {idx}:")
        if costs is not None and idx < len(costs):
            lines.append(f"{cost_label}: {costs[idx]}")
        for row in state:
            lines.append(" ".join(str(v) if v != 0 else "_" for v in row))
        lines.append("".join(["-" for _ in range(15)]))
    return "\n".join(lines)


def format_move_sequence(path):
    """Định dạng đường đi tốt nhất từ trạng thái ban đầu đến đích"""
    moves = [get_move_name(path[i], path[i + 1]) for i in range(len(path) - 1)]
    return " → ".join(moves)


# ==================== THUẬT TOÁN BFS CÁCH 1: CHECK ON POP ====================
def bfs_check_on_pop(start_state):
    """
    BFS Cách 1: Kiểm tra mục tiêu khi LẤY NÚT RA khỏi hàng đợi
    
    Mã giả:
        function BFS(problem) returns a solution node or failure
            node ← NODE(problem.INITIAL)
            frontier ← a FIFO queue, with node as an element
            reached ← {problem.INITIAL}
            
            while not IS-EMPTY(frontier) do
                node ← POP(frontier)
                **--- KIỂM TRA MỤC TIÊU Ở ĐÂY (KHI LẤY RA) ---**
                if problem.IS-GOAL(node.state) then return node
                
                add node.state to reached
                
                for each child in EXPAND(problem, node) do
                    C ← child.state
                    if C is not in reached then
                        add child to frontier
            
            return failure
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
    }
    
    # Kiểm tra trạng thái ban đầu
    if is_goal(start_state):
        stats['nodes_created'] = 1
        return [start_state], stats
    
    # Khởi tạo hàng đợi và reached
    queue = deque([(start_state, [start_state])])
    reached = {matrix_to_tuple(start_state)}
    stats['nodes_created'] = 1
    
    while queue:
        stats['frontier_max'] = max(stats['frontier_max'], len(queue))
        
        current_state, path = queue.popleft()
        stats['nodes_expanded'] += 1
        
        # **--- KIỂM TRA MỤC TIÊU KHI LẤY RA ---**
        if is_goal(current_state):
            return path, stats
        
        # Mở rộng nút hiện tại
        neighbors = get_neighbors(current_state)
        
        for neighbor in neighbors:
            neighbor_tuple = matrix_to_tuple(neighbor)
            
            # Chỉ thêm vào frontier nếu chưa visited
            if neighbor_tuple not in reached:
                reached.add(neighbor_tuple)
                queue.append((neighbor, path + [neighbor]))
                stats['nodes_created'] += 1
    
    return None, stats

# ==================== THUẬT TOÁN UCS: UNIFORM COST SEARCH ====================
def misplaced_tiles(state):
    """Đếm số ô sai so với trạng thái đích, không tính ô trắng (0)."""
    wrong = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0 and state[i][j] != GOAL_STATE[i][j]:
                wrong += 1
    return wrong


def uniform_cost_search(start_state):
    """
    UCS sử dụng chi phí g(n) = g(parent) + số ô sai của node con.
    Kiểm tra chi phí trước khi thêm vào frontier và luôn lấy node có chi phí nhỏ nhất khi pop.
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'goal_checks': 0,
    }

    # Nếu trạng thái ban đầu đã là đích thì trả về luôn
    if is_goal(start_state):
        stats['nodes_created'] = 1
        stats['solution_costs'] = [0]
        stats['total_cost'] = 0
        return [start_state], stats

    # frontier lưu các nút chờ mở rộng theo thứ tự chi phí nhỏ đến lớn
    # mỗi entry: (chi phí tổng g(n), thứ tự tăng dần, state, path, cost_path)
    start_tuple = matrix_to_tuple(start_state)
    frontier = []
    heapq.heappush(frontier, (0, 0, start_state, [start_state], [0]))

    # reached_cost lưu chi phí nhỏ nhất đã tìm được tới mỗi trạng thái
    reached_cost = {start_tuple: 0}
    stats['nodes_created'] = 1
    counter = 1

    while frontier:
        stats['frontier_max'] = max(stats['frontier_max'], len(frontier))

        # Lấy node có chi phí g(n) nhỏ nhất ra để mở rộng
        current_cost, _, current_state, path, cost_path = heapq.heappop(frontier)
        current_tuple = matrix_to_tuple(current_state)

        # Nếu trạng thái này đã được tìm với chi phí thấp hơn thì bỏ qua
        if current_cost != reached_cost.get(current_tuple, None):
            continue

        stats['nodes_expanded'] += 1

        # Nếu đạt đích thì trả về đường đi hiện tại
        if is_goal(current_state):
            stats['solution_costs'] = cost_path
            stats['total_cost'] = current_cost
            return path, stats

        # Mở rộng các trạng thái con
        for neighbor in get_neighbors(current_state):
            neighbor_tuple = matrix_to_tuple(neighbor)

            # Chi phí bước của node con là số ô bị đặt sai
            step_cost = misplaced_tiles(neighbor)
            new_cost = current_cost + step_cost
            stats['goal_checks'] += 1

            # Nếu chưa thấy trạng thái này hoặc tìm được chi phí nhỏ hơn thì cập nhật
            if neighbor_tuple not in reached_cost or new_cost < reached_cost[neighbor_tuple]:
                reached_cost[neighbor_tuple] = new_cost
                heapq.heappush(frontier, (new_cost, counter, neighbor, path + [neighbor], cost_path + [new_cost]))
                counter += 1
                stats['nodes_created'] += 1

    return None, stats


# ==================== THUẬT TOÁN GREEDY ====================

def tuple_to_matrix(tpl):
    """Chuyển trạng thái tuple về dạng ma trận list để hiển thị và so sánh."""
    return [list(row) for row in tpl]


def reconstruct_path(parent, goal_tuple):
    """Dựng lại đường đi từ node đích bằng cách đi ngược về node gốc qua bảng parent."""
    path = []
    current = goal_tuple
    while current is not None:
        path.append(tuple_to_matrix(current))
        current = parent.get(current)
    return list(reversed(path))


def greedy_search(start_state):
    """
    Greedy Search sử dụng heuristic h(n) = số ô sai so với trạng thái đích.
    Luôn mở rộng node có h(n) nhỏ nhất.

    Mã giả:
        function Greedy_Search(Start, Goal):                          function Greedy_Search(Start, Goal):
            frontier = PriorityQueue()                                     1. Khởi tạo tập Frontier = {Start} 
            frontier.push(Start, h(Start))                                 Tính hàm đánh giá Start: h(Start)      

            reached = set()                                                2. Khởi tạo tập Reached = ∅      

            while frontier is not empty:                                   3. TRONG KHI (frontier không rỗng):
                n = frontier.pop()   // node có h nhỏ nhất                        a. Chọn trạng thái n từ frontier có h(n) nhỏ nhất.

                if n == Goal:                                                     NẾU n == Goal:
                    return Path(n)                                                TRẢ VỀ "Thành công" và truy xuất lại đường đi từ Start đến n.

                reached.add(n)                                                    c. Loại bỏ n khỏi frontier và thêm n vào reached.

                for each neighbor m of n:                                         d. Với mỗi trạng thái m kề với n:
                    if m not in frontier and m not in reached:                          i. NẾU m chưa có trong cả frontier và reached:
                        parent[m] = n                                                   Gán đỉnh cha của m là n.  Tính giá trị heuristic h(m).
                        frontier.push(m, h(m))                                          Thêm m vào frontier.
                                                                                        ii. NẾU m đã có trong frontier hoặc reached:  Bỏ qua m.
            return Failure                                                 4. TRẢ VỀ "Thất bại" (Không tìm thấy đường đi).
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'goal_checks': 0,
    }

    # Nếu trạng thái ban đầu đã là trạng thái đích
    if is_goal(start_state):
        stats['nodes_created'] = 1
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        return [start_state], stats

    start_tuple = matrix_to_tuple(start_state)

    # frontier lưu các nút chờ mở rộng ưu tiên theo giá trị heuristic h(n)
    frontier = []  # heap queue (priority queue)
    frontier_set = {start_tuple}  # theo dõi các trạng thái đang trong frontier
    parent = {start_tuple: None}  # lưu cha để lát dựng lại đường đi

    # Đẩy trạng thái ban đầu vào frontier với trọng số h(start_state)
    heapq.heappush(frontier, (misplaced_tiles(start_state), 0, start_tuple))
    stats['nodes_created'] = 1
    counter = 1
    reached = set()

    while frontier:
        stats['frontier_max'] = max(stats['frontier_max'], len(frontier))

        # Lấy node có h nhỏ nhất
        _, _, current_tuple = heapq.heappop(frontier)
        frontier_set.discard(current_tuple)

        current_state = tuple_to_matrix(current_tuple)
        stats['nodes_expanded'] += 1
        stats['goal_checks'] += 1

        # Kiểm tra mục tiêu khi lấy ra
        if is_goal(current_state):
            path = reconstruct_path(parent, current_tuple)
            stats['solution_costs'] = [misplaced_tiles(state) for state in path]
            return path, stats

        reached.add(current_tuple)

        # Mở rộng neighbor
        for neighbor in get_neighbors(current_state):
            neighbor_tuple = matrix_to_tuple(neighbor)
            if neighbor_tuple not in reached and neighbor_tuple not in frontier_set:
                parent[neighbor_tuple] = current_tuple  # lưu cha của node con
                heapq.heappush(frontier, (misplaced_tiles(neighbor), counter, neighbor_tuple))
                frontier_set.add(neighbor_tuple)
                counter += 1
                stats['nodes_created'] += 1

    return None, stats


# ==================== THUẬT TOÁN BFS CÁCH 2: CHECK ON PUSH ====================
def bfs_check_on_push(start_state):
    """
   BFS Cách 2: Kiểm tra mục tiêu TRƯỚC khi cho vào hàng đợi
    
    Mã giả:
        function BREADTH-FIRST-SEARCH(problem) returns a solution node or failure
            node ← NODE(problem.INITIAL)
            **--- KIỂM TRA MỤC TIÊU SỚM (Nút gốc) ---**
            if problem.IS-GOAL(node.STATE) then return node
            
            frontier ← a FIFO queue, with node as an element
            reached ← {problem.INITIAL}
            
            while not IS-EMPTY(frontier) do
                node ← POP(frontier)
                
                for each child in EXPAND(problem, node) do
                    s ← child.STATE
                    **--- KIỂM TRA MỤC TIÊU SỚM (Child) ---**
                    if problem.IS-GOAL(s) then return child
                    
                    if s is not in reached then
                        add s to reached
                        add child to frontier
            
            return failure
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'goal_checks': 0,
    }
    
    # **--- KIỂM TRA MỤC TIÊU SỚM (Nút gốc) ---**
    stats['nodes_created'] = 1
    stats['goal_checks'] = 1
    if is_goal(start_state):
        return [start_state], stats
    
    # Khởi tạo hàng đợi và reached
    queue = deque([(start_state, [start_state])])
    reached = {matrix_to_tuple(start_state)}
    
    while queue:
        stats['frontier_max'] = max(stats['frontier_max'], len(queue))
        
        current_state, path = queue.popleft()
        stats['nodes_expanded'] += 1
        
        # Mở rộng nút hiện tại
        neighbors = get_neighbors(current_state)
        
        for neighbor in neighbors:
            neighbor_tuple = matrix_to_tuple(neighbor)
            
            # **--- KIỂM TRA MỤC TIÊU SỚM (Nút con) ---**
            stats['goal_checks'] += 1
            if is_goal(neighbor):
                return path + [neighbor], stats
            
            # Chỉ thêm vào frontier nếu chưa visited
            if neighbor_tuple not in reached:
                reached.add(neighbor_tuple)
                queue.append((neighbor, path + [neighbor]))
                stats['nodes_created'] += 1
    
    return None, stats


# ==================== THUẬT TOÁN A* ====================
def a_star_search(start_state):
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 0,
        'frontier_max': 0,
        'goal_checks': 0,
    }

    if is_goal(start_state):
        stats['nodes_created'] = 1
        stats['solution_costs'] = [0]
        stats['total_cost'] = 0
        return [start_state], stats

    start_tuple = matrix_to_tuple(start_state)
    frontier = []
    g_cost = {start_tuple: 0}
    parent = {start_tuple: None}
    start_f = misplaced_tiles(start_state)

    heapq.heappush(frontier, (start_f, 0, start_tuple))
    stats['nodes_created'] = 1
    counter = 1
    closed = set()

    while frontier:
        stats['frontier_max'] = max(stats['frontier_max'], len(frontier))
        f_current, _, current_tuple = heapq.heappop(frontier)
        current_state = tuple_to_matrix(current_tuple)
        current_g = g_cost[current_tuple]
        current_h = misplaced_tiles(current_state)

        # Bỏ qua entry cũ nếu không còn phù hợp
        if f_current != current_g + current_h:
            continue

        stats['nodes_expanded'] += 1
        stats['goal_checks'] += 1

        if is_goal(current_state):
            path = reconstruct_path(parent, current_tuple)
            costs = []
            for depth, state in enumerate(path):
                g = depth
                h = misplaced_tiles(state)
                costs.append(g + h)
            stats['solution_costs'] = costs
            stats['total_cost'] = costs[-1]
            return path, stats

        closed.add(current_tuple)

        for neighbor in get_neighbors(current_state):
            neighbor_tuple = matrix_to_tuple(neighbor)
            tentative_g = current_g + 1

            if neighbor_tuple in closed and tentative_g >= g_cost.get(neighbor_tuple, float('inf')):
                continue

            if tentative_g < g_cost.get(neighbor_tuple, float('inf')):
                g_cost[neighbor_tuple] = tentative_g
                parent[neighbor_tuple] = current_tuple
                f_new = tentative_g + misplaced_tiles(neighbor)
                heapq.heappush(frontier, (f_new, counter, neighbor_tuple))
                counter += 1
                stats['nodes_created'] += 1

    return None, stats


# ==================== THUẬT TOÁN IDA* ====================

def ida_star_limited_search(current_tuple, g, threshold, path, stats):
    current_state = tuple_to_matrix(current_tuple)
    stats['nodes_expanded'] += 1
    stats['frontier_max'] = max(stats['frontier_max'], len(path))

    h = misplaced_tiles(current_state)
    f = g + h

    if f > threshold:
        return None, f

    if is_goal(current_state):
        return list(path), f

    minimum = float('inf')
    for neighbor in get_neighbors(current_state):
        neighbor_tuple = matrix_to_tuple(neighbor)
        if neighbor_tuple in path:
            continue

        stats['nodes_created'] += 1
        path.append(neighbor_tuple)
        result, next_threshold = ida_star_limited_search(neighbor_tuple, g + 1, threshold, path, stats)
        path.pop()

        if result is not None:
            return result, next_threshold

        minimum = min(minimum, next_threshold)

    return None, minimum


def ida_star_search(start_state):
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'iterations': 0,
    }

    if is_goal(start_state):
        stats['solution_costs'] = [0]
        stats['total_cost'] = 0
        return [start_state], stats

    start_tuple = matrix_to_tuple(start_state)
    threshold = misplaced_tiles(start_state)
    path = [start_tuple]

    while True:
        stats['iterations'] += 1
        result, next_threshold = ida_star_limited_search(start_tuple, 0, threshold, path, stats)

        if result is not None:
            solution = [tuple_to_matrix(state_tuple) for state_tuple in result]
            costs = []
            for depth, state in enumerate(solution):
                g = depth
                h = misplaced_tiles(state)
                costs.append(g + h)
            stats['solution_costs'] = costs
            stats['total_cost'] = costs[-1]
            return solution, stats

        if next_threshold == float('inf'):
            return None, stats

        threshold = next_threshold


# ==================== THUẬT TOÁN HILL CLIMBING (LOCAL SEARCH) ====================
def simple_hill_climbing(start_state):
    """
    Simple Hill Climbing (Local Search).

    Pseudocode adapted: minimize misplaced_tiles (h). Move to a neighbor with strictly lower h.
    Returns the path of visited states (from start to final local optimum or goal) and stats.
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
    }

    # Nếu trạng thái ban đầu đã là đích
    if is_goal(start_state):
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        stats['total_cost'] = stats['solution_costs'][-1]
        return [start_state], stats

    current = [row[:] for row in start_state]
    path = [current]
    current_h = misplaced_tiles(current)

    while True:
        neighbors = get_neighbors(current)
        stats['frontier_max'] = max(stats['frontier_max'], len(neighbors))

        moved = False
        # First-improvement: move to the first neighbor that improves h
        for neighbor in neighbors:
            stats['nodes_created'] += 1
            h = misplaced_tiles(neighbor)
            if h < current_h:
                stats['nodes_expanded'] += 1
                current = neighbor
                path.append(current)
                current_h = h
                moved = True
                break

        if moved:
            if is_goal(current):
                break
            continue

        # No improving neighbor -> local maximum (or minimum depending on objective)
        break

    stats['solution_costs'] = [misplaced_tiles(s) for s in path]
    stats['total_cost'] = stats['solution_costs'][-1]
    return path, stats


def stochastic_hill_climbing(start_state):
    """
    Stochastic Hill Climbing (Local Search).

    Chọn ngẫu nhiên một neighbor tốt hơn khi tồn tại.
    Trả về đường đi cho tới cực tiểu địa phương hoặc đích.
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
    }

    if is_goal(start_state):
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        stats['total_cost'] = stats['solution_costs'][-1]
        return [start_state], stats

    current = [row[:] for row in start_state]
    path = [current]
    current_h = misplaced_tiles(current)

    while True:
        neighbors = get_neighbors(current)
        stats['frontier_max'] = max(stats['frontier_max'], len(neighbors))

        better_neighbors = []
        for neighbor in neighbors:
            stats['nodes_created'] += 1
            h = misplaced_tiles(neighbor)
            if h < current_h:
                better_neighbors.append((neighbor, h))

        if not better_neighbors:
            break

        next_state, next_h = random.choice(better_neighbors)
        stats['nodes_expanded'] += 1
        current = next_state
        current_h = next_h
        path.append(current)

        if is_goal(current):
            break

    stats['solution_costs'] = [misplaced_tiles(s) for s in path]
    stats['total_cost'] = stats['solution_costs'][-1]
    return path, stats


def local_beam_search(start_state, k=4):
    """Local Beam Search.

    Khởi tạo k trạng thái ngẫu nhiên từ Start bằng các bước đi ngẫu nhiên.
    Trong mỗi vòng lặp, mở rộng tất cả neighbor của các trạng thái hiện tại,
    chọn k trạng thái có h nhỏ nhất để tiếp tục.
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'beams': k,
    }

    if is_goal(start_state):
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        stats['total_cost'] = stats['solution_costs'][-1]
        return [start_state], stats

    def random_state_from(start):
        state = [row[:] for row in start]
        for _ in range(10):
            neighbors = get_neighbors(state)
            state = random.choice(neighbors)
        return state

    current_set = []
    seen = set()
    while len(current_set) < k:
        candidate = random_state_from(start_state)
        candidate_tuple = matrix_to_tuple(candidate)
        if candidate_tuple not in seen:
            seen.add(candidate_tuple)
            current_set.append(candidate)
            stats['nodes_created'] += 1

    while True:
        neighbor_states = []
        for state in current_set:
            for neighbor in get_neighbors(state):
                neighbor_tuple = matrix_to_tuple(neighbor)
                if neighbor_tuple not in seen:
                    seen.add(neighbor_tuple)
                    stats['nodes_created'] += 1
                neighbor_states.append(neighbor)

        stats['frontier_max'] = max(stats['frontier_max'], len(neighbor_states))

        if not neighbor_states:
            current_set.sort(key=misplaced_tiles)
            best = current_set[0]
            stats['solution_costs'] = [misplaced_tiles(best)]
            stats['total_cost'] = misplaced_tiles(best)
            return [best], stats

        for neighbor in neighbor_states:
            if is_goal(neighbor):
                stats['nodes_expanded'] += 1
                stats['solution_costs'] = [misplaced_tiles(neighbor)]
                stats['total_cost'] = misplaced_tiles(neighbor)
                return [neighbor], stats

        neighbor_states.sort(key=misplaced_tiles)
        current_set = neighbor_states[:k]
        stats['nodes_expanded'] += 1

        if all(matrix_to_tuple(state) == matrix_to_tuple(current_set[0]) for state in current_set):
            best = current_set[0]
            stats['solution_costs'] = [misplaced_tiles(best)]
            stats['total_cost'] = misplaced_tiles(best)
            return [best], stats


def steepest_ascent_hill_climbing(start_state):
    """
    Steepest-Ascent Hill Climbing: choose the neighbor with the best (lowest) h(n).
    Returns path and stats similar to other solvers.
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
    }

    if is_goal(start_state):
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        stats['total_cost'] = stats['solution_costs'][-1]
        return [start_state], stats

    current = [row[:] for row in start_state]
    path = [current]
    current_h = misplaced_tiles(current)

    while True:
        neighbors = get_neighbors(current)
        stats['frontier_max'] = max(stats['frontier_max'], len(neighbors))

        best_neighbor = None
        best_h = current_h

        for neighbor in neighbors:
            stats['nodes_created'] += 1
            h = misplaced_tiles(neighbor)
            if h < best_h:
                best_h = h
                best_neighbor = neighbor

        if best_neighbor is not None and best_h < current_h:
            stats['nodes_expanded'] += 1
            current = best_neighbor
            path.append(current)
            current_h = best_h
            if is_goal(current):
                break
            continue

        # no better neighbor
        break

    stats['solution_costs'] = [misplaced_tiles(s) for s in path]
    stats['total_cost'] = stats['solution_costs'][-1]
    return path, stats


def random_restart_hill_climbing(start_state, max_restarts=10):
    """Random Restart Hill Climbing.

    Thực hiện tối đa max_restarts lần khởi động lại. Mỗi lần chạy sử dụng
    Stochastic Hill Climbing để chọn ngẫu nhiên một neighbor tốt hơn.
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'restarts': 0,
    }

    if is_goal(start_state):
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        stats['total_cost'] = stats['solution_costs'][-1]
        return [start_state], stats

    for _ in range(max_restarts):
        stats['restarts'] += 1
        path, sub_stats = stochastic_hill_climbing(start_state)

        stats['nodes_expanded'] += sub_stats['nodes_expanded']
        stats['nodes_created'] += sub_stats['nodes_created']
        stats['frontier_max'] = max(stats['frontier_max'], sub_stats['frontier_max'])

        if path and is_goal(path[-1]):
            stats['solution_costs'] = [misplaced_tiles(s) for s in path]
            stats['total_cost'] = stats['solution_costs'][-1]
            return path, stats

    return None, stats


def simulated_annealing(start_state, T0=1.0, Tmin=1e-6, alpha=0.95):
    """Simulated Annealing for the 8-puzzle local search.

    current state = start
    T = T0
    while T > Tmin:
        if current state == goal:
            return current state

        next state = RandomNeighbor(current state)
        Δ = h(next state) - h(current state)

        if Δ < 0:
            current state = next state
        else:
            p = exp(-Δ / T)
            if Random(0,1) < p:
                current state = next state

        T = α * T

    return current state
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'temperature_steps': 0,
    }

    if is_goal(start_state):
        stats['solution_costs'] = [misplaced_tiles(start_state)]
        stats['total_cost'] = stats['solution_costs'][-1]
        return [start_state], stats

    current = [row[:] for row in start_state]
    path = [current]
    current_h = misplaced_tiles(current)
    temperature = T0

    while temperature > Tmin:
        if is_goal(current):
            break

        neighbors = get_neighbors(current)
        stats['frontier_max'] = max(stats['frontier_max'], len(neighbors))

        if not neighbors:
            break

        next_state = random.choice(neighbors)
        stats['nodes_created'] += 1
        next_h = misplaced_tiles(next_state)
        delta = next_h - current_h
        stats['nodes_expanded'] += 1
        stats['temperature_steps'] += 1

        if delta < 0 or random.random() < math.exp(-delta / temperature):
            current = next_state
            current_h = next_h
            path.append(current)
            if is_goal(current):
                break

        temperature *= alpha

    stats['solution_costs'] = [misplaced_tiles(s) for s in path]
    stats['total_cost'] = stats['solution_costs'][-1]
    return path, stats

# ==================== THUẬT TOÁN DFS ====================
def deep_first_search(start_state):
    """
    Tìm kiếm theo chiều sâu (Deep-First Search)
    
    Mã giả (DEEP-FIRST-SEARCH):
        node ← NODE(problem.INITIAL)
        if problem.IS-GOAL(node.STATE) then return node
        frontier ← a LIFO stack, with node as an element
        reached ← {problem.INITIAL}
        while not IS-EMPTY(frontier) do
            node ← POP(frontier)
            for each child in EXPAND(problem, node) do
                s ← child.STATE
                if problem.IS-GOAL(s) then return child
                if s is not in reached and child is not in frontier then
                    add s to reached
                    add child to frontier
        return failure
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
    }
    
    # Kiểm tra trạng thái ban đầu
    if is_goal(start_state):
        return [start_state], stats
    
    # Khởi tạo stack và reached (sử dụng list làm LIFO stack)
    stack = [(start_state, [start_state])]
    reached = {matrix_to_tuple(start_state)}
    
    while stack:
        stats['frontier_max'] = max(stats['frontier_max'], len(stack))
        
        current_state, path = stack.pop()  # POP từ stack (LIFO)
        stats['nodes_expanded'] += 1
        
        # Mở rộng nút hiện tại
        neighbors = get_neighbors(current_state)
        
        for neighbor in neighbors:
            neighbor_tuple = matrix_to_tuple(neighbor)
            s = neighbor
            
            # Kiểm tra mục tiêu
            if is_goal(s):
                return path + [neighbor], stats
            
            # Chỉ thêm vào frontier nếu chưa visited
            if neighbor_tuple not in reached:
                reached.add(neighbor_tuple)
                stack.append((neighbor, path + [neighbor]))
                stats['nodes_created'] += 1
    
    return None, stats


# ==================== THUẬT TOÁN DFS VARIANT (CHECK FRONTIER) ====================
def deep_first_search_check_frontier(start_state):
    """
    Tìm kiếm theo chiều sâu Variant - Kiểm tra frontier
    
    Mã giả (DEEP-FIRST-SEARCH - Variant):
        node ← NODE(problem.INITIAL)
        if problem.IS-GOAL(node.STATE) then return node
        
        frontier ← a LIFO stack, with node as an element
        reached ← {problem.INITIAL}
        
        while not IS-EMPTY(frontier) do
            node ← POP(frontier)
            for each child in EXPAND(problem, node) do
                s ← child.STATE
                if problem.IS-GOAL(s) then return child
                if s is not in reached and child is not in frontier then
                    add s to reached
                    add child to frontier
                    
        return failure
    
    Khác biệt: Kiểm tra "child is not in frontier" trước khi thêm vào stack
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
    }
    
    # Kiểm tra trạng thái ban đầu
    if is_goal(start_state):
        return [start_state], stats
    
    # Khởi tạo stack, reached, và frontier (tập các nút trong stack)
    start_tuple = matrix_to_tuple(start_state)
    stack = [(start_state, [start_state])]
    reached = {start_tuple}
    frontier = {start_tuple}  # Theo dõi những gì đang trong stack
    
    while stack:
        stats['frontier_max'] = max(stats['frontier_max'], len(stack))
        
        current_state, path = stack.pop()
        current_tuple = matrix_to_tuple(current_state)
        frontier.discard(current_tuple)  # Loại bỏ khỏi frontier khi lấy ra
        stats['nodes_expanded'] += 1
        
        # Mở rộng nút hiện tại
        neighbors = get_neighbors(current_state)
        
        for neighbor in neighbors:
            neighbor_tuple = matrix_to_tuple(neighbor)
            s = neighbor
            
            # Kiểm tra mục tiêu
            if is_goal(s):
                return path + [neighbor], stats
            
            # Kiểm tra: not in reached AND not in frontier
            if neighbor_tuple not in reached and neighbor_tuple not in frontier:
                reached.add(neighbor_tuple)
                frontier.add(neighbor_tuple)  # Thêm vào frontier
                stack.append((neighbor, path + [neighbor]))
                stats['nodes_created'] += 1
    
    return None, stats


# ==================== THUẬT TOÁN ITERATIVE DEEPENING SEARCH ====================
def depth_limited_search(start_state, limit, path=None):
    """
    Tìm kiếm giới hạn chiều sâu (Depth-Limited Search)
    
    Mã giả:
        frontier ← a LIFO queue (stack) with NODE(problem.INITIAL) as an element
        result ← failure
        
        while not IS-EMPTY(frontier) do
            node ← POP(frontier)
            if problem.Is-GOAL(node.STATE) then return node
            if DEPTH(node) >= l then
                result ← cutoff
            else if not IS-CYCLE(node) do
                for each child in EXPAND(problem, node) do
                    add child to frontier
                    
        return result
    """
    # Tìm kiếm giới hạn chiều sâu (lặp) sử dụng frontier LIFO (stack)
    # Mỗi phần tử của stack là tuple: (state, path, depth)
    stack = [(start_state, [start_state], 0)]
    cutoff_occurred = False

    while stack:
        current_state, current_path, depth = stack.pop()

        # Kiểm tra đích khi nút được lấy ra (theo mã giả)
        if is_goal(current_state):
            return current_path, False

        # Nếu đạt giới hạn độ sâu, đánh dấu cutoff và không mở rộng nút
        if depth >= limit:
            cutoff_occurred = True
            continue

        # Mở rộng nút và thêm các con vào frontier (LIFO)
        current_path_tuples = {matrix_to_tuple(s) for s in current_path}
        for neighbor in get_neighbors(current_state):
            neighbor_tuple = matrix_to_tuple(neighbor)

            # Tránh vòng lặp (bỏ qua nếu neighbor đã có trong đường đi hiện tại)
            if neighbor_tuple in current_path_tuples:
                continue

            stack.append((neighbor, current_path + [neighbor], depth + 1))

    return None, cutoff_occurred


def iterative_deepening_search(start_state):
    """
    Tìm kiếm theo chiều sâu dần (Iterative Deepening Search)
    
    Mã giả (ITERATIVE-DEEPENING-SEARCH):
        for depth = 0 to ∞ do
            result ← DEPTH-LIMITED-SEARCH(problem, depth)
            if result ≠ cutoff then return result
    """
    stats = {
        'nodes_expanded': 0,
        'nodes_created': 1,
        'frontier_max': 0,
        'iterations': 0,
    }
    
    # Thử từng độ sâu tăng dần
    for depth in range(100):  # Giới hạn tối đa để tránh vòng lặp vô hạn
        stats['iterations'] = depth + 1
        
        if is_goal(start_state):
            return [start_state], stats
        
        result, cutoff = depth_limited_search(start_state, depth)
        
        if result is not None:
            stats['nodes_created'] += len(result)
            stats['nodes_expanded'] += 1
            return result, stats
        
        if not cutoff:
            # Không có giải pháp
            return None, stats
    
    return None, stats


# ==================== GIAO DIỆN GAME ====================
class PuzzleGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle - Solver")
        # Start the window maximized / fullscreen so algorithm names are clear
        try:
            # Prefer maximizing on Windows
            self.root.state('zoomed')
        except Exception:
            try:
                self.root.attributes('-fullscreen', True)
            except Exception:
                pass
        self.root.resizable(True, True)
        
        self.current_state = [row[:] for row in INITIAL_STATE]
        self.solution_path = None
        self.solution_step = 0
        self.tile_buttons = []
        self.algorithm_stats = {}
        self.start_matrix_count = tk.IntVar(value=2)
        self.observation_mask = tk.StringVar(value="default")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Khung chính cho tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.main_tab = ttk.Frame(self.notebook)
        self.complex_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Giao diện chính")
        self.notebook.add(self.complex_tab, text="Môi Trường Phức Tạp")

        main_frame = ttk.Frame(self.main_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tiêu đề
        title_label = ttk.Label(main_frame, text="8 PUZZLE SOLVER", 
                       font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Bên trái: Ma trận ban đầu và ma trận đích
        left_frame = ttk.LabelFrame(main_frame, text="TRÒ CHƠI")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        left_frame.configure(width=680)
        
        matrix_frame = ttk.Frame(left_frame)
        matrix_frame.pack(pady=5)
        
        start_frame = ttk.LabelFrame(matrix_frame, text="Trạng thái ban đầu")
        start_frame.pack(side=tk.LEFT, padx=5)
        
        self.tile_buttons = []
        for i in range(3):
            row_buttons = []
            for j in range(3):
                btn = tk.Button(start_frame, font=("Arial", 17, "bold"),
                              width=7, height=3, bg="#4CAF50", fg="white",
                              command=lambda x=i, y=j: self.click_tile(x, y))
                btn.grid(row=i, column=j, padx=4, pady=3)
                row_buttons.append(btn)
            self.tile_buttons.append(row_buttons)
        
        goal_frame = ttk.LabelFrame(matrix_frame, text="Ma trận đích")
        goal_frame.pack(side=tk.LEFT, padx=5)
        
        self.goal_tile_labels = []
        for i in range(3):
            row_labels = []
            for j in range(3):
                lbl = tk.Label(goal_frame, font=("Arial", 17, "bold"),
                               width=7, height=3, bg="#555555", fg="white", relief=tk.RIDGE)
                lbl.grid(row=i, column=j, padx=4, pady=3)
                row_labels.append(lbl)
            self.goal_tile_labels.append(row_labels)
        
        self.update_display()
        self.update_goal_display()
        self.build_complex_tab()
        
        # Nút điều khiển
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="🔀 Xáo Trộn", 
                   command=self.shuffle_puzzle).pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="🔄 Reset", 
                   command=self.reset_puzzle).pack(side=tk.LEFT, padx=3)
        
        # Nút giải (thuật toán)
        solver_label = ttk.Label(left_frame, text="Chọn Thuật Toán", font=("Arial", 11, "bold"))
        solver_label.pack(pady=5)
        
        solver_container = ttk.Frame(left_frame)
        solver_container.pack(pady=5, fill=tk.X, padx=10)

        self.uninformed_open = True
        self.informed_open = True
        self.local_open = True

        groups_container = ttk.Frame(solver_container)
        groups_container.pack(fill=tk.X)

        self.uninformed_group = ttk.Frame(groups_container)
        self.uninformed_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.uninformed_toggle_button = ttk.Button(
            self.uninformed_group,
            text="▼ Uninformed Search Algorithms",
            command=self.toggle_uninformed_algorithms
        )
        self.uninformed_toggle_button.pack(fill=tk.X, pady=(0, 3))

        self.uninformed_frame = ttk.Frame(self.uninformed_group, height=100)
        self.uninformed_frame.pack(fill=tk.BOTH, expand=True)
        self.uninformed_frame.pack_propagate(False)

        main_canvas = tk.Canvas(self.uninformed_frame, borderwidth=0, highlightthickness=0, height=120)
        main_scrollbar = ttk.Scrollbar(self.uninformed_frame, orient=tk.VERTICAL, command=main_canvas.yview)
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        main_buttons_frame = ttk.Frame(main_canvas)
        main_canvas.create_window((0, 0), window=main_buttons_frame, anchor='nw')
        main_buttons_frame.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox('all')))

        ttk.Button(main_buttons_frame, text="✓ BFS (Check on Pop)", 
                   command=lambda: self.solve("CHECK_ON_POP")).pack(pady=2, fill=tk.X)
        ttk.Button(main_buttons_frame, text="✓ BFS (Check on Push)", 
                   command=lambda: self.solve("CHECK_ON_PUSH")).pack(pady=2, fill=tk.X)
        ttk.Button(main_buttons_frame, text="✓ DFS (Deep First Search)", 
                   command=lambda: self.solve("DFS")).pack(pady=2, fill=tk.X)
        ttk.Button(main_buttons_frame, text="✓ DFS (Check Frontier)", 
                   command=lambda: self.solve("DFS_FRONTIER")).pack(pady=2, fill=tk.X)
        ttk.Button(main_buttons_frame, text="✓ UCS (Misplaced Tiles)", 
                   command=lambda: self.solve("UCS")).pack(pady=2, fill=tk.X)
        ttk.Button(main_buttons_frame, text="✓ IDS (Iterative Deepening Search)", 
                   command=lambda: self.solve("IDS")).pack(pady=2, fill=tk.X)

        self.informed_group = ttk.Frame(groups_container)
        self.informed_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.informed_toggle_button = ttk.Button(
            self.informed_group,
            text="▼ Informed Search Algorithms",
            command=self.toggle_informed_algorithms
        )
        self.informed_toggle_button.pack(fill=tk.X, pady=(0, 3))

        self.informed_frame = ttk.Frame(self.informed_group, height=100)
        self.informed_frame.pack(fill=tk.BOTH, expand=True)
        self.informed_frame.pack_propagate(False)

        greedy_canvas = tk.Canvas(self.informed_frame, borderwidth=0, highlightthickness=0, height=100)
        greedy_scrollbar = ttk.Scrollbar(self.informed_frame, orient=tk.VERTICAL, command=greedy_canvas.yview)
        greedy_canvas.configure(yscrollcommand=greedy_scrollbar.set)
        greedy_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        greedy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        greedy_buttons_frame = ttk.Frame(greedy_canvas)
        greedy_canvas.create_window((0, 0), window=greedy_buttons_frame, anchor='nw')
        greedy_buttons_frame.bind('<Configure>', lambda e: greedy_canvas.configure(scrollregion=greedy_canvas.bbox('all')))

        ttk.Button(greedy_buttons_frame, text="✓ Greedy (Misplaced Tiles)", 
                   command=lambda: self.solve("GREEDY")).pack(pady=2, fill=tk.X)
        ttk.Button(greedy_buttons_frame, text="✓ A* (Misplaced Tiles)", 
               command=lambda: self.solve("ASTAR")).pack(pady=2, fill=tk.X)
        ttk.Button(greedy_buttons_frame, text="✓ IDA* (Misplaced Tiles)", 
           command=lambda: self.solve("IDASTAR")).pack(pady=2, fill=tk.X)

        # ================= Local Search Group =================
        self.local_group = ttk.Frame(groups_container)
        self.local_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.local_toggle_button = ttk.Button(
            self.local_group,
            text="▼ Local Search Algorithms",
            command=self.toggle_local_algorithms
        )
        self.local_toggle_button.pack(fill=tk.X, pady=(0, 3))

        self.local_frame = ttk.Frame(self.local_group, height=150)
        self.local_frame.pack(fill=tk.BOTH, expand=True)
        self.local_frame.pack_propagate(False)

        local_canvas = tk.Canvas(self.local_frame, borderwidth=0, highlightthickness=0, height=140)
        local_scrollbar = ttk.Scrollbar(self.local_frame, orient=tk.VERTICAL, command=local_canvas.yview)
        local_canvas.configure(yscrollcommand=local_scrollbar.set)
        local_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        local_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        local_buttons_frame = ttk.Frame(local_canvas)
        local_canvas.create_window((0, 0), window=local_buttons_frame, anchor='nw')
        local_buttons_frame.bind('<Configure>', lambda e: local_canvas.configure(scrollregion=local_canvas.bbox('all')))

        ttk.Button(local_buttons_frame, text="✓ Simple Hill Climbing (First-Improvement)", 
               command=lambda: self.solve("HILL")).pack(pady=2, fill=tk.X)
        ttk.Button(local_buttons_frame, text="✓ Steepest-Ascent Hill Climbing", 
               command=lambda: self.solve("STEPEST")).pack(pady=2, fill=tk.X)
        ttk.Button(local_buttons_frame, text="✓ Stochastic Hill Climbing", 
               command=lambda: self.solve("STOCHASTIC")).pack(pady=2, fill=tk.X)
        ttk.Button(local_buttons_frame, text="✓ Random-Restart Hill Climbing", 
               command=lambda: self.solve("RESTART")).pack(pady=2, fill=tk.X)
        ttk.Button(local_buttons_frame, text="✓ Simulated Annealing", 
               command=lambda: self.solve("SIMANN")).pack(pady=2, fill=tk.X)
        ttk.Button(local_buttons_frame, text="✓ Local Beam Search", 
               command=lambda: self.solve("BEAM")).pack(pady=2, fill=tk.X)

        # ================= CSP Group =================
        self.csp_group = ttk.Frame(groups_container)
        self.csp_group.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.csp_toggle_button = ttk.Button(
            self.csp_group,
            text="▼ CSP Algorithms",
            command=self.toggle_csp_algorithms
        )
        self.csp_toggle_button.pack(fill=tk.X, pady=(0, 3))

        self.csp_frame = ttk.Frame(self.csp_group, height=80)
        self.csp_frame.pack(fill=tk.BOTH, expand=True)
        self.csp_frame.pack_propagate(False)

        csp_canvas = tk.Canvas(self.csp_frame, borderwidth=0, highlightthickness=0, height=70)
        csp_scrollbar = ttk.Scrollbar(self.csp_frame, orient=tk.VERTICAL, command=csp_canvas.yview)
        csp_canvas.configure(yscrollcommand=csp_scrollbar.set)
        csp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        csp_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        csp_buttons_frame = ttk.Frame(csp_canvas)
        csp_canvas.create_window((0, 0), window=csp_buttons_frame, anchor='nw')
        csp_buttons_frame.bind('<Configure>', lambda e: csp_canvas.configure(scrollregion=csp_canvas.bbox('all')))

        ttk.Button(csp_buttons_frame, text="✓ CSP (Backtracking Search)",
                   command=lambda: self.solve("CSP")).pack(pady=2, fill=tk.X)
        ttk.Button(csp_buttons_frame, text="✓ CSP (Min-Conflicts)",
                   command=lambda: self.solve("MINCONFLICTS")).pack(pady=2, fill=tk.X)
        ttk.Button(csp_buttons_frame, text="✓ CSP (AC-3 Filtering)",
                   command=lambda: self.solve("AC3")).pack(pady=2, fill=tk.X)

        self.status_label = ttk.Label(left_frame, text="Trạng thái: Sẵn sàng", 
                          font=("Arial", 11))
        self.status_label.pack(pady=5)
        
        # Bên phải: Các trạng thái di chuyển
        right_frame = ttk.LabelFrame(main_frame, text="CÁC TRẠNG THÁI DI CHUYỂN")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8)
        
        self.stats_text = tk.Text(
            right_frame,
            height=26,
            width=58,
            font=("Courier", 11),
            relief=tk.SUNKEN,
            borderwidth=1,
            wrap=tk.NONE
        )
        self.stats_text.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # Hàng ngang dưới cùng: đường đi tốt nhất
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 6))
        
        path_label = ttk.Label(bottom_frame, text="Đường đi tốt nhất từ trạng thái ban đầu đến đích:", 
                               font=("Arial", 10, "bold"))
        path_label.pack(anchor=tk.W, pady=(0, 4))
        
        self.path_text = tk.Text(
            bottom_frame,
            height=2,
            font=("Arial", 12),
            relief=tk.SUNKEN,
            borderwidth=1,
            wrap=tk.WORD
        )
        self.path_text.pack(fill=tk.X)
        self.path_text.config(state=tk.DISABLED)
    
    def update_display(self):
        """Cập nhật hiển thị bảng đố"""
        for i in range(3):
            for j in range(3):
                value = self.current_state[i][j]
                if value == 0:
                    self.tile_buttons[i][j].config(text="", bg="#CCCCCC", state=tk.DISABLED)
                else:
                    self.tile_buttons[i][j].config(text=str(value), bg="#4CAF50", state=tk.NORMAL)
    
    def update_goal_display(self):
        """Cập nhật ma trận đích"""
        for i in range(3):
            for j in range(3):
                value = GOAL_STATE[i][j]
                if value == 0:
                    self.goal_tile_labels[i][j].config(text="", bg="#555555")
                else:
                    self.goal_tile_labels[i][j].config(text=str(value), bg="#555555")

    def build_complex_tab(self):
        """Xây dựng tab giao diện dành riêng cho môi trường phức tạp."""
        header_frame = ttk.Frame(self.complex_tab)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header_frame, text="Môi Trường Phức Tạp", font=("Arial", 14, "bold")).pack(anchor=tk.W)

        control_frame = ttk.Frame(self.complex_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(control_frame, text="Số ma trận bắt đầu:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.complex_count_spinbox = tk.Spinbox(control_frame, from_=2, to=2, textvariable=self.start_matrix_count, width=5, state='readonly')
        self.complex_count_spinbox.pack(side=tk.LEFT, padx=4)
        ttk.Button(control_frame, text="Tạo lại ma trận bắt đầu", command=self.refresh_complex_boards).pack(side=tk.LEFT, padx=8)
        ttk.Button(control_frame, text="◀ Quay lại giao diện ban đầu", command=self.return_to_main_tab).pack(side=tk.LEFT, padx=8)

        self.complex_description_label = ttk.Label(
            self.complex_tab,
            text="Các ma trận bắt đầu sẽ được tạo tương ứng với số ma trận start (tối đa 4). Chế độ Partial Observable chỉ đánh giá phần quan sát được.",
            font=("Arial", 9),
            wraplength=560,
            justify=tk.LEFT
        )
        self.complex_description_label.pack(fill=tk.X, padx=10)

        self.observation_mask_frame = ttk.LabelFrame(self.complex_tab, text="Chế độ quan sát một phần")
        self.observation_mask_frame_visible = False

        ttk.Radiobutton(self.observation_mask_frame, text="Mặc định (hàng trên + trung tâm + cuối)",
                        variable=self.observation_mask, value="default").pack(anchor=tk.W, padx=4, pady=2)
        ttk.Radiobutton(self.observation_mask_frame, text="Quan sát hàng đầu tiên",
                        variable=self.observation_mask, value="row0").pack(anchor=tk.W, padx=4, pady=2)
        ttk.Radiobutton(self.observation_mask_frame, text="Quan sát đường chéo",
                        variable=self.observation_mask, value="diag").pack(anchor=tk.W, padx=4, pady=2)

        button_frame = ttk.Frame(self.complex_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        ttk.Button(button_frame, text="✓ No Observation", command=lambda: self.solve("NO_OBSERVATION")).pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        ttk.Button(button_frame, text="✓ AND-OR Graph Search", command=lambda: self.solve("ANYF")).pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)
        self.partial_observable_button = ttk.Button(button_frame, text="✓ Partial Observable", command=self.prepare_partial_observable)
        self.partial_observable_button.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)

        self.complex_action_label = ttk.Label(self.complex_tab, text="", font=("Arial", 10, "italic"))
        self.complex_action_label.pack(fill=tk.X, padx=10, pady=(4, 8))

        complex_visual_frame = ttk.Frame(self.complex_tab)
        complex_visual_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        parent_frame = ttk.Frame(complex_visual_frame)
        parent_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), anchor=tk.N)

        self.parent_matrix_frame = ttk.LabelFrame(parent_frame, text="Ma trận cha (Parent Matrix)")
        self.parent_matrix_frame.pack(side=tk.TOP, fill=tk.Y, padx=(0, 0), pady=(0, 6))

        self.parent_matrix_labels = []
        for i in range(3):
            row_labels = []
            for j in range(3):
                lbl = tk.Label(self.parent_matrix_frame, text="", font=("Arial", 12, "bold"),
                               width=4, height=2, bg="#4CAF50" if (i + j) % 2 == 0 else "#8BC34A",
                               fg="white", relief=tk.RIDGE)
                lbl.grid(row=i, column=j, padx=2, pady=2)
                row_labels.append(lbl)
            self.parent_matrix_labels.append(row_labels)

        self.parent_matrix_info = ttk.Label(
            parent_frame,
            text="Ma trận cha hiển thị trạng thái gốc dùng làm điểm xuất phát cho môi trường phức tạp.",
            font=("Arial", 9),
            wraplength=420,
            justify=tk.LEFT
        )
        self.parent_matrix_info.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)

        child_frame = ttk.Frame(complex_visual_frame)
        child_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.complex_board_canvas = tk.Canvas(child_frame, borderwidth=0, highlightthickness=0)
        self.complex_board_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.complex_board_scrollbar = ttk.Scrollbar(child_frame, orient=tk.VERTICAL, command=self.complex_board_canvas.yview)
        self.complex_board_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.complex_board_canvas.configure(yscrollcommand=self.complex_board_scrollbar.set)

        self.complex_board_inner = ttk.Frame(self.complex_board_canvas)
        self.complex_board_canvas.create_window((0, 0), window=self.complex_board_inner, anchor='nw')
        self.complex_board_inner.bind('<Configure>', lambda e: self.complex_board_canvas.configure(scrollregion=self.complex_board_canvas.bbox('all')))

        self.complex_state_frames = []
        self.complex_result_frame = ttk.LabelFrame(self.complex_tab, text="Kết quả môi trường phức tạp")
        self.complex_result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        # Left: statistics summary; Right: two solution panes side-by-side
        self.complex_stats_text = tk.Text(
            self.complex_result_frame,
            height=15,
            width=48,
            font=("Courier", 10),
            relief=tk.SUNKEN,
            borderwidth=1,
            wrap=tk.NONE
        )
        self.complex_stats_text.pack(fill=tk.BOTH, expand=False, side=tk.LEFT)
        complex_text_scroll = ttk.Scrollbar(self.complex_result_frame, orient=tk.VERTICAL, command=self.complex_stats_text.yview)
        complex_text_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.complex_stats_text.configure(yscrollcommand=complex_text_scroll.set)

        # Solutions frame (two panes side-by-side)
        self.complex_solutions_container = ttk.Frame(self.complex_result_frame)
        self.complex_solutions_container.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        self.complex_solution_texts = []
        for i in range(2):
            t = tk.Text(self.complex_solutions_container, height=15, width=48, font=("Courier", 10), relief=tk.SUNKEN, borderwidth=1, wrap=tk.NONE)
            t.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if i==0 else 6, 0))
            scroll = ttk.Scrollbar(self.complex_solutions_container, orient=tk.VERTICAL, command=t.yview)
            scroll.pack(side=tk.LEFT, fill=tk.Y)
            t.configure(yscrollcommand=scroll.set)
            self.complex_solution_texts.append(t)
        self.refresh_complex_boards()

    def update_parent_matrix(self, state):
        """Cập nhật ma trận cha hiển thị trong tab môi trường phức tạp."""
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                lbl = self.parent_matrix_labels[i][j]
                if value == 0:
                    lbl.config(text="", bg="#CCCCCC", fg="white")
                else:
                    lbl.config(text=str(value), bg="#4CAF50", fg="white")

    def refresh_complex_boards(self):
        """Tạo và cập nhật các bảng ma trận bắt đầu trong tab phức tạp."""
        for child in self.complex_board_inner.winfo_children():
            child.destroy()
        self.complex_state_frames.clear()

        start_count = 2
        self.start_matrix_count.set(start_count)
        self.complex_start_states = generate_complex_start_states([row[:] for row in self.current_state], start_count)

        for idx, state in enumerate(self.complex_start_states, start=1):
            frame = ttk.LabelFrame(self.complex_board_inner, text=f"Ma trận bắt đầu {idx}")
            frame.grid(row=(idx - 1) // 4, column=(idx - 1) % 4, padx=8, pady=8, sticky=tk.N)
            for i in range(3):
                for j in range(3):
                    value = state[i][j]
                    label = tk.Label(frame, text=str(value) if value != 0 else "_",
                                     font=("Arial", 12, "bold"), width=4, height=2,
                                     bg="#4CAF50" if value != 0 else "#CCCCCC", fg="white", relief=tk.RAISED)
                    label.grid(row=i, column=j, padx=2, pady=2)
            self.complex_state_frames.append(frame)

        self.complex_board_canvas.update_idletasks()
        self.complex_board_canvas.configure(scrollregion=self.complex_board_canvas.bbox('all'))
        self.update_parent_matrix([row[:] for row in self.current_state])

    def toggle_uninformed_algorithms(self):
        """Ẩn/hiện khung thuật toán Uninformed."""
        if self.uninformed_open:
            self.uninformed_frame.pack_forget()
            self.uninformed_toggle_button.config(text="▶ Uninformed Search Algorithms")
        else:
            self.uninformed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            self.uninformed_toggle_button.config(text="▼ Uninformed Search Algorithms")
        self.uninformed_open = not self.uninformed_open

    def toggle_informed_algorithms(self):
        """Ẩn/hiện khung thuật toán Informed."""
        if self.informed_open:
            self.informed_frame.pack_forget()
            self.informed_toggle_button.config(text="▶ Informed Search Algorithms")
        else:
            self.informed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.informed_toggle_button.config(text="▼ Informed Search Algorithms")
        self.informed_open = not self.informed_open

    def toggle_local_algorithms(self):
        """Ẩn/hiện khung thuật toán Local Search."""
        if self.local_open:
            self.local_frame.pack_forget()
            self.local_toggle_button.config(text="▶ Local Search Algorithms")
        else:
            self.local_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.local_toggle_button.config(text="▼ Local Search Algorithms")
        self.local_open = not self.local_open

    def toggle_csp_algorithms(self):
        """Ẩn/hiện khung thuật toán CSP."""
        if self.csp_frame.winfo_ismapped():
            self.csp_frame.pack_forget()
            self.csp_toggle_button.config(text="▶ CSP Algorithms")
        else:
            self.csp_frame.pack(fill=tk.BOTH, expand=True)
            self.csp_toggle_button.config(text="▼ CSP Algorithms")

    def toggle_complex_algorithms(self):
        """Chuyển sang tab môi trường phức tạp hoặc quay lại tab chính."""
        current_tab = self.notebook.select()
        if current_tab == str(self.complex_tab):
            self.notebook.select(self.main_tab)
            self.complex_toggle_button.config(text="▼ Môi Trường Phức Tạp")
        else:
            self.notebook.select(self.complex_tab)
            self.complex_toggle_button.config(text="◀ Quay lại giao diện chính")
            self.refresh_complex_boards()

    def return_to_main_tab(self):
        """Quay lại giao diện chính từ tab môi trường phức tạp."""
        self.notebook.select(self.main_tab)
        self.complex_toggle_button.config(text="▼ Môi Trường Phức Tạp")

    def prepare_partial_observable(self):
        """Hiện chế độ quan sát một phần và chạy khi người dùng bấm lại."""
        if not self.observation_mask_frame_visible:
            self.observation_mask_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
            self.observation_mask_frame_visible = True
            self.partial_observable_button.config(text="▶ Giải Partial Observable")
            self.complex_action_label.config(text="Chọn chế độ quan sát một phần rồi nhấn lại Partial Observable")
            return
        self.solve("PARTIAL_OBSERVABLE")

    def set_best_path(self, path):
        """Hiển thị đường đi tốt nhất ở hàng dưới cùng"""
        move_sequence = format_move_sequence(path) if path else ""
        self.path_text.config(state=tk.NORMAL)
        self.path_text.delete(1.0, tk.END)
        self.path_text.insert(tk.END, move_sequence)
        self.path_text.config(state=tk.DISABLED)
    
    def click_tile(self, i, j):
        """Xử lý click trên ô"""
        zero_i, zero_j = find_zero(self.current_state)
        
        if (abs(i - zero_i) == 1 and j == zero_j) or \
           (abs(j - zero_j) == 1 and i == zero_i):
            self.current_state[zero_i][zero_j], self.current_state[i][j] = \
            self.current_state[i][j], self.current_state[zero_i][zero_j]
            self.update_display()
            
            if is_goal(self.current_state):
                self.status_label.config(text="🎉 Thành công! Bạn đã giải được đố!")
    
    def shuffle_puzzle(self):
        """Xáo trộn puzzle"""
        
        import random
        
        state = [row[:] for row in GOAL_STATE]

        for _ in range(50):
            neighbors = get_neighbors(state)
            state = random.choice(neighbors)

        self.current_state = state
        self.solution_path = None
        self.solution_step = 0

        self.update_display()
        self.update_parent_matrix(self.current_state)

        self.status_label.config(text="Đã xáo trộn")
        self.stats_text.delete(1.0, tk.END)
    
    def reset_puzzle(self):
        """Reset puzzle"""
        self.current_state = [row[:] for row in INITIAL_STATE]
        self.solution_path = None
        self.solution_step = 0
        self.update_display()
        self.update_parent_matrix(self.current_state)
        self.status_label.config(text="Đã reset")
        self.stats_text.delete(1.0, tk.END)
    
    def solve(self, algorithm):
        """Giải puzzle"""
        self.status_label.config(text=f"Đang giải ({algorithm})...")
        self.root.update()
        
        try:
            start_time = time.time()
            
            if algorithm == "CHECK_ON_POP":
                solution, stats = bfs_check_on_pop([row[:] for row in self.current_state])
            elif algorithm == "ANYF":
                solution, stats = and_or_graph_search_solver([row[:] for row in self.current_state])
            elif algorithm == "CHECK_ON_PUSH":
                solution, stats = bfs_check_on_push([row[:] for row in self.current_state])
            elif algorithm == "DFS":
                solution, stats = deep_first_search([row[:] for row in self.current_state])
            elif algorithm == "DFS_FRONTIER":
                solution, stats = deep_first_search_check_frontier([row[:] for row in self.current_state])
            elif algorithm == "UCS":
                solution, stats = uniform_cost_search([row[:] for row in self.current_state])
            elif algorithm == "ASTAR":
                solution, stats = a_star_search([row[:] for row in self.current_state])
            elif algorithm == "IDASTAR":
                solution, stats = ida_star_search([row[:] for row in self.current_state])
            elif algorithm == "HILL":
                solution, stats = simple_hill_climbing([row[:] for row in self.current_state])
            elif algorithm == "STEPEST":
                solution, stats = steepest_ascent_hill_climbing([row[:] for row in self.current_state])
            elif algorithm == "STOCHASTIC":
                solution, stats = stochastic_hill_climbing([row[:] for row in self.current_state])
            elif algorithm == "RESTART":
                solution, stats = random_restart_hill_climbing([row[:] for row in self.current_state], max_restarts=10)
            elif algorithm == "SIMANN":
                solution, stats = simulated_annealing([row[:] for row in self.current_state], T0=1.0, Tmin=1e-6, alpha=0.95)
            elif algorithm == "BEAM":
                solution, stats = local_beam_search([row[:] for row in self.current_state], k=4)
            elif algorithm == "GREEDY":
                solution, stats = greedy_search([row[:] for row in self.current_state])
            elif algorithm == "CSP":
                solution, stats = csp_backtracking_search([row[:] for row in self.current_state])
            elif algorithm == "MINCONFLICTS":
                solution, stats = min_conflicts_csp([row[:] for row in self.current_state], max_steps=2000)
            elif algorithm == "AC3":
                solution, stats = csp_ac3_backtracking_search([row[:] for row in self.current_state])
            elif algorithm == "NO_OBSERVATION":
                self.complex_action_label.config(
                    text=f"Đang chạy No Observation với {self.start_matrix_count.get()} ma trận bắt đầu..."
                )
                solution, stats = no_observation_environment(self.start_matrix_count.get(), [row[:] for row in self.current_state])
            elif algorithm == "PARTIAL_OBSERVABLE":
                mask_type = self.observation_mask.get()
                self.complex_action_label.config(
                    text=f"Đang chạy Partial Observable ({mask_type}) với {self.start_matrix_count.get()} ma trận bắt đầu..."
                )
                solution, stats = partial_observable_environment(self.start_matrix_count.get(), [row[:] for row in self.current_state], mask_type=mask_type)
            else:  # IDS
                solution, stats = iterative_deepening_search([row[:] for row in self.current_state])
            
            elapsed_time = time.time() - start_time
            self.algorithm_stats[algorithm] = stats

            if algorithm == "NO_OBSERVATION":
                self.solution_path = None
                self.solution_step = 0
                self.display_no_observation_statistics(stats, elapsed_time)
                self.status_label.config(text="✓ No Observation đã hoàn thành")
            elif algorithm == "ANYF":
                self.solution_path = None
                self.solution_step = 0
                self.display_statistics(algorithm, stats, elapsed_time, solution)
                self.status_label.config(text="✓ AND-OR Graph Search đã hoàn thành")
            elif algorithm == "PARTIAL_OBSERVABLE":
                self.solution_path = None
                self.solution_step = 0
                self.display_partial_observable_statistics(stats, elapsed_time)
                self.status_label.config(text="✓ Partial Observable đã hoàn thành")
            elif algorithm == "CSP":
                self.solution_path = None
                self.solution_step = 0
                if solution:
                    self.current_state = [row[:] for row in solution]
                    self.update_display()
                self.display_statistics(algorithm, stats, elapsed_time, solution)
                self.status_label.config(text="✓ CSP (Backtracking) đã hoàn thành")
            elif algorithm == "AC3":
                self.solution_path = None
                self.solution_step = 0
                if solution:
                    self.current_state = [row[:] for row in solution]
                    self.update_display()
                    self.status_label.config(text="✓ CSP (AC-3) + Backtracking đã hoàn thành")
                else:
                    self.status_label.config(text="✗ AC-3/Backtracking không tìm được cấu hình")
                self.display_statistics(algorithm, stats, elapsed_time, solution)
            elif algorithm == "MINCONFLICTS":
                # Min-Conflicts trả về một bàn cờ CSP hoàn chỉnh, không phải
                # danh sách trạng thái để animate như BFS/A*/DFS.
                self.solution_path = None
                self.solution_step = 0
                if solution:
                    self.current_state = [row[:] for row in solution]
                    self.update_display()
                    self.status_label.config(
                        text=f"✓ Min-Conflicts hoàn thành sau {stats.get('steps', 0)} bước"
                    )
                else:
                    self.status_label.config(text="✗ Min-Conflicts không tìm được cấu hình")
                self.display_statistics(algorithm, stats, elapsed_time, solution)
            elif solution:
                self.solution_path = solution
                self.solution_step = 0
                self.current_state = [row[:] for row in self.solution_path[0]]
                self.update_display()
                self.display_statistics(algorithm, stats, elapsed_time, solution)
                self.set_best_path(solution)
                self.status_label.config(text=f"✓ Đã tìm lời giải ({len(solution) - 1} bước), đang chạy tự động...")
                self.root.after(500, self.animate_solution)
            else:
                if algorithm in ("NO_OBSERVATION", "PARTIAL_OBSERVABLE"):
                    self.display_statistics(algorithm, stats, elapsed_time, solution)
                    self.set_best_path(None)
                    attempted = stats.get('attempted_steps', 0)
                    self.status_label.config(text=f"✗ Chưa giải được sau {attempted} bước")
                else:
                    messagebox.showerror("Lỗi", "Không tìm được lời giải!")
                    self.status_label.config(text="✗ Không tìm được lời giải")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
    
    def display_statistics(self, algorithm, stats, elapsed_time, solution):
        """Hiển thị các trạng thái di chuyển và thống kê"""
        target_text = self.complex_stats_text if algorithm in ("NO_OBSERVATION", "PARTIAL_OBSERVABLE", "ANYF") else self.stats_text
        target_text.config(state=tk.NORMAL)
        target_text.delete(1.0, tk.END)
        
        if algorithm == "CHECK_ON_POP":
            algorithm_name = "BFS (Check on Pop)"
        elif algorithm == "CHECK_ON_PUSH":
            algorithm_name = "BFS (Check on Push)"
        elif algorithm == "DFS":
            algorithm_name = "DFS (Deep First Search)"
        elif algorithm == "DFS_FRONTIER":
            algorithm_name = "DFS (Check Frontier)"
        elif algorithm == "UCS":
            algorithm_name = "UCS (Misplaced Tiles)"
        elif algorithm == "ASTAR":
            algorithm_name = "A* (Misplaced Tiles)"
        elif algorithm == "IDASTAR":
            algorithm_name = "IDA* (Misplaced Tiles)"
        elif algorithm == "GREEDY":
            algorithm_name = "Greedy (Misplaced Tiles)"
        elif algorithm == "HILL":
            algorithm_name = "Simple Hill Climbing (Local Search)"
        elif algorithm == "STEPEST":
            algorithm_name = "Steepest-Ascent Hill Climbing (Local Search)"
        elif algorithm == "STOCHASTIC":
            algorithm_name = "Stochastic Hill Climbing (Local Search)"
        elif algorithm == "RESTART":
            algorithm_name = "Random-Restart Hill Climbing (Local Search)"
        elif algorithm == "SIMANN":
            algorithm_name = "Simulated Annealing (Local Search)"
        elif algorithm == "BEAM":
            algorithm_name = "Local Beam Search (Local Search)"
        elif algorithm == "CSP":
            algorithm_name = "CSP (Backtracking Search)"
        elif algorithm == "AC3":
            algorithm_name = "CSP AC-3 (Arc Consistency)"
        elif algorithm == "MINCONFLICTS":
            algorithm_name = "CSP Min-Conflicts"
        elif algorithm == "NO_OBSERVATION":
            algorithm_name = "No Observation (Complex Environment)"
        elif algorithm == "PARTIAL_OBSERVABLE":
            algorithm_name = "Partial Observable (Complex Environment)"
        elif algorithm == "ANYF":
            algorithm_name = "AND-OR Graph Search"
        else:
            algorithm_name = "IDS (Iterative Deepening Search)"
        
        if algorithm == "NO_OBSERVATION" and 'solutions' in stats:
            move_steps = sum((len(item['solution']) - 1) for item in stats['solutions'] if item['solution'])
        elif algorithm == "ANYF":
            move_steps = 0
            if isinstance(solution, (list, tuple, dict)):
                move_steps = len(solution)
        elif algorithm == "AC3":
            move_steps = 0
        elif algorithm == "MINCONFLICTS":
            move_steps = stats.get('steps', 0)
        else:
            move_steps = len(solution) - 1 if isinstance(solution, (list, tuple)) and solution else stats.get('attempted_steps', 0)
        text_content = f"""
╔══════════════════════════════════════════════╗
║    Thuật Toán: {algorithm_name:<25}     ║
╚══════════════════════════════════════════════╝

📊 KẾT QUẢ:
   • Số bước di chuyển: {move_steps}
   • Thời gian: {elapsed_time:.4f}s

📈 THỐNG KÊ THUẬT TOÁN:
   • Nút được mở rộng: {stats['nodes_expanded']}
   • Nút được tạo: {stats['nodes_created']}
   • Frontier tối đa: {stats['frontier_max']}
"""
        
        if 'start_count' in stats:
            text_content += f"   • Số ma trận bắt đầu: {stats['start_count']}\n"
            text_content += f"   • Số ma trận giải được: {stats['solved_count']}\n"
        if 'mask_type' in stats:
            text_content += f"   • Chế độ quan sát: {stats['mask_type']}\n"
        if 'goal_checks' in stats:
            text_content += f"   • Lần kiểm tra đích: {stats['goal_checks']}\n"
        if algorithm == "CSP":
            text_content += f"   • Số lần vi phạm ràng buộc: {stats.get('constraint_violations', 0)}\n"
            text_content += f"   • Số lần quay lui: {stats.get('backtracks', 0)}\n"
        
        if 'iterations' in stats:
            text_content += f"   • Số lần lặp (độ sâu tối đa): {stats['iterations']}\n"
        if 'temperature_steps' in stats:
            text_content += f"   • Số bước nhiệt độ: {stats['temperature_steps']}\n"
        if 'trials' in stats:
            text_content += f"   • Số lần thử: {stats['trials']}\n"
        if 'restarts' in stats:
            text_content += f"   • Số lần khởi động lại: {stats['restarts']}\n"
        if 'beams' in stats:
            text_content += f"   • Kích thước beam: {stats['beams']}\n"
        
        if algorithm == "UCS" and 'solution_costs' in stats:
            text_content += f"\n   • Tổng chi phí: {stats['total_cost']}\n"
        if algorithm == "ASTAR" and 'solution_costs' in stats:
            text_content += f"\n   • Giá trị f(n): {stats['total_cost']}\n"
        if algorithm in ["ASTAR", "IDASTAR"] and 'solution_costs' in stats:
            text_content += f"\n   • Giá trị f(n): {stats['total_cost']}\n"
        text_content += "\n╔═══════════════════════════════════════╗\n"
        text_content += "║       Các trạng thái di chuyển        ║\n"
        text_content += "╚═══════════════════════════════════════╝\n\n"

        if algorithm == "ANYF":
            text_content += "\n📌 Kế hoạch AND-OR (đã mô tả theo thuật toán):\n"
            if solution == FAILURE:
                text_content += "   • Trạng thái: Không tìm được lời giải theo AND-OR graph search\n"
            else:
                text_content += "\n"
                text_content += format_and_or_tree(solution)
            text_content += "\n"
        elif algorithm == "CSP":
            text_content += "\n📜 Nhật ký Backtracking CSP (Console Log):\n"
            logs = stats.get('csp_log', [])
            if logs:
                text_content += "\n".join(f"   {line}" for line in logs)
            else:
                text_content += "   • Chưa có nhật ký thử nghiệm CSP."
            text_content += "\n"
        elif algorithm == "AC3":
            text_content += "\n📜 Nhật ký AC-3 (Arc Consistency):\n"
            logs = stats.get('csp_log', [])
            if logs:
                text_content += "\n".join(f"   {line}" for line in logs)
            else:
                text_content += "   • Chưa có nhật ký AC-3."
            text_content += "\n\n📦 Miền sau khi AC-3 lọc:\n"
            final_domains = stats.get('final_domains', {})
            for var, domain in final_domains.items():
                text_content += f"   • {var}: {domain}\n"
            text_content += "\n"
            text_content += f"   • Giá trị đã loại: {stats.get('values_pruned', 0)}\n"
            text_content += f"   • Miền trung bình: {stats.get('average_domain_size', 0.0):.2f} giá trị/ô\n"
            text_content += f"   • Số lần sửa đổi miền: {stats.get('revisions', 0)}\n"
            text_content += f"   • Arc-consistent: {'Có' if stats.get('is_arc_consistent') else 'Không'}\n"
            text_content += "\n"
        elif algorithm == "MINCONFLICTS":
            text_content += "\n📜 Nhật ký Min-Conflicts CSP:\n"
            logs = stats.get('csp_log', [])
            if logs:
                text_content += "\n".join(f"   {line}" for line in logs)
            else:
                text_content += "   • Chưa có nhật ký Min-Conflicts."
            text_content += "\n"
            text_content += f"   • Số bước: {stats.get('steps', 0)} / {stats.get('max_steps', 0)}\n"
            text_content += f"   • Xung đột ban đầu: {stats.get('initial_conflicts', 0)}\n"
            text_content += f"   • Xung đột cuối: {stats.get('final_conflicts', 0)}\n"
            text_content += f"   • Nút tạo: {stats.get('nodes_created', 0)}\n"
            text_content += f"   • Nút mở rộng: {stats.get('nodes_expanded', 0)}\n"
            text_content += "\n"
        elif solution:
            if algorithm in ("GREEDY", "HILL", "STEPEST", "STOCHASTIC", "RESTART", "BEAM", "SIMANN"):
                text_content += format_solution_steps(
                    solution,
                    stats.get('solution_costs'),
                    cost_label="Giá trị h(n)"
                )
            elif algorithm == "ASTAR":
                text_content += format_solution_steps(
                    solution,
                    stats.get('solution_costs'),
                    cost_label="Giá trị f(n)"
                )
            elif algorithm in ["ASTAR", "IDASTAR"]:
                text_content += format_solution_steps(
                    solution,
                    stats.get('solution_costs'),
                    cost_label="Giá trị f(n)"
                )
            else:
                text_content += format_solution_steps(
                    solution,
                    stats.get('solution_costs')
                )
        else:
            if algorithm in ("NO_OBSERVATION", "PARTIAL_OBSERVABLE"):
                attempted_steps = stats.get('attempted_steps', 0)
                text_content += f"   • Trạng thái: Chưa giải được sau {attempted_steps} bước thử\n"
            else:
                text_content += "   • Trạng thái: Không tìm được lời giải\n"
        
        target_text.insert(1.0, text_content)
        target_text.config(state=tk.DISABLED)

    def display_no_observation_statistics(self, stats, elapsed_time):
        self.complex_stats_text.config(state=tk.NORMAL)
        self.complex_stats_text.delete(1.0, tk.END)

        algorithm_name = "No Observation (Complex Environment)"
        total_moves = sum((len(item['solution']) - 1) for item in stats.get('solutions', []) if item['solution'])
        text_content = f"""
╔══════════════════════════════════════════════╗
║    Thuật Toán: {algorithm_name:<25}     ║
╚══════════════════════════════════════════════╝

📊 KẾT QUẢ:
   • Tổng số bước di chuyển: {total_moves}
   • Thời gian: {elapsed_time:.4f}s

📈 THỐNG KÊ THUẬT TOÁN:
   • Số ma trận bắt đầu: {stats.get('start_count', 0)}
   • Số ma trận giải được: {stats.get('solved_count', 0)}
   • Nút được mở rộng: {stats.get('nodes_expanded', 0)}
   • Nút được tạo: {stats.get('nodes_created', 0)}
   • Frontier tối đa: {stats.get('frontier_max', 0)}
   • Lần kiểm tra đích: {stats.get('goal_checks', 0)}
"""

        for solution_info in stats.get('solutions', []):
            index = solution_info['index']
            solved = solution_info['solved']
            solution_path = solution_info['solution']
            text_content += f"\n--- Ma trận bắt đầu {index} ---\n"
            text_content += f"   • Giải được: {'Có' if solved else 'Không'}\n"
            if solved and solution_path:
                text_content += f"   • Số bước: {len(solution_path) - 1}\n"
                text_content += format_solution_steps(solution_path, solution_info['stats'].get('solution_costs'), cost_label="Chi phí g(n)")
            else:
                text_content += "   • Trạng thái: Không tìm được lời giải\n"

        self.complex_stats_text.insert(1.0, text_content)
        self.complex_stats_text.config(state=tk.DISABLED)

        # Fill the two solution panes side-by-side
        sols = stats.get('solutions', [])
        for i in range(2):
            t = self.complex_solution_texts[i]
            t.config(state=tk.NORMAL)
            t.delete(1.0, tk.END)
            if i < len(sols):
                info = sols[i]
                if info['solved'] and info['solution']:
                    t.insert(tk.END, f"Ma trận bắt đầu {info['index']} - Có lời giải\n\n")
                    t.insert(tk.END, format_solution_steps(info['solution'], info['stats'].get('solution_costs')))
                else:
                    t.insert(tk.END, f"Ma trận bắt đầu {info['index']} - Không tìm được lời giải\n")
            else:
                t.insert(tk.END, "(Không có ma trận)")
            t.config(state=tk.DISABLED)

    def animate_solution(self):
        """Tự động chạy các bước giải"""
        if not self.solution_path:
            return
        
        if self.solution_step < len(self.solution_path) - 1:
            self.solution_step += 1
            self.current_state = [row[:] for row in self.solution_path[self.solution_step]]
            self.update_display()
            self.status_label.config(text=f"Đang chạy tự động: Bước {self.solution_step}/{len(self.solution_path) - 1}")
            self.root.after(400, self.animate_solution)
        else:
            self.status_label.config(text=f"✓ Hoàn thành lời giải ({len(self.solution_path) - 1} bước)")
    
    def next_step(self):
        """Xem bước tiếp theo"""
        if not self.solution_path:
            messagebox.showwarning("Cảnh Báo", "Vui lòng giải puzzle trước!")
            return

    def display_partial_observable_statistics(self, stats, elapsed_time):
        """Hiển thị kết quả Partial Observable: summary + hai pane giải song song."""
        # Summary on left
        self.complex_stats_text.config(state=tk.NORMAL)
        self.complex_stats_text.delete(1.0, tk.END)

        algorithm_name = "Partial Observable (Complex Environment)"
        text_content = f"""
╔══════════════════════════════════════════════╗
║    Thuật Toán: {algorithm_name:<25}     ║
╚══════════════════════════════════════════════╝

📊 KẾT QUẢ:
   • Thời gian: {elapsed_time:.4f}s

📈 THỐNG KÊ:
   • Số ma trận bắt đầu: {stats.get('start_count', 0)}
   • Số ma trận giải được: {stats.get('solved_count', 0)}
   • Nút được mở rộng: {stats.get('nodes_expanded', 0)}
   • Nút được tạo: {stats.get('nodes_created', 0)}
   • Frontier tối đa: {stats.get('frontier_max', 0)}
   • Chế độ quan sát: {stats.get('mask_type', 'default')}
"""
        self.complex_stats_text.insert(1.0, text_content)
        self.complex_stats_text.config(state=tk.DISABLED)

        # Populate per-start solution panes
        sols = stats.get('solutions', [])
        for i in range(2):
            t = self.complex_solution_texts[i]
            t.config(state=tk.NORMAL)
            t.delete(1.0, tk.END)
            if i < len(sols):
                info = sols[i]
                if info['solved'] and info['solution']:
                    t.insert(tk.END, f"Ma trận bắt đầu {info['index']} - Có lời giải\n\n")
                    t.insert(tk.END, format_solution_steps(info['solution'], info['stats'].get('solution_costs')))
                else:
                    t.insert(tk.END, f"Ma trận bắt đầu {info['index']} - Không tìm được lời giải\n")
            else:
                t.insert(tk.END, "(Không có ma trận)")
            t.config(state=tk.DISABLED)
        
        if self.solution_step < len(self.solution_path) - 1:
            self.solution_step += 1
            self.current_state = [row[:] for row in self.solution_path[self.solution_step]]
            self.update_display()
            self.status_label.config(text=f"Bước {self.solution_step}/{len(self.solution_path) - 1}")
    
    def prev_step(self):
        """Quay lại bước trước"""
        if not self.solution_path:
            messagebox.showwarning("Cảnh Báo", "Vui lòng giải puzzle trước!")
            return
        
        if self.solution_step > 0:
            self.solution_step -= 1
            self.current_state = [row[:] for row in self.solution_path[self.solution_step]]
            self.update_display()
            self.status_label.config(text=f"Bước {self.solution_step}/{len(self.solution_path) - 1}")


# ==================== MAIN ====================
if __name__ == "__main__":
    print("="*70)
    print("8 PUZZLE SOLVER ")
    print("="*70)
    print("\n🎮 Chạy ứng dụng GUI...\n")
    
    root = tk.Tk()
    app = PuzzleGameGUI(root)
    root.mainloop()
