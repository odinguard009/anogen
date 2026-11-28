# Rencana Perbaikan Bahasa & Gaya — Bab 1–50

Tanggal: 28 Nov 2026
Status: **RENCANA SAJA — belum ada bab yang diubah. Menunggu perintah dari pemilik.**

## 1. Masukan pemilik

1. Bahasa Inggris sudah lebih mudah dibaca, tetapi banyak maksud kalimat yang masih tidak dipahami, dan banyak ungkapan/idiom yang tidak dipahami.
2. Banyak kata yang sulit diterjemahkan atau tidak lazim dipakai sehari-hari. Contoh: **“Lance Nine”** dibaca seperti “tombak nomor sembilan”, padahal itu nama grup/unit.
3. Contoh gaya yang diinginkan: `https://novelphoenix.com/novel/holy-emperors-grandson-is-a-necromancer/chapters` (riset sudah dilakukan; lihat bagian 2).
4. Rencana ini **jangan dikerjakan** sebelum ada perintah.

## 2. Hasil riset gaya rujukan

Saya membaca Chapter 1, 2, dan 6 dari novel rujukan itu. Ciri yang menonjol:

- Kalimat pendek dan langsung, satu ide per kalimat. Contoh: *“I gripped the shovel real tight and slammed it hard against the ground.”*
- Kata kerja dan benda konkret: *shovel, wagon, corpses, fog, monastery, potato, firewood*. Jarang kata abstrak.
- Narator memberi penjelasan datar tentang istilah begitu istilah muncul: *“I was working as a Gravekeeper.” / “the class I picked … became my current ‘Profession’.”* Tidak ada istilah yang dibiarkan mengambang.
- Perbandingan hanya yang kongret dan langsung dimengerti: *“heavy like a soaked sponge.”* Tidak ada rangkaian metafora bertingkat.
- Humor dan komentar diri pendek, lalu cerita lanjut. Dialogue pendek, satu maksud per giliran bicara.
- Daftar istilah/kemampuan ditulis datar: *[Resurrection of the Dead], [Dead Spirit Soldier], [Mind’s Eye]*.
- Adanya idiom juga, tetapi idiom yang dipakai bersifat sehari-hari dan langsung jelas konteksnya (*no picnic, flipped his lid*). Pelajaran yang diambil: bukan “tanpa idiom sama sekali”, melainkan **idiom hanya bila maknanya langsung terlihat dari kalimat**.

## 3. Diagnosis bab 1–50 (data dari repo)

- 50 bab, 105.107 kata, 9.345 kalimat, rata-rata **11,2 kata/kalimat**.
- **1.074 kalimat lebih dari 20 kata** (~11,5% dari semua kalimat). Ini sumber utama kalimat yang “gagal dipahami”.
- `like a` = 61 kali, `as if` = 78 kali, `the way` = 56 kali, `came back` = 63 kali, `went quiet` = 25 kali, `went still` = 11 kali. Sebagian besar adalah perbandingan/ungkapan kabur.
- Kata panjang/berat yang sering muncul: *groundskeeper* (18), *handkerchief* (16), *headmistress* (14), *scholarship* (5), *technically* (5), *quartermaster* (3), *lamplighter* (2), *explanation* (3), *disturbance* (3).
- Istilah grup like **Lance Nine / Lance One** muncul 9 kali tanpa penjelasan di tempat pertama yang cukup keras untuk dibaca pembaca sebagai “unit lima orang, bukan senjata”.

Catatan: aturan lama yang sudah dikunci tidak boleh dilanggar tanpa izin: POV close-third, Eden flat, CEFR A1–A2, 2000–3000 kata per bab, tanpa padding, label `**[Name]**`, dan milestone (rahasia ibu ~ch 400, pengakuan ~ch 500). Rencana ini hanya menyentuh **lapisan bahasa**, bukan alur/canon/POV.

## 4. Aturan baru yang diusulkan (untuk disetujui dulu)

1. **Satu kalimat = satu ide.** Rata-rata 8–10 kata; batas keras 16 kata; tidak ada kalimat >18 kata. Satu koma per kalimat maksimal. Tidak ada klausa bertingkat.
2. **Daftar kata sehari-hari.** Pakai kata yang paling umum. Kata berat diganti atau dijelaskan saat first use:
   - *groundskeeper* → “the man who looks after the grounds” (lalu boleh disingkat “the grounds man”)
   - *handkerchief* → “a small cloth”
   - *headmistress* → “the woman who runs the school” (nama tetap Dame Hildegard)
   - *scholarship* → “a paid place at school”
   - *quartermaster* → “the man who keeps the stores”
   - *lamplighter* → “the lamp man”
   - *Lance Nine* → “Lance Nine, five students, not a weapon” pada kemunculan pertama; sesudah itu “the five”.
3. **Tanpa perbandingan abstrak.** `like a` dan `as if` hanya boleh untuk benda yang benar-benar terlihat. Target: `like a` ≤ 1 per bab, `as if` = 0. Ungkapan kabur seperti *went quiet / went still / came back / the way* diganti dengan kalimat konkret: “the birds stopped calling”, “his hands did not move”.
4. **Istilah harus langsung dijelaskan.** Setiap nama kelompok, job, gelar, dan benda aneh mendapat satu kalimat penjelasan datar pada pemakaian pertama — paling lambat kalimat berikutnya.
5. **Dialogue pendek dan literal.** Satu ide per giliran bicara, tidak ada teka-teki, tidak ada “jawaban yang benar tapi tidak memberi tahu apa-apa” kecuali memang disengaja untuk efek dan diberi penanda jelas.
6. **Tidak ada padding.** Jumlah kata tetap 2000–3000; penggantian kalimat harus memakai beats nyata, bukan menambah deskripsi kosong.
7. **Guard permanen** (setelah disetujui): tambahkan ke `check_chapter.py` / `quality-contract.md` / `writing-rules.md`:
   - error bila mean > 10,5; warning bila ada kalimat > 16 kata; error bila > 20 kata;
   - batas `like a` dan `as if`;
   - daftar kata terlarang/peringatan;
   - pemeriksaan first-use gloss untuk istilah baru. Guard lama tetap dipertahankan.

## 5. Tahap kerja (urutan, bukan eksekusi)

- **Tahap 0 — Persetujuan.** Pemilik menyetujui/menyesuaikan aturan di bagian 4. Belum ada file bab yang disentuh.
- **Tahap 1 — Kunci aturan.** Ubah hanya file aturan: `profile.md`, `banned.md`, `quality-contract.md`, `writing-rules.md`, `tools/check_chapter.py`, ditambah glossary kecil `story/bible/plain-words.md`. Tidak ada bab diubah.
- **Tahap 2 — Pilot.** Tulis ulang 2 bab sebagai contoh: **ch 1** (quiet) dan **ch 6** (group introduction + mystery). Jalankan checker, lalu minta pemilik membaca kedua hasil sebelum lanjut.
- **Tahap 3 — Produksi 1–50.** Setelah pilot disetujui, kerjakan bertahap 3–5 bab per batch, critic tiap 10 bab, cek 6-gram antar bab dan milestone tiap batch.
- **Tahap 4 — Penutup.** Audit arc, `validate 1-50`, `milestone_check`, rebuild EPUB, kirim file baru.

## 6. Kriteria selesai

- Rata-rata panjang kalimat 8–10 kata; kalimat >20 kata = 0.
- `like a` ≤ 1/bab, `as if` = 0, tidak ada ungkapan kabur yang tercantum di bagian 3.
- Istilah grup/job/gelar semua punya penjelapan datar saat first use.
- 50/50 bab tetap lolos `check_chapter.py --strict`, `validate`, dan `milestone_check`.
- Pemilik menyatakan kalimat dan maksudnya bisa dipahami tanpa harus menekan “terjemahkan”.

## 7. Status

Rencana ini **belum dijalankan**. Menunggu perintah eksplisit dari pemilik.
