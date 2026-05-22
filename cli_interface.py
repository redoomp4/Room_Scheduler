# -*- coding: utf-8 -*-
"""
cli_interface.py - Command Line Interface (CLI)
==============================================
Modul ini menyediakan antarmuka baris perintah (CLI) yang interaktif,
rapi, dan profesional untuk mengoperasikan sistem penjadwalan.
Dilengkapi dengan visualisasi tabel ASCII dan validasi input yang ketat.
"""

import os
from engine import Kuliah, parse_time, greedy_schedule, get_dummy_data, export_schedule_to_file


def clear_screen():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Menampilkan header dekoratif."""
    print("=" * 65)
    print(f"{title.center(65)}")
    print("=" * 65)

def print_table(headers, rows):
    """
    Mencetak tabel ASCII secara manual tanpa dependensi eksternal.
    
    Args:
        headers (list): Judul kolom
        rows (list): Data baris, list of lists
    """
    if not rows:
        print("[!] Tidak ada data untuk ditampilkan.")
        return

    # Hitung lebar maksimum tiap kolom
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))

    # Garis pembatas tabel
    sep = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    
    print(sep)
    # Cetak header
    header_str = "|" + "|".join([f" {headers[i]:<{widths[i]}} " for i in range(len(headers))]) + "|"
    print(header_str)
    print(sep)
    
    # Cetak baris data
    for row in rows:
        row_str = "|" + "|".join([f" {str(val):<{widths[i]}} " for i, val in enumerate(row)]) + "|"
        print(row_str)
    print(sep)

def format_class_rows(classes):
    """Mengubah daftar objek Kuliah menjadi format list of lists untuk tabel."""
    rows = []
    # Urutkan berdasarkan Kode Kelas untuk tampilan yang rapi
    sorted_cls = sorted(classes, key=lambda x: x.code)
    for c in sorted_cls:
        rows.append([c.code, c.nama, c.ruangan, c.jam_mulai, c.jam_selesai])
    return rows

def input_text(prompt, allow_empty=False):
    """Membaca input teks dengan validasi tidak boleh kosong."""
    while True:
        val = input(prompt).strip()
        if not val and not allow_empty:
            print("[x] Error: Input tidak boleh kosong!")
            continue
        return val

def input_time(prompt):
    """Membaca input waktu HH:MM dengan validasi."""
    while True:
        time_str = input(prompt).strip()
        try:
            parse_time(time_str)
            return time_str
        except ValueError as e:
            print(f"[x] Error: {e}")

def add_schedule_cli(classes):
    """Mengelola alur tambah kelas dari CLI."""
    print_header("TAMBAH PERMINTAAN JADWAL BARU")
    
    # Auto-generate kode kelas baru
    existing_nums = []
    for c in classes:
        if c.code.startswith('C') and c.code[1:].isdigit():
            existing_nums.append(int(c.code[1:]))
    next_num = max(existing_nums) + 1 if existing_nums else 1
    new_code = f"C{next_num:02d}"
    
    print(f"Kode Kelas Otomatis: {new_code}")
    nama = input_text("Nama Mata Kuliah: ")
    ruangan = input_text("Nama Ruangan (misal: AULA, LAB-01): ").upper()
    
    while True:
        jam_mulai = input_time("Jam Mulai (HH:MM, misal 08:30): ")
        jam_selesai = input_time("Jam Selesai (HH:MM, misal 10:30): ")
        
        # Validasi: Jam mulai harus sebelum jam selesai
        try:
            m_mulai = parse_time(jam_mulai)
            m_selesai = parse_time(jam_selesai)
            if m_mulai >= m_selesai:
                print("[x] Error: Jam selesai harus setelah jam mulai! Silakan input ulang.")
                continue
            break
        except ValueError as e:
            print(f"[x] Error: {e}")
            
    new_class = Kuliah(new_code, nama, ruangan, jam_mulai, jam_selesai)
    classes.append(new_class)
    print(f"\n[v] Sukses: Kelas '{nama}' ({new_code}) di {ruangan} berhasil diajukan!")
    input("\nTekan Enter untuk kembali ke menu...")

def view_schedules_cli(classes):
    """Menampilkan semua permintaan kelas yang diajukan."""
    print_header("DAFTAR PERMINTAAN JADWAL KULIAH (RAW DATA)")
    print(f"Total permintaan masuk: {len(classes)} kelas\n")
    headers = ["Kode", "Mata Kuliah", "Ruangan", "Jam Mulai", "Jam Selesai"]
    rows = format_class_rows(classes)
    print_table(headers, rows)
    input("\nTekan Enter untuk kembali ke menu...")

def run_optimization_cli(classes):
    """Menjalankan proses greedy dan mengembalikan hasilnya."""
    print_header("PROSES OPTIMASI JADWAL (GREEDY ALGORITHM)")
    print("[...] Mengoptimalkan jadwal per ruangan...")
    
    accepted, conflicted = greedy_schedule(classes)
    
    print("\n[v] Optimasi Selesai!")
    print(f"- Jumlah kelas diterima  : {len(accepted)}")
    print(f"- Jumlah kelas bentrok   : {len(conflicted)}")
    
    input("\nTekan Enter untuk melihat hasil rincian...")
    return accepted, conflicted

def view_optimization_results_cli(accepted, conflicted):
    """Menampilkan hasil akhir optimasi penjadwalan."""
    clear_screen()
    print_header("HASIL OPTIMASI RUANGAN (DITERIMA - OPTIMAL)")
    if accepted:
        # Kelompokkan berdasarkan ruangan untuk visualisasi lebih baik
        headers = ["Kode", "Mata Kuliah", "Ruangan", "Jam Mulai", "Jam Selesai"]
        rows = format_class_rows(accepted)
        print_table(headers, rows)
    else:
        print("[!] Belum ada kelas yang disetujui.")

    print("\n")
    print_header("DAFTAR JADWAL BENTROK (DITOLAK)")
    if conflicted:
        headers = ["Kode", "Mata Kuliah", "Ruangan", "Jam Mulai", "Jam Selesai"]
        rows = format_class_rows(conflicted)
        print_table(headers, rows)
        print("\n> [NOTE] Kelas di atas bentrok dengan kelas lain yang selesai lebih awal.")
    else:
        print("[v] Luar biasa! Tidak ada jadwal yang bentrok.")

    print("\n" + "="*65)
    print(f"RINGKASAN EFISIENSI PENJADWALAN".center(65))
    print("="*65)
    total = len(accepted) + len(conflicted)
    success_rate = (len(accepted) / total * 100) if total > 0 else 0
    print(f"- Total Pengajuan Kelas : {total}")
    print(f"- Berhasil Dijadwalkan  : {len(accepted)}")
    print(f"- Gagal / Bentrok       : {len(conflicted)}")
    print(f"- Persentase Penerimaan : {success_rate:.2f}%")
    print("="*65)
    
    input("\nTekan Enter untuk kembali ke menu...")

def explain_algorithm_cli():
    """Menampilkan penjelasan teori algoritma greedy dan kompleksitasnya."""
    clear_screen()
    print_header("EDUKASI: ALGORITMA GREEDY & KOMPLEKSITAS")
    print("""
1. Cara Kerja Algoritma Greedy (Activity Selection):
   - Strategi utama: "Pilih kelas dengan waktu selesai tercepat terlebih dahulu."
   - Alasan: Dengan memilih kelas yang selesai lebih awal, kita menyisakan 
     waktu luang sebesar mungkin untuk menampung kelas berikutnya.
   - Langkah:
     a. Kelompokkan pengajuan jadwal berdasarkan Ruangan.
     b. Sortir kelas di tiap ruangan berdasarkan waktu selesai (ascending).
     c. Ambil kelas pertama.
     d. Untuk kelas-kelas berikutnya, jika waktu mulai kelas >= waktu selesai
        kelas sebelumnya yang diambil, maka terima kelas tersebut.

2. Struktur Data yang Digunakan:
   - Objek Kelas (Class Kuliah): Menyimpan properti kelas dan konversi menit.
   - List: Menampung kumpulan kelas yang diinput.
   - Dictionary: Mengelompokkan list kelas berdasarkan kunci nama ruangan.

3. Analisis Kompleksitas Waktu: O(n log n)
   - Mengelompokkan kelas: O(n) di mana n adalah jumlah kelas.
   - Mengurutkan kelas: Untuk ruangan r dengan k kelas, proses pengurutan
     membutuhkan O(k log k). Jika dijumlahkan seluruh ruangan, totalnya 
     adalah O(n log n).
   - Pencarian linear non-overlap: O(n) karena kita hanya memindai data
     satu kali untuk setiap kelas.
   - Sehingga, Total Kompleksitas Waktu adalah O(n log n).
""")
    input("Tekan Enter untuk kembali ke menu...")

def search_filter_cli(classes):
    """Mencari atau menyaring data kelas berdasarkan kriteria tertentu."""
    print_header("CARI & FILTER PERMINTAAN JADWAL")
    print(" [1] Filter Berdasarkan Nama Mata Kuliah")
    print(" [2] Filter Berdasarkan Nama Ruangan")
    print(" [3] Kembali")
    print("-" * 65)
    
    pilihan = input("Pilih Kriteria (1-3): ").strip()
    if pilihan == '3':
        return
        
    filtered = []
    if pilihan == '1':
        keyword = input_text("Masukkan kata kunci nama mata kuliah: ").lower()
        filtered = [c for c in classes if keyword in c.nama.lower()]
    elif pilihan == '2':
        room = input_text("Masukkan nama ruangan (misal: AULA): ").upper()
        filtered = [c for c in classes if room == c.ruangan.upper()]
    else:
        print("[x] Pilihan tidak valid!")
        input("\nTekan Enter...")
        return
        
    print_header(f"HASIL FILTER DATA ({len(filtered)} ditemukan)")
    if filtered:
        headers = ["Kode", "Mata Kuliah", "Ruangan", "Jam Mulai", "Jam Selesai"]
        rows = format_class_rows(filtered)
        print_table(headers, rows)
    else:
        print("[!] Tidak ada data yang cocok dengan kriteria.")
    input("\nTekan Enter untuk kembali...")

def delete_schedule_cli(classes):
    """Menghapus jadwal kuliah tertentu berdasarkan kode kelas."""
    print_header("HAPUS JADWAL KULIAH")
    if not classes:
        print("[!] Data kosong, tidak ada kelas untuk dihapus.")
        input("\nTekan Enter...")
        return
        
    code_to_delete = input_text("Masukkan Kode Kelas yang ingin dihapus (misal C01): ").upper()
    found = False
    for c in classes:
        if c.code.upper() == code_to_delete:
            classes.remove(c)
            found = True
            print(f"\n[v] Sukses: Kelas '{c.nama}' ({c.code}) berhasil dihapus!")
            break
            
    if not found:
        print(f"\n[x] Error: Kelas dengan kode '{code_to_delete}' tidak ditemukan.")
    input("\nTekan Enter...")

def export_schedule_cli(classes, accepted, conflicted, optimized_run):
    """Mengekspor laporan hasil optimasi ke file eksternal."""
    print_header("EKSPOR LAPORAN JADWAL")
    if not optimized_run:
        print("[!] Anda harus menjalankan optimasi (Menu 5) terlebih dahulu!")
        input("\nTekan Enter...")
        return
        
    filename = input("Masukkan nama file laporan (default: hasil_optimasi.txt): ").strip()
    if not filename:
        filename = "hasil_optimasi.txt"
        
    try:
        export_schedule_to_file(filename, classes, accepted, conflicted)
        print(f"\n[v] Sukses: Laporan berhasil diekspor ke '{filename}'!")
    except Exception as e:
        print(f"\n[x] Gagal mengekspor file: {e}")
    input("\nTekan Enter...")

def run_cli_main(classes):
    """Looping Menu CLI Utama."""
    # Simpan hasil optimasi sementara agar bisa dilihat berulang
    accepted = []
    conflicted = []
    optimized_run = False
    
    while True:
        clear_screen()
        print_header("Sistem Penjadwalan Ruangan Kampus - Greedy Algorithm")
        print(" [1] Lihat Seluruh Permintaan Jadwal (Raw Data)")
        print(" [2] Tambah Permintaan Jadwal Baru")
        print(" [3] Cari / Filter Permintaan Jadwal")
        print(" [4] Hapus Jadwal Tertentu (Berdasarkan Kode)")
        print(" [5] Proses Optimasi Penjadwalan (Greedy)")
        print(" [6] Lihat Hasil Optimasi Terakhir")
        print(" [7] Ekspor Hasil Optimasi ke File Teks")
        print(" [8] Reset Data ke Data Dummy")
        print(" [9] Hapus/Reset Seluruh Data")
        print(" [10] Edukasi Teori & Kompleksitas Algoritma")
        print(" [11] Keluar dari CLI")
        print("-" * 65)
        
        pilihan = input("Pilih Menu (1-11): ").strip()
        
        if pilihan == '1':
            if not classes:
                print("\n[!] Data kosong. Silakan tambah data atau reset ke data dummy.")
                input("\nTekan Enter...")
            else:
                view_schedules_cli(classes)
        elif pilihan == '2':
            add_schedule_cli(classes)
            optimized_run = False # Hasil optimasi sebelumnya sudah tidak valid karena ada data baru
        elif pilihan == '3':
            if not classes:
                print("\n[!] Data kosong.")
                input("\nTekan Enter...")
            else:
                search_filter_cli(classes)
        elif pilihan == '4':
            delete_schedule_cli(classes)
            optimized_run = False
        elif pilihan == '5':
            if not classes:
                print("\n[!] Tidak ada data untuk dioptimalkan.")
                input("\nTekan Enter...")
            else:
                accepted, conflicted = run_optimization_cli(classes)
                optimized_run = True
        elif pilihan == '6':
            if not optimized_run:
                print("\n[!] Silakan jalankan proses optimasi (Menu 5) terlebih dahulu!")
                input("\nTekan Enter...")
            else:
                view_optimization_results_cli(accepted, conflicted)
        elif pilihan == '7':
            export_schedule_cli(classes, accepted, conflicted, optimized_run)
        elif pilihan == '8':
            classes.clear()
            classes.extend(get_dummy_data())
            accepted.clear()
            conflicted.clear()
            optimized_run = False
            print("\n[v] Sukses: Data berhasil di-reset ke 14 data dummy kampus!")
            input("\nTekan Enter...")
        elif pilihan == '9':
            classes.clear()
            accepted.clear()
            conflicted.clear()
            optimized_run = False
            print("\n[v] Sukses: Seluruh data jadwal telah dihapus!")
            input("\nTekan Enter...")
        elif pilihan == '10':
            explain_algorithm_cli()
        elif pilihan == '11':
            print("\nTerima kasih telah menggunakan sistem ini.")
            break
        else:
            print("\n[x] Pilihan tidak valid! Silakan masukkan angka 1-11.")
            input("\nTekan Enter...")

