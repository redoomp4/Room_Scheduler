# -*- coding: utf-8 -*-
"""
test_scheduler.py - Unit Test Sederhana
========================================
Skrip ini memverifikasi bahwa Algoritma Greedy (Activity Selection) berjalan
dengan benar dan menjamin tidak ada jadwal kuliah yang tumpang tindih (overlap)
pada ruangan yang sama, serta memverifikasi fungsi rekomendasi saran jadwal.
"""

from engine import get_dummy_data, greedy_schedule, get_schedule_suggestions

def test_no_overlap():
    print("[...] Menjalankan pengujian algoritma...")
    classes = get_dummy_data()
    accepted, conflicted = greedy_schedule(classes)
    
    # 1. Pastikan seluruh kelas terdaftar
    assert len(accepted) + len(conflicted) == len(classes), "Total kelas tidak cocok!"
    
    # 2. Kelompokkan kelas yang diterima berdasarkan ruangan
    rooms_schedule = {}
    for c in accepted:
        if c.ruangan not in rooms_schedule:
            rooms_schedule[c.ruangan] = []
        rooms_schedule[c.ruangan].append(c)
        
    # 3. Periksa bentrok/overlapping untuk setiap ruangan
    for room, room_classes in rooms_schedule.items():
        # Urutkan berdasarkan waktu mulai untuk pengecekan sekuensial
        room_classes.sort(key=lambda x: x.mulai_menit)
        
        for i in range(len(room_classes) - 1):
            c1 = room_classes[i]
            c2 = room_classes[i+1]
            
            # Waktu mulai kelas kedua harus >= waktu selesai kelas pertama
            assert c2.mulai_menit >= c1.selesai_menit, (
                f"BENTROK TERDETEKSI pada {room}: "
                f"'{c1.nama}' ({c1.jam_mulai}-{c1.jam_selesai}) "
                f"dan '{c2.nama}' ({c2.jam_mulai}-{c2.jam_selesai})"
            )
            
    print("[v] Sukses: Pengujian Berhasil! Algoritma menjamin tidak ada jadwal overlap.")
    print(f"    - Total Pengajuan: {len(classes)} kelas")
    print(f"    - Berhasil dijadwalkan secara optimal: {len(accepted)} kelas")
    print(f"    - Bentrok disaring: {len(conflicted)} kelas")


def test_schedule_suggestions():
    print("[...] Menjalankan pengujian saran jadwal alternatif...")
    classes = get_dummy_data()
    accepted, conflicted = greedy_schedule(classes)
    
    # Cari satu kelas yang bentrok (misal C02)
    c02 = next((c for c in conflicted if c.code == 'C02'), None)
    assert c02 is not None, "Kelas C02 harusnya bentrok!"
    
    suggestions = get_schedule_suggestions(c02, classes, accepted)
    
    # Pastikan output dictionary memiliki format yang benar
    assert isinstance(suggestions, dict), "Output harus berupa dictionary!"
    assert 'alt_rooms' in suggestions, "Kunci 'alt_rooms' tidak ditemukan!"
    assert 'alt_times' in suggestions, "Kunci 'alt_times' tidak ditemukan!"
    
    # C02 (08:00-10:00) bentrok di AULA. 
    # Di AULA (setelah C05 selesai pukul 13:00), harusnya ada slot kosong
    assert len(suggestions['alt_times']) > 0, "Saran slot waktu di AULA harus tersedia!"
    
    print("[v] Sukses: Pengujian Saran Jadwal Berhasil!")
    print("    Saran Ruangan Lain untuk C02:")
    for r in suggestions['alt_rooms']:
        print(f"      - {r}")
    print("    Saran Waktu Lain untuk C02:")
    for t in suggestions['alt_times']:
        print(f"      - {t}")


if __name__ == "__main__":
    test_no_overlap()
    print("-" * 50)
    test_schedule_suggestions()
