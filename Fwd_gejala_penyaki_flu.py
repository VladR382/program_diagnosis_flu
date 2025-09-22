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

        # Membuat canvas dan scrollbar utama
        self.main_canvas = tk.Canvas(root)
        self.main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.main_frame = ttk.Frame(self.main_canvas)

        self.main_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # Load data dari JSON
        self.json_file = 'gejala_penyakit.json'
        self.load_data()
        
        # Inisialisasi fakta
        self.facts = {gejala["id"]: False for gejala in self.gejala_list}
        
        # Inisialisasi riwayat sebelum create_gui
        self.riwayat_file = 'riwayat_diagnosis.json'
        self.riwayat = []
        self.load_riwayat()
        
        # Buat GUI di dalam main_frame
        self.create_gui()
    
    def load_data(self):
        try:
            with open(self.json_file, 'r') as file:
                data = json.load(file)
            self.gejala_list = data["gejala"]
            self.rules = data["aturan"]
            self.solusi = data["solusi"]
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {self.json_file} tidak ditemukan!")
            self.root.destroy()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Format JSON tidak valid!")
            self.root.destroy()
    
    def load_riwayat(self):
        try:
            with open(self.riwayat_file, 'r') as file:
                self.riwayat = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.riwayat = []
    
    def save_riwayat(self):
        try:
            with open(self.riwayat_file, 'w') as file:
                json.dump(self.riwayat, file, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan riwayat: {str(e)}")
    
    def create_gui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook untuk tab, dipasang di main_frame
        self.notebook = ttk.Notebook(self.main_frame)
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
        self.tab_diagnosis.grid_rowconfigure(1, weight=1)
        self.tab_diagnosis.grid_columnconfigure(0, weight=1)

        header_frame = ttk.Frame(self.tab_diagnosis)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Label(
            header_frame, 
            text="Sistem Pakar Diagnosis Flu", 
            font=("Arial", 18, "bold")
        ).pack()
        
        ttk.Label(
            header_frame, 
            text="Pilih gejala yang Anda alami:", 
            font=("Arial", 12)
        ).pack(pady=5)
        
        gejala_frame = ttk.Frame(self.tab_diagnosis)
        gejala_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        gejala_frame.grid_rowconfigure(0, weight=1)
        gejala_frame.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(gejala_frame)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(gejala_frame, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.gejala_vars = {}
        
        for i, gejala in enumerate(self.gejala_list):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill='x', padx=5, pady=2)
            
            var = tk.BooleanVar()
            self.gejala_vars[gejala["id"]] = var
            
            cb = ttk.Checkbutton(
                frame, 
                text=gejala["nama"], 
                variable=var
            )
            cb.pack(side='left')
            
            self.create_tooltip(cb, gejala["deskripsi"])
        
        btn_frame = ttk.Frame(self.tab_diagnosis)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Diagnosa", 
            command=self.run_diagnosis,
            style="Accent.TButton"
        ).pack(side='left', padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Reset", 
            command=self.reset_form
        ).pack(side='left', padx=5)
        
        result_frame = ttk.LabelFrame(self.tab_diagnosis, text="Hasil Diagnosis")
        result_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        result_frame.grid_rowconfigure(1, weight=1)
        result_frame.grid_rowconfigure(3, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(result_frame, text="Log Proses:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.log_text = scrolledtext.ScrolledText(result_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        ttk.Label(result_frame, text="Kesimpulan:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.result_text = scrolledtext.ScrolledText(result_frame, height=6, wrap=tk.WORD)
        self.result_text.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
    
    def create_riwayat_tab(self):
        self.tab_riwayat.grid_rowconfigure(1, weight=1)
        self.tab_riwayat.grid_columnconfigure(0, weight=1)

        ttk.Label(
            self.tab_riwayat, 
            text="Riwayat Diagnosis", 
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, pady=10)
        
        riwayat_frame = ttk.Frame(self.tab_riwayat)
        riwayat_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        riwayat_frame.grid_rowconfigure(0, weight=1)
        riwayat_frame.grid_columnconfigure(0, weight=1)
        
        columns = ('tanggal', 'diagnosis', 'tingkat_keyakinan')
        self.tree = ttk.Treeview(riwayat_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('tanggal', text='Tanggal')
        self.tree.heading('diagnosis', text='Diagnosis')
        self.tree.heading('tingkat_keyakinan', text='Tingkat Keyakinan')
        
        self.tree.column('tanggal', width=150)
        self.tree.column('diagnosis', width=400)
        self.tree.column('tingkat_keyakinan', width=150)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        ttk.Button(
            self.tab_riwayat, 
            text="Hapus Riwayat", 
            command=self.hapus_riwayat
        ).grid(row=2, column=0, pady=10)
        
        self.update_riwayat_tree()
    
    def create_info_tab(self):
        self.tab_info.grid_rowconfigure(1, weight=1)
        self.tab_info.grid_columnconfigure(0, weight=1)

        ttk.Label(
            self.tab_info, 
            text="Informasi Penyakit Flu", 
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, pady=10)
        
        info_frame = ttk.Frame(self.tab_info)
        info_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        info_frame.grid_rowconfigure(0, weight=1)
        info_frame.grid_columnconfigure(0, weight=1)
        
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, width=80, height=20)
        info_text.grid(row=0, column=0, sticky="nsew")
        
        info_content = """
FLU (INFLUENZA)

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
- Memiliki kondisi medis kronis
"""
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
    
    def create_tooltip(self, widget, text):
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip, 
                text=text, 
                background="lightyellow", 
                relief="solid", 
                borderwidth=1,
                font=("Arial", 9)
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def run_diagnosis(self):
        for gejala in self.gejala_list:
            self.facts[gejala["id"]] = self.gejala_vars[gejala["id"]].get()
        
        for rule in self.rules:
            conclusion = rule["conclusion"]
            if conclusion in self.facts:
                self.facts[conclusion] = False
        
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        
        self.log_text.insert(tk.END, "Fakta Awal:\n")
        for fact, value in self.facts.items():
            if value:
                gejala = next((g for g in self.gejala_list if g["id"] == fact), None)
                if gejala:
                    self.log_text.insert(tk.END, f"- {gejala['nama']}: {value}\n")
        
        new_facts = True
        conclusions = {}
        
        while new_facts:
            new_facts = False
            for rule in self.rules:
                conclusion = rule["conclusion"]
                if conclusion not in self.facts or not self.facts[conclusion]:
                    conditions_met = all(self.facts.get(cond, False) for cond in rule["conditions"])
                    if conditions_met:
                        self.facts[conclusion] = True
                        new_facts = True
                        conclusions[conclusion] = rule.get("bobot", 1.0)
                        self.log_text.insert(tk.END, 
                            f"\nAturan diterapkan: JIKA {', '.join(rule['conditions'])} MAKA {conclusion} "
                            f"(Bobot: {rule.get('bobot', 1.0)})\n")
        
        diagnosis_results = []
        recommendations = []
        
        for conclusion, confidence in conclusions.items():
            if conclusion.startswith("kemungkinan_"):
                diagnosis_name = conclusion.replace("kemungkinan_", "").replace("_", " ").title()
                diagnosis_results.append((diagnosis_name, confidence))
        
        for key in self.solusi:
            if self.facts.get(key, False):
                recommendations.append(self.solusi[key])
        
        if diagnosis_results:
            self.result_text.insert(tk.END, "Hasil Diagnosis:\n")
            for diagnosis, confidence in diagnosis_results:
                self.result_text.insert(tk.END, f"- {diagnosis} (Keyakinan: {confidence*100:.1f}%)\n")
        else:
            self.result_text.insert(tk.END, "Tidak ada diagnosis yang dapat disimpulkan dari gejala yang dipilih.\n")
        
        if recommendations:
            self.result_text.insert(tk.END, "\nRekomendasi:\n")
            for rec in recommendations:
                self.result_text.insert(tk.END, f"- {rec}\n")
        else:
            self.result_text.insert(tk.END, "\nTidak ada rekomendasi khusus.\n")
        
        diagnosis_str = ", ".join([f"{d} ({c*100:.1f}%)" for d, c in diagnosis_results]) if diagnosis_results else "Tidak ada diagnosis"
        self.simpan_riwayat(diagnosis_str, max([c for _, c in diagnosis_results], default=0))
        
        self.update_riwayat_tree()
        
        messagebox_info = diagnosis_str if diagnosis_results else "Tidak ada diagnosis yang dapat disimpulkan"
        if recommendations:
            messagebox_info += "\n\nRekomendasi:\n" + "\n".join([f"- {rec}" for rec in recommendations])
        
        messagebox.showinfo("Hasil Diagnosis", messagebox_info)
    
    def reset_form(self):
        for var in self.gejala_vars.values():
            var.set(False)
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
    
    def simpan_riwayat(self, diagnosis, confidence):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gejala_terpilih = [g["nama"] for g in self.gejala_list if self.gejala_vars[g["id"]].get()]
        
        riwayat_entry = {
            "tanggal": now,
            "gejala": gejala_terpilih,
            "diagnosis": diagnosis,
            "tingkat_keyakinan": confidence,
            "rekomendasi": [self.solusi[key] for key in self.solusi if self.facts.get(key, False)]
        }
        
        self.riwayat.append(riwayat_entry)
        self.save_riwayat()
    
    def update_riwayat_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for entry in self.riwayat:
            self.tree.insert('', 'end', values=(
                entry["tanggal"],
                entry["diagnosis"],
                f"{entry['tingkat_keyakinan']*100:.1f}%"
            ))
    
    def hapus_riwayat(self):
        if messagebox.askyesno("Konfirmasi", "Hapus semua riwayat diagnosis?"):
            self.riwayat = []
            self.save_riwayat()
            self.update_riwayat_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiagnosisApp(root)
    root.mainloop()