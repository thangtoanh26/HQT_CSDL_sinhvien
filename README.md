# HƯỚNG DẪN SỬ DỤNG - Quản Lý Sinh Viên

## 1. YÊU CẦU HỆ THỐNG
- Python 3.10 trở lên
- Không cần cài đặt thư viện ngoài

## 2. CHẠY CHƯƠNG TRÌNH
```
python QuanLySinhVien.py
```

## 3. CẤU TRÚC B-TREE BẬC 3 (2-3 Tree)
- Mỗi node có TỐI ĐA 2 keys, tối đa 3 children
- Mỗi node NON-ROOT có ÍT NHẤT 1 key
- Có 2 chỉ mục song song: theo MSSV (Mã số sinh viên) và theo Họ tên
- Kí hiệu: 
```
            [...|...]  = node chứa 2 keys
            [...]     = node chứa 1 key
            [...]* = leaf node
```

## 4. CHỨC NĂNG

### [1] THÊM SINH VIÊN
- Nhập các thông tin: MSSV, Họ tên, Giới tính, Ngày sinh, Lớp, Điểm TB
- Chương trình hiển thị bảng dữ liệu và 2 cây chỉ mục TRƯỚC và SAU khi thêm
- Nút bị tô sáng (màu xanh) là phần tử vừa được thêm
- Quy tắc INSERT của B-Tree bậc 3:
  - Chèn vào leaf -> nếu tràn (3 keys) -> tách (split) node
  - Key giữa nối lên node cha -> có thể kéo theo split lan ra gốc

  Ví dụ thêm SV001, SV002, SV003:
  ```
    - Bước 1: thêm SV001 -> ROOT: [SV001]*
    - Bước 2: thêm SV002 -> ROOT: [SV001|SV002]*  (đầy)
    - Bước 3: thêm SV003 -> tạm thời [SV001|SV002|SV003] -> TÁCH
                         -> ROOT: [SV002]
                                /          \
                         [SV001]*      [SV003]*
  ```

### [2] XÓA SINH VIÊN
- Nhập MSSV cần xóa, xác nhận y/n
- Hiển thị trạng thái TRƯỚC (tô sáng bản ghi cần xóa) và SAU khi xóa
- Quy tắc DELETE của B-Tree bậc 3:
  - Nếu key nằm ở leaf có >= 2 keys: xóa trực tiếp
  - Nếu key nằm ở leaf có 1 key:
    * Mượn từ anh (sibling) qua parent nếu anh có 2 keys
    * Nếu không: merge 2 node + key trên parent thành 1 node
  - Nếu key nằm ở internal node:
    * Thay bằng predecessor (key lớn nhất cây con trái)
    * Hoặc successor (key nhỏ nhất cây con phải)

### [3] TÌM THEO MSSV
- Nhập MSSV cần tìm
- Hiển thị TỪNG BƯỚC duyệt cây từ root xuống (điểm sáng node đang xét)
- Độ phức tạp: O(log n) bước duyệt
- Kết quả được tô sáng trên bảng và trên cây

### [4] TÌM THEO HỌ TÊN
- Nhập từ khóa (có thể là một phần tên)
- Tìm kiếm partial match trên bảng dữ liệu: O(n)
- Đồng thời trả về đường đi trên B-Tree (khớp chính xác)
- Hiển thị tất cả sinh viên có tên chứa từ khóa

### [5] XEM TẤT CẢ
- Hiển thị toàn bộ bảng dữ liệu và 2 cây chỉ mục (MSSV + Họ tên)
- Có level-order view (theo từng mức của cây)

## 5. VÍ DỤ MINH HỌA

Sau khi thêm 5 sinh viên mẫu:
```
B-Tree Index [MSSV]:
  ROOT --- [SV002 | SV004]
      +-- [SV001]*
      +-- [SV003]*
      +-- [SV005]*
  Level-order:
  Root:  [SV002|SV004]
  Muc 1: [SV001]*  [SV003]*  [SV005]*
```
```
B-Tree Index [Họ tên]:
  ROOT --- [ nguyen thi b ]
      +-- [ hoang van e | le minh c ]*
      +-- [ nguyen van a | pham thi d ]*

  Level-order:
  Root:  [ nguyen thi b ]
  Muc 1: [ hoang van e | le minh c ]*   [ nguyen van a | pham thi d ]*
```

## 6. ĐỘ PHỨC TẠP
| Thao tác  | Bảng gốc (list) | B-Tree (2 chỉ mục) |
|-----------|-----------------|---------------------|
| Thêm      | O(1) append     | O(log n) mỗi index  |
| Xóa       | O(n) scan       | O(log n) mỗi index  |
| Tìm MSSV  | O(n) scan       | O(log n) B-Tree     |
| Tìm Họ tên| O(n) partial    | O(log n)            |

Với n sinh viên và B-Tree bậc 3: chiều cao cây <= log2(n+1)/2
=> Tìm kiếm rất nhanh khi n lớn.

## 7. GHI CHÚ
- File: QuanLySinhVien.py (1 file duy nhất)
- Class BTree: dùng phương pháp "insert-then-split-on-overflow" 
  (tránh lỗi split khi node chỉ có 2 keys)
- Class StudentDB: quản lý 2 BTree song song (MSSV + Họ tên)
- Màu sắc terminal sử dụng ANSI escape codes (hỗ trợ Linux/Mac/Windows10+)
