# -*- coding: utf-8 -*-
"""
engine.py - Core Scheduling Engine
==================================
Modul ini mengimplementasikan logika inti penjadwalan kuliah berbasis ruangan
menggunakan Algoritma Greedy. Strategi greedy yang digunakan adalah
"Activity Selection Problem" dengan kriteria pemilihan:
"Pilih kelas dengan waktu selesai paling cepat terlebih dahulu agar ruangan 
dapat digunakan semaksimal mungkin."

Analisis Kompleksitas Waktu:
-----------------------------
1. Pengelompokkan kelas berdasarkan ruangan: O(n) di mana n adalah jumlah total kelas.
2. Pengurutan kelas berdasarkan waktu selesai per ruangan: O(k log k) untuk setiap ruangan dengan k kelas.
   Akumulasi untuk semua ruangan: O(n log n).
3. Seleksi linear untuk menentukan kelas yang tidak overlap: O(n).
Sehingga, total kompleksitas waktu sistem ini adalah O(n log n).

Struktur Data:
--------------
- Objek/Class `Kuliah`: Menyimpan data setiap jadwal kuliah.
- List: Digunakan untuk menampung seluruh daftar kelas.
- Dictionary: Digunakan untuk mengelompokkan kelas berdasarkan nama ruangan.
"""

def parse_time(time_str):
    """
    Mengonversi string format HH:MM menjadi integer (menit sejak tengah malam).
    Contoh: '07:30' -> 7 * 60 + 30 = 450 menit.
    
    Args:
        time_str (str): Format waktu 'HH:MM'
        
    Returns:
        int: Menit sejak tengah malam
    """
    try:
        parts = time_str.split(':')
        if len(parts) != 2:
            raise ValueError("Format tidak valid.")
        hours = int(parts[0])
        minutes = int(parts[1])
        if not (0 <= hours < 24) or not (0 <= minutes < 60):
            raise ValueError("Jam atau menit di luar jangkauan.")
        return hours * 60 + minutes
    except Exception:
        raise ValueError(f"Waktu '{time_str}' tidak valid. Harus berformat HH:MM (00:00 - 23:59).")


def minutes_to_str(minutes):
    """Mengonversi menit integer sejak tengah malam kembali menjadi string HH:MM."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


class Kuliah:
    def __init__(self, code, nama, ruangan, jam_mulai, jam_selesai, hari="Senin"):
        """
        Konstruktor kelas Kuliah.
        
        Args:
            code (str): Kode kelas unik (misal: 'K01')
            nama (str): Nama mata kuliah
            ruangan (str): Nama ruangan kampus
            jam_mulai (str): Waktu mulai kelas format 'HH:MM'
            jam_selesai (str): Waktu selesai kelas format 'HH:MM'
            hari (str): Hari pelaksanaan kelas (default: 'Senin')
        """
        self.code = code
        self.nama = nama
        self.ruangan = ruangan
        self.jam_mulai = jam_mulai
        self.jam_selesai = jam_selesai
        self.hari = hari
        
        # Konversi waktu ke bentuk menit untuk memudahkan komparasi matematis
        self.mulai_menit = parse_time(jam_mulai)
        self.selesai_menit = parse_time(jam_selesai)

    def to_dict(self):
        """Mengembalikan representasi dictionary dari objek Kuliah."""
        return {
            'code': self.code,
            'nama': self.nama,
            'ruangan': self.ruangan,
            'jam_mulai': self.jam_mulai,
            'jam_selesai': self.jam_selesai,
            'hari': self.hari,
            'mulai_menit': self.mulai_menit,
            'selesai_menit': self.selesai_menit
        }

    def __repr__(self):
        return f"Kuliah({self.code}, {self.nama}, {self.ruangan}, {self.hari} {self.jam_mulai}-{self.jam_selesai})"


def get_dummy_data():
    """
    Menyediakan minimal 10 data dummy perkuliahan untuk pengujian awal.
    Terdapat beberapa data yang saling bentrok pada ruangan dan hari yang sama.
    
    Returns:
        list: Daftar objek Kuliah
    """
    dummy_configs = [
        # Ruang AULA (Tersebar di Senin dan Selasa)
        ('C01', 'Perancangan & Analisis Algoritma', 'AULA', '07:00', '09:00', 'Senin'),
        ('C02', 'Aljabar Linear', 'AULA', '08:00', '10:00', 'Senin'),  # Bentrok dengan C01 di Senin
        ('C03', 'Struktur Data', 'AULA', '09:00', '11:00', 'Senin'),   # Mulai tepat saat C01 selesai di Senin
        ('C04', 'Pemrograman Web', 'AULA', '10:30', '12:30', 'Selasa'),
        ('C05', 'Kecerdasan Buatan', 'AULA', '11:00', '13:00', 'Selasa'),# Bentrok dengan C04 di Selasa
 
        # Ruang LAB-01 (Tersebar di Rabu dan Kamis)
        ('C06', 'Basis Data', 'LAB-01', '07:30', '09:30', 'Rabu'),
        ('C07', 'Keamanan Informasi', 'LAB-01', '09:00', '10:30', 'Rabu'), # Bentrok dengan C06 di Rabu
        ('C08', 'Jaringan Komputer', 'LAB-01', '09:40', '11:40', 'Rabu'),  # Mulai setelah C06 selesai di Rabu
        ('C09', 'Interaksi Manusia Komputer', 'LAB-01', '11:00', '13:00', 'Kamis'),
        ('C10', 'Grafika Komputer', 'LAB-01', '12:00', '14:00', 'Kamis'),   # Bentrok dengan C09 di Kamis
 
        # Ruang 301 (Tersebar di Jumat)
        ('C11', 'Sistem Operasi', 'Ruang 301', '08:00', '10:00', 'Jumat'),
        ('C12', 'Metode Numerik', 'Ruang 301', '09:30', '11:30', 'Jumat'),   # Bentrok dengan C11 di Jumat
        ('C13', 'Bahasa Indonesia', 'Ruang 301', '10:00', '11:30', 'Jumat'), # Mulai tepat saat C11 selesai di Jumat
        ('C14', 'Fisika Dasar', 'Ruang 301', '11:30', '13:00', 'Jumat'),      # Mulai setelah C13 selesai di Jumat
    ]
    return [Kuliah(*config) for config in dummy_configs]


def greedy_schedule(classes):
    """
    Melakukan proses optimasi penjadwalan menggunakan Greedy Algorithm.
    Strategi: Activity Selection Problem
    
    Alur Kerja Greedy:
    1. Kelompokkan seluruh kelas berdasarkan pasangan (ruangan, hari) (karena optimasi dilakukan per ruangan per hari).
    2. Untuk setiap kombinasi (ruangan, hari):
       - Urutkan kelas berdasarkan waktu selesai (selesai_menit) terkecil ke terbesar.
         Hal ini memastikan bahwa ruangan dibebaskan secepat mungkin untuk kelas berikutnya.
       - Ambil kelas pertama yang selesai paling cepat. Kelas ini otomatis DITERIMA.
       - Untuk setiap kelas berikutnya dalam antrean terurut:
         - Periksa apakah waktu mulai kelas >= waktu selesai kelas terakhir yang diterima.
         - Jika ya, kelas DITERIMA, dan perbarui referensi kelas terakhir yang diterima.
         - Jika tidak, kelas dinyatakan BENTROK dan ditolak dari ruangan tersebut pada hari itu.
         
    Args:
        classes (list): Daftar seluruh objek Kuliah yang diajukan.
        
    Returns:
        tuple: (accepted_classes, conflicted_classes)
               - accepted_classes (list): Daftar kelas yang berhasil dijadwalkan (optimal).
               - conflicted_classes (list): Daftar kelas yang tidak dapat dijadwalkan karena bentrok.
    """
    if not classes:
        return [], []

    # 1. Kelompokkan kelas berdasarkan (ruangan, hari)
    rooms_days_schedule = {}
    for c in classes:
        key = (c.ruangan, c.hari)
        if key not in rooms_days_schedule:
            rooms_days_schedule[key] = []
        rooms_days_schedule[key].append(c)

    accepted_classes = []
    conflicted_classes = []

    # 2. Proses optimasi Greedy untuk setiap (ruangan, hari)
    for (room, day), group_classes in rooms_days_schedule.items():
        # Langkah A: Urutkan kelas berdasarkan waktu selesai paling cepat (selesai_menit)
        # Jika waktu selesai sama, urutkan berdasarkan waktu mulai (mulai_menit) secara ascending.
        sorted_classes = sorted(group_classes, key=lambda x: (x.selesai_menit, x.mulai_menit))

        # Langkah B: Pilih kelas pertama (Greedy Choice)
        last_accepted = sorted_classes[0]
        accepted_classes.append(last_accepted)

        # Langkah C: Seleksi linear sisa kelas
        for i in range(1, len(sorted_classes)):
            current_class = sorted_classes[i]
            # Mengecek kondisi tidak tumpang tindih (non-overlap)
            if current_class.mulai_menit >= last_accepted.selesai_menit:
                accepted_classes.append(current_class)
                last_accepted = current_class
            else:
                conflicted_classes.append(current_class)

    # Kembalikan daftar yang sudah disortir agar rapi secara visual saat ditampilkan
    # Diurutkan berdasarkan: Hari -> Ruangan -> Jam Mulai
    day_order = {'Senin': 0, 'Selasa': 1, 'Rabu': 2, 'Kamis': 3, 'Jumat': 4, 'Sabtu': 5, 'Minggu': 6}
    accepted_classes.sort(key=lambda x: (day_order.get(x.hari, 7), x.ruangan, x.mulai_menit))
    conflicted_classes.sort(key=lambda x: (day_order.get(x.hari, 7), x.ruangan, x.mulai_menit))

    return accepted_classes, conflicted_classes


def export_schedule_to_file(filepath, classes, accepted, conflicted):
    """
    Mengekspor laporan optimasi jadwal ke file teks terformat.
    
    Args:
        filepath (str): Lokasi file tujuan ekspor
        classes (list): Seluruh pengajuan kelas
        accepted (list): Kelas yang diterima
        conflicted (list): Kelas yang bentrok
    """
    total = len(classes)
    acc_count = len(accepted)
    conf_count = len(conflicted)
    ratio = (acc_count / total * 100) if total > 0 else 0
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=================================================================\n")
        f.write("            LAPORAN OPTIMASI JADWAL RUANGAN KAMPUS              \n")
        f.write("                 METODE: GREEDY ALGORITHM                        \n")
        f.write("=================================================================\n\n")
        
        f.write(f"Total Pengajuan Kelas : {total}\n")
        f.write(f"Berhasil Dijadwalkan  : {acc_count}\n")
        f.write(f"Bentrok (Ditolak)     : {conf_count}\n")
        f.write(f"Persentase Penerimaan : {ratio:.2f}%\n\n")
        
        f.write("-----------------------------------------------------------------\n")
        f.write("1. DAFTAR JADWAL YANG DITERIMA (OPTIMAL)\n")
        f.write("-----------------------------------------------------------------\n")
        if accepted:
            f.write(f"{'Kode':<6} | {'Mata Kuliah':<30} | {'Ruangan':<10} | {'Waktu':<15}\n")
            f.write("-" * 70 + "\n")
            for c in sorted(accepted, key=lambda x: (x.ruangan, x.mulai_menit)):
                f.write(f"{c.code:<6} | {c.nama:<30} | {c.ruangan:<10} | {c.jam_mulai}-{c.jam_selesai}\n")
        else:
            f.write("Tidak ada jadwal yang disetujui.\n")
        f.write("\n")
        
        f.write("-----------------------------------------------------------------\n")
        f.write("2. DAFTAR JADWAL BENTROK (DITOLAK)\n")
        f.write("-----------------------------------------------------------------\n")
        if conflicted:
            f.write(f"{'Kode':<6} | {'Mata Kuliah':<30} | {'Ruangan':<10} | {'Waktu':<15}\n")
            f.write("-" * 70 + "\n")
            for c in sorted(conflicted, key=lambda x: (x.ruangan, x.mulai_menit)):
                f.write(f"{c.code:<6} | {c.nama:<30} | {c.ruangan:<10} | {c.jam_mulai}-{c.jam_selesai}\n")
        else:
            f.write("Tidak ada jadwal bentrok.\n")
        f.write("\n")
        f.write("=================================================================\n")
        f.write("Laporan dibuat secara otomatis oleh Sistem Penjadwalan Greedy.\n")


def get_schedule_suggestions(target_class, all_classes, accepted_classes):
    """
    Mencari saran jadwal alternatif untuk sebuah kelas yang bentrok.
    Mengembalikan tiga jenis saran:
      1. Alternatif Ruangan: Ruangan lain di mana slot waktu dan hari yang SAMA tersedia.
      2. Alternatif Waktu: Slot waktu kosong di hari dan ruangan yang SAMA.
      3. Alternatif Hari: Hari lain di mana slot waktu dan ruangan yang SAMA tersedia.

    Args:
        target_class: Objek Kuliah yang bentrok.
        all_classes (list): Seluruh daftar kelas yang diajukan.
        accepted_classes (list): Daftar kelas yang sudah diterima oleh greedy.

    Returns:
        dict: {
            'alt_rooms': list[str]  -> saran ruangan alternatif,
            'alt_times': list[str]  -> saran slot waktu alternatif,
            'alt_days': list[str]   -> saran hari alternatif
        }
    """
    durasi = target_class.selesai_menit - target_class.mulai_menit

    # --- Kelompokkan kelas yang DITERIMA berdasarkan (hari, ruangan) ---
    accepted_by_day_room = {}
    for c in accepted_classes:
        key = (c.hari, c.ruangan)
        if key not in accepted_by_day_room:
            accepted_by_day_room[key] = []
        accepted_by_day_room[key].append(c)

    # Ambil semua nama ruangan unik dari seluruh pengajuan
    all_rooms = sorted(set(c.ruangan for c in all_classes))
    work_days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']

    # ----------------------------------------------------------------
    # Saran 1: Ruangan Alternatif (Hari & Jam yang sama, Ruangan berbeda)
    # ----------------------------------------------------------------
    alt_rooms = []
    for room in all_rooms:
        if room == target_class.ruangan:
            continue  # Skip ruangan asal

        occupied = accepted_by_day_room.get((target_class.hari, room), [])
        can_fit = True
        for c in occupied:
            if target_class.mulai_menit < c.selesai_menit and target_class.selesai_menit > c.mulai_menit:
                can_fit = False
                break
        if can_fit:
            alt_rooms.append(
                f"Ruang '{room}' ({target_class.jam_mulai}-{target_class.jam_selesai})"
            )

    # ----------------------------------------------------------------
    # Saran 2: Waktu Alternatif (Hari & Ruangan yang sama, Waktu berbeda)
    # ----------------------------------------------------------------
    alt_times = []
    same_day_room_accepted = sorted(
        accepted_by_day_room.get((target_class.hari, target_class.ruangan), []),
        key=lambda x: x.mulai_menit
    )

    # Rentang jam operasional kampus: 07:00 - 20:00
    ops_start = 7 * 60   # 420 menit
    ops_end   = 20 * 60  # 1200 menit

    occupied_slots = [(c.mulai_menit, c.selesai_menit) for c in same_day_room_accepted]
    occupied_slots.sort()

    gaps = []
    prev_end = ops_start
    for (s, e) in occupied_slots:
        if s > prev_end:
            gaps.append((prev_end, s))
        prev_end = max(prev_end, e)
    if prev_end < ops_end:
        gaps.append((prev_end, ops_end))

    MAX_SUGGESTIONS = 3
    for (gap_start, gap_end) in gaps:
        if gap_end - gap_start >= durasi:
            slot_mulai = gap_start
            slot_selesai = gap_start + durasi
            alt_times.append(
                f"{minutes_to_str(slot_mulai)}-{minutes_to_str(slot_selesai)}"
            )
            if len(alt_times) >= MAX_SUGGESTIONS:
                break

    # ----------------------------------------------------------------
    # Saran 3: Hari Alternatif (Ruangan & Jam yang sama, Hari berbeda)
    # ----------------------------------------------------------------
    alt_days = []
    for day in work_days:
        if day == target_class.hari:
            continue

        occupied = accepted_by_day_room.get((day, target_class.ruangan), [])
        can_fit = True
        for c in occupied:
            if target_class.mulai_menit < c.selesai_menit and target_class.selesai_menit > c.mulai_menit:
                can_fit = False
                break
        if can_fit:
            alt_days.append(day)

    return {'alt_rooms': alt_rooms, 'alt_times': alt_times, 'alt_days': alt_days}
