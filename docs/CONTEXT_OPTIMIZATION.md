# Context Optimization (Stage 2 dan 4)

Label: **Measured** = diukur alat, **Estimated** = chars/4, **Not tested**.

## Lapisan context (peta ke alat yang ada)
| Lapisan | Isi | Alat |
|---|---|---|
| L0 inti | aturan permanen: style profile, banned, series | `context_pack.py --part static` (sekali per batch) |
| L1 state ringkas | premise, characters, state, who-knows-what | pack static + bagian State |
| L2 memory relevan | thread/twist/timeline/ringkasan lama yang cocok dengan outline | `--retrieve` (`memory_retrieve.py`), dan indeks `memory_index.py query` |
| L3 bab terbaru | 3 ringkasan terakhir + 300 kata akhir bab | `--part delta` |
| L4 historis | ringkasan arsip, bab lama | hanya lewat retrieval/indeks, atas permintaan |

## Yang dibangun
- **Fingerprint:** setiap pack mencetak `[context fingerprint <sha12>; N chars ...]`. Hash sumber static sudah dipakai sebagai kunci cache (`static_hash`).
- **Incremental + cache + invalidasi:** sudah ada (State/Debts/Secrets hanya diff; cache gugur bila bab tidak berurutan, >3 jam, atau sumber static berubah). Diuji.
- **Log ukuran:** `--log` menambahkan satu baris ke `ops/context-log.jsonl` (chars, fingerprint, ukuran per bagian, bagian yang dibuang). Hanya karakter; token = unavailable. `usage_log.py report` merangkumnya.
- **Anggaran dapat dikonfigurasi:** `--budget N` (default: setting `context_pack_max_chars`). Bila lebih, bagian prioritas rendah dibuang UTUH berurutan: `Extra:`, `Retrieved memory`, `Pacing`, dan dicatat di `[PACK NOTE ...]`. Bagian terlindungi (style, banned, series, characters, premise, outline, state, debts, secrets, ringkasan, akhir bab sebelumnya, precheck, inbox) tidak pernah dibuang; bila hanya itu pun melebihi anggaran, pemotongan ekor lama dan exit 4 tetap berlaku (tidak diam-diam).
- **Deduplikasi:** baris identik >= 80 karakter hanya dimuat sekali di dalam satu pack; jumlah karakter yang dihapus dicetak di footer.
- **Style split (disetujui owner 2026-11-25):** `--style auto` (default) mengganti tiga blok situasional (SPECIAL ATTACK LABEL, bagian ARMOR di SCENE FEEL AND ARMOR, Battles and aura) dengan satu baris `[STYLE NOTE ...]` HANYA bila baris outline bab N..N+4 tidak memuat kata pertarungan/armor/kekuatan; tanpa baris outline = style penuh. `--style full` selalu memuat semua. Aturan permanen lain (LEVEL, CLARITY, FIRST USE, SCENE FEEL mood, HUMAN FEEL, READABILITY, NATURAL FLOW) selalu dimuat. File `profile.md` tidak diubah.
- **Pemisahan context:** self-review memakai `tools/review_pack.py N`: teks bab, baris outline, canon relevan (retrieval dengan file:baris), baris reveal-ladder/first-use untuk bab itu, Debts/Secrets, checklist, tingkat risiko. Tidak memuat style profile, premise, characters.

## Hasil pengukuran (`tools/bench_context.py`, karakter, bab 26/31/36/41/46)
Lihat `docs/COST_BENCHMARK.md`. Ringkas: pack static +114 karakter dan delta +100..+136 karakter dibanding commit 7815569 (hanya baris footer fingerprint). **Tidak ada pengurangan input pada pack yang ada sekarang.**
- Duplikasi baris identik di pack: 0 karakter (Measured), jadi target "pengurangan duplikasi 80%+" tidak punya apa-apa untuk dikurangi; yang ada hanyalah penjaga bila duplikasi muncul.
- Style split: semua baris outline arc 1 (bab 26-50) memuat kata pertarungan/kekuatan, jadi blok situasional tetap dimuat: hemat 0. Pada outline tanpa pertarungan (diuji dengan contoh) hemat 2.435 karakter dari 17.453 (14%).
- Penghematan nyata yang terukur hanya mode incremental yang sudah ada: 31,6% lebih kecil pada fixture beku (`ctx_compare.py`), di bab ke-2 dan seterusnya dalam satu batch.
Target 30-50% pengurangan input token: **tidak tercapai dan tidak dapat dibuktikan** (tidak ada data token provider; pada pengukuran karakter hanya mode incremental yang mengurangi).

## Keterbatasan
- Pengurangan context diukur dalam karakter, bukan token provider.
- Review pack ~22.800 karakter untuk bab 25 (teks bab ~13 ribu); self-review menambah input per bab. Dampak biaya bersih belum diukur.
- Klasifikasi risiko (`tools/risk.py`) berbasis kata kunci dan tabel; false positive/negative tidak diukur.
