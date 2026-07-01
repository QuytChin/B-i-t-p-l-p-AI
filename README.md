# BÁO CÁO MÔN HỌC: TRÍ TUỆ NHÂN TẠO
*TRƯỜNG ĐẠI HỌC CÔNG NGHỆ KỸ THUẬT TP. HỒ CHÍ MINH (HCMUTE)*
*KHOA CÔNG NGHỆ THÔNG TIN*

## ĐỀ TÀI: GIẢI ĐỐ 8-PUZZLE AI

- **Lớp học phần:** 252ARIN330585_08
- **Giảng viên hướng dẫn:** TS. Phan Thị Huyền Trang
- **Thời gian hoàn thành:** Tháng 6 năm 2026

## Nhóm sinh viên thực hiện:
1. **Trần Quyết Chiến** - 24110171

---

## 1. Giới thiệu dự án
Dự án **8-Puzzle AI** là một ứng dụng mô phỏng đồ họa và trực quan hóa trò chơi xếp số ô lưới $3 \times 3$ sử dụng thư viện `pygame-ce` và giao diện cấu hình `tkinter`. Phần mềm cho phép xáo trộn ngẫu nhiên và áp dụng hệ thống thuật toán AI để đưa cấu hình ma trận từ một trạng thái bất kỳ về trạng thái đích tiêu chuẩn.

### Quy ước cấu hình ma trận (State):
* **INITIAL_STATE:** `[[1, 2, 3], [4, 0, 6], [7, 5, 8]]` (Hoặc cấu hình xáo trộn ngẫu nhiên).
* **GOAL_STATE:** `[[1, 2, 3], [4, 5, 6], [7, 8, 0]]` (Ô trống ký hiệu là số `0`).

### Cơ chế hiển thị & Mô phỏng 2 Giai Đoạn (Phases):
* **Phase 1 (Duyệt tìm kiếm):** Thuật toán AI chạy ngầm để tính toán không gian trạng thái, tự động xuất các thông số thống kê thời gian thực lên panel điều khiển đồ họa (`nodes_expanded`, `nodes_created`, `frontier_max`, `goal_checks`).
* **Phase 2 (Thực thi chuỗi nước đi):** Trình mô phỏng tự động thực hiện việc trượt ô số trên màn hình theo chuỗi hành động kết quả được trả về từ AI bao gồm: dịch lên (`move_up`), dịch xuống (`move_down`), dịch trái (`move_left`), và dịch phải (`move_right`).

---

## 2. Mô hình PEAS
* **P - Performance Measure:** Tìm được chuỗi trạng thái di chuyển tối ưu, tối thiểu hóa số nút mở rộng (`nodes_expanded`), tránh mắc kẹt vòng lặp (`cycles_avoided`), tối ưu số lần kiểm tra đích (`goal_checks`) và giữ tốc độ phản hồi tính toán thời gian thực mượt mà.
* **E - Environment:** Bản đồ ma trận lưới ô số kích thước $3 \times 3$. Môi trường có thể tùy chỉnh: Tĩnh tất định hoàn toàn, Động xáo trộn ngẫu nhiên (`Shuffle`), hoặc sinh cấu hình ràng buộc đặc biệt phục vụ cho các thuật toán logic nâng cao.
* **A - Actuators:** Các hàm dịch chuyển vị trí ô trống `0` hoán đổi với các ô xung quanh: `move_up`, `move_down`, `move_left`, `move_right` thông qua hàm bổ trợ `swap(mt, x1, y1, x2, y2)`.
* **S - Sensors:** Hàm định vị ô trống `find_zero(mt)`, hàm kiểm tra trạng thái đích `is_goal(mt)`, bộ cảm biến thu thập thông số chi phí nước đi và hàm ước lượng Heuristic sai khác vị trí.

---

## 3. Hệ thống Thuật toán AI Áp dụng

### Nhóm 1: Uninformed Search (Tìm kiếm mù)
*Duyệt cây trạng thái dựa trên cấu trúc dữ liệu thuần túy, chi phí các bước dịch chuyển đồng nhất.*
* **BFS (Breadth-First Search):** Sử dụng hàng đợi `deque`. Quét không gian trạng thái theo từng tầng độ sâu, đảm bảo tìm ra chuỗi nước đi ngắn nhất về đích.
* **DFS (Depth-First Search):** Đi sâu tối đa vào một nhánh trạng thái đến khi chạm ngõ cụt hoặc lặp chu trình mới tiến hành quay lui.
* **UCS (Uniform Cost Search):** Tìm kiếm chi phí đồng nhất, mở rộng các nút dựa trên tổng chi phí tích lũy thấp nhất.
* **IDS (Iterative Deepening Search):** Duyệt DFS lặp tăng dần giới hạn độ sâu nhằm tiết kiệm tài nguyên bộ nhớ lưu trữ.

### Nhóm 2: Informed & Complex Search (Tìm kiếm nâng cao)
*Tích hợp các giải thuật xử lý bài toán tìm kiếm đồ thị phức tạp và cấu trúc cây phân nhánh.*
* **A\* Search:** Kết hợp chi phí đường đi hiện tại và hàm đánh giá Heuristic vị trí ô số để tối ưu hóa quỹ đạo tìm kiếm ngắn nhất.
* **AND-OR Graph Search:** Ứng dụng lớp bài toán `AndOrGraphProblem` để xây dựng cây tìm kiếm tích hợp nút chọn hành động (OR) và nút kiểm tra kết quả (AND). Thuật toán sử dụng hàm duyệt sâu tăng dần `AND_OR_GRAPH_SEARCH` với cơ chế kiểm soát chu trình `cycles_avoided`, loại bỏ các nhánh lỗi bằng trạng thái `FAILURE` hoặc `CUTOFF`.

### Nhóm 3: Constraint Satisfaction Problem (Bài toán thỏa mãn ràng buộc - CSP)
*Mô hình hóa bàn cờ 8-Puzzle thành hệ thống 9 biến số $x_1 \rightarrow x_9$ ứng với 9 vị trí trên lưới. Miền giá trị từ $0 \rightarrow 8$. Ràng buộc là tất cả các biến phải có giá trị khác nhau (`AllDifferent`) và trùng khớp hoàn toàn với cấu hình mục tiêu.*
* **Backtracking CSP (`csp_backtracking_search`):** Gán thử giá trị tuần tự cho từng ô trên bàn cờ, tự động kiểm tra tính nhất quán qua hàm `consistent` và ghi nhận nhật ký `csp_log`. Thực hiện hàm `backtrack` quay lui có hệ thống khi phát hiện vi phạm.
* **Min-Conflicts CSP (`min_conflicts_csp`):** Thuật toán tìm kiếm cục bộ giải quyết ràng buộc. Khởi tạo gán tất cả vị trí theo ma trận ban đầu, đếm tổng số lỗi xung đột qua hàm `count_conflicts`. Ở mỗi bước lặp, chọn ngẫu nhiên một biến bị xung đột và thực hiện phép tráo vị trí tốt nhất (`best_swaps`) giúp giảm thiểu tối đa số lỗi, giải quyết bài toán ma trận chỉ sau vài bước lặp.
* **Bộ lọc cạnh AC-3 (`ac_3_csp` & `ac3_filter_blank_moves`):** Thực hiện kiểm tra tính nhất quán cung (Arc Consistency) giữa các biến số. Hàm sử dụng hàng đợi cạnh `deque` liên tục rà soát và sàng lọc miền giá trị thông qua hàm sửa đổi `revise`. Loại bỏ sớm các giá trị không tương thích (`values_pruned`) giúp thu hẹp không gian tìm kiếm trước khi đưa vào bộ giải Backtracking.

---

## 4. Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu hệ thống:
* Python 3.10 trở lên
* Thư viện đồ họa nâng cao `pygame-ce`
* Thư viện giao diện tiêu chuẩn `tkinter`

### Các bước cài đặt:
```bash
# Tạo và kích hoạt môi trường ảo (Khuyến nghị)
python -m venv .venv

# Kích hoạt trên Windows:
.venv\Scripts\activate
# Kích hoạt trên macOS/Linux:
source .venv/bin/activate

# Cài đặt thư viện pygame-ce bắt buộc
pip install pygame-ce pytest

Thao tác trên giao diện đồ họa (UI):
Khởi chạy chương trình: Hệ thống sẽ hiển thị màn hình giao diện game với ma trận trạng thái mặc định.

Nút SHUFFLE (Xáo trộn): Bấm nút xáo trộn trên bảng điều khiển để tạo ra một cấu hình trạng thái ngẫu nhiên ngẫu nhiên trên lưới.

Chọn Thuật toán AI: Sử dụng thanh menu Dropdown hoặc các nút chọn thuật toán tương ứng trên giao diện (BFS, DFS, UCS, IDS, A*, AND-OR, hoặc các chế độ giải CSP nâng cao như Backtracking, Min-Conflicts, AC-3).

Nút RUN / SOLVE: Kích hoạt thuật toán AI chạy tính toán lời giải, hệ thống tự động vẽ sơ đồ trực quan hóa số lượng nút và chuỗi bước đi.

Điều khiển Replay: Sử dụng các phím điều hướng < hoặc > để xem từng bước dịch chuyển của ô trống hoặc nhấn AUTO để hệ thống tự động trượt các ô số về vị trí đích mong muốn.
