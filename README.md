# StatVista — UTS Statistika 1B

Aplikasi interaktif statistika deskriptif berbasis Python dan Streamlit.

## Cara menjalankan
1. Instal Python 3.10 atau versi lebih baru.
2. Buka terminal di folder proyek ini.
3. Jalankan `pip install -r requirements.txt`.
4. Jalankan `streamlit run app.py`.
5. Browser akan membuka aplikasi (biasanya http://localhost:8501).

## Fitur
- Unggah Excel (.xlsx, .xls) dan CSV; tampilkan dataset.
- Pilih satu atau beberapa variabel numerik.
- Pilih N, min, maks, mean, median, modus, varians, standar deviasi, Q1, Q2, Q3.
- Histogram, boxplot, diagram batang, diagram lingkaran.
- Distribusi frekuensi nilai unik atau interval, frekuensi kumulatif, persentase.
- Deteksi data kosong, interpretasi ringkas, unduh CSV/Excel.

## Catatan statistik
- Data kosong dikeluarkan per variabel, sehingga N adalah jumlah observasi valid.
- Varians dan standar deviasi adalah statistik sampel (ddof=1).
- Kuartil dihitung menggunakan interpolasi linear Pandas.
- Modus bisa lebih dari satu; maksimal lima nilai ditampilkan.
- Nilai statistik yang tidak terdefinisi ditampilkan sebagai tanda pisah.

## Pengumpulan
Sertakan folder kode, file dataset Excel, dan screenshot aplikasi setelah dijalankan.
Gunakan data contoh yang disediakan untuk menguji aplikasi, atau unggah data Anda sendiri.
