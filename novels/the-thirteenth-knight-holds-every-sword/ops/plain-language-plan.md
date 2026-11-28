# Rencana Perbaikan Bahasa, Gaya, dan Konsistensi — Bab 1–50

Tanggal: 28 Nov 2026
Status: **RENCANA + SETTING. Tidak ada bab yang diubah.**

## 1. Masukan pemilik

1. Bahasa Inggris sudah lebih mudah dibaca, tetapi banyak maksud kalimat yang masih tidak dipahami, dan banyak ungkapan/idiom yang tidak dipahami.
2. Banyak kata yang sulit diterjemahkan atau tidak lazim dipakai sehari-hari. Contoh: **“Lance Nine”** dibaca seperti “tombak nomor sembilan”, padahal itu nama grup/unit.
3. Riset harus memakai sekitar **50 chapter** rujukan, bukan kurang dari 10.
4. Audience minimal **15 tahun**, kebanyakan **bukan penutur asli** bahasa Inggris, termasuk pembaca dari negara dengan sumber daya bahasa Inggris terbatas. Jangan pakai kata, sebutan, atau idiom yang rumit.
5. Ada inkosistensi di bab 1–50 yang harus dicek dan dibuatkan setting agar konsisten.
6. Rencana diperbaiki sesuai arahan ini. Bab belum boleh dikerjakan sebelum perintah.

## 2. Riset 50 chapter rujukan

Sumber: `https://novelphoenix.com/novel/holy-emperors-grandson-is-a-necromancer/chapter-1` sampai `chapter-50`.
Saya mengambil teks 50 chapter (0 gagal), lalu mengukur gaya dan membaca contoh Chapter 1, 2, dan 6.

### Data 50 chapter rujukan

| Hal | Rujukan (50 ch) | Novel kita (50 ch) |
|---|---|---|
| Kata | 37.663 | 105.113 |
| Kalimat | 2.765 | 9.345 |
| Rata-rata kata/kalimat | **13,6** | **11,2** |
| Kalimat >15 kata | 987 (35,7%) | 1.074 (11,5%) |
| Kalimat >20 kata | 514 (18,6%) | ~0 setelah checker kita |
| Kata ≥9 huruf | 2.480 (6,6%) | 1.285 (1,2%) |
| `like a` | 22 | 61 |
| `as if` | 23 | 78 |
| Kata percakapan (*well, right, yup, stuff…*) | 265 | 119 |
| Tanda tanya / seruan | 498 / 307 | 413 / 18 |

### Temuan penting (koreksi terhadap rencana lama)

Rencana lama mengusulkan “rata-rata 8–10 kata dan maksimal 16 kata”. **Itu ternyata bukan sumber kesederhanaan rujukan.** Rujukan justru punya kalimat lebih panjang dari novel kita. Yang membuatnya terasa mudah dibaca adalah:

1. **Kata benda konkret dan diulang**: *shovel, wagon, corpses, village, water, body, head, eyes, farmers, monastery, zombie*. Pembaca tidak perlu menerjemahkan hal abstrak.
2. **Istilah langsung diberi nama dan penjelasan datar**: *“I was working as a Gravekeeper.” / “the class I picked … became my current ‘Profession’.”* Tidak ada istilah yang mengambang.
3. **Suara percakapan**: narator berkomentar pendek dengan kata sehari-hari (*yup, well, honestly, right*), lalu cerita lanjut.
4. **Perbandingan kongret**: *“heavy like a soaked sponge.”* Bukan rangkaian metafora abstrak seperti “city noise came up through the stone like water through a pipe”.
5. **Satu ide per giliran bicara**, tanda tanya dan seruan dipakai bebas, humor langsung terlihat.
6. Daftar kemampuan ditulis datar: `[Resurrection of the Dead], [Mind's Eye]`.

Jadi fokus perbaikan bukan “memendekkan kalimat”, melainkan **mengganti kata abstrak/idiom dengan kata konkret, menjelaskan istilah di tempat, dan memakai suara yang berbicara langsung kepada pembaca**.

## 3. Setting yang sudah dipasang di repo (belum ada bab yang diubah)

- `story/style/audience.md` — audience 15+, non-native, kata umum, idiom hanya jika maknanya terlihat, satu ide per kalimat, istilah dijelaskan saat first use, pakai satu kata yang sama untuk benda yang sama.
- `story/bible/consistency-arc1.md` — nama kanonik, daftar benda yang tidak boleh tertukar, dan 8 inkosistensi yang ditemukan.

## 4. Inkonsistensi yang ditemukan di bab 1–50

1. **Thirteenth Vigil** vs **Black Thirteen** (ch 21 vs ch 3/13/20/36/37) — satu hal, dua nama.
2. **Husk** (9 bab) vs **Hushborn** (ch 31, 46) — tidak pernah dijelaskan bedanya.
3. **Lance Nine / Lance One** — tidak ada penjelasan bahwa itu grup lima siswa, bukan senjata.
4. **veinline** dan **vein-steel** (ch 28) — dipakai sekali tanpa penjelasan.
5. **Halvard Strent** dan **Strent** — campur; full name tidak selalu dipakai di first use tiap bab.
6. ch 27: surat panggilan datang “Saturday morning”, padahal rentang bab itu 14–18 Dec (Senin–Jumat). Perlu dicek dengan `calendar.md`.
7. **handkerchief** (kain putih bersulam bulu) dan **scarf** ( wol abu-abu) — dua benda berbeda; harus dipastikan tidak tertukar.
8. Label **[Tavu]**, **[Ithe]**, **[Wyl]**, **[Osk]**, **[Thessa]**, **[Grask]**, **[Citation]**, **[Lampwick]** sudah ada di `first-use.md`; deskripsi dan batasnya harus ikut dipertahankan saat rewrite.

Semua poin sudah diberikan aturan kanoniknya di `consistency-arc1.md`.

## 5. Aturan gaya yang direvisi (menunggu eksekusi)

1. **Kata konkret.** Daftar kata umum dipakai. Kata berat dijelaskan atau diganti saat first use: *groundskeeper* → "the man who looks after the grounds"; *handkerchief* → "a small cloth"; *headmistress* → "the woman who runs the school"; *scholarship* → "a paid place at school"; *quartermaster* → "the man who keeps the stores"; *lamplighter* → "the lamp man".
2. **Nama group/job/creature wajib dijelaskan.** Contoh: "Lance Nine, a group of five students, not a weapon." Kalau bisa disalahartikan, sebut juga apa BUKAN itu.
3. **Tanpa perbandingan abstrak.** `like a` maksimal 1 per bab, `as if` = 0. Kata kabur (*went quiet, went still, came back, the way*) diganti kalimat konkret: "the birds stopped calling", "his hands did not move".
4. **Idiom hanya jika maknanya terlihat.** Kalau perlu diterjemahkan, hapus.
5. **Satu ide per kalimat dan per giliran bicara.** Rata-rata 9–12 kata tetap dipertahankan, tetapi bukan target utama; yang utama adalah kata yang dimengerti.
6. **Ulang kata yang sama untuk benda yang sama.** Jangan berganti sinonim agar terdengar sastra.
7. **Tidak ada padding.** 2000–3000 kata tetap; penggantian kata harus memakai beats nyata.
8. **Guard diperbarui** (setelah disetujui): batas idiom, daftar kata berat, first-use gloss, dan daftar nama kanonik. Guard lama tidak dihapus.

## 6. Tahap kerja

- **Tahap 0 — Selesai:** riset 50 chapter, setting audience, setting konsistensi, rencana ini.
- **Tahap 1 — Menunggu perintah:** kunci aturan baru ke `profile.md`, `banned.md`, `quality-contract.md`, `writing-rules.md`, `tools/check_chapter.py`, dan glossary kecil. Tidak ada bab diubah.
- **Tahap 2 — Pilot:** tulis ulang 2 bab sebagai contoh, misalnya **ch 1** (perkenalan) dan **ch 6** (Lance Nine). Minta pemilik membaca hasil sebelum lanjut.
- **Tahap 3 — Produksi:** bab 1–50 per batch 3–5 bab, critic tiap 10 bab, cek konsistensi dan 6-gram tiap batch.
- **Tahap 4 — Penutup:** audit arc, `validate 1-50`, `milestone_check`, rebuild EPUB.

## 7. Kriteria selesai

- Pembaca 15 tahun non-native bisa memahami kalimat tanpa kamus (uji baca oleh pemilik).
- Istilah grup/job/creature punya penjelasan datar saat first use.
- Tidak ada lagi dua nama untuk satu hal (Vigil/Black Thirteen, Husk/Hushborn).
- `like a` ≤ 1/bab, `as if` = 0, idiom kabur = 0.
- 50/50 bab tetap lolos `check_chapter.py --strict`, `validate`, `milestone_check`.

## 8. Status

Setting sudah dipasang, rencana sudah diperbarui. **Chapter 1–50 belum diubah.** Menunggu perintah eksplisit untuk Tahap 1/2.
