# 📚 Sistem Manajemen Perpustakaan
Aplikasi GUI berbasis **Python (Tkinter)** yang terhubung ke **MySQL/MariaDB**, digunakan untuk mengelola data buku dan anggota perpustakaan dengan fitur login, CRUD, dan dashboard statistik sederhana.

## 🧩 Fitur Utama
✅ **Login Sistem**
- Validasi username dan password langsung dari database (`users` table).
- Mengarahkan ke dashboard setelah login sukses.

✅ **Dashboard Utama**
- Menampilkan menu navigasi.
- Statistik jumlah buku dan anggota.
- Tombol logout.

✅ **Manajemen Buku**
- Tambah, ubah, hapus, dan tampilkan daftar buku.
- Validasi input tahun dan stok (harus angka).
- Cegah duplikasi `kode_buku`.

✅ **Manajemen Anggota**
- Tambah, ubah, hapus, dan tampilkan data anggota.
- Validasi format email dan nomor telepon.
- Cegah duplikasi `kode_anggota`.

## 🛠️ Teknologi yang Digunakan
| Komponen | Keterangan |
|-----------|------------|
| **Python** | Bahasa pemrograman utama |
| **Tkinter** | Library GUI bawaan Python |
| **MySQL Connector** | Modul koneksi Python ↔ MySQL/MariaDB |
| **MariaDB/MySQL** | Database backend |
| **Regex (re)** | Untuk validasi email |

## ⚙️ Persiapan Lingkungan
### 1️⃣ Instalasi Modul Python
```bash
pip install mysql-connector-python
```
### 2️⃣ Jalankan MariaDB / MySQL
Jika menggunakan **XAMPP**: buka panel dan klik **Start** di bagian **MySQL**  
Atau di Linux:
```bash
sudo systemctl start mariadb
```
### 3️⃣ Buat Database
```sql
CREATE DATABASE perpustakaan_db;
USE perpustakaan_db;
```
### 4️⃣ Buat Tabel yang Dibutuhkan
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin'
);
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');

CREATE TABLE buku (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_buku VARCHAR(20) UNIQUE NOT NULL,
    judul VARCHAR(100),
    pengarang VARCHAR(100),
    penerbit VARCHAR(100),
    tahun_terbit INT,
    stok INT
);

CREATE TABLE anggota (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_anggota VARCHAR(20) UNIQUE NOT NULL,
    nama VARCHAR(100),
    alamat VARCHAR(255),
    telepon VARCHAR(20),
    email VARCHAR(100)
);
```

## 🚀 Cara Menjalankan Aplikasi
1. Simpan file Python ini sebagai `perpustakaan_app.py`
2. Pastikan database aktif dan sudah dibuat.
3. Jalankan:
```bash
python perpustakaan_app.py
```
4. Login dengan:
```
Username: admin
Password: admin123
```

## 🧱 Struktur Aplikasi
```
📂 Project Folder
├── perpustakaan_app.py
├── README.md
└── database_setup.sql
```

## 👨‍💻 Pembuat
**Nama:** Khoirum Nurfatikhaamin  
**Mata Kuliah:** Rekayasa Perangkat Lunak  
**Proyek:** GUI Python dengan MySQL Integration
