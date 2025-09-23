import tkinter as tk
from tkinter import ttk, scrolledtext

class GuiBuilder:
    def __init__(self, app):
        self.app = app

    def create_main_tabs(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Accent.TButton", foreground="white", background="#0078D7")
        style.configure("Success.TButton", foreground="white", background="#28a745")
        style.configure("Warning.TButton", foreground="white", background="#ffc107")

        self.app.notebook = ttk.Notebook(self.app.root)
        self.app.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.app.tab_diagnosis = ttk.Frame(self.app.notebook)
        self.app.tab_riwayat = ttk.Frame(self.app.notebook)
        self.app.tab_info = ttk.Frame(self.app.notebook)

        self.app.notebook.add(self.app.tab_diagnosis, text="🔍 Diagnosis")
        self.app.notebook.add(self.app.tab_riwayat, text="📋 Riwayat Diagnosis")
        self.app.notebook.add(self.app.tab_info, text="ℹ️ Info Penyakit")

        self.create_diagnosis_tab()
        self.create_riwayat_tab()
        self.create_info_tab()

    def create_diagnosis_tab(self):
        main_canvas = tk.Canvas(self.app.tab_diagnosis, highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.app.tab_diagnosis, orient="vertical", command=main_canvas.yview)
        scrollable_container = ttk.Frame(main_canvas)
        scrollable_container.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        canvas_window = main_canvas.create_window((0, 0), window=scrollable_container, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_canvas.bind("<Configure>", lambda e: main_canvas.itemconfig(canvas_window, width=e.width))
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        header_frame = ttk.Frame(scrollable_container)
        header_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(header_frame, text="🏥 Sistem Pakar Diagnosis Flu", font=("Arial", 18, "bold")).pack()
        ttk.Label(header_frame, text="Pilih gejala yang Anda alami:", font=("Arial", 12)).pack(pady=5)

        gejala_outer_frame = ttk.Frame(scrollable_container)
        gejala_outer_frame.pack(fill='x', expand=True, padx=5, pady=5)
        gejala_outer_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        kategori_frames = {}
        for i, nama_kategori in enumerate(["Gejala Umum", "Gejala Pernapasan", "Gejala Lainnya"]):
            frame = ttk.LabelFrame(gejala_outer_frame, text=f"📌 {nama_kategori}", padding=(10, 5))
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            kategori_frames[nama_kategori] = frame
        
        for gejala in self.app.gejala_list:
            kategori = gejala.get("kategori", "Gejala Lainnya")
            if kategori in kategori_frames:
                var = tk.BooleanVar()
                self.app.gejala_vars[gejala["id"]] = var
                cb = ttk.Checkbutton(kategori_frames[kategori], text=gejala["nama"], variable=var)
                cb.pack(anchor='w', padx=5, pady=2)
                self.create_tooltip(cb, gejala.get("deskripsi", "Tidak ada deskripsi"))

        btn_frame = ttk.Frame(scrollable_container)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text="🔍 Mulai Diagnosis", command=self.app.run_diagnosis, style="Accent.TButton").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="🔄 Reset Form", command=self.app.reset_form).pack(side='left', padx=5)

        result_frame = ttk.LabelFrame(scrollable_container, text="📊 Hasil Diagnosis")
        result_frame.pack(fill='x', expand=True, padx=10, pady=10)
        result_frame.grid_columnconfigure((0, 1), weight=1)

        left_frame = ttk.Frame(result_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)
        ttk.Label(left_frame, text="🔄 Log Proses Inferensi:", font=("Arial", 12, "bold")).pack(anchor='w', padx=5)
        self.app.log_text = scrolledtext.ScrolledText(left_frame, height=12, wrap=tk.WORD, font=("Courier New", 9))
        self.app.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(result_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        ttk.Label(right_frame, text="✅ Kesimpulan Diagnosis:", font=("Arial", 12, "bold")).pack(anchor='w', padx=5)
        self.app.result_text = scrolledtext.ScrolledText(right_frame, height=12, wrap=tk.WORD, font=("Arial", 10))
        self.app.result_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.app.reset_form()

    def create_riwayat_tab(self):
        # Frame Pencarian
        search_frame = ttk.LabelFrame(self.app.tab_riwayat, text="🔍 Pencarian & Filter")
        search_frame.pack(fill='x', padx=10, pady=5)
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill='x', padx=5, pady=5)
        
        # Widget Pencarian Teks
        ttk.Label(search_input_frame, text="Cari diagnosis:").pack(side='left', padx=5)
        self.app.search_var = tk.StringVar()
        self.app.search_var.trace('w', self.app.filter_riwayat)
        search_entry = ttk.Entry(search_input_frame, textvariable=self.app.search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        # Widget Filter Bulan
        ttk.Label(search_input_frame, text="Filter bulan:").pack(side='left', padx=(20, 5))
        self.app.month_filter_var = tk.StringVar()
        month_combo = ttk.Combobox(search_input_frame, textvariable=self.app.month_filter_var, width=15, state="readonly")
        month_combo['values'] = ['Semua', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        month_combo.pack(side='left', padx=5)
        ttk.Button(search_input_frame, text="🗑️ Clear", command=self.app.clear_filters).pack(side='left', padx=5)

        # --- PEMBUATAN WIDGET UTAMA (TREEVIEW) DILAKUKAN DI SINI ---
        tree_frame = ttk.Frame(self.app.tab_riwayat)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        columns = ('tanggal', 'diagnosis', 'tingkat_keyakinan')
        self.app.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        self.app.tree.heading('tanggal', text='📅 Tanggal & Waktu')
        self.app.tree.heading('diagnosis', text='🩺 Diagnosis')
        self.app.tree.heading('tingkat_keyakinan', text='📊 Tingkat Keyakinan')
        self.app.tree.column('tanggal', width=180, anchor='center')
        self.app.tree.column('diagnosis', width=400)
        self.app.tree.column('tingkat_keyakinan', width=150, anchor='center')
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.app.tree.yview)
        self.app.tree.configure(yscrollcommand=tree_scrollbar.set)
        self.app.tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')
        self.app.tree.bind("<Double-1>", self.app.show_riwayat_detail)
        
        # Frame Tombol Aksi
        action_frame = ttk.Frame(self.app.tab_riwayat)
        action_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(action_frame, text="📄 Export ke CSV", command=lambda: self.app.export_manager.export_to_csv(self.app.filtered_riwayat), style="Success.TButton").pack(side='left', padx=5)
        ttk.Button(action_frame, text="📑 Export ke PDF", command=lambda: self.app.export_manager.export_to_pdf(self.app.filtered_riwayat), style="Success.TButton").pack(side='left', padx=5)
        ttk.Button(action_frame, text="🗑️ Hapus Semua Riwayat", command=self.app.hapus_riwayat, style="Warning.TButton").pack(side='right', padx=5)
        self.app.info_label = ttk.Label(action_frame, text="", font=("Arial", 9))
        self.app.info_label.pack(side='right', padx=20)
        
        # --- PERUBAHAN KUNCI ADA DI SINI ---
        # Atur trace dan nilai default SETELAH semua widget (terutama self.app.tree) dibuat
        self.app.month_filter_var.trace('w', self.app.filter_riwayat)
        month_combo.set('Semua') # Pemicu pertama kali terjadi di sini, tapi sekarang aman
        
        # Panggil update_riwayat_tree secara manual untuk memastikan data awal dimuat jika riwayat sudah ada
        self.app.update_riwayat_tree()

    def create_info_tab(self):
        info_text = scrolledtext.ScrolledText(self.app.tab_info, wrap=tk.WORD, width=80, height=20, font=("Arial", 11), bd=1, relief="solid")
        info_text.pack(padx=15, pady=15, fill="both", expand=True)
        info_content = """🦠 FLU (INFLUENZA)

Flu adalah infeksi virus yang menyerang sistem pernapasan bagian atas dan bawah. Virus influenza dapat menyebar dengan mudah dari orang ke orang melalui droplet pernapasan.

📋 GEJALA UMUM:
• Demam (biasanya 38°C atau lebih)
• Batuk kering atau berdahak
• Pilek dan hidung tersumbat
• Sakit tenggorokan
• Nyeri otot dan sendi
• Sakit kepala
• Kelelahan dan lemas
• Bersin-bersin
• Menggigil
• Kehilangan nafsu makan

🛡️ PENCEGAHAN:
1. Vaksinasi flu tahunan (sangat direkomendasikan)
2. Cuci tangan secara teratur dengan sabun dan air mengalir
3. Gunakan hand sanitizer berbasis alkohol
4. Hindari kontak dengan orang yang sakit
5. Tutup mulut dan hidung saat batuk atau bersin
6. Hindari menyentuh mata, hidung, dan mulut
7. Jaga kebersihan lingkungan sekitar
8. Tingkatkan daya tahan tubuh dengan:
    - Makan makanan bergizi seimbang
    - Istirahat cukup (7-8 jam per hari)
    - Olahraga teratur
    - Kelola stress dengan baik

💊 PENGOBATAN:
1. Istirahat total di rumah
2. Banyak minum air putih (minimal 8 gelas/hari)
3. Konsumsi makanan bergizi dan mudah dicerna
4. Obat pereda gejala (paracetamol untuk demam dan nyeri)
5. Obat batuk sesuai kebutuhan
6. Berkumur dengan air garam hangat
7. Gunakan humidifier atau hirup uap air hangat
8. Antiviral (jika diresepkan dokter dalam 48 jam pertama)

⚠️ KAPAN HARUS SEGERA KE DOKTER:
• Demam tinggi di atas 39°C yang tidak turun
• Sesak napas atau kesulitan bernapas
• Nyeri dada yang persisten
• Pusing berlebihan atau kebingungan
• Muntah berkelanjutan
• Gejala memburuk setelah 3-5 hari pengobatan
• Dehidrasi berat
• Memiliki kondisi medis kronis (diabetes, asma, penyakit jantung)
• Usia di atas 65 tahun atau di bawah 2 tahun
• Wanita hamil dengan gejala flu berat

⚕️ KONSULTASI MEDIS:
Selalu konsultasikan kondisi Anda dengan tenaga medis profesional untuk mendapatkan diagnosis dan pengobatan yang tepat. Sistem pakar ini hanya sebagai alat bantu awal dan tidak menggantikan konsultasi medis."""
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)

    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+15}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#FFFACD", relief="solid", borderwidth=1, font=("Arial", 9), padx=5, pady=3)
            label.pack()
            widget.tooltip = tooltip
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)