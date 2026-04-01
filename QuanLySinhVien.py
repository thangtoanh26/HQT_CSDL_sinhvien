#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# ─────────────────────────────────────────────
#  MÀU SẮC TERMINAL (ANSI)
# ─────────────────────────────────────────────
class C:
    RST  = '\033[0m'
    BOLD = '\033[1m'
    RED  = '\033[91m'
    GRN  = '\033[92m'
    YEL  = '\033[93m'
    BLU  = '\033[94m'
    MAG  = '\033[95m'
    CYN  = '\033[96m'
    WHT  = '\033[97m'
    BGRN = '\033[42m'

def clr(text, *codes): return ''.join(codes) + str(text) + C.RST


# ─────────────────────────────────────────────
#  CLASS SINH VIEN
# ─────────────────────────────────────────────
class Student:
    def __init__(self, ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb=0.0):
        self.ma_sv     = str(ma_sv).strip().upper()
        self.ho_ten    = str(ho_ten).strip()
        self.gioi_tinh = str(gioi_tinh).strip()
        self.ngay_sinh = str(ngay_sinh).strip()
        self.lop       = str(lop).strip()
        self.diem_tb   = float(diem_tb)

    def row(self, highlight=False):
        def h(t, w):
            s = str(t)[:w].ljust(w)
            return clr(s, C.BOLD, C.BGRN) if highlight else s
        return (
            f"| {h(self.ma_sv,10)} "
            f"| {h(self.ho_ten,22)} "
            f"| {h(self.gioi_tinh,8)} "
            f"| {h(self.ngay_sinh,12)} "
            f"| {h(self.lop,10)} "
            f"| {h(str(self.diem_tb),7)} |"
        )


# ─────────────────────────────────────────────
#  B-TREE
# ─────────────────────────────────────────────
ORDER    = 3
MAX_KEYS = ORDER - 1           # = 2  (tối da 2 key/node)
MIN_KEYS = (ORDER - 1) // 2   # = 1  (tối thiểu 1 key/node, trừ root)


class BNode:
    _counter = 0

    def __init__(self, leaf=True):
        BNode._counter += 1
        self.nid      = BNode._counter
        self.leaf     = leaf
        self.keys     = []
        self.values   = []
        self.children = []


class BTree:
    """
    B-Tree bậc 3.
    Dùng INSERT: chèn trước vào node lá, sau đó tách
    khi node đang có > MAX_KEYS (tức 3 keys = overflow).
    """

    def __init__(self, label=""):
        BNode._counter = 0
        self.root  = BNode(leaf=True)
        self.label = label
        self.size  = 0

    # ──────────────────────────────────────────
    #  TÌM KIẾM (SEARCH)
    # ──────────────────────────────────────────
    def search(self, key, node=None, path=None):
        """
        Tìm key trong cây.
        Trả về: (node, index, path) nếu tìm thấy, 
                (None, -1, path) nếu không tìm thấy.
        """
        if node is None:
            node = self.root
        if path is None:
            path = []
        path.append(node)

        key = str(key).strip()
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return node, i, path

        if node.leaf:
            return None, -1, path

        return self.search(key, node.children[i], path)

    # ──────────────────────────────────────────
    #  CHÈN (INSERT)
    # ──────────────────────────────────────────
    def insert(self, key, value):
        key      = str(key).strip()
        overflow = self._insert_rec(self.root, key, value)

        if overflow is not None:
            mid_k, mid_v, right = overflow
            new_root = BNode(leaf=False)
            new_root.keys     = [mid_k]
            new_root.values   = [mid_v]
            new_root.children = [self.root, right]
            self.root = new_root

        self.size += 1

    def _insert_rec(self, node, key, value):
        """
        Chèn key vào node (đệ quy xuống lá).
        Trả về: (mid_key, mid_value, right_node) nếu node bị tràn,
                None nếu không tràn.
        """
        if node.leaf:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            node.keys.insert(i, key)
            node.values.insert(i, value)
        else:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            overflow = self._insert_rec(node.children[i], key, value)

            if overflow is not None:
                mid_k, mid_v, right = overflow
                node.keys.insert(i, mid_k)
                node.values.insert(i, mid_v)
                node.children.insert(i + 1, right)

        if len(node.keys) > MAX_KEYS:
            return self._split(node)

        return None

    def _split(self, node):
        """
        Tách node đang tràn (3 keys):
            node (giữ k0) + key noi (k1) + right_node (giữ k2)
        Trả về (k1, v1, right_node).
        """
        mid = len(node.keys) // 2

        right          = BNode(leaf=node.leaf)
        right.keys     = node.keys[mid + 1:]
        right.values   = node.values[mid + 1:]

        if not node.leaf:
            right.children = node.children[mid + 1:]
            node.children  = node.children[:mid + 1]

        mid_k = node.keys[mid]
        mid_v = node.values[mid]

        node.keys   = node.keys[:mid]
        node.values = node.values[:mid]

        return mid_k, mid_v, right

    # ──────────────────────────────────────────
    #  XÓA (DELETE)
    # ──────────────────────────────────────────
    def delete(self, key):
        key = str(key).strip()
        ok  = self._delete(self.root, key)
        if ok:
            if not self.root.keys and not self.root.leaf:
                self.root = self.root.children[0]
            self.size -= 1
        return ok

    def _delete(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            if node.leaf:
                node.keys.pop(i)
                node.values.pop(i)
                return True
            else:
                left  = node.children[i]
                right = node.children[i + 1]

                if len(left.keys) > MIN_KEYS:
                    pk, pv = self._rightmost(left)
                    node.keys[i]   = pk
                    node.values[i] = pv
                    return self._delete(left, pk)

                elif len(right.keys) > MIN_KEYS:
                    sk, sv2 = self._leftmost(right)
                    node.keys[i]   = sk
                    node.values[i] = sv2
                    return self._delete(right, sk)

                else:
                    self._merge(node, i)
                    return self._delete(node.children[i], key)

        if node.leaf:
            return False

        if len(node.children[i].keys) <= MIN_KEYS:
            i = self._fix_child(node, i)

        return self._delete(node.children[i], key)

    def _fix_child(self, parent, i):
        """Đảm bảo children[i] đang có > MIN_KEYS keys."""
        if i > 0 and len(parent.children[i - 1].keys) > MIN_KEYS:
            self._borrow_left(parent, i)

        elif (i < len(parent.children) - 1
              and len(parent.children[i + 1].keys) > MIN_KEYS):
            self._borrow_right(parent, i)

        else:
            if i < len(parent.children) - 1:
                self._merge(parent, i)
            else:
                self._merge(parent, i - 1)
                i -= 1

        return i

    def _borrow_left(self, parent, i):
        child   = parent.children[i]
        sibling = parent.children[i - 1]
        child.keys.insert(0,   parent.keys[i - 1])
        child.values.insert(0, parent.values[i - 1])
        parent.keys[i - 1]   = sibling.keys.pop()
        parent.values[i - 1] = sibling.values.pop()
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

    def _borrow_right(self, parent, i):
        child   = parent.children[i]
        sibling = parent.children[i + 1]
        child.keys.append(parent.keys[i])
        child.values.append(parent.values[i])
        parent.keys[i]   = sibling.keys.pop(0)
        parent.values[i] = sibling.values.pop(0)
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

    def _merge(self, parent, i):
        left  = parent.children[i]
        right = parent.children[i + 1]
        left.keys.append(parent.keys.pop(i))
        left.values.append(parent.values.pop(i))
        left.keys.extend(right.keys)
        left.values.extend(right.values)
        if not left.leaf:
            left.children.extend(right.children)
        parent.children.pop(i + 1)

    def _rightmost(self, node):
        while not node.leaf:
            node = node.children[-1]
        return node.keys[-1], node.values[-1]

    def _leftmost(self, node):
        while not node.leaf:
            node = node.children[0]
        return node.keys[0], node.values[0]

    # ──────────────────────────────────────────
    #  HIỂN THỊ CÂY (DISPLAY)
    # ──────────────────────────────────────────
    def display(self, highlight_key=None):
        hk = str(highlight_key).strip() if highlight_key else None
        print(clr(
            f"  [B-Tree: {self.label}]  Bac {ORDER}  |  "
            f"MAX={MAX_KEYS} keys/node  |  MIN={MIN_KEYS} key/node  |  "
            f"So phan tu: {self.size}",
            C.BOLD, C.YEL
        ))
        if not self.root.keys:
            print(clr("  (Cay rong)", C.YEL))
            return
        print()
        lines = []
        self._tree_lines(self.root, "", True, lines, hk)
        for ln in lines:
            print(ln)
        print()
        print(clr("  Level-order:", C.YEL))
        self._level_order(hk)

    def _node_str(self, node, hk):
        parts = []
        for k in node.keys:
            if hk and k == hk:
                parts.append(clr(f" {k} ", C.BOLD, C.BGRN))
            else:
                parts.append(clr(f" {k} ", C.CYN))
        sep   = clr("|", C.YEL)
        inner = sep.join(parts) if parts else clr("empty", C.RED)
        label = clr("[", C.YEL) + inner + clr("]", C.YEL)
        if node.leaf:
            label += clr("*", C.MAG)
        return label

    def _tree_lines(self, node, prefix, is_root, lines, hk):
        ns = self._node_str(node, hk)
        if is_root:
            lines.append(f"  {clr('ROOT', C.BOLD+C.YEL)} --- {ns}")
        else:
            lines.append(f"  {prefix}{ns}")

        if not node.leaf:
            n = len(node.children)
            for idx, child in enumerate(node.children):
                last    = (idx == n - 1)
                branch  = "+-- " if last else "+-- "
                extend  = "    " if last else "|   "
                np_ = (prefix + branch) if not is_root else "    " + branch
                self._tree_lines(child, np_, False, lines, hk)

    def _level_order(self, hk):
        queue  = [(self.root, 0)]
        levels = {}
        while queue:
            node, lv = queue.pop(0)
            levels.setdefault(lv, []).append(self._node_str(node, hk))
            for c in node.children:
                queue.append((c, lv + 1))
        for lv, nodes in sorted(levels.items()):
            tag = clr(f"  {'Root' if lv==0 else 'Muc '+str(lv)}: ", C.YEL)
            print(tag + "   ".join(nodes))
        print()


# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────
class StudentDB:
    def __init__(self):
        self.students  = []
        self.idx_masv  = BTree("MSSV")
        self.idx_hoten = BTree("Ho va Ten")

    def _find_raw(self, ma_sv):
        ma_sv = str(ma_sv).strip().upper()
        for sv in self.students:
            if sv.ma_sv == ma_sv:
                return sv
        return None

    def add(self, sv):
        if self._find_raw(sv.ma_sv) is not None:
            return False
        self.students.append(sv)
        self.idx_masv.insert(sv.ma_sv, sv)
        self.idx_hoten.insert(sv.ho_ten.lower(), sv)
        return True

    def remove(self, ma_sv):
        sv = self._find_raw(ma_sv)
        if sv is None:
            return None
        self.students.remove(sv)
        self.idx_masv.delete(sv.ma_sv)
        self.idx_hoten.delete(sv.ho_ten.lower())
        return sv

    def search_masv(self, ma_sv):
        node, i, path = self.idx_masv.search(ma_sv.upper())
        return (node.values[i] if node else None), path

    def search_hoten(self, keyword):
        kw  = keyword.strip().lower()
        res = [sv for sv in self.students if kw in sv.ho_ten.lower()]
        _, _, path = self.idx_hoten.search(kw)
        return res, path


# ─────────────────────────────────────────────
#  GIAO DIỆN & HỖ TRỢ NHẬP/XUẤT
# ─────────────────────────────────────────────
W    = 72
SEP  = clr("-" * W, C.BLU)
SEP2 = clr("=" * W, C.YEL)
TH   = (
    clr("+------------+------------------------+----------+--------------+------------+---------+", C.BLU) + "\n" +
    clr("|", C.BLU) + clr(" MSSV      ", C.BOLD+C.WHT) +
    clr("|", C.BLU) + clr(" Ho va Ten               ", C.BOLD+C.WHT) +
    clr("|", C.BLU) + clr(" Gioi tinh", C.BOLD+C.WHT) +
    clr("|", C.BLU) + clr(" Ngay sinh    ", C.BOLD+C.WHT) +
    clr("|", C.BLU) + clr(" Lop        ", C.BOLD+C.WHT) +
    clr("|", C.BLU) + clr(" Diem TB ", C.BOLD+C.WHT) +
    clr("|", C.BLU) + "\n" +
    clr("+------------+------------------------+----------+--------------+------------+---------+", C.BLU)
)
TF = clr("+------------+------------------------+----------+--------------+------------+---------+", C.BLU)


def print_table(db, hi_masv=None):
    print(clr("\n[BANG DU LIEU GOC - Physical Table]", C.BOLD+C.GRN))
    print(TH)
    if not db.students:
        print(clr("|  (Chua co du lieu)".ljust(W-1) + "|", C.YEL))
    else:
        for sv in db.students:
            hi = hi_masv and sv.ma_sv == hi_masv.upper()
            print(clr("|", C.BLU) + sv.row(highlight=hi))
    print(TF)
    print(clr(f"  Tong: {len(db.students)} sinh vien\n", C.CYN))


def print_indexes(db, hi_masv=None, hi_hoten=None):
    print(clr("[CHI MUC B-TREE - Indexes]", C.BOLD+C.MAG))
    print(SEP)
    db.idx_masv.display(highlight_key=hi_masv)
    print(SEP)
    db.idx_hoten.display(highlight_key=hi_hoten)
    print(SEP)


def section(title):
    print()
    print(clr(f">>> {title}", C.BOLD+C.YEL))
    print(SEP)

def ok(msg):    print(clr(f"\n  [OK]  {msg}", C.GRN))
def err(msg):   print(clr(f"\n  [ERR] {msg}", C.RED))
def info(msg):  print(clr(f"\n  [i]  {msg}", C.CYN))
def ask(msg):   return input(clr(f"  >  {msg}", C.WHT)).strip()


# ─────────────────────────────────────────────
#  CÁC THAO TÁC CHÍNH
# ─────────────────────────────────────────────
def op_add(db):
    section("THEM SINH VIEN MOI")

    ma_sv = ask("MSSV          : ").upper()
    if not ma_sv: err("MSSV khong duoc rong."); return

    ho_ten = ask("Ho va Ten      : ")
    if not ho_ten: err("Ho ten khong duoc rong."); return

    gioi_tinh = ask("Gioi tinh (Nam/Nu): ") or "Nam"
    ngay_sinh = ask("Ngay sinh (dd/mm/yyyy): ") or "01/01/2000"
    lop       = ask("Lop           : ") or "CNTT01"
    try:
        diem_tb = float(ask("Diem TB (0-10): ") or "0")
    except ValueError:
        diem_tb = 0.0

    sv = Student(ma_sv, ho_ten, gioi_tinh, ngay_sinh, lop, diem_tb)

    print(clr("\n  ---- Trang thai TRUOC khi them ----", C.BOLD+C.BLU))
    print_table(db)
    print_indexes(db)

    added = db.add(sv)
    if not added:
        err(f"MSSV '{ma_sv}' da ton tai!"); return

    print(clr("\n  ---- Trang thai SAU khi them ----", C.BOLD+C.GRN))
    print_table(db, hi_masv=ma_sv)
    print_indexes(db, hi_masv=ma_sv, hi_hoten=ho_ten.lower())
    ok(f"Da them [{ma_sv}] {ho_ten}")


def op_delete(db):
    section("XOA SINH VIEN")

    ma_sv = ask("Nhap MSSV can xoa: ").upper()
    if not ma_sv: return

    sv, _ = db.search_masv(ma_sv)
    if sv is None:
        err(f"Khong tim thay MSSV '{ma_sv}'."); return

    info(f"Sinh vien: [{sv.ma_sv}] {sv.ho_ten}")
    confirm = ask("Xac nhan xoa? (y/n): ").lower()
    if confirm != 'y':
        info("Da huy."); return

    print(clr("\n  ---- Trang thai TRUOC khi xoa ----", C.BOLD+C.BLU))
    print_table(db, hi_masv=ma_sv)
    print_indexes(db, hi_masv=ma_sv, hi_hoten=sv.ho_ten.lower())

    removed = db.remove(ma_sv)

    print(clr("\n  ---- Trang thai SAU khi xoa ----", C.BOLD+C.RED))
    print_table(db)
    print_indexes(db)
    ok(f"Da xoa [{removed.ma_sv}] {removed.ho_ten}")


def op_search_masv(db):
    section("TIM KIEM THEO MSSV")

    ma_sv = ask("Nhap MSSV: ").upper()
    if not ma_sv: return

    sv, path = db.search_masv(ma_sv)

    print(clr("\n  [Duong duyet tren B-Tree Index: MSSV]", C.BOLD+C.CYN))
    print(SEP)
    for depth, node in enumerate(path):
        tag  = clr("ROOT" if depth == 0 else f"Muc {depth}", C.YEL)
        keys = " | ".join(
            clr(k, C.BOLD, C.BGRN) if k == ma_sv else clr(k, C.CYN)
            for k in node.keys
        )
        typ  = clr(" *leaf", C.MAG) if node.leaf else ""
        print(f"  {tag}: [{keys}]{typ}")
    print(SEP)

    if sv:
        ok(f"TIM THAY sau {len(path)} buoc!")
        print_table(db, hi_masv=ma_sv)
        print_indexes(db, hi_masv=ma_sv)
    else:
        err(f"Khong tim thay '{ma_sv}'.")


def op_search_hoten(db):
    section("TIM KIEM THEO HO VA TEN")

    kw = ask("Tu khoa ho ten: ")
    if not kw: return

    results, path = db.search_hoten(kw)

    print(clr(f"\n  [Duong duyet tren B-Tree Index: Ho ten (khop chinh xac '{kw.lower()}')]",
              C.BOLD+C.CYN))
    print(SEP)
    for depth, node in enumerate(path):
        tag  = clr("ROOT" if depth == 0 else f"Muc {depth}", C.YEL)
        keys = " | ".join(
            clr(k, C.BOLD, C.BGRN) if k == kw.lower() else clr(k, C.CYN)
            for k in node.keys
        )
        typ  = clr(" *leaf", C.MAG) if node.leaf else ""
        print(f"  {tag}: [{keys}]{typ}")
    print(SEP)

    info(f"Tim kiem partial match '{kw}' -> {len(results)} ket qua")
    if results:
        print(TH)
        for s in results:
            print(clr("|", C.BLU) + s.row(highlight=True))
        print(TF)
        print_indexes(db, hi_hoten=kw.lower())
    else:
        err(f"Khong tim thay sinh vien nao chua '{kw}'.")


def op_show_all(db):
    section("HIEN THI TOAN BO DU LIEU & CHI MUC")
    print_table(db)
    print_indexes(db)


# ─────────────────────────────────────────────
#  DU LIEU MAU
# ─────────────────────────────────────────────
SAMPLES = [
    ("SV001", "Nguyen Van A", "Nam", "15/03/2007", "CNTT01", 7.5),
    ("SV002", "Nguyen Thi B", "Nu",  "22/07/2007", "CNTT01", 8.2),
    ("SV003", "Le Minh C", "Nam", "10/11/2008", "CNTT02", 6.9),
    ("SV004", "Pham Thi D", "Nu",  "05/01/2008", "CNTT02", 9.0),
    ("SV005", "Hoang Van E", "Nam", "18/09/2006", "CNTT03", 7.1),
]

def load_samples(db):
    for s in SAMPLES:
        db.add(Student(*s))


# ─────────────────────────────────────────────
#  MENU CHINH
# ─────────────────────────────────────────────
MENU = [
    ("1", "Them sinh vien",                 op_add),
    ("2", "Xoa sinh vien",                  op_delete),
    ("3", "Tim theo MSSV",                 op_search_masv),
    ("4", "Tim theo Ho ten",                op_search_hoten),
    ("5", "Xem tat ca du lieu & chi muc",   op_show_all),
    ("0", "Thoat",                          None),
]


def banner():
    print(clr("=" * W, C.YEL))
    print(clr("   QUAN LY SINH VIEN  -  B-Tree Index (Bac 3)".center(W), C.BOLD+C.CYN))
    print(clr("=" * W, C.YEL))
    print(clr(
        f"  B-Tree Bac {ORDER}: MAX {MAX_KEYS} keys/node | MIN {MIN_KEYS} key/node (non-root)\n",
        C.MAG
    ))


def main():
    banner()
    db = StudentDB()

    print(clr("  Tai du lieu mau (5 sinh vien)? (y/n): ", C.WHT), end="")
    if input().strip().lower() == 'y':
        load_samples(db)
        ok("Da nap 5 sinh vien mau.\n")

    while True:
        print("\n" + SEP2)
        print(clr("  MENU CHINH", C.BOLD+C.YEL))
        print(SEP2)
        for code, label, _ in MENU:
            print(f"  {clr('['+code+']', C.BOLD+C.GRN)}  {label}")
        print(SEP2)

        choice = ask("Chon chuc nang: ")
        fn     = next((f for c, _, f in MENU if c == choice), None)

        if choice == "0":
            print(clr("\n  Tam biet!\n", C.YEL)); break
        elif fn is None:
            err("Lua chon khong hop le.")
        else:
            fn(db)

        input(clr("\n  [Enter de tiep tuc...]", C.MAG))


if __name__ == "__main__":
    main()
