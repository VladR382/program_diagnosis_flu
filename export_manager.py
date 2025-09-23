from tkinter import filedialog, messagebox
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ExportManager:
    def export_to_csv(self, filtered_data):
        """Export riwayat diagnosis ke file CSV."""
        if not filtered_data:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diekspor!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Simpan Riwayat sebagai CSV"
        )
        if not filename: return

        try:
            export_data = [{
                'Tanggal': entry['tanggal'],
                'Diagnosis': entry['diagnosis'],
                'Tingkat_Keyakinan': f"{entry['tingkat_keyakinan']*100:.1f}%",
                'Gejala': '; '.join(entry['gejala']),
                'Rekomendasi': '; '.join(entry['rekomendasi']) if entry['rekomendasi'] else 'Tidak ada'
            } for entry in filtered_data]
            
            df = pd.DataFrame(export_data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            messagebox.showinfo("Sukses", f"Data berhasil diekspor ke:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor data:\n{str(e)}")

    def export_to_pdf(self, filtered_data):
        """Export riwayat diagnosis ke file PDF."""
        if not filtered_data:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diekspor!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Simpan Riwayat sebagai PDF"
        )
        if not filename: return

        try:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            cell_style = ParagraphStyle(name='CellStyle', parent=styles['Normal'], alignment=0, leading=12)
            header_style = ParagraphStyle(name='HeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', textColor=colors.whitesmoke, alignment=0, leading=12)
            story = []
            
            story.append(Paragraph("Riwayat Diagnosis Flu", styles['Title']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"Diekspor pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            table_headers = [Paragraph(h, header_style) for h in ['Tanggal', 'Diagnosis', 'Keyakinan', 'Gejala Utama']]
            table_data = [table_headers]
            
            for entry in filtered_data:
                gejala_summary = ', '.join(entry['gejala'][:3])
                if len(entry['gejala']) > 3:
                    gejala_summary += f" (+{len(entry['gejala'])-3} lainnya)"
                
                row_data = [
                    Paragraph(entry['tanggal'][:16], cell_style),
                    Paragraph(entry['diagnosis'], cell_style),
                    Paragraph(f"{entry['tingkat_keyakinan']*100:.1f}%", cell_style),
                    Paragraph(gejala_summary, cell_style)
                ]
                table_data.append(row_data)
            
            table = Table(table_data, colWidths=[90, 170, 60, 180])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(table)
            doc.build(story)
            messagebox.showinfo("Sukses", f"Data berhasil diekspor ke:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekspor PDF:\n{str(e)}")