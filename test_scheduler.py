# -*- coding: utf-8 -*-
"""
test_scheduler.py - Unit Test Sederhana
========================================
Skrip ini memverifikasi bahwa Algoritma Greedy (Activity Selection) berjalan
dengan benar dan menjamin tidak ada jadwal kuliah yang tumpang tindih (overlap)
pada ruangan yang sama dan hari yang sama, serta memverifikasi fungsi rekomendasi saran jadwal.
"""

import os
from engine import get_dummy_data, greedy_schedule, get_schedule_suggestions, save_to_json, load_from_json, validate_operational_hours, parse_time

def test_no_overlap():
    print("[...] Menjalankan pengujian algoritma...")
    classes = get_dummy_data()
    accepted, conflicted = greedy_schedule(classes)
    
    # 1. Pastikan seluruh kelas terdaftar
    assert len(accepted) + len(conflicted) == len(classes), "Total kelas tidak cocok!"
    
    # 2. Kelompokkan kelas yang diterima berdasarkan (ruangan, hari)
    rooms_days_schedule = {}
    for c in accepted:
        key = (c.ruangan, c.hari)
        if key not in rooms_days_schedule:
            rooms_days_schedule[key] = []
        rooms_days_schedule[key].append(c)
        
    # 3. Periksa bentrok/overlapping untuk setiap ruangan pada hari yang sama
    for (room, day), room_classes in rooms_days_schedule.items():
        # Urutkan berdasarkan waktu mulai untuk pengecekan sekuensial
        room_classes.sort(key=lambda x: x.mulai_menit)
        
        for i in range(len(room_classes) - 1):
            c1 = room_classes[i]
            c2 = room_classes[i+1]
            
            # Waktu mulai kelas kedua harus >= waktu selesai kelas pertama
            assert c2.mulai_menit >= c1.selesai_menit, (
                f"BENTROK TERDETEKSI pada {room} hari {day}: "
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
    assert 'alt_days' in suggestions, "Kunci 'alt_days' tidak ditemukan!"
    
    # C02 (08:00-10:00) bentrok di Lab Kom 2 hari Senin.
    # Di Lab Kom 2 (setelah C03 selesai pukul 11:00), harusnya ada slot kosong
    assert len(suggestions['alt_times']) > 0, "Saran slot waktu di Lab Kom 2 harus tersedia!"
    
    print("[v] Sukses: Pengujian Saran Jadwal Berhasil!")
    print("    Saran Ruangan Lain untuk C02:")
    for r in suggestions['alt_rooms']:
        print(f"      - {r}")
    print("    Saran Waktu Lain untuk C02:")
    for t in suggestions['alt_times']:
        print(f"      - {t}")
    print("    Saran Hari Lain untuk C02:")
    for d in suggestions['alt_days']:
        print(f"      - Pindah ke hari {d}")


def test_json_persistence():
    print("[...] Menjalankan pengujian persistensi data JSON...")
    classes = get_dummy_data()
    temp_filename = "temp_test_schedule.json"
    
    try:
        # Simpan ke JSON
        save_to_json(temp_filename, classes)
        assert os.path.exists(temp_filename), "Berkas JSON tidak terbuat!"
        
        # Muat dari JSON
        loaded_classes = load_from_json(temp_filename)
        assert len(loaded_classes) == len(classes), "Jumlah kelas yang dimuat tidak sama!"
        
        for c1, c2 in zip(classes, loaded_classes):
            assert c1.code == c2.code, "Kode kelas tidak cocok!"
            assert c1.nama == c2.nama, "Nama kelas tidak cocok!"
            assert c1.ruangan == c2.ruangan, "Ruangan tidak cocok!"
            assert c1.jam_mulai == c2.jam_mulai, "Jam mulai tidak cocok!"
            assert c1.jam_selesai == c2.jam_selesai, "Jam selesai tidak cocok!"
            assert c1.hari == c2.hari, "Hari tidak cocok!"
            
        print("[v] Sukses: Pengujian Persistensi JSON Berhasil!")
    finally:
        # Bersihkan file temp
        if os.path.exists(temp_filename):
            os.remove(temp_filename)


def test_operational_hours_validation():
    print("[...] Menjalankan pengujian validasi jam operasional...")
    
    # Jam valid (di dalam 07:00 - 20:00)
    try:
        validate_operational_hours(parse_time("07:00"), parse_time("20:00"))
        validate_operational_hours(parse_time("08:00"), parse_time("10:00"))
    except ValueError as e:
        assert False, f"Seharusnya valid tetapi terdeteksi error: {e}"
        
    # Jam tidak valid (di luar 07:00 - 20:00)
    try:
        validate_operational_hours(parse_time("06:59"), parse_time("09:00"))
        assert False, "Seharusnya gagal untuk jam mulai sebelum 07:00!"
    except ValueError:
        pass
        
    try:
        validate_operational_hours(parse_time("18:00"), parse_time("20:01"))
        assert False, "Seharusnya gagal untuk jam selesai setelah 20:00!"
    except ValueError:
        pass

    try:
        validate_operational_hours(parse_time("10:00"), parse_time("09:00"))
        assert False, "Seharusnya gagal jika jam mulai >= jam selesai!"
    except ValueError:
        pass
        
    print("[v] Sukses: Pengujian Validasi Jam Operasional Berhasil!")


if __name__ == "__main__":
    test_no_overlap()
    print("-" * 50)
    test_schedule_suggestions()
    print("-" * 50)
    test_json_persistence()
    print("-" * 50)
    test_operational_hours_validation()

