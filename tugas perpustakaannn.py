import tkinter as tk # GUI library
from tkinter import ttk, messagebox # GUI components
import mysql.connector # MySQL connector
from mysql.connector import Error # MySQL error handling
import re # Regular expressions

# =========================
# Konfigurasi koneksi DB
# =========================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # isi sesuai setup kamu
    'database': 'perpustakaan_db'
}

# =========================
# Utility Functions
# =========================
def valid_email(email: str) -> bool:
    """Cek format email sederhana."""
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email or '') is not None

def is_int(value: str) -> bool:
    """Cek apakah string bisa dikonversi ke integer."""
    try:
        int(value)
        return True
    except:
        return False

# =========================
# Class Database
# =========================
class Database:
    def __init__(self, config):
        self.config = config
        self.conn = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            return True
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal koneksi ke database:\n{e}")
            return False

    def close(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def fetchone(self, query, params=()):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query, params)
        row = cursor.fetchone()
        cursor.close()
        return row

    def fetchall(self, query, params=()):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        lastrowid = cursor.lastrowid
        cursor.close()
        return lastrowid

# =========================
# Class Aplikasi Utama
# =========================
class PerpustakaanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Manajemen Perpustakaan")
        self.root.geometry("900x600")

        self.db = Database(DB_CONFIG)
        if not self.db.connect():
            root.destroy()
            return

        self.session = {}
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_login_frame()

    # =========================
    # LOGIN
    # =========================
    def create_login_frame(self):
        self.clear_frame()
        frame = ttk.Frame(self.main_frame, padding=20)
        frame.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        ttk.Label(frame, text="Login Sistem", font=("Helvetica", 16)).grid(row=0, column=0, columnspan=2, pady=(0,10))
        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_username = ttk.Entry(frame)
        self.entry_username.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_password = ttk.Entry(frame, show="*")
        self.entry_password.grid(row=2, column=1, pady=5)

        ttk.Button(frame, text="Login", command=self.perform_login).grid(row=3, column=0, columnspan=2, pady=10)

    def perform_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("Validasi", "Username dan password tidak boleh kosong.")
            return

        try:
            user = self.db.fetchone(
                "SELECT id, username, role FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
        except Error as e:
            messagebox.showerror("Database Error", f"Gagal query login:\n{e}")
            return

        if user:
            self.session['user'] = user
            self.create_dashboard()
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")

    # =========================
    # DASHBOARD
    # =========================
    def create_dashboard(self):
        self.clear_frame()

        top = ttk.Frame(self.main_frame, padding=10)
        top.pack(fill=tk.X)
        user = self.session.get('user', {})
        ttk.Label(top, text=f"Selamat Datang, {user.get('username','')}", font=("Helvetica", 14)).pack(side=tk.LEFT)

        ttk.Button(top, text="Logout", command=self.logout).pack(side=tk.RIGHT)

        content = ttk.Frame(self.main_frame, padding=10)
        content.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        left = ttk.Frame(content, width=220)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))

        ttk.Button(left, text="Manajemen Buku", command=self.create_buku_frame).pack(fill=tk.X, pady=5)
        ttk.Button(left, text="Manajemen Anggota", command=self.create_anggota_frame).pack(fill=tk.X, pady=5)

        stats = ttk.LabelFrame(left, text="Statistik Singkat", padding=10)
        stats.pack(fill=tk.X, pady=10)

        jumlah_buku = self.db.fetchone("SELECT COUNT(*) AS jml FROM buku")['jml']
        jumlah_anggota = self.db.fetchone("SELECT COUNT(*) AS jml FROM anggota")['jml']

        ttk.Label(stats, text=f"Jumlah Buku: {jumlah_buku}").pack(anchor=tk.W)
        ttk.Label(stats, text=f"Jumlah Anggota: {jumlah_anggota}").pack(anchor=tk.W)

        # Konten utama
        self.content_area = ttk.Frame(content)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.content_area, text="Pilih menu di kiri untuk mengelola data.", font=("Helvetica", 12)).pack(pady=20)

    def logout(self):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin logout?"):
            self.session = {}
            self.create_login_frame()

    # =========================
    # MANAJEMEN BUKU
    # =========================
    def create_buku_frame(self):
        self.clear_content_area()

        frame = ttk.Frame(self.content_area, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(frame, text="Form Buku", padding=10)
        form.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))

        fields = [
            ("Kode Buku", "b_kode"),
            ("Judul", "b_judul"),
            ("Pengarang", "b_pengarang"),
            ("Penerbit", "b_penerbit"),
            ("Tahun Terbit", "b_tahun"),
            ("Stok", "b_stok")
        ]
        self.entries = {}
        for i, (label, name) in enumerate(fields):
            ttk.Label(form, text=label+":").grid(row=i, column=0, sticky=tk.W, pady=3)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, pady=3)
            self.entries[name] = entry

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Tambah", command=self.add_buku).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Update", command=self.update_buku).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Hapus", command=self.delete_buku).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Clear", command=self.clear_buku_form).pack(side=tk.LEFT, padx=4)

        # Tabel Buku
        table = ttk.LabelFrame(frame, text="Daftar Buku", padding=10)
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_buku = ttk.Treeview(table, columns=("kode", "judul", "pengarang", "penerbit", "tahun", "stok"), show='headings')
        for col in ("kode", "judul", "pengarang", "penerbit", "tahun", "stok"):
            self.tree_buku.heading(col, text=col.title())
            self.tree_buku.column(col, width=120)
        self.tree_buku.pack(fill=tk.BOTH, expand=True)
        self.tree_buku.bind("<<TreeviewSelect>>", self.on_buku_select)

        self.load_buku()

    def clear_buku_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)

    def load_buku(self):
        for item in self.tree_buku.get_children():
            self.tree_buku.delete(item)
        rows = self.db.fetchall("SELECT * FROM buku ORDER BY judul")
        for r in rows:
            self.tree_buku.insert("", tk.END, values=(r['kode_buku'], r['judul'], r['pengarang'], r['penerbit'], r['tahun_terbit'], r['stok']))

    def on_buku_select(self, event):
        sel = self.tree_buku.selection()
        if not sel:
            return
        values = self.tree_buku.item(sel[0], "values")
        keys = list(self.entries.keys())
        for i in range(len(keys)):
            self.entries[keys[i]].delete(0, tk.END)
            self.entries[keys[i]].insert(0, values[i])

    def add_buku(self):
        kode = self.entries["b_kode"].get().strip()
        judul = self.entries["b_judul"].get().strip()
        pengarang = self.entries["b_pengarang"].get().strip()
        penerbit = self.entries["b_penerbit"].get().strip()
        tahun = self.entries["b_tahun"].get().strip()
        stok = self.entries["b_stok"].get().strip()

        if not (kode and judul and pengarang and penerbit and tahun and stok):
            messagebox.showwarning("Validasi", "Semua field harus diisi.")
            return
        if not is_int(tahun) or not is_int(stok):
            messagebox.showwarning("Validasi", "Tahun dan Stok harus angka.")
            return

        if self.db.fetchone("SELECT id FROM buku WHERE kode_buku=%s", (kode,)):
            messagebox.showerror("Error", "Kode buku sudah ada.")
            return

        self.db.execute("INSERT INTO buku (kode_buku, judul, pengarang, penerbit, tahun_terbit, stok) VALUES (%s,%s,%s,%s,%s,%s)",
                        (kode, judul, pengarang, penerbit, int(tahun), int(stok)))
        messagebox.showinfo("Sukses", "Buku berhasil ditambahkan.")
        self.load_buku()
        self.clear_buku_form()

    def update_buku(self):
        kode = self.entries["b_kode"].get().strip()
        if not kode:
            messagebox.showwarning("Validasi", "Masukkan kode buku yang akan diupdate.")
            return

        if not self.db.fetchone("SELECT id FROM buku WHERE kode_buku=%s", (kode,)):
            messagebox.showerror("Error", "Kode buku tidak ditemukan.")
            return

        self.db.execute("UPDATE buku SET judul=%s, pengarang=%s, penerbit=%s, tahun_terbit=%s, stok=%s WHERE kode_buku=%s",
                        (self.entries["b_judul"].get(), self.entries["b_pengarang"].get(),
                         self.entries["b_penerbit"].get(), self.entries["b_tahun"].get(),
                         self.entries["b_stok"].get(), kode))
        messagebox.showinfo("Sukses", "Data buku diperbarui.")
        self.load_buku()

    def delete_buku(self):
        kode = self.entries["b_kode"].get().strip()
        if not kode:
            messagebox.showwarning("Validasi", "Masukkan kode buku yang akan dihapus.")
            return
        if not self.db.fetchone("SELECT id FROM buku WHERE kode_buku=%s", (kode,)):
            messagebox.showerror("Error", "Kode buku tidak ditemukan.")
            return
        if messagebox.askyesno("Konfirmasi", f"Hapus buku dengan kode {kode}?"):
            self.db.execute("DELETE FROM buku WHERE kode_buku=%s", (kode,))
            messagebox.showinfo("Sukses", "Buku berhasil dihapus.")
            self.load_buku()
            self.clear_buku_form()

    # =========================
    # MANAJEMEN ANGGOTA
    # =========================
    def create_anggota_frame(self):
        self.clear_content_area()

        frame = ttk.Frame(self.content_area, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(frame, text="Form Anggota", padding=10)
        form.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))

        self.a_entries = {}
        fields = [("Kode Anggota", "a_kode"), ("Nama", "a_nama"), ("Alamat", "a_alamat"), ("Telepon", "a_telepon"), ("Email", "a_email")]
        for i, (label, name) in enumerate(fields):
            ttk.Label(form, text=label+":").grid(row=i, column=0, sticky=tk.W, pady=3)
            entry = ttk.Entry(form)
            entry.grid(row=i, column=1, pady=3)
            self.a_entries[name] = entry

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Tambah", command=self.add_anggota).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Update", command=self.update_anggota).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Hapus", command=self.delete_anggota).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Clear", command=self.clear_anggota_form).pack(side=tk.LEFT, padx=4)

        table = ttk.LabelFrame(frame, text="Daftar Anggota", padding=10)
        table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_anggota = ttk.Treeview(table, columns=("kode", "nama", "alamat", "telepon", "email"), show='headings')
        for c in ("kode", "nama", "alamat", "telepon", "email"):
            self.tree_anggota.heading(c, text=c.title())
            self.tree_anggota.column(c, width=120)
        self.tree_anggota.pack(fill=tk.BOTH, expand=True)
        self.tree_anggota.bind("<<TreeviewSelect>>", self.on_anggota_select)

        self.load_anggota()

    def clear_anggota_form(self):
        for e in self.a_entries.values():
            e.delete(0, tk.END)

    def load_anggota(self):
        for item in self.tree_anggota.get_children():
            self.tree_anggota.delete(item)
        rows = self.db.fetchall("SELECT * FROM anggota ORDER BY nama")
        for r in rows:
            self.tree_anggota.insert("", tk.END, values=(r['kode_anggota'], r['nama'], r['alamat'], r['telepon'], r['email']))

    def on_anggota_select(self, event):
        sel = self.tree_anggota.selection()
        if not sel:
            return
        values = self.tree_anggota.item(sel[0], "values")
        keys = list(self.a_entries.keys())
        for i in range(len(keys)):
            self.a_entries[keys[i]].delete(0, tk.END)
            self.a_entries[keys[i]].insert(0, values[i])

    def add_anggota(self):
        kode = self.a_entries["a_kode"].get().strip()
        nama = self.a_entries["a_nama"].get().strip()
        alamat = self.a_entries["a_alamat"].get().strip()
        telepon = self.a_entries["a_telepon"].get().strip()
        email = self.a_entries["a_email"].get().strip()

        if not (kode and nama and alamat and telepon):
            messagebox.showwarning("Validasi", "Kode, nama, alamat, dan telepon wajib diisi.")
            return
        if not telepon.isdigit():
            messagebox.showwarning("Validasi", "Telepon harus angka.")
            return
        if email and not valid_email(email):
            messagebox.showwarning("Validasi", "Format email tidak valid.")
            return
        if self.db.fetchone("SELECT id FROM anggota WHERE kode_anggota=%s", (kode,)):
            messagebox.showerror("Error", "Kode anggota sudah terdaftar.")
            return

        self.db.execute("INSERT INTO anggota (kode_anggota, nama, alamat, telepon, email) VALUES (%s,%s,%s,%s,%s)",
                        (kode, nama, alamat, telepon, email))
        messagebox.showinfo("Sukses", "Anggota berhasil ditambahkan.")
        self.load_anggota()
        self.clear_anggota_form()

    def update_anggota(self):
        kode = self.a_entries["a_kode"].get().strip()
        if not kode:
            messagebox.showwarning("Validasi", "Masukkan kode anggota yang akan diupdate.")
            return
        if not self.db.fetchone("SELECT id FROM anggota WHERE kode_anggota=%s", (kode,)):
            messagebox.showerror("Error", "Kode anggota tidak ditemukan.")
            return

        self.db.execute("UPDATE anggota SET nama=%s, alamat=%s, telepon=%s, email=%s WHERE kode_anggota=%s",
                        (self.a_entries["a_nama"].get(), self.a_entries["a_alamat"].get(),
                         self.a_entries["a_telepon"].get(), self.a_entries["a_email"].get(), kode))
        messagebox.showinfo("Sukses", "Data anggota diperbarui.")
        self.load_anggota()

    def delete_anggota(self):
        kode = self.a_entries["a_kode"].get().strip()
        if not kode:
            messagebox.showwarning("Validasi", "Masukkan kode anggota yang akan dihapus.")
            return
        if not self.db.fetchone("SELECT id FROM anggota WHERE kode_anggota=%s", (kode,)):
            messagebox.showerror("Error", "Kode anggota tidak ditemukan.")
            return
        if messagebox.askyesno("Konfirmasi", f"Hapus anggota dengan kode {kode}?"):
            self.db.execute("DELETE FROM anggota WHERE kode_anggota=%s", (kode,))
            messagebox.showinfo("Sukses", "Anggota berhasil dihapus.")
            self.load_anggota()
            self.clear_anggota_form()

    # =========================
    # Helper
    # =========================
    def clear_frame(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    def clear_content_area(self):
        for w in self.content_area.winfo_children():
            w.destroy()

# =========================
# Jalankan Aplikasi
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = PerpustakaanApp(root)
    root.mainloop()
