# Rencana Implementasi: Edit Jadwal, Indikator Bentrok Visual (Merah), dan Saran Jadwal Alternatif

Rencana ini memaparkan desain teknis untuk menambahkan fitur edit jadwal, pewarnaan visual (hijau untuk diterima, merah untuk bentrok), dan sistem rekomendasi otomatis untuk mencarikan ruang/waktu kosong bagi kelas yang bentrok.

---

## Proposed Changes

### 1. Engine Penjadwalan (`engine.py`)
Meningkatkan logika penjadwalan dengan menambahkan fungsi utilitas rekomendasi jadwal.

#### [MODIFY] [engine.py](file:///d:/Kuliah ITK/Materi Kuliah Semester 4/PAA/Tubes/engine.py)
* **Tambah Fungsi `get_schedule_suggestions(classes, target_class, accepted_classes)`**:
  * Jika sebuah kelas bentrok, fungsi ini akan mencari dua jenis alternatif:
    1. **Alternatif Ruangan (Waktu Sama)**: Mencari ruangan lain di mana rentang waktu kelas tersebut (`jam_mulai` - `jam_selesai`) tidak bentrok dengan kelas mana pun yang sudah diterima di ruangan tersebut.
    2. **Alternatif Waktu (Ruangan Sama)**: Mencari slot waktu kosong terdekat di ruangan yang sama. Misalnya, mencari setelah jam selesai kelas terakhir di ruangan tersebut, atau mencari sela-sela waktu kosong (*gap*) di antara kelas-kelas yang diterima yang memiliki durasi cukup.
  * Mengembalikan daftar string rekomendasi yang ramah pengguna.

---

### 2. Antarmuka GUI (`gui_interface.py`)
Menambahkan form edit, pewarnaan visual dinamis, dan integrasi rekomendasi jadwal.

#### [MODIFY] [gui_interface.py](file:///d:/Kuliah ITK/Materi Kuliah Semester 4/PAA/Tubes/gui_interface.py)
* **Pewarnaan Tabel Treeview**:
  * Menggunakan tag Treeview untuk mewarnai latar belakang/teks baris:
    * Baris berstatus **Diterima** diwarnai hijau muda/lembut.
    * Baris berstatus **Bentrok (Ditolak)** diwarnai merah muda/lembut.
* **Timeline Canvas Dinamis (Merah/Hijau)**:
  * Pada mode **"Tampilkan Semua Pengajuan"**, setelah optimasi dijalankan:
    * Kelas yang lolos optimasi digambar dengan warna **Hijau** (`#2ECC71`).
    * Kelas yang bentrok digambar dengan warna **Merah** (`#E74C3C`).
  * **Pencegahan Tumpang Tindih Visual**:
    * Di dalam satu baris ruangan, tinggi box akan dibagi atau digeser secara vertikal (offset). Misalnya, kelas yang diterima digambar di 60% tinggi atas baris, sedangkan kelas yang bentrok digambar di 40% tinggi bawah baris dengan tinggi yang lebih tipis. Ini memastikan kedua kelas yang bertabrakan waktu tetap terlihat jelas di timeline.
* **Fitur Edit Jadwal**:
  * Menambahkan tombol **"Edit Kelas Terpilih"** di bawah tabel.
  * Saat tombol diklik, sebuah jendela dialog pop-up (`Toplevel` window) akan muncul berisi form yang sudah terisi data kelas terpilih (Nama, Ruangan, Jam Mulai, Jam Selesai).
  * Pengguna dapat mengubah data dan menekan "Simpan". Perubahan divalidasi (misal format jam, jam mulai < jam selesai), objek diubah, status optimasi di-reset ke belum dioptimasi, dan UI diperbarui.
* **Integrasi Rekomendasi di Detail Pop-up**:
  * Ketika kotak kelas berkode merah (bentrok) diklik di timeline, pop-up rincian detail akan menampilkan **"Saran Jadwal Alternatif"** yang dihasilkan oleh fungsi engine.

---

### 3. Antarmuka CLI (`cli_interface.py`)
Mendukung pengeditan jadwal dan penampilan saran jadwal di terminal.

#### [MODIFY] [cli_interface.py](file:///d:/Kuliah ITK/Materi Kuliah Semester 4/PAA/Tubes/cli_interface.py)
* **Tambah Opsi Edit Jadwal**:
  * Menambahkan menu baru: `[11] Edit Jadwal` (dan mengubah menu Keluar menjadi opsi `[12]`).
  * Meminta input Kode Kelas yang ingin diedit.
  * Menampilkan data lama dan meminta input baru. Jika pengguna langsung menekan `Enter`, nilai lama dipertahankan.
  * Melakukan validasi input waktu baru.
* **Tampilkan Saran di Tabel Hasil**:
  * Pada hasil optimasi (Menu `[6]`), di bawah tabel **"DAFTAR JADWAL BENTROK"**, tampilkan saran solusi ruangan/waktu alternatif untuk masing-masing kelas yang bentrok secara otomatis.

---

### 4. Dokumentasi (`walkthrough.md`)
Memperbarui panduan agar sesuai dengan fitur baru.

#### [MODIFY] [walkthrough.md](file:///d:/Kuliah ITK/Materi Kuliah Semester 4/PAA/Tubes/walkthrough.md)
* Menambahkan penjelasan tentang fitur **Edit Jadwal**, skema pewarnaan bentrok (Merah vs Hijau), dan algoritma **Saran Jadwal Alternatif**.

---

### 5. Skrip Pengujian (`test_scheduler.py`)
Menguji fungsi rekomendasi baru.

#### [MODIFY] [test_scheduler.py](file:///d:/Kuliah ITK/Materi Kuliah Semester 4/PAA/Tubes/test_scheduler.py)
* Menambahkan unit test baru untuk memastikan fungsi pencarian rekomendasi mengembalikan alternatif ruangan/waktu yang benar-benar kosong (tidak bentrok).

---

## Verification Plan

### Automated Tests
* Menjalankan `python test_scheduler.py` untuk menguji fungsionalitas algoritma greedy dan pencarian rekomendasi.

### Manual Verification
1. **Verifikasi GUI**:
   * Jalankan `python main.py --gui`.
   * Klik tombol **"Jalankan Optimasi"** dan perhatikan pewarnaan baris tabel (Merah/Hijau) serta timeline.
   * Pilih kelas bentrok (merah) di timeline dan verifikasi adanya saran solusi di dialog detail.
   * Pilih salah satu kelas di tabel, klik **"Edit Kelas Terpilih"**, ubah ruang/waktunya, lalu simpan. Periksa apakah tabel dan timeline diperbarui secara real-time.
2. **Verifikasi CLI**:
   * Jalankan `python main.py --cli`.
   * Jalankan optimasi lalu lihat hasilnya. Pastikan di bawah daftar jadwal bentrok tertulis saran alternatif ruangan atau waktu.
   * Coba menu Edit Jadwal dan verifikasi inputnya terupdate dengan benar.
