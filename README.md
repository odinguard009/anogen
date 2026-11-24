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
- `roles/`: instruksi peran (editor pengembangan, penulis, editor naskah, penjaga kanon, manajer redaksi).

## Catatan jujur
- Pemakaian kuota per bab belum diukur. Ukur setelah bab pertama (claude.ai/settings/usage) lalu catat.
- Belum diverifikasi: apakah tugas terjadwal bisa push ke GitHub dan berapa kuota yang dipakainya.
