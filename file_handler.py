import json
import os
from tkinter import messagebox

def load_app_data(file_path):
    """Memuat data gejala, aturan, dan solusi dari file JSON utama."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"✓ Data aplikasi berhasil dimuat dari {file_path}")
        return data.get("gejala", []), data.get("aturan", []), data.get("solusi", {})
    except FileNotFoundError:
        messagebox.showerror("Error Kritis", f"File data '{file_path}' tidak ditemukan! Aplikasi akan ditutup.")
        return None, None, None
    except json.JSONDecodeError:
        messagebox.showerror("Error Kritis", f"Format file data '{file_path}' tidak valid! Aplikasi akan ditutup.")
        return None, None, None

def load_history(file_path):
    """Memuat riwayat diagnosis dari file JSON."""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                riwayat = json.load(file)
            print(f"✓ Riwayat dimuat: {len(riwayat)} entri")
            return riwayat
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠ Riwayat tidak dapat dimuat, akan dibuat file baru.")
    return []

def save_history(file_path, data):
    """Menyimpan riwayat diagnosis ke file JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("✓ Riwayat berhasil disimpan")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan riwayat: {str(e)}")
        return False