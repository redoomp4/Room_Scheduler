# -*- coding: utf-8 -*-
"""
gui_interface.py - Graphical User Interface (GUI)
==================================================
Modul ini mengimplementasikan GUI desktop berbasis Tkinter untuk memvisualisasikan
jadwal kuliah secara interaktif. Menyediakan visualisasi timeline ruangan,
penambahan data lewat form, dan grafik status optimasi (Diterima vs Bentrok).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from engine import Kuliah, parse_time, greedy_schedule, get_dummy_data, minutes_to_str, export_schedule_to_file, get_schedule_suggestions


class AppGUI:
    def __init__(self, root, classes):
        self.root = root
        self.classes = classes
        
        # Inisialisasi status optimasi
        self.accepted = []
        self.conflicted = []
        self.is_optimized = False

        # Konfigurasi Window Utama
        self.root.title("Sistem Penjadwalan Ruangan Kampus - Greedy Algorithm")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 650)
        
        # Mengatur tema warna modern (Dark Mode Palette)
        self.bg_dark = "#121214"
        self.bg_card = "#1A1A1E"
        self.bg_input = "#26262B"
        self.fg_white = "#F8F8F2"
        self.color_primary = "#6C5CE7" # Purple
        self.color_primary_hover = "#5b4dbf"
        self.color_success = "#2ECC71" # Green
        self.color_danger = "#E74C3C"  # Red
        self.color_info = "#3498DB"    # Blue
        self.color_grid = "#2D2D35"

        self.root.configure(bg=self.bg_dark)
        
        # Konfigurasi Style TTK
        self.setup_styles()
        
        # Layout Utama
        self.create_layout()
        
        # Load Awal Data
        self.update_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Konfigurasi style umum
        style.configure(".", bg=self.bg_dark, fg=self.fg_white)
        style.configure("TFrame", background=self.bg_dark)
        
        # Style Notebook (Tabs)
        style.configure("TNotebook", background=self.bg_dark, borderwidth=0)
        style.configure("TNotebook.Tab", 
                        background=self.bg_card, 
                        foreground=self.fg_white, 
                        padding=[15, 5], 
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=0)
        style.map("TNotebook.Tab", 
                  background=[("selected", self.color_primary)],
                  foreground=[("selected", "#FFFFFF")])

        # Style Treeview (Tabel)
        style.configure("Treeview", 
                        background=self.bg_card, 
                        fieldbackground=self.bg_card, 
                        foreground=self.fg_white, 
                        rowheight=25,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", 
                        background=self.bg_dark, 
                        foreground=self.fg_white, 
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=1)
        style.map("Treeview", 
                  background=[("selected", self.color_primary)],
                  foreground=[("selected", "#FFFFFF")])

    def create_layout(self):
        # -------------------------------------------------------------
        # Left Panel (Control Panel & Input Form)
        # -------------------------------------------------------------
        left_panel = tk.Frame(self.root, bg=self.bg_card, width=320, padx=15, pady=15)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)

        # Title/Logo
        title_lbl = tk.Label(left_panel, text="ROOM SCHEDULER", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 14, "bold"))
        title_lbl.pack(anchor=tk.W, pady=(0, 5))
        sub_lbl = tk.Label(left_panel, text="Greedy Optimization System", bg=self.bg_card, fg=self.color_primary, font=("Segoe UI", 9, "italic"))
        sub_lbl.pack(anchor=tk.W, pady=(0, 20))

        # --- Form Input ---
        form_frame = tk.LabelFrame(left_panel, text="Tambah Jadwal Baru", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 10, "bold"), padx=10, pady=10, bd=1, relief=tk.SOLID)
        form_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(form_frame, text="Mata Kuliah:", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 2))
        self.ent_nama = tk.Entry(form_frame, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10))
        self.ent_nama.pack(fill=tk.X, ipady=4, pady=(0, 8))

        tk.Label(form_frame, text="Ruangan:", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(2, 2))
        self.ent_ruang = tk.Entry(form_frame, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10))
        self.ent_ruang.pack(fill=tk.X, ipady=4, pady=(0, 8))

        time_frame = tk.Frame(form_frame, bg=self.bg_card)
        time_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(time_frame, text="Mulai (HH:MM):", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ent_mulai = tk.Entry(time_frame, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10), width=10)
        self.ent_mulai.grid(row=1, column=0, ipady=4, padx=(0, 5), sticky=tk.W)

        tk.Label(time_frame, text="Selesai (HH:MM):", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.ent_selesai = tk.Entry(time_frame, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10), width=10)
        self.ent_selesai.grid(row=1, column=1, ipady=4, padx=(5, 0), sticky=tk.W)

        btn_add = tk.Button(form_frame, text="Tambah Jadwal", bg=self.color_primary, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground=self.color_primary_hover, activeforeground=self.fg_white, command=self.add_class_gui)
        btn_add.pack(fill=tk.X, ipady=5, pady=(5, 0))

        # --- Tombol Kontrol ---
        btn_opt = tk.Button(left_panel, text="JALANKAN OPTIMASI GREEDY", bg=self.color_success, fg="#121214", font=("Segoe UI", 10, "bold"), bd=0, activebackground="#27ae60", activeforeground="#121214", command=self.run_greedy_gui)
        btn_opt.pack(fill=tk.X, ipady=8, pady=(0, 10))

        btn_reset = tk.Button(left_panel, text="Muat Data Dummy (14 Kelas)", bg=self.color_info, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground="#2980b9", activeforeground=self.fg_white, command=self.load_dummy_gui)
        btn_reset.pack(fill=tk.X, ipady=5, pady=(0, 5))

        btn_clear = tk.Button(left_panel, text="Kosongkan Semua Data", bg=self.color_danger, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground="#c0392b", activeforeground=self.fg_white, command=self.clear_all_gui)
        btn_clear.pack(fill=tk.X, ipady=5, pady=(0, 20))

        # --- Panel Statistik ---
        self.stats_frame = tk.LabelFrame(left_panel, text="Statistik Penjadwalan", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 10, "bold"), padx=10, pady=10, bd=1, relief=tk.SOLID)
        self.stats_frame.pack(fill=tk.BOTH, expand=True)

        self.lbl_total = tk.Label(self.stats_frame, text="Total Pengajuan: -", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9))
        self.lbl_total.pack(anchor=tk.W, pady=2)
        
        self.lbl_accepted = tk.Label(self.stats_frame, text="Diterima (Optimal): -", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9))
        self.lbl_accepted.pack(anchor=tk.W, pady=2)

        self.lbl_conflicted = tk.Label(self.stats_frame, text="Bentrok (Ditolak): -", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9))
        self.lbl_conflicted.pack(anchor=tk.W, pady=2)

        self.lbl_ratio = tk.Label(self.stats_frame, text="Efisiensi Ruangan: -", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9))
        self.lbl_ratio.pack(anchor=tk.W, pady=2)

        # -------------------------------------------------------------
        # Right Panel (Tabbed Workspace)
        # -------------------------------------------------------------
        right_panel = tk.Frame(self.root, bg=self.bg_dark, padx=5, pady=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10))

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Visualisasi Timeline
        self.tab_visual = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.tab_visual, text="  Visualisasi Jadwal  ")
        self.setup_tab_visual()

        # Tab 2: Tabel Data
        self.tab_table = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.tab_table, text="  Daftar Tabel Kelas  ")
        self.setup_tab_table()

        # Tab 3: Teori Algoritma
        self.tab_theory = tk.Frame(self.notebook, bg=self.bg_dark)
        self.notebook.add(self.tab_theory, text="  Edukasi Greedy  ")
        self.setup_tab_theory()

    def setup_tab_visual(self):
        # Frame atas tab visualisasi untuk kontrol tampilan
        ctrl_frame = tk.Frame(self.tab_visual, bg=self.bg_dark, pady=10)
        ctrl_frame.pack(fill=tk.X)
        
        self.vis_mode_var = tk.StringVar(value="optimal")
        
        self.rbtn_raw = tk.Radiobutton(ctrl_frame, text="Tampilkan Semua Pengajuan (Tumpang Tindih)", variable=self.vis_mode_var, value="raw", 
                                       bg=self.bg_dark, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_dark, activeforeground=self.fg_white,
                                       font=("Segoe UI", 9, "bold"), command=self.draw_timeline)
        self.rbtn_raw.pack(side=tk.LEFT, padx=10)
        
        self.rbtn_opt = tk.Radiobutton(ctrl_frame, text="Tampilkan Jadwal Hasil Optimasi Greedy (Optimal)", variable=self.vis_mode_var, value="optimal", 
                                       bg=self.bg_dark, fg=self.fg_white, selectcolor=self.bg_dark, activebackground=self.bg_dark, activeforeground=self.fg_white,
                                       font=("Segoe UI", 9, "bold"), command=self.draw_timeline)
        self.rbtn_opt.pack(side=tk.LEFT, padx=20)

        # Canvas untuk menggambar grafik timeline
        self.canvas_frame = tk.Frame(self.tab_visual, bg=self.bg_card, bd=1, relief=tk.SOLID)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_card, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Binds window resize to redraw timeline dynamically
        self.canvas.bind("<Configure>", lambda event: self.draw_timeline())

    def setup_tab_table(self):
        # Pembagi atas dan bawah: Tabel Pengajuan vs Tabel Bentrok
        table_frame = tk.Frame(self.tab_table, bg=self.bg_dark, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Frame untuk Filter Pencarian
        filter_frame = tk.Frame(table_frame, bg=self.bg_dark)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filter_frame, text="Cari/Filter Kelas:", bg=self.bg_dark, fg=self.fg_white, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        # Bind key release event for live filtering
        self.search_var.trace_add("write", lambda *args: self.filter_table_live())
        
        self.ent_search = tk.Entry(filter_frame, textvariable=self.search_var, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10), width=30)
        self.ent_search.pack(side=tk.LEFT, ipady=4)

        # Keterangan filter
        tk.Label(filter_frame, text="*Menyaring berdasarkan nama/ruangan secara otomatis", bg=self.bg_dark, fg="#888888", font=("Segoe UI", 8, "italic")).pack(side=tk.LEFT, padx=15)

        # Label Header Tabel
        self.lbl_table_header = tk.Label(table_frame, text="Daftar Kelas (Menunggu Optimasi)", bg=self.bg_dark, fg=self.fg_white, font=("Segoe UI", 10, "bold"))
        self.lbl_table_header.pack(anchor=tk.W, pady=(5, 5))

        columns = ("code", "nama", "ruangan", "jam_mulai", "jam_selesai", "status")
        self.tree_classes = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        self.tree_classes.heading("code", text="Kode")
        self.tree_classes.heading("nama", text="Mata Kuliah")
        self.tree_classes.heading("ruangan", text="Ruangan")
        self.tree_classes.heading("jam_mulai", text="Jam Mulai")
        self.tree_classes.heading("jam_selesai", text="Jam Selesai")
        self.tree_classes.heading("status", text="Status")

        self.tree_classes.column("code", width=60, anchor=tk.CENTER)
        self.tree_classes.column("nama", width=250, anchor=tk.W)
        self.tree_classes.column("ruangan", width=120, anchor=tk.CENTER)
        self.tree_classes.column("jam_mulai", width=100, anchor=tk.CENTER)
        self.tree_classes.column("jam_selesai", width=100, anchor=tk.CENTER)
        self.tree_classes.column("status", width=150, anchor=tk.CENTER)

        self.tree_classes.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Konfigurasi warna baris tabel
        self.tree_classes.tag_configure("accepted", background="#1a3d2b", foreground="#2ECC71")
        self.tree_classes.tag_configure("conflicted", background="#3d1b1d", foreground="#E74C3C")
        self.tree_classes.tag_configure("pending", background="#1A1A1E", foreground="#F8F8F2")

        # Scrollbar untuk Treeview
        scroll = ttk.Scrollbar(self.tree_classes, orient=tk.VERTICAL, command=self.tree_classes.yview)
        self.tree_classes.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame untuk Tombol Aksi Tabel
        tbl_btn_frame = tk.Frame(table_frame, bg=self.bg_dark)
        tbl_btn_frame.pack(fill=tk.X, pady=(5, 0))

        btn_delete_sel = tk.Button(tbl_btn_frame, text="Hapus Kelas Terpilih", bg=self.color_danger, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground="#c0392b", activeforeground=self.fg_white, command=self.delete_selected_gui)
        btn_delete_sel.pack(side=tk.LEFT, ipady=5, ipadx=10, padx=(0, 10))

        btn_edit_sel = tk.Button(tbl_btn_frame, text="Edit Kelas Terpilih", bg=self.color_info, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground="#2980b9", activeforeground=self.fg_white, command=self.edit_selected_gui)
        btn_edit_sel.pack(side=tk.LEFT, ipady=5, ipadx=10, padx=(0, 10))

        btn_export = tk.Button(tbl_btn_frame, text="Ekspor Laporan (.txt)", bg=self.color_primary, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground=self.color_primary_hover, activeforeground=self.fg_white, command=self.export_report_gui)
        btn_export.pack(side=tk.LEFT, ipady=5, ipadx=10)


    def setup_tab_theory(self):
        # Teks edukasi algoritma greedy
        text_frame = tk.Frame(self.tab_theory, bg=self.bg_card, padx=15, pady=15, bd=1, relief=tk.SOLID)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        title = tk.Label(text_frame, text="Bagaimana Greedy Algorithm Menyelesaikan Penjadwalan?", bg=self.bg_card, fg=self.color_primary, font=("Segoe UI", 12, "bold"))
        title.pack(anchor=tk.W, pady=(0, 10))

        explanation = """
Sistem ini menggunakan strategi Greedy "Activity Selection Problem" dengan kriteria pemilihan:
"Pilih kelas dengan waktu selesai paling cepat terlebih dahulu."

Kenapa strategi ini optimal?
Dengan memilih kelas yang selesai lebih dahulu, ruangan dibebaskan secepat mungkin. Ruangan yang cepat kosong memiliki peluang lebih besar untuk menampung kelas berikutnya. Hal ini terbukti secara matematis selalu menghasilkan jumlah kelas maksimal yang dapat dijadwalkan pada satu ruangan (Optimal Solution).

Langkah-langkah Eksekusi Algoritma:
1. Pengelompokkan: Kelas dikelompokkan berdasarkan ruangan masing-masing.
2. Pengurutan (Sorting): Di setiap ruangan, kelas diurutkan berdasarkan waktu selesai secara ascending (meningkat).
3. Seleksi (Greedy Choice): 
   - Pilih kelas pertama yang selesai paling cepat dan masukkan ke daftar 'Diterima'.
   - Untuk setiap kelas berikutnya, bandingkan waktu mulainya dengan waktu selesai kelas terakhir yang diterima.
   - Jika waktu mulai >= waktu selesai kelas terakhir, terima kelas tersebut.
   - Jika tidak, kelas tersebut dinyatakan 'Bentrok' karena waktu pelaksanaannya bertabrakan dengan kelas yang sudah disetujui.

Analisis Kompleksitas Waktu:
- Pengurutan (Sorting) adalah langkah paling berat dalam algoritma ini, membutuhkan kompleksitas O(n log n), di mana n adalah jumlah kelas.
- Penyeleksian kelas dilakukan secara linier dengan kompleksitas O(n).
- Dengan demikian, total kompleksitas waktu program ini adalah O(n log n).
"""
        lbl_body = tk.Label(text_frame, text=explanation, bg=self.bg_card, fg=self.fg_white, justify=tk.LEFT, font=("Segoe UI", 9), anchor=tk.NW, wraplength=700)
        lbl_body.pack(fill=tk.BOTH, expand=True)

    # -------------------------------------------------------------
    # Logika Interaksi UI
    # -------------------------------------------------------------
    def update_ui(self):
        """Memperbarui visualisasi timeline, tabel, dan statistik."""
        # 1. Update Statistik
        total = len(self.classes)
        self.lbl_total.config(text=f"Total Pengajuan: {total} kelas")
        
        if self.is_optimized:
            acc_count = len(self.accepted)
            conf_count = len(self.conflicted)
            self.lbl_accepted.config(text=f"Diterima (Optimal): {acc_count} kelas", fg=self.color_success)
            self.lbl_conflicted.config(text=f"Bentrok (Ditolak): {conf_count} kelas", fg=self.color_danger)
            
            efficiency = (acc_count / total * 100) if total > 0 else 0
            self.lbl_ratio.config(text=f"Efisiensi Ruangan: {efficiency:.1f}%")
            self.lbl_table_header.config(text="Daftar Status Kelas Setelah Optimasi")
        else:
            self.lbl_accepted.config(text="Diterima (Optimal): - (Belum dioptimasi)", fg=self.fg_white)
            self.lbl_conflicted.config(text="Bentrok (Ditolak): - (Belum dioptimasi)", fg=self.fg_white)
            self.lbl_ratio.config(text="Efisiensi Ruangan: -")
            self.lbl_table_header.config(text="Daftar Kelas Pengajuan (Belum Dioptimasi)")

        # 2. Update Tabel (Treeview)
        self.filter_table_live()

        # 3. Gambar Ulang Timeline
        self.draw_timeline()

    def draw_timeline(self):
        """Menggambar grafik jadwal perkuliahan pada Canvas."""
        self.canvas.delete("all")
        
        if not self.classes:
            self.canvas.create_text(
                self.canvas.winfo_width()/2, self.canvas.winfo_height()/2,
                text="Tidak ada data kelas. Tambahkan data atau muat data dummy.",
                fill="#888888", font=("Segoe UI", 11)
            )
            return

        # Dapatkan daftar ruangan unik
        rooms = sorted(list(set(c.ruangan for c in self.classes)))
        
        # Hitung rentang waktu visualisasi secara dinamis
        min_min = 420  # 07:00
        max_min = 900  # 15:00
        for c in self.classes:
            min_min = min(min_min, c.mulai_menit)
            max_min = max(max_min, c.selesai_menit)
            
        # Bulatkan ke jam terdekat
        start_hour = min_min // 60
        end_hour = (max_min + 59) // 60
        
        # Cegah pembagian dengan nol atau rentang aneh
        if end_hour <= start_hour:
            end_hour = start_hour + 8
            
        total_minutes = (end_hour - start_hour) * 60

        # Parameter Geometri Canvas
        margin_left = 100
        margin_right = 20
        margin_top = 40
        margin_bottom = 30
        
        canvas_width = max(self.canvas.winfo_width(), 600)
        canvas_height = max(self.canvas.winfo_height(), 400)
        
        plot_width = canvas_width - margin_left - margin_right
        plot_height = canvas_height - margin_top - margin_bottom

        # Menghitung skala piksel per menit
        scale_x = plot_width / total_minutes
        
        # Gambar header Jam di bagian atas
        for h in range(start_hour, end_hour + 1):
            curr_min = (h - start_hour) * 60
            x = margin_left + (curr_min * scale_x)
            
            # Gambar garis grid vertikal
            self.canvas.create_line(x, margin_top, x, canvas_height - margin_bottom, fill=self.color_grid, width=1)
            # Label jam
            time_str = f"{h:02d}:00"
            self.canvas.create_text(x, margin_top - 15, text=time_str, fill="#888888", font=("Segoe UI", 8, "bold"))

        # Menggambar baris per ruangan
        row_height = plot_height / len(rooms) if rooms else plot_height
        
        for idx, room in enumerate(rooms):
            y_mid = margin_top + (idx * row_height) + (row_height / 2)
            
            # Garis horizontal batas ruangan
            self.canvas.create_line(margin_left, margin_top + (idx + 1)*row_height, canvas_width - margin_right, margin_top + (idx + 1)*row_height, fill=self.color_grid, width=1)
            
            # Tulis nama Ruangan di kolom kiri
            self.canvas.create_text(45, y_mid, text=room, fill=self.fg_white, font=("Segoe UI", 10, "bold"))

            # Dapatkan kelas untuk ruangan ini
            room_classes = [c for c in self.classes if c.ruangan == room]
            
            # Tentukan visualisasi berdasarkan pilihan radio button
            mode = self.vis_mode_var.get()
            
            # Urutkan agar penggambaran rapi
            room_classes.sort(key=lambda x: x.mulai_menit)

            for c in room_classes:
                # Koordinat X
                x1 = margin_left + ((c.mulai_menit - (start_hour * 60)) * scale_x)
                x2 = margin_left + ((c.selesai_menit - (start_hour * 60)) * scale_x)
                
                # Koordinat Y (buat box berada di tengah baris ruangan)
                box_h = min(row_height * 0.7, 40)
                
                if self.is_optimized:
                    if mode == "optimal":
                        if c in self.accepted:
                            y1 = y_mid - (box_h / 2)
                            y2 = y_mid + (box_h / 2)
                            color = self.color_success
                            text_color = "#121214"
                        else:
                            # Abaikan kelas yang bentrok dari visualisasi timeline agar bersih
                            continue
                    else: # mode == "raw" setelah optimasi: tampilkan kedua kelas (hijau & merah) dengan offset vertikal
                        if c in self.accepted:
                            y1 = y_mid - box_h * 0.85
                            y2 = y_mid - box_h * 0.05
                            color = self.color_success
                            text_color = "#121214"
                        else:
                            y1 = y_mid + box_h * 0.1
                            y2 = y_mid + box_h * 0.7
                            color = self.color_danger
                            text_color = "#FFFFFF"
                else: # Belum dioptimasi
                    y1 = y_mid - (box_h / 2)
                    y2 = y_mid + (box_h / 2)
                    if mode == "optimal":
                        color = "#F1C40F"
                        text_color = "#121214"
                    else:
                        color = self.color_info
                        text_color = "#FFFFFF"
                
                # Gambar rounded rectangle menggunakan canvas
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333333", width=1, dash=None)
                
                # Batasi teks agar tidak keluar dari kotak jika durasi kelas terlalu singkat
                rect_width = x2 - x1
                display_text = c.code
                if rect_width > 90:
                    display_text = f"{c.code}: {c.nama}"
                elif rect_width > 40:
                    display_text = c.nama[:8] + ".."
                
                y_box_mid = (y1 + y2) / 2
                box_height_actual = y2 - y1
                # Tulis judul mata kuliah di dalam box
                text_id1 = self.canvas.create_text((x1 + x2)/2, y_box_mid - 5, text=display_text, fill=text_color, font=("Segoe UI", 8 if box_height_actual > 25 else 7, "bold"))
                # Tulis jam di dalam box
                text_id2 = self.canvas.create_text((x1 + x2)/2, y_box_mid + 7, text=f"{c.jam_mulai}-{c.jam_selesai}", fill=text_color, font=("Segoe UI", 7 if box_height_actual > 25 else 6))
                
                # Bind klik mouse kiri (Button-1) untuk menampilkan popup detail kelas
                # Gunakan capture variable default argument `item=c` agar objek terikat dengan benar
                self.canvas.tag_bind(rect_id, "<Button-1>", lambda event, item=c: self.show_class_details(item))
                self.canvas.tag_bind(text_id1, "<Button-1>", lambda event, item=c: self.show_class_details(item))
                self.canvas.tag_bind(text_id2, "<Button-1>", lambda event, item=c: self.show_class_details(item))


    # --- Aksi Tombol ---
    def add_class_gui(self):
        nama = self.ent_nama.get().strip()
        ruangan = self.ent_ruang.get().strip().upper()
        jam_mulai = self.ent_mulai.get().strip()
        jam_selesai = self.ent_selesai.get().strip()

        if not nama or not ruangan or not jam_mulai or not jam_selesai:
            messagebox.showerror("Error Input", "Semua kolom input wajib diisi!")
            return

        try:
            # Validasi format waktu
            m_mulai = parse_time(jam_mulai)
            m_selesai = parse_time(jam_selesai)
            
            if m_mulai >= m_selesai:
                messagebox.showerror("Error Input", "Jam selesai harus setelah jam mulai!")
                return
        except ValueError as e:
            messagebox.showerror("Error Input", str(e))
            return

        # Auto-generate kode kelas
        existing_nums = []
        for c in self.classes:
            if c.code.startswith('C') and c.code[1:].isdigit():
                existing_nums.append(int(c.code[1:]))
        next_num = max(existing_nums) + 1 if existing_nums else 1
        new_code = f"C{next_num:02d}"

        # Tambahkan kelas baru
        new_class = Kuliah(new_code, nama, ruangan, jam_mulai, jam_selesai)
        self.classes.append(new_class)
        
        # Reset input form
        self.ent_nama.delete(0, tk.END)
        self.ent_ruang.delete(0, tk.END)
        self.ent_mulai.delete(0, tk.END)
        self.ent_selesai.delete(0, tk.END)
        
        # Tandai bahwa data berubah dan perlu optimasi ulang
        self.is_optimized = False
        self.accepted.clear()
        self.conflicted.clear()
        
        self.update_ui()
        messagebox.showinfo("Sukses", f"Kelas '{nama}' ({new_code}) di {ruangan} berhasil ditambahkan.")

    def run_greedy_gui(self):
        if not self.classes:
            messagebox.showwarning("Data Kosong", "Tidak ada data kelas untuk dioptimasi!")
            return
            
        self.accepted, self.conflicted = greedy_schedule(self.classes)
        self.is_optimized = True
        self.vis_mode_var.set("optimal") # Beralih otomatis ke visualisasi optimal
        self.update_ui()
        
        messagebox.showinfo("Optimasi Berhasil", 
                            f"Optimasi Greedy selesai!\n"
                            f"Diterima: {len(self.accepted)} kelas\n"
                            f"Bentrok (Ditolak): {len(self.conflicted)} kelas.")

    def load_dummy_gui(self):
        self.classes.clear()
        self.classes.extend(get_dummy_data())
        self.is_optimized = False
        self.accepted.clear()
        self.conflicted.clear()
        self.vis_mode_var.set("optimal")
        self.update_ui()
        messagebox.showinfo("Reset Data", "Berhasil memuat 14 data dummy kampus untuk pengujian.")

    def clear_all_gui(self):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus semua data jadwal?"):
            self.classes.clear()
            self.is_optimized = False
            self.accepted.clear()
            self.conflicted.clear()
            self.update_ui()
            messagebox.showinfo("Hapus Data", "Semua data berhasil dibersihkan.")

    def filter_table_live(self):
        """Menyaring baris Treeview secara real-time berdasarkan isi entri pencarian."""
        keyword = self.search_var.get().strip().lower()
        
        # Hapus data tabel lama
        for item in self.tree_classes.get_children():
            self.tree_classes.delete(item)
            
        # Isi dengan data yang sesuai
        for c in sorted(self.classes, key=lambda x: (x.ruangan, x.mulai_menit)):
            if not keyword or keyword in c.nama.lower() or keyword in c.ruangan.lower() or keyword in c.code.lower():
                status = "Menunggu Optimasi"
                row_tag = "pending"
                if self.is_optimized:
                    if c in self.accepted:
                        status = "Diterima"
                        row_tag = "accepted"
                    else:
                        status = "Bentrok (Ditolak)"
                        row_tag = "conflicted"
                self.tree_classes.insert("", tk.END, values=(c.code, c.nama, c.ruangan, c.jam_mulai, c.jam_selesai, status), tags=(row_tag,))

    def delete_selected_gui(self):
        """Menghapus jadwal kuliah yang dipilih pada tabel Treeview."""
        selected_item = self.tree_classes.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih baris pada tabel terlebih dahulu untuk menghapus!")
            return
            
        # Dapatkan nilai kolom pertama (Kode Kelas)
        values = self.tree_classes.item(selected_item[0], "values")
        if not values:
            return
        code = values[0]
        
        # Cari objek kelas berdasarkan kode
        target_class = None
        for c in self.classes:
            if c.code == code:
                target_class = c
                break
                
        if target_class:
            if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus kelas '{target_class.nama}' ({target_class.code})?"):
                self.classes.remove(target_class)
                self.is_optimized = False
                self.accepted.clear()
                self.conflicted.clear()
                self.update_ui()
                messagebox.showinfo("Hapus Berhasil", f"Kelas '{target_class.nama}' berhasil dihapus.")

    def edit_selected_gui(self):
        """Membuka dialog modal untuk mengedit kelas yang dipilih pada tabel."""
        selected_item = self.tree_classes.selection()
        if not selected_item:
            messagebox.showwarning("Peringatan", "Pilih baris pada tabel terlebih dahulu untuk mengedit!")
            return
            
        values = self.tree_classes.item(selected_item[0], "values")
        if not values:
            return
        code = values[0]
        
        target_class = None
        for c in self.classes:
            if c.code == code:
                target_class = c
                break
                
        if not target_class:
            return

        # Buat Window Toplevel Modal
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Edit Jadwal Kelas - {target_class.code}")
        edit_win.geometry("400x320")
        edit_win.resizable(False, False)
        edit_win.configure(bg=self.bg_card)
        edit_win.transient(self.root)
        edit_win.grab_set()

        # Letakkan window di tengah screen relatif ke root
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        win_x = root_x + (root_w - 400) // 2
        win_y = root_y + (root_h - 320) // 2
        edit_win.geometry(f"+{win_x}+{win_y}")

        # Label Header
        lbl_title = tk.Label(edit_win, text=f"Edit Kelas {target_class.code}", bg=self.bg_card, fg=self.color_primary, font=("Segoe UI", 12, "bold"))
        lbl_title.pack(pady=(15, 15))

        # Container Frame
        container = tk.Frame(edit_win, bg=self.bg_card, padx=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Nama Matkul
        tk.Label(container, text="Mata Kuliah:", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        ent_nama = tk.Entry(container, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10))
        ent_nama.insert(0, target_class.nama)
        ent_nama.grid(row=0, column=1, fill=tk.X, sticky=tk.W+tk.E, padx=(10, 0), ipady=4, pady=5)

        # Ruangan
        tk.Label(container, text="Ruangan:", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        ent_ruang = tk.Entry(container, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10))
        ent_ruang.insert(0, target_class.ruangan)
        ent_ruang.grid(row=1, column=1, fill=tk.X, sticky=tk.W+tk.E, padx=(10, 0), ipady=4, pady=5)

        # Jam Mulai
        tk.Label(container, text="Mulai (HH:MM):", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=5)
        ent_mulai = tk.Entry(container, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10))
        ent_mulai.insert(0, target_class.jam_mulai)
        ent_mulai.grid(row=2, column=1, fill=tk.X, sticky=tk.W+tk.E, padx=(10, 0), ipady=4, pady=5)

        # Jam Selesai
        tk.Label(container, text="Selesai (HH:MM):", bg=self.bg_card, fg=self.fg_white, font=("Segoe UI", 9)).grid(row=3, column=0, sticky=tk.W, pady=5)
        ent_selesai = tk.Entry(container, bg=self.bg_input, fg=self.fg_white, insertbackground=self.fg_white, bd=0, font=("Segoe UI", 10))
        ent_selesai.insert(0, target_class.jam_selesai)
        ent_selesai.grid(row=3, column=1, fill=tk.X, sticky=tk.W+tk.E, padx=(10, 0), ipady=4, pady=5)

        # Konfigurasi grid weight agar Entry memanjang
        container.grid_columnconfigure(1, weight=1)

        def save_changes():
            nama_val = ent_nama.get().strip()
            ruang_val = ent_ruang.get().strip().upper()
            mulai_val = ent_mulai.get().strip()
            selesai_val = ent_selesai.get().strip()

            if not nama_val or not ruang_val or not mulai_val or not selesai_val:
                messagebox.showerror("Error Input", "Semua kolom wajib diisi!", parent=edit_win)
                return

            try:
                m_mulai = parse_time(mulai_val)
                m_selesai = parse_time(selesai_val)
                if m_mulai >= m_selesai:
                    messagebox.showerror("Error Input", "Jam selesai harus setelah jam mulai!", parent=edit_win)
                    return
            except ValueError as e:
                messagebox.showerror("Error Input", str(e), parent=edit_win)
                return

            # Simpan perubahan
            target_class.nama = nama_val
            target_class.ruangan = ruang_val
            target_class.jam_mulai = mulai_val
            target_class.jam_selesai = selesai_val
            target_class.mulai_menit = m_mulai
            target_class.selesai_menit = m_selesai

            # Reset optimasi
            self.is_optimized = False
            self.accepted.clear()
            self.conflicted.clear()

            self.update_ui()
            edit_win.destroy()
            messagebox.showinfo("Sukses", f"Kelas '{target_class.nama}' ({target_class.code}) berhasil diperbarui.")

        # Tombol aksi
        btn_frame = tk.Frame(edit_win, bg=self.bg_card, pady=15)
        btn_frame.pack(fill=tk.X)

        btn_cancel = tk.Button(btn_frame, text="Batal", bg=self.color_danger, fg=self.fg_white, font=("Segoe UI", 9, "bold"), bd=0, activebackground="#c0392b", activeforeground=self.fg_white, command=edit_win.destroy, width=10)
        btn_cancel.pack(side=tk.RIGHT, padx=(10, 20), ipady=4)

        btn_save = tk.Button(btn_frame, text="Simpan", bg=self.color_success, fg="#121214", font=("Segoe UI", 9, "bold"), bd=0, activebackground="#27ae60", activeforeground="#121214", command=save_changes, width=10)
        btn_save.pack(side=tk.RIGHT, ipady=4)

    def export_report_gui(self):
        """Mengekspor laporan optimasi ke berkas teks via dialog file."""
        if not self.is_optimized:
            messagebox.showwarning("Belum Dioptimasi", "Silakan jalankan optimasi Greedy terlebih dahulu sebelum mengekspor laporan!")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Simpan Laporan Optimasi Sebagai"
        )
        
        if filepath:
            try:
                export_schedule_to_file(filepath, self.classes, self.accepted, self.conflicted)
                messagebox.showinfo("Ekspor Berhasil", f"Laporan optimasi berhasil disimpan ke:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Ekspor Gagal", f"Gagal menyimpan berkas: {e}")

    def show_class_details(self, item):
        """Menampilkan popup rincian detail jadwal saat diklik pada linimasa."""
        duration = item.selesai_menit - item.mulai_menit
        hours = duration // 60
        mins = duration % 60
        duration_str = f"{hours} jam" + (f" {mins} menit" if mins > 0 else "")
        
        status = "Menunggu Optimasi"
        is_conflicted = False
        if self.is_optimized:
            if item in self.accepted:
                status = "Diterima (Optimal)"
            else:
                status = "Bentrok (Ditolak)"
                is_conflicted = True
            
        detail_msg = (
            f"=== RINCIAN JADWAL KULIAH ===\n\n"
            f"• Kode Kelas      : {item.code}\n"
            f"• Mata Kuliah     : {item.nama}\n"
            f"• Ruangan         : {item.ruangan}\n"
            f"• Jam Mulai       : {item.jam_mulai}\n"
            f"• Jam Selesai     : {item.jam_selesai}\n"
            f"• Durasi Kelas    : {duration_str}\n"
            f"• Status Jadwal   : {status}"
        )
        
        if is_conflicted:
            suggestions = get_schedule_suggestions(item, self.classes, self.accepted)
            alt_rooms = suggestions['alt_rooms']
            alt_times = suggestions['alt_times']
            
            sug_text = "\n\n=== SARAN JADWAL ALTERNATIF ==="
            if alt_rooms:
                sug_text += "\n\nSaran Ruangan Lain (Jam Sama):"
                for s in alt_rooms:
                    sug_text += f"\n  * {s}"
            if alt_times:
                sug_text += "\n\nSaran Waktu Lain (Ruangan Sama):"
                for s in alt_times:
                    sug_text += f"\n  * {s}"
            if not alt_rooms and not alt_times:
                sug_text += "\n\nTidak ditemukan saran alternatif otomatis."
            detail_msg += sug_text

        messagebox.showinfo("Detail Informasi Kelas", detail_msg)

def launch_gui(classes):
    """Fungsi pembantu untuk meluncurkan GUI."""
    root = tk.Tk()
    app = AppGUI(root, classes)
    root.mainloop()

