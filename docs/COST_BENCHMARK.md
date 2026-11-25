# Cost Benchmark (Stage 6 dan 7)

Label: **Measured** (alat), **Estimated** (chars/4), **Not available**, **Not tested**.

## Data biaya aktual
**Not available.** Tidak ada `ops/usage.jsonl`; host tidak mengekspos token atau biaya ke repo. Karena itu:
- Biaya per bab, per arc, per 100 bab dan proyeksi 850 bab **belum dapat dihitung**. `python3 tools/usage_log.py report` mencetak "UNMEASURED" sampai ada data, dan proyeksi hanya muncul bila ada biaya dari provider (`--actual-cost`) atau harga di `engine/prices.json` plus token berlabel `reported`/`manual`. Proyeksi selalu berlabel "PROJECTION (linear, NOT a measurement)".
- Data `reported`, `manual`, `estimate` tidak pernah dijumlahkan satu sama lain (diuji).
- Klaim penghematan biaya aktual: **tidak ada**.

## Alat pencatatan (Stage 6)
`usage_log.py add` kini menyimpan: timestamp, novel, role/operation, model, provider, range bab, input/output/total tokens, cache read/write, actual_cost (hanya bila provider melaporkan), context_characters, context_fingerprint, revision_count, source (reported/manual/estimate). `report` menampilkan per sumber: token per bab, biaya per bab, per 100 bab, proyeksi 850 (berlabel), tahap per bab, revisi per bab, dan ringkasan `context-log.jsonl` (karakter, bukan token). Diuji dengan tes `cost:*` dan `usage*`.

## Benchmark ukuran context (Measured, karakter)
BEFORE = alat commit 7815569; AFTER = alat sekarang; data novel sama. Dibuat dengan `python3 tools/bench_context.py`.

| chapter | part | BEFORE chars (7815569) | AFTER chars (now) | change |
|---|---|---:|---:|---:|
| 26 | static | 32195 | 32309 | +114 (+0.4%) |
| 26 | delta | 20834 | 20925 | +91 (+0.4%) |
| 31 | static | 32195 | 32309 | +114 (+0.4%) |
| 31 | delta | 18402 | 18472 | +70 (+0.4%) |
| 36 | static | 32195 | 32309 | +114 (+0.4%) |
| 36 | delta | 18366 | 18508 | +142 (+0.8%) |
| 41 | static | 32195 | 32309 | +114 (+0.4%) |
| 41 | delta | 18102 | 18189 | +87 (+0.5%) |
| 46 | static | 32195 | 32309 | +114 (+0.4%) |
| 46 | delta | 18794 | 18844 | +50 (+0.3%) |
| total | | 255473 | 256483 | +1010 (+0.4%) |

About 63868 -> 64120 tokens over these packs (ESTIMATE chars/4; no provider data).

Pembacaan jujur: tidak ada pengurangan. Selisih +0,4-0,7% hanyalah baris footer fingerprint (~114 karakter). Style split tidak aktif karena semua outline arc 1 memuat kata pertarungan/kekuatan; duplikasi baris identik 0 karakter. Satu-satunya penghematan terukur adalah mode incremental yang sudah ada: 31,6% lebih kecil pada fixture beku (76.406 -> 52.285 karakter, bab 23-27, `ctx_compare.py`), bukan data produksi.

## Self-review (penambahan input)
Review pack bab 25: 22.809 karakter (Measured; teks bab ikut di dalamnya). Ini input tambahan per bab; biaya bersihnya terhadap critic per 10 bab **belum diukur**.

## Tidak diuji
- Kualitas narasi sebelum/sesudah (blind evaluation): **Not tested**. Tidak ada bab baru yang ditulis dengan alur baru, jadi tidak ada data kualitas.
- Retrieval precision/recall, revision rate, continuity error pada 20-30 bab: **Not tested** (hanya 25 bab ada, dan tidak ada set berlabel).
- Target pengurangan input token 30-50%: **tidak tercapai/tidak terbukti**. Penyebab: pack yang ada sudah memakai incremental; sisa isi adalah canon dan aturan gaya permanen yang tidak boleh dipotong; tidak ada token provider untuk membuktikan apa pun.

## Cara membuktikan nanti
1. Setiap batch: `usage_log.py add ... --source reported` bila host melaporkan token, atau `manual` dari halaman usage owner, plus `--context-chars/--context-fingerprint`.
2. Jalankan batch yang sama dengan `--style full` dan `auto`, bandingkan `usage_log.py report`.
3. Setelah >= 20 bab dengan alur baru, lakukan penilaian blind oleh owner terhadap sampel bab lama vs baru.
