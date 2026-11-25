# Anogen (AI Novel Generator pribadi)

Panduan untuk Odin. Kamu tidak perlu menyentuh kode. Semua perintah diberikan lewat chat dengan Claude; Claude yang menjalankan, menyimpan ke GitHub, dan mengirim EPUB.

## Perintah yang bisa kamu ucapkan
- **mulai cerita baru: judul X** (boleh tambah ide, atau "bebas"): membuat folder novel sendiri di `novels/<slug>/` dengan kerangka netral
- **daftar novel** / **pilih novel X**: lihat semua novel / ganti novel aktif (perintah lain berlaku untuk novel aktif)
- **tulis bab berikutnya**
- **kerjakan 10 bab** (atau 20/30/...): menulis tanpa henti, berhenti rapi jika kuota habis, lanjut dengan "lanjutkan"
- **generate 1 arc maksimal 50 bab** (atau 60/70/...): arc direncanakan selesai dalam batas itu; EPUB baru dibuat setelah arc tamat
- **ide: ...** / **belokkan arah: ...**: masuk ke inbox, dikembangkan otomatis sesuai gayamu
- **laporan**: status singkat
- **hidupkan jadwal** / **matikan jadwal**: saklar penjadwalan (default MATI)

## Isi folder
Setiap novel punya folder sendiri dan tidak berbagi kanon, nama, gaya, atau status dengan novel lain:
- `novels/<slug>/story/`: bahan cerita (brief, gaya, bible, outline, inbox). Gaya ada di `story/style/profile.md` per novel.
- `novels/<slug>/chapters/`: bab-bab. Judul bab selalu `# Chapter N: Judul`.
- `novels/<slug>/ops/`: status mesin, log, skor, jadwal milik novel itu. `novels/<slug>/out/`: EPUB dan halaman baca.
- `novels/ACTIVE`: novel yang sedang aktif.
- `engine/`: aturan, prompt, dan pengaturan model yang dipakai semua novel. `templates/novel/`: kerangka novel baru.
- Aturan "satu agen pada satu waktu" berlaku global untuk semua novel.
- `tools/`: skrip pembantu (termasuk `novel.py` untuk membuat/memilih novel dan `rename.py` untuk mengganti nama di seluruh novel, dry-run dulu) (tidak memakai kuota).
- `docs/`: laporan audit, peta jalan, baseline performa, arsitektur, catatan perubahan.
- `tests/fixtures/`: data beku untuk membandingkan paket konteks.
- `roles/`: instruksi peran (editor pengembangan, penulis, editor naskah, penjaga kanon, manajer redaksi).

## Catatan jujur
- Pemakaian token dan biaya **belum terukur**. Ada alat pencatat (`python3 tools/usage_log.py add ...` dan `report`), tetapi angka asli dari penyedia hanya ada kalau host AI melaporkannya dan seseorang mencatatnya. Laporan memisahkan data "reported" (dari penyedia), "manual" (dibaca dari halaman pemakaian) dan "estimate" (perkiraan); ketiganya tidak pernah dijumlahkan. Harga hanya dari `engine/prices.json` buatan Anda, tidak ada harga bawaan.
- Penghematan konteks (`ctx_compare.py`) adalah hitungan karakter pada fixture beku; token hanyalah perkiraan (karakter / 4), bukan pengukuran penyedia.
- Belum diverifikasi: apakah tugas terjadwal bisa push ke GitHub dan berapa kuota yang dipakainya. Jadwal tetap MATI sampai Anda bilang "hidupkan jadwal".
- Critic berjalan setiap 10 bab. Bab yang diedit setelah direview (misalnya lewat rewrite) memblokir penulisan baru sampai critic memeriksa ulang bab itu (`engine_state.py rereview N`).
- Tes: `python3 tools/test_tools.py` (juga dijalankan GitHub Actions pada setiap PR).

## Aturan cerita permanen (perintah Odin 2026-11-25)
- Tidak ada level yang menentukan rank karakter; ada Class/Job dari registri planet, label serangan khusus **[Nama]**, deskripsi saat pertama kali senjata/kemampuan dipakai, dan setiap reveal punya tangga petunjuk (`story/bible/reveal-ladder.md`).
- Tidak pernah memakai subagent; semua peran dikerjakan satu per satu oleh orkestrator.
