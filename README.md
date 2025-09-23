# Sistem Pakar Diagnosis Flu 

Sebuah aplikasi desktop modular yang dibangun dengan Python dan Tkinter untuk mendiagnosis kemungkinan penyakit flu. Proyek ini menerapkan arsitektur *Object-Oriented Programming* (OOP) dan menggunakan sistem pakar berbasis aturan (*rule-based*) dengan metode penalaran *forward chaining* untuk memberikan diagnosis yang informatif.

## Deskripsi

Versi kedua dari aplikasi ini telah dirancang ulang sepenuhnya dengan memisahkan logika utama ke dalam modul-modul spesifik: antarmuka (GUI), manajemen file, logika diagnosis, dan fungsionalitas ekspor. Pengguna dapat memilih gejala yang mereka alami, dan sistem akan menjalankan proses inferensi untuk menghasilkan diagnosis, tingkat keyakinan, serta rekomendasi penanganan yang detail.

Selain itu, aplikasi kini dilengkapi dengan fitur-fitur canggih seperti filter dan pencarian riwayat, serta kemampuan untuk mengekspor data diagnosis ke format CSV dan PDF.

## Fitur Utama

  - **Arsitektur Modular (OOP)**: Kode lebih bersih, terorganisir, dan mudah dikembangkan berkat pemisahan logika ke dalam kelas dan file yang berbeda.
  - **Antarmuka yang Disempurnakan**: Tampilan lebih modern dengan ikon, *tooltip* deskriptif, dan *layout* yang responsif.
  - **Manajemen Riwayat Canggih**:
      - **Pencarian**: Cari riwayat diagnosis secara dinamis berdasarkan teks.
      - **Filter**: Saring riwayat berdasarkan bulan kejadian.
  - **Ekspor Data**: Ekspor daftar riwayat diagnosis ke dalam format **CSV** untuk dianalisis di spreadsheet atau **PDF** untuk laporan formal.
  - **Log Inferensi Detail**: Pengguna dapat melihat proses penalaran *forward chaining* langkah demi langkah, dari fakta awal hingga kesimpulan akhir.
  - **Hasil Diagnosis Informatif**: Kesimpulan kini disajikan dengan interpretasi (misalnya, "Sangat Mungkin") dan emoji visual berdasarkan tingkat keyakinan.
  - **Basis Pengetahuan Eksternal**: Gejala dan aturan tetap disimpan dalam file `gejala_penyakit.json` yang mudah dimodifikasi.

## Cara Menjalankan

1.  **Clone atau Unduh Proyek**:
    Pastikan semua file berada dalam satu direktori.

2.  **Instal Dependensi**:
    Proyek ini memerlukan beberapa pustaka eksternal. Buka terminal atau Command Prompt dan jalankan perintah berikut:

    ```bash
    pip install pandas reportlab
    ```

3.  **Jalankan Aplikasi**:
    Eksekusi skrip `main.py` untuk memulai aplikasi.

    ```bash
    python main.py
    ```

## Struktur Proyek

Proyek ini dibagi menjadi beberapa file Python untuk memisahkan tanggung jawab:

  - **`main.py`**:
    Titik masuk utama aplikasi. File ini menginisialisasi kelas-kelas utama, menghubungkan semua modul, dan menjalankan *main loop* Tkinter.

  - **`gui_builder.py`**:
    Bertanggung jawab untuk membangun dan menata semua komponen antarmuka grafis (GUI), seperti jendela utama, tab, tombol, dan area teks.

  - **`file_handler.py`**:
    Mengelola semua operasi yang berkaitan dengan file, seperti memuat basis pengetahuan dari `gejala_penyakit.json` serta memuat dan menyimpan `riwayat_diagnosis.json`.

  - **`export_manager.py`**:
    Berisi logika untuk mengekspor data riwayat ke format file eksternal seperti CSV dan PDF, menggunakan pustaka `pandas` dan `reportlab`.

  - **`gejala_penyakit.json`**:
    Berfungsi sebagai basis pengetahuan (*knowledge base*) yang berisi daftar gejala, aturan inferensi, dan solusi.

## Analisis dan Tabel Basis Pengetahuan

Berikut adalah rincian lengkap dari seluruh gejala dan kesimpulan yang digunakan oleh sistem pakar ini.

### Tabel Gejala Lengkap

| ID | Nama | Deskripsi |
| :--- | :--- | :--- |
| demam | Demam | Suhu tubuh di atas 38°C |
| batuk | Batuk | Batuk kering atau berdahak |
| pilek | Pilek | Hidung berair atau tersumbat |
| sakit\_tenggorokan | Sakit Tenggorokan | Nyeri saat menelan |
| nyeri\_otot | Nyeri Otot | Nyeri pada otot seluruh tubuh |
| sakit\_kepala | Sakit Kepala | Nyeri di area kepala |
| lemas | Lemas | Merasa lelah berlebihan |
| bersin | Bersin | Bersin-bersin berulang |
| menggigil | Menggigil | Sensasi dingin yang tidak terkontrol |
| mata\_berair | Mata Berair | Mata terasa gatal dan berair berlebih |
| kehilangan\_nafsu\_makan| Kehilangan Nafsu Makan| Berkurangnya keinginan untuk makan |
| sakit\_perut | Sakit Perut | Nyeri atau kram di area perut |

### Tabel Konklusi (Kesimpulan)

| ID Konklusi | Bobot | Deskripsi |
| :--- | :--- | :--- |
| kemungkinan\_infeksi\_pernapasan| 0.8 / 0.6 | Infeksi pada saluran pernapasan, bisa mengarah ke flu. |
| kemungkinan\_flu | 0.9 | Kondisi umum flu, gejala sedang. |
| kemungkinan\_flu\_ringan | 0.7 / 0.8 | Kondisi flu yang tidak terlalu parah. |
| kemungkinan\_flu\_berat | 0.85 / 0.95 | Kondisi flu yang membutuhkan perhatian lebih. |
| saran\_istirahat | 1.0 | Rekomendasi untuk istirahat cukup. |
| saran\_minum\_air | 1.0 | Rekomendasi untuk menjaga hidrasi. |
| saran\_konsultasi\_dokter | 1.0 | Rekomendasi untuk segera ke dokter. |
| saran\_obat\_warung | 0.8 | Rekomendasi penggunaan obat bebas. |

**Catatan**: Bobot di tabel kesimpulan dapat bervariasi karena tergantung pada aturan spesifik yang memicunya.
