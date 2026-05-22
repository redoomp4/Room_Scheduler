# -*- coding: utf-8 -*-
"""
cli_interface.py - Command Line Interface (CLI)
==============================================
Modul ini menyediakan antarmuka baris perintah (CLI) yang interaktif,
rapi, dan profesional untuk mengoperasikan sistem penjadwalan.
Dilengkapi dengan visualisasi tabel ASCII, validasi bentrok real-time,
filter per hari (Senin-Minggu), dan auto-reoptimize setelah setiap
operasi modifikasi data.
"""

import os
from engine import Kuliah, parse_time, greedy_schedule, get_dummy_data, export_schedule_to_file, get_schedule_suggestions, VALID_ROOMS

# Urutan hari untuk pengurutan tabel
DAY_ORDER = {'Senin': 0, 'Selasa': 1, 'Rabu': 2, 'Kamis': 3, 'Jumat': 4, 'Sabtu': 5, 'Minggu': 6}
VALID_DAYS = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']


def clear_screen():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Menampilkan header dekoratif."""
    print("=" * 70)
    print(f"{title.center(70)}")
    print("=" * 70)

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
    """Mengubah daftar objek Kuliah menjadi format list of lists untuk tabel (dengan kolom Hari)."""
    rows = []
    # Urutkan berdasarkan Hari -> Ruangan -> Jam Mulai
    sorted_cls = sorted(classes, key=lambda x: (DAY_ORDER.get(x.hari, 7), x.ruangan, x.mulai_menit))
    for c in sorted_cls:
        rows.append([c.code, c.nama, c.hari, c.ruangan, c.jam_mulai, c.jam_selesai])
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

def input_hari(prompt, default=None):
    """
    Membaca pilihan hari dari input CLI.
    Menampilkan daftar pilihan bernomor dan memvalidasi pilihan.
    
    Args:
        prompt (str): Teks prompt di atas pilihan.
        default (str): Nilai default yang dipilih jika Enter ditekan langsung (untuk mode edit).
    
    Returns:
        str: Nama hari yang dipilih.
    """
    print(prompt)
    for i, day in enumerate(VALID_DAYS, 1):
        marker = " <-- (saat ini)" if default and day == default else ""
        print(f"  [{i}] {day}{marker}")
    
    while True:
        if default:
            raw = input(f"Pilih hari (1-{len(VALID_DAYS)}) [Enter = '{default}']: ").strip()
            if not raw:
                return default
        else:
            raw = input(f"Pilih hari (1-{len(VALID_DAYS)}): ").strip()
        
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(VALID_DAYS):
                return VALID_DAYS[idx]
        # Izinkan input nama langsung (tidak case-sensitive)
        match = next((d for d in VALID_DAYS if d.lower() == raw.lower()), None)
        if match:
            return match
        print(f"[x] Pilihan tidak valid. Masukkan angka 1-{len(VALID_DAYS)} atau nama hari.")


def input_ruangan(prompt, default=None):
    """
    Membaca pilihan ruangan dari input CLI.
    Menampilkan daftar pilihan bernomor dan memvalidasi pilihan.
    """
    print(prompt)
    print("  Gedung E Lantai 1:")
    print("    [1] E101    [2] E102    [3] E103    [4] E104    [5] E105")
    print("  Gedung E Lantai 2:")
    print("    [6] E201    [7] E202    [8] E203    [9] E204    [10] E205")
    print("  Gedung E Lantai 3:")
    print("    [11] E301   [12] E302   [13] E303   [14] E304   [15] E305")
    print("  Laboratorium Komputer:")
    print("    [16] Lab Kom 1      [17] Lab Kom 2")
    if default:
        print(f"  (Ruangan saat ini: '{default}')")
        
    while True:
        if default:
            raw = input(f"Pilih ruangan (1-{len(VALID_ROOMS)}) [Enter = '{default}']: ").strip()
            if not raw:
                return default
        else:
            raw = input(f"Pilih ruangan (1-{len(VALID_ROOMS)}): ").strip()
            
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(VALID_ROOMS):
                return VALID_ROOMS[idx]
                
        match = next((r for r in VALID_ROOMS if r.lower() == raw.lower()), None)
        if match:
            return match
            
        print(f"[x] Pilihan tidak valid. Masukkan angka 1-{len(VALID_ROOMS)} atau nama ruangan.")


def _check_conflict_dry_run(classes, new_or_edited_class, original_code=None):
    """
    Melakukan simulasi greedy (dry-run) untuk mendeteksi bentrok sebelum benar-benar menyimpan.
    
    Args:
        classes (list): Daftar kelas saat ini.
        new_or_edited_class (Kuliah): Objek kelas yang akan dicek (baru atau hasil edit).
        original_code (str|None): Kode kelas yang sedang diedit (None jika tambah baru).
    
    Returns:
        tuple: (is_conflicted: bool, overlapping_classes: list[Kuliah])
    """
    sim_classes = []
    for c in classes:
        if original_code and c.code == original_code:
            # Ganti dengan versi yang sudah diedit
            sim_classes.append(new_or_edited_class)
        else:
            sim_classes.append(Kuliah(c.code, c.nama, c.ruangan, c.jam_mulai, c.jam_selesai, c.hari))
    
    if original_code is None:
        # Tambah baru: kelas belum ada di list, masukkan ke sim
        sim_classes.append(new_or_edited_class)
    
    sim_accepted, sim_conflicted = greedy_schedule(sim_classes)
    is_conflicted = any(c.code == new_or_edited_class.code for c in sim_conflicted)
    
    overlapping = []
    if is_conflicted:
        for c in sim_accepted:
            if (c.ruangan == new_or_edited_class.ruangan and
                    c.hari == new_or_edited_class.hari and
                    c.code != new_or_edited_class.code):
                if (new_or_edited_class.mulai_menit < c.selesai_menit and
                        new_or_edited_class.selesai_menit > c.mulai_menit):
                    overlapping.append(c)
    
    return is_conflicted, overlapping


def _print_conflict_warning(new_class, overlapping):
    """Mencetak pesan peringatan bentrok yang terformat dengan detail kelas penabrak."""
    print()
    print("!" * 70)
    print("  [PERINGATAN BENTROK]".center(70))
    print("!" * 70)
    print(f"  Jadwal yang Anda masukkan BENTROK pada:")
    print(f"    Hari     : {new_class.hari}")
    print(f"    Ruangan  : {new_class.ruangan}")
    print(f"    Waktu    : {new_class.jam_mulai} - {new_class.jam_selesai}")
    if overlapping:
        print()
        print("  Kelas yang menabrak (sudah diterima greedy):")
        for c in overlapping:
            print(f"    * {c.code}: {c.nama} ({c.jam_mulai}-{c.jam_selesai})")
    print("!" * 70)


def add_schedule_cli(classes, accepted, conflicted, optimized_run):
    """
    Mengelola alur tambah kelas dari CLI.
    Fitur: input Hari, validasi bentrok real-time (dry-run), auto-reoptimize.
    
    Returns:
        tuple: (accepted, conflicted, optimized_run) yang sudah diperbarui.
    """
    print_header("TAMBAH PERMINTAAN JADWAL BARU")
    
    # Auto-generate kode kelas baru
    existing_nums = []
    for c in classes:
        if c.code.startswith('C') and c.code[1:].isdigit():
            existing_nums.append(int(c.code[1:]))
    next_num = max(existing_nums) + 1 if existing_nums else 1
    new_code = f"C{next_num:02d}"
    
    print(f"Kode Kelas Otomatis: {new_code}\n")
    nama    = input_text("Nama Mata Kuliah: ")
    ruangan = input_ruangan("Pilih Ruangan Pelaksanaan:")
    hari    = input_hari("Pilih Hari Pelaksanaan:")
    
    while True:
        jam_mulai  = input_time("Jam Mulai  (HH:MM, misal 08:30): ")
        jam_selesai = input_time("Jam Selesai (HH:MM, misal 10:30): ")
        try:
            m_mulai   = parse_time(jam_mulai)
            m_selesai = parse_time(jam_selesai)
            if m_mulai >= m_selesai:
                print("[x] Error: Jam selesai harus setelah jam mulai! Silakan input ulang.")
                continue
            break
        except ValueError as e:
            print(f"[x] Error: {e}")
    
    new_class = Kuliah(new_code, nama, ruangan, jam_mulai, jam_selesai, hari)
    
    # --- Validasi Bentrok Real-Time (Dry-Run) ---
    is_conflicted, overlapping = _check_conflict_dry_run(classes, new_class, original_code=None)
    
    if is_conflicted:
        _print_conflict_warning(new_class, overlapping)
        pilihan = input("\n  Apakah Anda tetap ingin menambahkan jadwal ini? (y/n): ").strip().lower()
        if pilihan != 'y':
            print("\n[!] Penambahan dibatalkan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return accepted, conflicted, optimized_run
    
    classes.append(new_class)
    
    # Auto-Reoptimize
    if optimized_run:
        accepted, conflicted = greedy_schedule(classes)
        status = "DITERIMA" if new_class in accepted else "BENTROK"
        print(f"\n[v] Sukses: Kelas '{nama}' ({new_code}) di {ruangan} ({hari}) ditambahkan.")
        print(f"    Status setelah re-optimasi: {status}")
    else:
        print(f"\n[v] Sukses: Kelas '{nama}' ({new_code}) di {ruangan} ({hari}) berhasil diajukan!")
    
    input("\nTekan Enter untuk kembali ke menu...")
    return accepted, conflicted, optimized_run


def view_schedules_cli(classes):
    """Menampilkan semua permintaan kelas yang diajukan (dengan kolom Hari)."""
    print_header("DAFTAR PERMINTAAN JADWAL KULIAH (RAW DATA)")
    print(f"Total permintaan masuk: {len(classes)} kelas\n")
    headers = ["Kode", "Mata Kuliah", "Hari", "Ruangan", "Jam Mulai", "Jam Selesai"]
    rows = format_class_rows(classes)
    print_table(headers, rows)
    input("\nTekan Enter untuk kembali ke menu...")

def run_optimization_cli(classes):
    """Menjalankan proses greedy dan mengembalikan hasilnya."""
    print_header("PROSES OPTIMASI JADWAL (GREEDY ALGORITHM)")
    print("[...] Mengoptimalkan jadwal per (ruangan, hari)...")
    
    accepted, conflicted = greedy_schedule(classes)
    
    print("\n[v] Optimasi Selesai!")
    print(f"  - Jumlah kelas diterima  : {len(accepted)}")
    print(f"  - Jumlah kelas bentrok   : {len(conflicted)}")
    
    input("\nTekan Enter untuk melihat hasil rincian...")
    return accepted, conflicted

def view_optimization_results_cli(classes, accepted, conflicted):
    """Menampilkan hasil akhir optimasi penjadwalan (dengan kolom Hari)."""
    clear_screen()
    print_header("HASIL OPTIMASI RUANGAN (DITERIMA - OPTIMAL)")
    if accepted:
        headers = ["Kode", "Mata Kuliah", "Hari", "Ruangan", "Jam Mulai", "Jam Selesai"]
        rows = format_class_rows(accepted)
        print_table(headers, rows)
    else:
        print("[!] Belum ada kelas yang disetujui.")

    print("\n")
    print_header("DAFTAR JADWAL BENTROK (DITOLAK)")
    if conflicted:
        headers = ["Kode", "Mata Kuliah", "Hari", "Ruangan", "Jam Mulai", "Jam Selesai"]
        rows = format_class_rows(conflicted)
        print_table(headers, rows)
        print("\n> [NOTE] Kelas di atas bentrok dengan kelas lain yang selesai lebih awal pada hari dan ruangan yang sama.")
        
        # Tampilkan saran jadwal alternatif per kelas bentrok
        print("\n" + "-" * 70)
        print("SARAN JADWAL ALTERNATIF UNTUK KELAS BENTROK:".center(70))
        print("-" * 70)
        for c in conflicted:
            suggestions = get_schedule_suggestions(c, classes, accepted)
            alt_rooms = suggestions['alt_rooms']
            alt_times = suggestions['alt_times']
            alt_days  = suggestions['alt_days']
            
            print(f"\n[!] Kelas: {c.nama} ({c.code}) | {c.hari} | {c.ruangan} | {c.jam_mulai}-{c.jam_selesai}")
            if not alt_rooms and not alt_times and not alt_days:
                print("    -> Tidak ditemukan saran alternatif otomatis.")
            else:
                if alt_rooms:
                    print("    Saran Ruangan Lain (Hari & Jam sama):")
                    for r_sug in alt_rooms:
                        print(f"      * {r_sug}")
                if alt_times:
                    print("    Saran Waktu Lain (Hari & Ruangan sama):")
                    for t_sug in alt_times:
                        print(f"      * {t_sug}")
                if alt_days:
                    print("    Saran Hari Lain (Ruangan & Jam sama):")
                    for d_sug in alt_days:
                        print(f"      * Pindah ke hari {d_sug}")
    else:
        print("[v] Luar biasa! Tidak ada jadwal yang bentrok.")

    print("\n" + "=" * 70)
    print("RINGKASAN EFISIENSI PENJADWALAN".center(70))
    print("=" * 70)
    total = len(accepted) + len(conflicted)
    success_rate = (len(accepted) / total * 100) if total > 0 else 0
    print(f"  - Total Pengajuan Kelas : {total}")
    print(f"  - Berhasil Dijadwalkan  : {len(accepted)}")
    print(f"  - Gagal / Bentrok       : {len(conflicted)}")
    print(f"  - Persentase Penerimaan : {success_rate:.2f}%")
    print("=" * 70)
    
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
     a. Kelompokkan pengajuan jadwal berdasarkan (Ruangan, Hari) — bentrok
        hanya terjadi jika ruangan, waktu, DAN hari yang sama.
     b. Sortir kelas di tiap kelompok berdasarkan waktu selesai (ascending).
     c. Ambil kelas pertama.
     d. Untuk kelas-kelas berikutnya, jika waktu mulai kelas >= waktu selesai
        kelas sebelumnya yang diambil, maka terima kelas tersebut.

2. Dimensi Hari (Senin-Minggu):
   - Hari kerja utama: Senin - Jumat.
   - Sabtu dan Minggu tersedia namun biasanya tidak dipakai.
   - Dua kelas tidak dianggap bentrok hanya karena ada di ruangan yang sama
     jika harinya berbeda.

3. Struktur Data yang Digunakan:
   - Objek Kelas (Class Kuliah): Menyimpan properti kelas dan konversi menit.
   - List: Menampung kumpulan kelas yang diinput.
   - Dictionary: Mengelompokkan list kelas berdasarkan kunci (ruangan, hari).

4. Analisis Kompleksitas Waktu: O(n log n)
   - Mengelompokkan kelas: O(n) di mana n adalah jumlah kelas.
   - Mengurutkan kelas: Untuk grup (ruangan, hari) dengan k kelas, proses
     pengurutan membutuhkan O(k log k). Totalnya O(n log n).
   - Pencarian linear non-overlap: O(n).
   - Sehingga, Total Kompleksitas Waktu adalah O(n log n).
""")
    input("Tekan Enter untuk kembali ke menu...")

def search_filter_cli(classes):
    """Mencari atau menyaring data kelas berdasarkan kriteria tertentu."""
    print_header("CARI & FILTER PERMINTAAN JADWAL")
    print(" [1] Filter Berdasarkan Nama Mata Kuliah")
    print(" [2] Filter Berdasarkan Nama Ruangan")
    print(" [3] Filter Berdasarkan Hari")
    print(" [4] Kembali")
    print("-" * 70)
    
    pilihan = input("Pilih Kriteria (1-4): ").strip()
    if pilihan == '4':
        return
        
    filtered = []
    if pilihan == '1':
        keyword = input_text("Masukkan kata kunci nama mata kuliah: ").lower()
        filtered = [c for c in classes if keyword in c.nama.lower()]
    elif pilihan == '2':
        room = input_text("Masukkan nama ruangan (misal: E101 atau Lab Kom 1): ").upper()
        filtered = [c for c in classes if room == c.ruangan.upper()]
    elif pilihan == '3':
        hari_cari = input_hari("Pilih hari untuk difilter:")
        filtered = [c for c in classes if c.hari == hari_cari]
    else:
        print("[x] Pilihan tidak valid!")
        input("\nTekan Enter...")
        return
        
    print_header(f"HASIL FILTER DATA ({len(filtered)} ditemukan)")
    if filtered:
        headers = ["Kode", "Mata Kuliah", "Hari", "Ruangan", "Jam Mulai", "Jam Selesai"]
        rows = format_class_rows(filtered)
        print_table(headers, rows)
    else:
        print("[!] Tidak ada data yang cocok dengan kriteria.")
    input("\nTekan Enter untuk kembali...")

def delete_schedule_cli(classes, accepted, conflicted, optimized_run):
    """
    Menghapus jadwal kuliah tertentu berdasarkan kode kelas.
    Fitur: auto-reoptimize setelah hapus.
    
    Returns:
        tuple: (accepted, conflicted, optimized_run) yang sudah diperbarui.
    """
    print_header("HAPUS JADWAL KULIAH")
    if not classes:
        print("[!] Data kosong, tidak ada kelas untuk dihapus.")
        input("\nTekan Enter...")
        return accepted, conflicted, optimized_run
        
    code_to_delete = input_text("Masukkan Kode Kelas yang ingin dihapus (misal C01): ").upper()
    found = False
    for c in classes:
        if c.code.upper() == code_to_delete:
            classes.remove(c)
            found = True
            print(f"\n[v] Sukses: Kelas '{c.nama}' ({c.code}) berhasil dihapus!")
            # Auto-Reoptimize
            if optimized_run and classes:
                accepted, conflicted = greedy_schedule(classes)
                print("    Re-optimasi dijalankan otomatis.")
            elif not classes:
                accepted.clear()
                conflicted.clear()
            break
            
    if not found:
        print(f"\n[x] Error: Kelas dengan kode '{code_to_delete}' tidak ditemukan.")
    input("\nTekan Enter...")
    return accepted, conflicted, optimized_run


def edit_schedule_cli(classes, accepted, conflicted, optimized_run):
    """
    Mengedit jadwal kuliah tertentu berdasarkan kode kelas.
    Fitur: saran alternatif otomatis, input Hari, validasi bentrok real-time (dry-run), auto-reoptimize.
    
    Returns:
        tuple: (accepted, conflicted, optimized_run) yang sudah diperbarui.
    """
    print_header("EDIT JADWAL KULIAH")
    if not classes:
        print("[!] Data kosong, tidak ada kelas untuk diedit.")
        input("\nTekan Enter...")
        return accepted, conflicted, optimized_run
        
    code_to_edit = input_text("Masukkan Kode Kelas yang ingin diedit (misal C01): ").upper()
    target_class = None
    for c in classes:
        if c.code.upper() == code_to_edit:
            target_class = c
            break
            
    if not target_class:
        print(f"\n[x] Error: Kelas dengan kode '{code_to_edit}' tidak ditemukan.")
        input("\nTekan Enter...")
        return accepted, conflicted, optimized_run

    print(f"\n--- Mengedit Kelas {target_class.code} ---")
    
    # --- Cari & Tampilkan Saran Alternatif ---
    accepted_for_sug = accepted if optimized_run else greedy_schedule(classes)[0]
    suggestions = get_schedule_suggestions(target_class, classes, accepted_for_sug)
    
    saran_list = []
    import re
    for item in suggestions.get('alt_rooms', []):
        match = re.search(r"Ruang '([^']+)'", item)
        if match:
            r_name = match.group(1)
            saran_list.append({
                'desc': f"Pindahkan ke Ruang '{r_name}' (Hari & Waktu tetap)",
                'ruangan': r_name, 'hari': target_class.hari, 'mulai': target_class.jam_mulai, 'selesai': target_class.jam_selesai
            })
    for t_slot in suggestions.get('alt_times', []):
        parts = t_slot.split('-')
        if len(parts) == 2:
            saran_list.append({
                'desc': f"Ubah Waktu ke {t_slot} (Ruangan & Hari tetap)",
                'ruangan': target_class.ruangan, 'hari': target_class.hari, 'mulai': parts[0], 'selesai': parts[1]
            })
    for day in suggestions.get('alt_days', []):
        saran_list.append({
            'desc': f"Ubah Hari ke {day} (Ruangan & Waktu tetap)",
            'ruangan': target_class.ruangan, 'hari': day, 'mulai': target_class.jam_mulai, 'selesai': target_class.jam_selesai
        })

    saran_choice = 0
    if saran_list:
        print("Saran Jadwal Alternatif yang Bebas Bentrok:")
        for idx, s in enumerate(saran_list, 1):
            print(f"  [{idx}] {s['desc']}")
        print(f"  [0] Edit Manual (Ketik satu per satu)")
        print("-" * 50)
        
        while True:
            raw_opt = input(f"Pilih Opsi (0-{len(saran_list)}) [Default = 0]: ").strip()
            if not raw_opt:
                saran_choice = 0
                break
            if raw_opt.isdigit():
                val = int(raw_opt)
                if 0 <= val <= len(saran_list):
                    saran_choice = val
                    break
            print(f"[x] Pilihan tidak valid. Masukkan angka 0 s.d. {len(saran_list)}.")

    if saran_choice > 0:
        selected_saran = saran_list[saran_choice - 1]
        print(f"\nMenerapkan saran: {selected_saran['desc']}")
        nama_final        = target_class.nama
        ruangan_final     = selected_saran['ruangan']
        hari_baru         = selected_saran['hari']
        jam_mulai_temp    = selected_saran['mulai']
        jam_selesai_temp  = selected_saran['selesai']
        m_mulai           = parse_time(jam_mulai_temp)
        m_selesai         = parse_time(jam_selesai_temp)
    else:
        print("\nTekan Enter langsung jika tidak ingin mengubah nilai tersebut.\n")
        nama_baru    = input(f"Nama Mata Kuliah [{target_class.nama}]: ").strip()
        ruangan_baru = input_ruangan("Pilih Ruangan Baru:", default=target_class.ruangan)
        hari_baru    = input_hari("Pilih Hari Baru:", default=target_class.hari)
        
        while True:
            jam_mulai_baru   = input(f"Jam Mulai  (HH:MM) [{target_class.jam_mulai}]: ").strip()
            jam_selesai_baru = input(f"Jam Selesai (HH:MM) [{target_class.jam_selesai}]: ").strip()
            
            jam_mulai_temp   = jam_mulai_baru   if jam_mulai_baru   else target_class.jam_mulai
            jam_selesai_temp = jam_selesai_baru if jam_selesai_baru else target_class.jam_selesai
            
            try:
                m_mulai   = parse_time(jam_mulai_temp)
                m_selesai = parse_time(jam_selesai_temp)
                if m_mulai >= m_selesai:
                    print("[x] Error: Jam selesai harus setelah jam mulai! Silakan input ulang.")
                    continue
                break
            except ValueError as e:
                print(f"[x] Error: {e}")
                continue
        
        # Nilai final (pakai lama jika tidak diubah)
        nama_final    = nama_baru    if nama_baru    else target_class.nama
        ruangan_final = ruangan_baru if ruangan_baru else target_class.ruangan
    
    # Buat objek simulasi untuk dry-run
    edited_sim = Kuliah(target_class.code, nama_final, ruangan_final,
                        jam_mulai_temp, jam_selesai_temp, hari_baru)
    
    # --- Validasi Bentrok Real-Time (Dry-Run) ---
    is_conflicted, overlapping = _check_conflict_dry_run(
        classes, edited_sim, original_code=target_class.code
    )
    
    if is_conflicted:
        _print_conflict_warning(edited_sim, overlapping)
        pilihan = input("\n  Apakah Anda tetap ingin menyimpan perubahan ini? (y/n): ").strip().lower()
        if pilihan != 'y':
            print("\n[!] Perubahan dibatalkan.")
            input("\nTekan Enter untuk kembali ke menu...")
            return accepted, conflicted, optimized_run
    
    # Terapkan perubahan ke objek asli
    target_class.nama        = nama_final
    target_class.ruangan     = ruangan_final
    target_class.hari        = hari_baru
    target_class.jam_mulai   = jam_mulai_temp
    target_class.jam_selesai = jam_selesai_temp
    target_class.mulai_menit  = m_mulai
    target_class.selesai_menit = m_selesai
    
    # Auto-Reoptimize
    if optimized_run:
        accepted, conflicted = greedy_schedule(classes)
        status = "DITERIMA" if target_class in accepted else "BENTROK"
        print(f"\n[v] Sukses: Kelas '{target_class.nama}' ({target_class.code}) berhasil diperbarui!")
        print(f"    Status setelah re-optimasi: {status}")
    else:
        print(f"\n[v] Sukses: Kelas '{target_class.nama}' ({target_class.code}) berhasil diperbarui!")
    
    input("\nTekan Enter...")
    return accepted, conflicted, optimized_run


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
    accepted      = []
    conflicted    = []
    optimized_run = False
    
    while True:
        clear_screen()
        opt_status = "[AKTIF]" if optimized_run else "[BELUM DIOPTIMASI]"
        print_header("Sistem Penjadwalan Ruangan Kampus - Greedy Algorithm")
        print(f"  Status Optimasi: {opt_status}  |  Total Kelas: {len(classes)}")
        print("-" * 70)
        print(" [1]  Lihat Seluruh Permintaan Jadwal (Raw Data)")
        print(" [2]  Tambah Permintaan Jadwal Baru")
        print(" [3]  Cari / Filter Permintaan Jadwal")
        print(" [4]  Hapus Jadwal Tertentu (Berdasarkan Kode)")
        print(" [5]  Proses Optimasi Penjadwalan (Greedy)")
        print(" [6]  Lihat Hasil Optimasi Terakhir")
        print(" [7]  Ekspor Hasil Optimasi ke File Teks")
        print(" [8]  Reset Data ke Data Dummy")
        print(" [9]  Hapus/Reset Seluruh Data")
        print(" [10] Edukasi Teori & Kompleksitas Algoritma")
        print(" [11] Edit Jadwal")
        print(" [12] Keluar dari CLI")
        print("-" * 70)
        
        pilihan = input("Pilih Menu (1-12): ").strip()
        
        if pilihan == '1':
            if not classes:
                print("\n[!] Data kosong. Silakan tambah data atau reset ke data dummy.")
                input("\nTekan Enter...")
            else:
                view_schedules_cli(classes)

        elif pilihan == '2':
            accepted, conflicted, optimized_run = add_schedule_cli(
                classes, accepted, conflicted, optimized_run
            )

        elif pilihan == '3':
            if not classes:
                print("\n[!] Data kosong.")
                input("\nTekan Enter...")
            else:
                search_filter_cli(classes)

        elif pilihan == '4':
            accepted, conflicted, optimized_run = delete_schedule_cli(
                classes, accepted, conflicted, optimized_run
            )

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
                view_optimization_results_cli(classes, accepted, conflicted)

        elif pilihan == '7':
            export_schedule_cli(classes, accepted, conflicted, optimized_run)

        elif pilihan == '8':
            classes.clear()
            classes.extend(get_dummy_data())
            accepted    = []
            conflicted  = []
            optimized_run = False
            print("\n[v] Sukses: Data berhasil di-reset ke 14 data dummy kampus!")
            input("\nTekan Enter...")

        elif pilihan == '9':
            classes.clear()
            accepted    = []
            conflicted  = []
            optimized_run = False
            print("\n[v] Sukses: Seluruh data jadwal telah dihapus!")
            input("\nTekan Enter...")

        elif pilihan == '10':
            explain_algorithm_cli()

        elif pilihan == '11':
            accepted, conflicted, optimized_run = edit_schedule_cli(
                classes, accepted, conflicted, optimized_run
            )

        elif pilihan == '12':
            print("\nTerima kasih telah menggunakan sistem ini.")
            break

        else:
            print("\n[x] Pilihan tidak valid! Silakan masukkan angka 1-12.")
            input("\nTekan Enter...")
