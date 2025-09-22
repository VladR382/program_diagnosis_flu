import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import os

class DiagnosisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Pakar Diagnosis Flu")
        self.root.geometry("800x600")

        self.json_file = 'gejala_penyakit.json'
        self.load_data()

        self.facts = {gejala["id"]: False for gejala in self.gejala_list}

        self.riwayat_file = 'riwayat_diagnosis.json'
        self.riwayat = []
        self.load_riwayat()

        self.create_gui()

    def load_data(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            self.gejala_list = data["gejala"]
            self.rules = data["aturan"]
            self.solusi = data["solusi"]
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {self.json_file} tidak ditemukan!")
            self.root.destroy()
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Format file {self.json_file} tidak valid!")
            self.root.destroy()

    def load_riwayat(self):
        try:
            if os.path.exists(self.riwayat_file):
                with open(self.riwayat_file, 'r', encoding='utf-8') as file:
                    self.riwayat = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.riwayat = []

    def save_riwayat(self):
        try:
            with open(self.riwayat_file, 'w', encoding='utf-8') as file:
                json.dump(self.riwayat, file, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan riwayat: {str(e)}")

    def create_gui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Accent.TButton", foreground="white", background="#0078D7")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_diagnosis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_diagnosis, text="Diagnosis")
        self.create_diagnosis_tab()

        self.tab_riwayat = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_riwayat, text="Riwayat Diagnosis")
        self.create_riwayat_tab()

        self.tab_info = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_info, text="Info Penyakit")
        self.create_info_tab()

    def create_diagnosis_tab(self):
        main_canvas = tk.Canvas(self.tab_diagnosis, highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(self.tab_diagnosis, orient="vertical", command=main_canvas.yview)
        
        scrollable_container = ttk.Frame(main_canvas)
        scrollable_container.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        canvas_window = main_canvas.create_window((0, 0), window=scrollable_container, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        
        def on_canvas_configure(event):
            canvas_width = event.width
            main_canvas.itemconfig(canvas_window, width=canvas_width)

        main_canvas.bind("<Configure>", on_canvas_configure)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        header_frame = ttk.Frame(scrollable_container)
        header_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(header_frame, text="Sistem Pakar Diagnosis Flu", font=("Arial", 18, "bold")).pack()
        ttk.Label(header_frame, text="Pilih gejala yang Anda alami:", font=("Arial", 12)).pack(pady=5)

        gejala_outer_frame = ttk.Frame(scrollable_container)
        gejala_outer_frame.pack(fill='x', expand=True, padx=5, pady=5)
        gejala_outer_frame.grid_columnconfigure((0, 1, 2), weight=1)

        kategori_frames = {}
        daftar_kategori = ["Gejala Umum", "Gejala Pernapasan", "Gejala Lainnya"]

        for i, nama_kategori in enumerate(daftar_kategori):
            frame = ttk.LabelFrame(gejala_outer_frame, text=nama_kategori, padding=(10, 5))
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            kategori_frames[nama_kategori] = frame
        
        self.gejala_vars = {}
        for gejala in self.gejala_list:
            kategori = gejala.get("kategori")
            if kategori in kategori_frames:
                var = tk.BooleanVar()
                self.gejala_vars[gejala["id"]] = var
                cb = ttk.Checkbutton(kategori_frames[kategori], text=gejala["nama"], variable=var)
                cb.pack(anchor='w', padx=5, pady=2)

        btn_frame = ttk.Frame(scrollable_container)
        btn_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(btn_frame, text="Diagnosa", command=self.run_diagnosis, style="Accent.TButton").pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Reset", command=self.reset_form).pack(side='left', padx=5)

        result_frame = ttk.LabelFrame(scrollable_container, text="Hasil Diagnosis")
        result_frame.pack(fill='x', expand=True, padx=10, pady=10)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_columnconfigure(1, weight=1)

        left_frame = ttk.Frame(result_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)
        ttk.Label(left_frame, text="Log Proses:", font=("Arial", 12, "bold")).pack(anchor='w', padx=5)
        self.log_text = scrolledtext.ScrolledText(left_frame, height=8, wrap=tk.WORD, font=("Courier New", 9))
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

        right_frame = ttk.Frame(result_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        ttk.Label(right_frame, text="Kesimpulan:", font=("Arial", 12, "bold")).pack(anchor='w', padx=5)
        self.result_text = scrolledtext.ScrolledText(right_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

    def create_riwayat_tab(self):
        columns = ('tanggal', 'diagnosis', 'tingkat_keyakinan')
        self.tree = ttk.Treeview(self.tab_riwayat, columns=columns, show='headings', height=15)
        self.tree.heading('tanggal', text='Tanggal')
        self.tree.heading('diagnosis', text='Diagnosis')
        self.tree.heading('tingkat_keyakinan', text='Tingkat Keyakinan')
        self.tree.column('tanggal', width=150, anchor='center')
        self.tree.column('diagnosis', width=400)
        self.tree.column('tingkat_keyakinan', width=150, anchor='center')
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree.bind("<Double-1>", self.show_riwayat_detail)
        
        ttk.Button(self.tab_riwayat, text="Hapus Semua Riwayat", command=self.hapus_riwayat).pack(pady=10)
        self.update_riwayat_tree()

    def show_riwayat_detail(self, event):
        selected_item_id = self.tree.focus()
        if not selected_item_id:
            return
            
        selected_item = self.tree.item(selected_item_id)
        tanggal_pilihan = selected_item['values'][0]

        detail_data = None
        for riwayat in self.riwayat:
            if riwayat['tanggal'] == tanggal_pilihan:
                detail_data = riwayat
                break
        
        if detail_data:
            win_detail = tk.Toplevel(self.root)
            win_detail.title(f"Detail Diagnosis - {tanggal_pilihan}")
            win_detail.geometry("400x450")
            win_detail.transient(self.root)
            win_detail.grab_set()

            text_widget = scrolledtext.ScrolledText(win_detail, wrap=tk.WORD, font=("Arial", 10), bd=0, relief="flat")
            text_widget.pack(padx=15, pady=15, fill="both", expand=True)

            konten = f"Tanggal: {detail_data['tanggal']}\n\n"
            konten += f"Diagnosis: {detail_data['diagnosis']}\n"
            konten += f"Tingkat Keyakinan: {detail_data['tingkat_keyakinan']*100:.1f}%\n\n"
            konten += "Gejala yang Dipilih:\n"
            for gejala in detail_data['gejala']:
                konten += f"- {gejala}\n"
            
            konten += "\n"
            konten += "Rekomendasi yang Diberikan:\n"
            if detail_data['rekomendasi']:
                for rek in detail_data['rekomendasi']:
                    konten += f"- {rek}\n"
            else:
                konten += "- Tidak ada rekomendasi khusus.\n"
            
            text_widget.insert(tk.END, konten)
            text_widget.config(state=tk.DISABLED)

    def create_info_tab(self):
        info_text = scrolledtext.ScrolledText(self.tab_info, wrap=tk.WORD, width=80, height=20, font=("Arial", 10))
        info_text.pack(padx=10, pady=10, fill="both", expand=True)
        info_content = """FLU (INFLUENZA)

Flu adalah infeksi virus yang menyerang sistem pernapasan. Gejala umum meliputi:
- Demam
- Batuk
- Pilek
- Sakit tenggorokan
- Nyeri otot
- Sakit kepala
- Lemas
- Bersin-bersin

PENCEGAHAN:
1. Cuci tangan secara teratur dengan sabun dan air
2. Hindari kontak dengan orang yang sakit
3. Tutup mulut dan hidung saat batuk atau bersin
4. Jaga kebersihan lingkungan
5. Tingkatkan daya tahan tubuh dengan makan bergizi dan istirahat cukup

PENGOBATAN:
1. Istirahat yang cukup
2. Banyak minum air putih
3. Konsumsi obat pereda gejala
4. Konsultasi ke dokter jika gejala berat atau tidak kunjung membaik

KAPAN HARUS KE DOKTER:
- Demam tinggi di atas 39°C
- Sesak napas
- Nyeri dada
- Pusing berlebihan
- Gejala memburuk setelah 3-5 hari
- Memiliki kondisi medis kronis"""
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)

    def run_diagnosis(self):
        gejala_terpilih = [gid for gid, var in self.gejala_vars.items() if var.get()]
        if not gejala_terpilih:
            messagebox.showwarning("Peringatan", "Anda belum memilih gejala apapun. Silakan pilih minimal satu gejala.")
            return

        self.facts = {gejala["id"]: False for gejala in self.gejala_list}
        for gid in gejala_terpilih:
            self.facts[gid] = True
        
        self.log_text.config(state=tk.NORMAL)
        self.result_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)

        new_facts_found = True
        conclusions = {}
        self.log_text.insert(tk.END, "FAKTA AWAL:\n" + ", ".join(gejala_terpilih) + "\n\n")

        while new_facts_found:
            new_facts_found = False
            for rule in self.rules:
                conclusion = rule["conclusion"]
                if not self.facts.get(conclusion, False):
                    conditions_met = all(self.facts.get(cond, False) for cond in rule["conditions"])
                    if conditions_met:
                        self.facts[conclusion] = True
                        new_facts_found = True
                        if conclusion.startswith("kemungkinan_"):
                            conclusions[conclusion] = rule.get("bobot", 1.0)
                        self.log_text.insert(tk.END, f"ATURAN DITERAPKAN: JIKA ({', '.join(rule['conditions'])}) MAKA {conclusion}\n")
        
        diagnosis_results = [(c.replace("kemungkinan_", "").replace("_", " ").title(), b) for c, b in conclusions.items()]
        recommendations = [self.solusi[key] for key in self.solusi if self.facts.get(key, False)]
        
        if diagnosis_results:
            self.result_text.insert(tk.END, "Hasil Diagnosis:\n")
            for diagnosis, confidence in diagnosis_results:
                self.result_text.insert(tk.END, f"- {diagnosis} (Keyakinan: {confidence*100:.1f}%)\n")
        else:
            self.result_text.insert(tk.END, "Tidak ada diagnosis yang dapat disimpulkan.\n")

        if recommendations:
            self.result_text.insert(tk.END, "\nRekomendasi:\n")
            for rec in recommendations:
                self.result_text.insert(tk.END, f"- {rec}\n")

        self.log_text.config(state=tk.DISABLED)
        self.result_text.config(state=tk.DISABLED)
        
        diagnosis_str = ", ".join([f"{d} ({c*100:.1f}%)" for d, c in diagnosis_results]) if diagnosis_results else "Tidak ada diagnosis"
        self.simpan_riwayat(diagnosis_str, max([c for _, c in diagnosis_results], default=0))
        self.update_riwayat_tree()

    def reset_form(self):
        for var in self.gejala_vars.values():
            var.set(False)
        
        self.log_text.config(state=tk.NORMAL)
        self.result_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.result_text.config(state=tk.DISABLED)

    def simpan_riwayat(self, diagnosis, confidence):
        gejala_terpilih_nama = [g["nama"] for g in self.gejala_list if self.gejala_vars[g["id"]].get()]
        riwayat_entry = {
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gejala": gejala_terpilih_nama,
            "diagnosis": diagnosis,
            "tingkat_keyakinan": confidence,
            "rekomendasi": [self.solusi[key] for key in self.solusi if self.facts.get(key, False)]
        }
        self.riwayat.insert(0, riwayat_entry)
        self.save_riwayat()

    def update_riwayat_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in self.riwayat:
            self.tree.insert('', 'end', values=(entry["tanggal"], entry["diagnosis"], f"{entry['tingkat_keyakinan']*100:.1f}%"))

    def hapus_riwayat(self):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus semua riwayat diagnosis?"):
            self.riwayat = []
            self.save_riwayat()
            self.update_riwayat_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiagnosisApp(root)
    root.mainloop()
