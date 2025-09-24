import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# Impor modul-modul yang sudah kita buat
import file_handler
from gui_builder import GuiBuilder
from export_manager import ExportManager

class DiagnosisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Pakar Diagnosis Flu")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        self.json_file = 'gejala_penyakit.json'
        self.riwayat_file = 'riwayat_diagnosis.json'
        
        self.gejala_list, self.rules, self.solusi = file_handler.load_app_data(self.json_file)
        if self.gejala_list is None:
            self.root.destroy()
            return
            
        self.riwayat = file_handler.load_history(self.riwayat_file)
        self.filtered_riwayat = self.riwayat.copy()
        
        self.facts = {gejala["id"]: False for gejala in self.gejala_list}
        self.gejala_vars = {}
        
        self.export_manager = ExportManager()
        self.gui_builder = GuiBuilder(self)
        
        self.gui_builder.create_main_tabs()

    def run_diagnosis(self):
        """
        Menjalankan proses diagnosis dengan output log dan hasil yang lengkap.
        """
        gejala_terpilih = [gid for gid, var in self.gejala_vars.items() if var.get()]
        if not gejala_terpilih:
            messagebox.showwarning("⚠️ Peringatan", "Pilih minimal satu gejala untuk melakukan diagnosis.")
            return

        self.facts = {gejala["id"]: False for gejala in self.gejala_list}
        for gid in gejala_terpilih:
            self.facts[gid] = True
        
        self.log_text.config(state=tk.NORMAL)
        self.result_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)

        new_facts_found, conclusions, iteration_count = True, {}, 0
        
        self.log_text.insert(tk.END, "🔍 MEMULAI PROSES DIAGNOSIS\n")
        self.log_text.insert(tk.END, "="*50 + "\n\n")
        self.log_text.insert(tk.END, "📝 FAKTA AWAL (Gejala yang dipilih):\n")
        for gid in gejala_terpilih:
            gejala_obj = next((g for g in self.gejala_list if g["id"] == gid), None)
            if gejala_obj:
                self.log_text.insert(tk.END, f"   ✓ {gejala_obj['nama']}\n")
        self.log_text.insert(tk.END, "\n" + "="*50 + "\n")
        self.log_text.insert(tk.END, "🔄 PROSES FORWARD CHAINING:\n\n")

        while new_facts_found:
            new_facts_found = False
            iteration_count += 1
            self.log_text.insert(tk.END, f"📍 Iterasi {iteration_count}:\n")
            
            for rule_idx, rule in enumerate(self.rules, 1):
                conclusion = rule["conclusion"]
                if not self.facts.get(conclusion, False):
                    if all(self.facts.get(cond, False) for cond in rule["conditions"]):
                        self.facts[conclusion] = True
                        new_facts_found = True
                        if conclusion.startswith("kemungkinan_"):
                            conclusions[conclusion] = rule.get("bobot", 1.0)
                        
                        conditions_text = ', '.join(rule['conditions'])
                        self.log_text.insert(tk.END, f"   ✅ Rule {rule_idx}: JIKA ({conditions_text}) MAKA {conclusion}\n")
                        self.log_text.insert(tk.END, f"      💡 Bobot keyakinan: {rule.get('bobot', 1.0)*100:.1f}%\n")
            
            if not new_facts_found:
                self.log_text.insert(tk.END, "   ❌ Tidak ada rule baru yang dapat diterapkan\n")
            
            self.log_text.insert(tk.END, "\n")
            if iteration_count > 50:
                self.log_text.insert(tk.END, "⚠️ Batas iterasi tercapai, proses dihentikan.\n")
                break

        self.log_text.insert(tk.END, "="*50 + "\n")
        self.log_text.insert(tk.END, "🏁 PROSES FORWARD CHAINING SELESAI\n")
        self.log_text.insert(tk.END, f"📊 Total iterasi: {iteration_count}\n")
        self.log_text.insert(tk.END, f"📋 Kesimpulan ditemukan: {len(conclusions)}\n")
        
        diagnosis_results = sorted(
            [(c.replace("kemungkinan_", "").replace("_", " ").title(), conf) for c, conf in conclusions.items()],
            key=lambda x: x[1], reverse=True
        )
        
        recommendations = [self.solusi[key] for key in self.solusi if self.facts.get(key, False)]
        
        self.result_text.insert(tk.END, "🩺 HASIL DIAGNOSIS\n" + "="*40 + "\n\n")
        
        if diagnosis_results:
            self.result_text.insert(tk.END, "📊 Diagnosis yang Terdeteksi:\n")
            for i, (diagnosis, confidence) in enumerate(diagnosis_results, 1):
                confidence_pct = confidence * 100
                emoji = "🔴" if confidence_pct >= 80 else "🟡" if confidence_pct >= 60 else "🟢"
                interpretasi = "Sangat mungkin" if confidence_pct >= 80 else "Kemungkinan besar" if confidence_pct >= 60 else "Mungkin" if confidence_pct >= 40 else "Kemungkinan kecil"
                self.result_text.insert(tk.END, f"{i}. {emoji} {diagnosis}\n")
                self.result_text.insert(tk.END, f"   Tingkat Keyakinan: {confidence_pct:.1f}%\n")
                self.result_text.insert(tk.END, f"   Interpretasi: {interpretasi}\n\n")
        else:
            self.result_text.insert(tk.END, "❌ Tidak ada diagnosis spesifik yang dapat disimpulkan.\n")
            self.result_text.insert(tk.END, "💡 Gejala tidak cukup spesifik atau tidak cocok dengan pola penyakit.\n\n")

        if recommendations:
            self.result_text.insert(tk.END, "💡 REKOMENDASI PENGOBATAN:\n" + "-" * 30 + "\n")
            for i, rec in enumerate(recommendations, 1): self.result_text.insert(tk.END, f"{i}. {rec}\n")
            self.result_text.insert(tk.END, "\n")
        else:
            self.result_text.insert(tk.END, "💡 REKOMENDASI UMUM:\n" + "-" * 20 + "\n")
            self.result_text.insert(tk.END, "• Istirahat yang cukup\n• Banyak minum air putih\n• Konsultasi dokter jika gejala memburuk\n\n")

        self.result_text.insert(tk.END, "⚠️ DISCLAIMER:\n")
        self.result_text.insert(tk.END, "Hasil ini hanya referensi awal. Selalu konsultasikan dengan tenaga medis profesional.\n")
        
        self.log_text.config(state=tk.DISABLED)
        self.result_text.config(state=tk.DISABLED)
        
        diagnosis_str = ", ".join([f"{d} ({c*100:.1f}%)" for d, c in diagnosis_results]) or "Tidak ada diagnosis"
        max_confidence = max([c for _, c in diagnosis_results], default=0)
        self.simpan_riwayat(diagnosis_str, max_confidence)
        self.update_riwayat_tree()
        self.result_text.see(tk.INSERT)

    def reset_form(self):
        for var in self.gejala_vars.values(): var.set(False)
        self.log_text.config(state=tk.NORMAL)
        self.result_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "📝 Log proses inferensi akan ditampilkan di sini...\n")
        self.log_text.insert(tk.END, "🔍 Pilih gejala dan klik 'Mulai Diagnosis' untuk memulai.")
        self.result_text.insert(tk.END, "📊 Hasil diagnosis akan ditampilkan di sini...\n")
        self.result_text.insert(tk.END, "💡 Silakan pilih gejala yang Anda alami terlebih dahulu.")
        self.log_text.config(state=tk.DISABLED)
        self.result_text.config(state=tk.DISABLED)

    def simpan_riwayat(self, diagnosis, confidence):
        gejala_terpilih_nama = [g["nama"] for g in self.gejala_list if self.gejala_vars.get(g["id"]) and self.gejala_vars[g["id"]].get()]
        rekomendasi = [self.solusi[key] for key in self.solusi if self.facts.get(key, False)]
        riwayat_entry = {
            "tanggal": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gejala": gejala_terpilih_nama, "diagnosis": diagnosis,
            "tingkat_keyakinan": confidence, "rekomendasi": rekomendasi
        }
        self.riwayat.insert(0, riwayat_entry)
        self.filtered_riwayat = self.riwayat.copy()
        file_handler.save_history(self.riwayat_file, self.riwayat)

    def update_riwayat_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for entry in self.filtered_riwayat:
            self.tree.insert('', 'end', values=(
                entry["tanggal"], entry["diagnosis"], f"{entry['tingkat_keyakinan']*100:.1f}%"
            ))
        total = len(self.riwayat)
        filtered = len(self.filtered_riwayat)
        info = f"📊 Total: {total} entri" if total == filtered else f"📊 Menampilkan: {filtered} dari {total} entri"
        self.info_label.config(text=info)

    def filter_riwayat(self, *args):
        search_text = self.search_var.get().lower()
        month_filter = self.month_filter_var.get()
        month_map = {'Januari': '01', 'Februari': '02', 'Maret': '03', 'April': '04', 'Mei': '05', 'Juni': '06', 'Juli': '07', 'Agustus': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Desember': '12'}
        
        self.filtered_riwayat = [
            entry for entry in self.riwayat
            if (search_text in entry['diagnosis'].lower()) and
                (month_filter == 'Semua' or entry['tanggal'][5:7] == month_map.get(month_filter))
        ]
        self.update_riwayat_tree()

    def clear_filters(self):
        self.search_var.set('')
        self.month_filter_var.set('Semua')

    def hapus_riwayat(self):
        if not self.riwayat:
            messagebox.showinfo("Informasi", "Tidak ada riwayat untuk dihapus.")
            return
        if not messagebox.askyesno("Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus SEMUA riwayat?\n\nTindakan ini tidak dapat dibatalkan."):
            return
        self.riwayat, self.filtered_riwayat = [], []
        file_handler.save_history(self.riwayat_file, self.riwayat)
        self.update_riwayat_tree()
        messagebox.showinfo("Berhasil", "Semua riwayat diagnosis telah dihapus.")

    def show_riwayat_detail(self, event):
        selected_item_id = self.tree.focus()
        if not selected_item_id: return
        tanggal_pilihan = self.tree.item(selected_item_id)['values'][0]
        detail_data = next((r for r in self.riwayat if r['tanggal'] == tanggal_pilihan), None)
        
        if detail_data:
            win_detail = tk.Toplevel(self.root)
            win_detail.title(f"📋 Detail Diagnosis - {tanggal_pilihan}")
            win_detail.geometry("500x550")
            win_detail.transient(self.root)
            win_detail.grab_set()
            text_widget = scrolledtext.ScrolledText(win_detail, wrap=tk.WORD, font=("Arial", 10))
            text_widget.pack(padx=15, pady=15, fill="both", expand=True)

            konten = f"📅 Tanggal: {detail_data['tanggal']}\n\n"
            konten += f"🩺 Diagnosis: {detail_data['diagnosis']}\n"
            konten += f"📊 Tingkat Keyakinan: {detail_data['tingkat_keyakinan']*100:.1f}%\n\n"
            konten += "📝 Gejala yang Dipilih:\n" + "\n".join(f"   • {g}" for g in detail_data['gejala'])
            konten += "\n\n💡 Rekomendasi:\n" + ("\n".join(f"   • {r}" for r in detail_data['rekomendasi']) if detail_data['rekomendasi'] else "   - Tidak ada rekomendasi khusus.")
            
            text_widget.insert(tk.END, konten)
            text_widget.config(state=tk.DISABLED)
            ttk.Button(win_detail, text="Tutup", command=win_detail.destroy).pack(pady=10)

if __name__ == "__main__":
    print("🏥 Memulai Sistem Pakar Diagnosis Flu")
    root = tk.Tk()
    app = DiagnosisApp(root)
    root.mainloop()

    print("👋 Aplikasi ditutup. Terima kasih!")
