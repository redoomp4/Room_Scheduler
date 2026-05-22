# -*- coding: utf-8 -*-
"""
main.py - Main Entry Point
=========================
Entry point utama untuk menjalankan aplikasi Sistem Penjadwalan Ruangan Kampus
berbasis Algoritma Greedy. Pengguna dapat memilih untuk menjalankan aplikasi
dalam Mode CLI (terminal) atau Mode GUI (desktop Tkinter).

Cara Menjalankan:
-----------------
1. Mode Interaktif (Menu Pemilihan):
   python main.py
   
2. Langsung Masuk Mode GUI:
   python main.py --gui
   
3. Langsung Masuk Mode CLI:
   python main.py --cli
"""

import sys
from engine import get_dummy_data
from cli_interface import run_cli_main, clear_screen, print_header
from gui_interface import launch_gui

def main():
    # Inisialisasi daftar kelas dengan data dummy awal (14 data)
    classes = get_dummy_data()
    
    # Periksa parameter argumen baris perintah untuk bypass menu pemilih
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--gui', '-g', 'gui']:
            launch_gui(classes)
            return
        elif arg in ['--cli', '-c', 'cli']:
            run_cli_main(classes)
            return

    # Tampilan pemilih mode interaktif jika tidak ada argumen
    while True:
        clear_screen()
        print_header("SISTEM PENJADWALAN RUANGAN KAMPUS (GREEDY)")
        print(" Selamat datang di aplikasi simulasi optimasi jadwal kuliah.")
        print(" Silakan pilih mode tampilan yang ingin Anda jalankan:\n")
        print(" [1] Mode CLI (Command Line Interface - Terminal Rapi)")
        print(" [2] Mode GUI (Graphical User Interface - Desktop Visual)")
        print(" [3] Keluar")
        print("-" * 65)
        
        pilihan = input("Pilih Mode (1-3): ").strip()
        
        if pilihan == '1':
            run_cli_main(classes)
        elif pilihan == '2':
            print("\n[...] Membuka jendela GUI. Silakan periksa taskbar/desktop Anda...")
            try:
                launch_gui(classes)
            except Exception as e:
                print(f"\n[x] Gagal memuat GUI: {e}")
                print("Pastikan sistem Anda mendukung library Tkinter.")
                input("\nTekan Enter untuk kembali...")
        elif pilihan == '3':
            print("\nTerima kasih! Sampai jumpa.")
            break
        else:
            print("\n[x] Pilihan tidak valid! Masukkan angka 1-3.")
            input("\nTekan Enter...")

if __name__ == "__main__":
    main()
