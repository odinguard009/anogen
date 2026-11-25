# Anogen (AI Novel Generator pribadi)

Panduan untuk Odin. Kamu tidak perlu menyentuh kode. Semua perintah diberikan lewat chat dengan Claude; Claude yang menjalankan, menyimpan ke GitHub, dan mengirim EPUB.

## Perintah yang bisa kamu ucapkan
- **mulai cerita baru** (boleh tambah ide, atau "bebas")
- **tulis bab berikutnya**
- **kerjakan 10 bab** (atau 20/30/...): menulis tanpa henti, berhenti rapi jika kuota habis, lanjut dengan "lanjutkan"
- **generate 1 arc maksimal 50 bab** (atau 60/70/...): arc direncanakan selesai dalam batas itu; EPUB baru dibuat setelah arc tamat
- **ide: ...** / **belokkan arah: ...**: masuk ke inbox, dikembangkan otomatis sesuai gayamu
- **laporan**: status singkat
- **hidupkan jadwal** / **matikan jadwal**: saklar penjadwalan (default MATI)

## Isi folder
- `story/`: bahan cerita (brief, gaya, bible, outline, inbox). Gaya ada di `story/style/profile.md` dan bisa diganti kapan saja.
- `chapters/`: bab-bab hasil tulisan.
- `out/`: file EPUB (untuk ReadEra).
- `ops/`: log, skor kualitas, pengaturan jadwal.
- `tools/`: skrip pembantu (tidak memakai kuota).
- `docs/`: laporan audit, peta jalan, baseline performa, arsitektur, catatan perubahan.
- `tests/fixtures/`: data beku untuk membandingkan paket konteks.
- `roles/`: instruksi peran (editor pengembangan, penulis, editor naskah, penjaga kanon, manajer redaksi).

## Catatan jujur
- Pemakaian token dan biaya **belum terukur**. Ada alat pencatat (`python3 tools/usage_log.py add ...` dan `report`), tetapi angka asli dari penyedia hanya ada kalau host AI melaporkannya dan seseorang mencatatnya. Laporan memisahkan data "reported" (dari penyedia), "manual" (dibaca dari halaman pemakaian) dan "estimate" (perkiraan); ketiganya tidak pernah dijumlahkan. Harga hanya dari `ops/prices.json` buatan Anda, tidak ada harga bawaan.
- Penghematan konteks (`ctx_compare.py`) adalah hitungan karakter pada fixture beku; token hanyalah perkiraan (karakter / 4), bukan pengukuran penyedia.
- Belum diverifikasi: apakah tugas terjadwal bisa push ke GitHub dan berapa kuota yang dipakainya. Jadwal tetap MATI sampai Anda bilang "hidupkan jadwal".
- Critic berjalan setiap 10 bab. Bab yang diedit setelah direview (misalnya lewat rewrite) memblokir penulisan baru sampai critic memeriksa ulang bab itu (`engine_state.py rereview N`).
- Tes: `python3 tools/test_tools.py` (juga dijalankan GitHub Actions pada setiap PR).
