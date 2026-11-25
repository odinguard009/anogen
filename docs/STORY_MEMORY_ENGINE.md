# Story Memory Engine (Stage 5)

Markdown tetap sumber kebenaran. `ops/memory.sqlite` (SQLite + FTS5, gitignored, bisa dibangun ulang kapan saja) hanya indeks turunan.

## Alat
`python3 tools/memory_index.py update|rebuild|query|stats|arc-digest`
- **Indeks otomatis:** `query`/`arc-digest` memanggil `update` lebih dulu; `save.py` memanggilnya (best effort, tidak pernah menggagalkan save) setelah tiap bab disimpan. Hanya file yang hash-nya berubah yang diindeks ulang.
- **Sumber -> tipe:** summaries (+arsip) = chapter; threads.md = thread; twists-*.md = twist; debts.md = debt; secrets.md = secret; timeline.md = event; characters.md = character; outline/arc-*.md = arc_outline.
- **Kolom:** id, type, chapter, arc, characters, summary, importance, status, source (provenance `file:baris`), last_updated, confidence, related_events, supersedes.
- **Aturan penurunan (tanpa AI, tanpa penilaian):** `characters` = nama kanon (`canon_names.txt`) yang muncul di teks; `arc` dari rentang arc di `ops/engine.json`; `importance=major` hanya bila barisnya sendiri menulis "(big)"/"major"; `status` dari `[open]/[paid]` atau `SUPERSEDED`; `confidence` selalu `derived`.
- **Deduplikasi:** baris bertipe sama dengan teks identik dimasukkan sekali (jumlah duplikat dilaporkan).
- **Query:** `--text` (FTS5), `--chars`, `--chapter` + `--near`, `--arc`, `--type`, `--status`, `--limit`; hasil urut major dulu.
- **Rolling arc digest:** `arc-digest K [--write]` = kalimat pertama tiap ringkasan bab di arc K (deterministik, dengan provenance). Bukan ringkasan tulisan AI.
- **Pemulihan:** indeks rusak dipindah ke `memory.sqlite.corrupt` dan dibangun ulang dari markdown.

## Hubungan dengan retrieval lama
`memory_retrieve.py` (berbasis nama dan nomor bab, dipakai `--retrieve`) tidak diganti. Indeks FTS adalah jalur tambahan untuk pertanyaan bebas (mis. "siapa yang tahu soal liontin?"). Belum ada bukti bahwa salah satu lebih baik.

## Belum diuji / belum ada
- Precision dan recall retrieval: **Not tested** (tidak ada kumpulan pertanyaan berlabel; membuatnya dari data yang sama akan sirkular).
- Skala 850 bab: **Not tested**. Saat ini 259 baris untuk 25 bab (Measured); FTS5 lokal cepat pada ukuran itu, tetapi tidak ada pengujian pada ribuan baris.
- Validasi data cerita terstruktur (status karakter berubah tanpa event, kontradiksi timeline) membutuhkan data terstruktur yang belum ada; markdown timeline berupa prosa. Tidak diimplementasikan, tidak dipalsukan. `validate.py` hanya memeriksa hal yang pasti (struktur, file, utang jatuh tempo, nama di luar kanon sebagai WARNING).
- Vector database: tidak ditambahkan; belum ada bukti SQLite/FTS5 gagal.
