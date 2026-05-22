# -*- coding: utf-8 -*-
"""
test_scheduler.py - Unit Test Sederhana
========================================
Skrip ini memverifikasi bahwa Algoritma Greedy (Activity Selection) berjalan
dengan benar dan menjamin tidak ada jadwal kuliah yang tumpang tindih (overlap)
pada ruangan yang sama.
"""

from engine import get_dummy_data, greedy_schedule

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

if __name__ == "__main__":
    test_no_overlap()
