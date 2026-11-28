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

### 2b. Kenapa bab 3 ke atas terasa abstrak (data dari novel kita)

Saya menghitung penanda kiasan/suasana per 10 bab:

| Rentang | Penanda per 1000 kata | Penanda terbanyak |
|---|---|---|
| ch 1–2 | 5,91 | *as if, like a, the way* |
| ch 3–10 | 6,85 | *cold* (28), *shadow* (24), *like a* (20), *as if* (17) |
| ch 11–20 | 4,73 | *shadow* (24), *cold* (24), *came back* (10) |
| ch 21–30 | 5,22 | *shadow* (43), *cold* (27) |
| ch 31–40 | 5,84 | *cold* (44), *shadow* (25), *came back* (16) |
| ch 41–50 | 6,64 | *shadow* (40), *came back* (21), *as if* (20) |

Kata *cold* dan *shadow* sering dipakai bukan sebagai fakta, melainkan sebagai jalan pintas untuk menggambarkan suasana. Di bab 1–2 hampir tidak ada; di bab 3 ke atas meningkat. Itu sesuai dengan keluhan pemilik. Aturan baru: **jangan pakai kiasan untuk suasana.** Sebut apa yang terlihat dan apa yang dilakukan orang.

Contoh penggantian gaya Holy Emperor:
- Lama: "The cold air settled over the yard." → Baru: "The men stood in the yard and blew on their hands."
- Lama: "A shadow moved at the gate." → Baru: "A man stepped out of the dark at the gate."
- Lama: "The thought sat in his mind like a stone in a boot." → Baru: "He thought about the order. He could not put it away."

Jadi fokus perbaikan bukan “memendekkan kalimat”, melainkan **mengganti kata abstrak/idiom dengan kata konkret, menjelaskan istilah di tempat, dan memakai suara yang berbicara langsung kepada pembaca**.

### 2c. Kenapa kata *doors, ash, knock, dust* dan kekuatan Eden/Valerius membingungkan

Data dari 50 bab kita:

- `door/doors` biasa dipakai 310 kali; `Door/Doors` (kekuatan Eden) 26 kali. **Satu ejaan untuk dua hal**: pintu rumah dan “pintu bayangan”.
- `knock/knocked/knocking` 67 kali. Kata yang sama dipakai untuk mengetuk pintu nyata dan untuk memicu kekuatan Eden. Pembaca tidak diberi tahu bahwa itu dua hal berbeda.
- `ash` 32 kali, `dust` 89 kali, tetapi hanya 25 yang menyebut "grey dust". Jadi pembaca tidak tahu apakah abu/debu itu sisa api, debu lantai, atau sisa musuh.
- Label kekuatan jarang muncul: **[Umra]** 8 kali, **[Inead]** 11 kali, **[Exa]** 18 kali, **[Door]** 26 kali, **[Injunction]** 1 kali, "aura" 4 kali. Artinya hampir semua penjelasan hanya ada di awal, lalu cerita lanjut dengan kata abstrak seperti *cold, shadow, the air went thick, frosted over*.

**Sebab utamanya:** kita memakai **nama kanon sebagai pengganti penjelasan**. Pembaca diberi label, bukan gambaran. Aturan lama malah memperkuat ini: "jangan perlihatkan ke mana Door pergi" → akhirnya tertulis "held in the dark" yang terdengar kabur. Kekuatan Valerius lebih parah karena hampir tidak pernah dijelaskan secara visual; yang ada hanya "a pale wall" dan "frosted over".

**Solusi yang diusulkan:**

1. Pisahkan kata: pintu nyata tetap "door"; kekuatan Eden jadi **"a black opening in the shadow"**, label **[Door]** hanya di first use.
2. Pisahkan gerakan: pintu nyata "knock"; pemicu Eden **"tap the shadow twice"** atau **"tap the ring once"**.
3. Pisahkan bahan: "ash" hanya sisa api; sisa musuh selalu **"grey dust"**; debu lantai "dirt"; debu batu "stone dust".
4. Tiap kekuatan dapat **kartu kekuatan**: satu kalimat tentang apa yang terlihat, satu frasa pengganti, satu kalimat biaya. Kartu sudah ditambahkan ke `story/bible/consistency-arc1.md` bagian 6c.
5. Valerius: tunjukkan garis di batu, kalimat yang ia ucapkan, dinding pucat yang berdiri, dan satu napas yang hilang. Jangan pakai "aura frosted over" sebagai penjelasan.
6. Guard baru: daftar kata yang harus punya penjelasan di dekat first use (*door/knock/dust/ash* dan semua label kekuatan).

## 3. Setting yang sudah dipasang di repo (belum ada bab yang diubah)

- `story/style/audience.md` — audience 15+, non-native, kata umum, idiom hanya jika maknanya terlihat, satu ide per kalimat, istilah dijelaskan saat first use, pakai satu kata yang sama untuk benda yang sama.
- `story/bible/consistency-arc1.md` — nama kanonik, daftar benda yang tidak boleh tertukar, 8 inkosistensi, peta kata *door/knock/dust/ash*, dan kartu kekuatan Eden–Valerius.

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

1. **Kata konkret, dan kata 'group' untuk tim.** Narasi memakai **group**, bukan *lance*, untuk unit siswa. "Lance Nine" hanya dipakai sekali sebagai nama resmi dengan penjelasan "a group of five students"; sesudah itu "the group". **[Black Lancer]** tetap dipakai sebagai nama job, bukan nama grup, dan dijelaskan "a knight with a dark lance". Kata umum lain dipakai seperti ini: *groundskeeper* → "the man who looks after the grounds"; *handkerchief* → "a small cloth"; *headmistress* → "the woman who runs the school"; *scholarship* → "a paid place at school"; *quartermaster* → "the man who keeps the stores"; *lamplighter* → "the lamp man".
2. **Nama group/job/creature wajib dijelaskan.** Contoh: "Lance Nine, a group of five students, not a weapon." Kalau bisa disalahartikan, sebut juga apa BUKAN itu.
3. **Tanpa kiasan untuk suasana atau aksi.** `like a` maksimal 1 per bab, `as if` = 0. Kata kabur (*went quiet, went still, came back, the way*) diganti kalimat konkret: "the birds stopped calling", "his hands did not move". Kata *cold* dan *shadow* hanya boleh bila benar-benar fakta fisik yang dibutuhkan cerita (misalnya Rotation di Wall), bukan sebagai pengganti "serius", "takut", atau "misterius". Suasana ditulis lewat tindakan: orang berhenti bicara, melihat ke pintu, meniup tangan, atau bersandar ke dinding.
4. **Idiom hanya jika maknanya terlihat.** Kalau perlu diterjemahkan, hapus.
5. **Satu ide per kalimat dan per giliran bicara.** Rata-rata 9–12 kata tetap dipertahankan, tetapi bukan target utama; yang utama adalah kata yang dimengerti.
6. **Ulang kata yang sama untuk benda yang sama.** Jangan berganti sinonim agar terdengar sastra.
7. **Tidak ada padding.** 2000–3000 kata tetap; penggantian kata harus memakai beats nyata.
8. **Guard diperbarui** (setelah disetujui): batas idiom, daftar kata berat, first-use gloss, dan daftar nama kanonik. Guard lama tidak dihapus.

## 6. Tahap kerja

- **Tahap 0 — Selesai:** riset 50 chapter, setting audience, setting konsistensi, rencana ini.
- **Tahap 1 — Menunggu perintah:** kunci aturan baru ke `profile.md`, `banned.md`, `quality-contract.md`, `writing-rules.md`, `tools/check_chapter.py`, dan glossary kecil. Tidak ada bab diubah.
- **Tahap 2 — Pilot:** tulis ulang 4 bab sebagai contoh: **ch 1** (perkenalan), **ch 3** (first use Door/Umra/Inead), **ch 6** (Lance Nine → "the group"), dan **ch 16** (Valerius/Injunction). Minta pemilik membaca hasil sebelum lanjut.
- **Tahap 3 — Produksi:** bab 1–50 per batch 3–5 bab, critic tiap 10 bab, cek konsistensi dan 6-gram tiap batch.
- **Tahap 4 — Penutup:** audit arc, `validate 1-50`, `milestone_check`, rebuild EPUB.

## 7. Kriteria selesai

- Pembaca 15 tahun non-native bisa memahami kalimat tanpa kamus (uji baca oleh pemilik).
- Istilah grup/job/creature punya penjelasan datar saat first use.
- Tidak ada lagi dua nama untuk satu hal (Vigil/Black Thirteen, Husk/Hushborn).
- `like a` ≤ 1/bab, `as if` = 0, idiom kabur = 0, penanda kiasan suasana turun dari ±6/1000 kata menjadi ≤2/1000 kata.
- Narasi memakai "group" untuk tim siswa; "lance" tidak dipakai lagi sebagai kata grup.
- Tidak ada lagi "Door" untuk kekuatan dalam narasi (pakai "a black opening"), tidak ada "knock" untuk pemicu (pakai "tap"), tidak ada "ash" untuk sisa musuh, tidak ada "dust" tanpa jenis.
- Kekuatan Eden dan Valerius selalu punya kalimat "apa yang terlihat" sebelum label dipakai.
- 50/50 bab tetap lolos `check_chapter.py --strict`, `validate`, `milestone_check`.

## 8. Status

Setting sudah dipasang, rencana sudah diperbarui. **Chapter 1–50 belum diubah.** Menunggu perintah eksplisit untuk Tahap 1/2.
