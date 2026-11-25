# Single-Agent Optimization Audit (Fase 0)

Tanggal: 2026-11-25. Dasar: commit `7815569` (main setelah PR #6). Backup: branch `backup/pre-single-agent-opt-20261125` di GitHub (sama dengan 7815569) dan bundle lokal di container (tidak permanen). Tag git di remote gagal (HTTP 403 dari proxy), jadi tag hanya ada lokal.

Label bukti: **Verified** (dijalankan/dibaca langsung), **Measured** (angka dari alat), **Estimated** (perkiraan chars/4, bukan data provider), **Not available** (tidak ada datanya).

Tidak ada file selain dokumen ini yang diubah pada fase audit.

## 1. Kondisi arsitektur saat ini (Verified)
- Repo tidak berisi klien model. `grep` untuk anthropic/openai/requests/urllib di `tools/` hanya mengenai `build_epub.py` (kata "http" untuk namespace EPUB), tidak ada panggilan jaringan ke provider. Semua pemanggilan AI terjadi di sesi host (Claude Code); repo adalah kotak alat deterministik (`tools/*.py`, 3.463 baris, stdlib saja).
- Locked setting 13 (AGENTS.md): tidak ada sub-agent; orkestrator mengerjakan tiap peran sendiri, berurutan, di bawah lock global (`novels/lock.json`).
- Satu novel aktif: `the-thirteenth-knight-holds-every-sword`, 25 bab (sekitar 55 ribu kata), arc 1 (1-50) sedang ditulis, jadwal OFF.
- CI: `.github/workflows/tests.yml` menjalankan `tools/test_tools.py` dan `tools/ctx_compare.py` pada tiap PR dan push ke main. Hasil terakhir untuk PR #6: success (Verified).
- Tes lokal sekarang: `python3 tools/test_tools.py` = ALL TESTS PASSED (Verified).

## 2. Pemanggilan AI yang ditemukan
Karena tidak ada klien model, "pemanggilan" = tahap kerja di sesi host. Tidak ada log token aktual (lihat bagian 14).

| Tahap | Lokasi instruksi | Model (tier) | Frekuensi | Bisa diganti Python? |
|---|---|---|---|---|
| Development editor (rencana arc, bible) | `roles/development-editor.md` | strong (opus) | per arc / ide besar | Tidak (kreatif) |
| Lead writer + canon keeper | `engine/batch-writer-prompt.md`, `roles/lead-writer.md`, `roles/canon-keeper.md` | standard (sonnet) | per batch 5 bab | Penulisan: tidak. Pembukuan state/ringkasan sebagian bisa dicek Python, belum diotomatisasi |
| Critic | `engine/batch-critic-prompt.md`, `roles/copy-critic.md` | strong (opus) | per 10 bab | Pre-pass sudah Python (`prepass.py`); penilaian rasa: tidak |
| Managing editor audit | `roles/managing-editor.md` | strong | di dalam run critic tiap 10/20/30 bab | Sebagian (statistik skor) |
| Rewrite | `engine/rewrite-prompt.md` | standard | atas perintah owner | Tidak |
Catatan: konfigurasi menyebut model per tier, tetapi dengan locked setting 13 model sesi yang dipakai; pembedaan opus/sonnet per peran tidak bisa dipilih dari dalam sesi (Verified dari AGENTS.md).

## 3. Penggunaan agent / sub-agent (Verified, via grep)
Instruksi yang masih bertentangan dengan single-agent:
1. `engine/models.json`: `"mode": "delegate"` pada tiga peran (development_editor, lead_writer, copy_critic); `concurrency.rule` berbunyi "before spawning an agent"; `orchestrator.where` berbunyi "spawns ONE agent at a time". File ini bertanda LOCKED.
2. `AGENTS.md` bagian Production flow: kalimat "spawn ONE agent" masih ada, hanya diberi catatan override di judul.
3. `docs/ARCHITECTURE.md`: kalimat pembuka dan diagram menyatakan orkestrator "spawns one agent at a time".
4. `engine/batch-writer-prompt.md` baris 1 dan 5, `engine/batch-critic-prompt.md` baris 5: "agent ... You are the only agent running" (tidak berbahaya tetapi ambigu).
5. `engine/sop.md`, `engine/PORTABILITY.md`: ada opsi "sesi baru terpisah per peran"; PORTABILITY juga masih menyebut "spawn an agent" sebagai fungsi.
6. `docs/AUDIT_REPORT.md`, `docs/PERFORMANCE_BASELINE.md`: dokumen historis yang menyebut sub-agent (≈0,42 agent run per bab sebagai ESTIMATE). Dokumen historis, tidak diubah selain diberi catatan.
7. Tidak ada tes yang menegakkan kebijakan no-subagent (Verified: tidak ada kata "subagent/delegate" di `tools/test_tools.py`).

Konsekuensi: tidak ada kode yang membuat agent, jadi risiko riil rendah; risikonya instruksi yang kontradiktif membuat AI lain/sesi baru memahami salah. Lihat Stage 1.

## 4. Sumber pemborosan biaya (Estimated)
Tidak ada data token aktual, jadi ini perkiraan dari ukuran file (chars/4, bukan pengukuran provider).
1. Style profile besar di pack statis (lihat bagian 5), dibaca satu kali per batch.
2. Bible dibaca penulis per batch lewat ekstra dan baris retrieval.
3. Critic per 10 bab membaca 10 bab penuh (sekitar 25 ribu kata, Estimated) ditambah checklist.
4. Pack delta per bab, sebagian berulang walau sudah ada mode incremental.
5. Tidak ada angka revisi/retry aktual (Not available).

## 5. Context cost breakdown (Measured: `context_pack.py`, bab 26, karakter)
- Pack statis (`--part static --extra combat-style`): **32.195 karakter** (~8.000 token, Estimated). Bagian terbesar: Style profile 17.453 karakter (Measured; LEVEL 2.067, CLARITY 2.956, SCENE FEEL AND ARMOR 2.459, READABILITY 1.841, HUMAN FEEL 1.233, NATURAL FLOW 1.094, dll), Characters 2.898, Premise 2.076, combat-style ekstra ~6.000.
- Pack delta awal batch (`--batch-start --retrieve`): **20.792 karakter**. Terbesar: Retrieved memory 3.492, Precheck 2.542, Outline 2.351, Debts 2.769, Secrets 2.253, End of previous chapter 1.591, tiga ringkasan terakhir ~2.200.
- Pack delta incremental bab berikutnya: **19.264 karakter** pada kondisi ini (hemat kecil karena State/Debts/Secrets baru direset).
- Fixture beku (`ctx_compare.py`, bab 23-27): A (penuh) 76.406 vs B (incremental) 52.285 karakter = **31,6% lebih kecil (Measured, karakter; token Estimated)**. Ini hanya fixture, bukan data produksi.
- File bible: 47 file, 258.589 karakter total di `story/bible/`; outline 49.109 karakter. Tidak semuanya dimuat; hanya yang disebut prompt.
- Duplikasi: `writer-digest.md` (baru, ringkas) menduplikasi bagian `power-system.md` dengan sengaja; `powers.md`, `armor.md`, `invaders.md`, `mana.md` memuat konten lama yang sebagian sudah SUPERSEDED (dimuat hanya jika dipanggil lewat --extra).
- Context writer vs critic sudah terpisah (prompt berbeda, critic mulai dari pre-pass).

## 6. Pekerjaan AI yang bisa dipindah ke Python
Sudah Python (Verified): hitung kata, format heading, struktur bab (`check_chapter.py`), go/no-go batch (`verify_batch.py`: file, heading, kata, ringkasan, outline, skor, git bersih), pre-pass kalimat/idiom/pengulangan (`prepass.py`), hash dan cache context, retrieval berbasis nama, state mesin (`engine_state.py`), arsip, EPUB, lock, usage log.
Celah yang masih ke AI atau belum ada:
- Validasi data cerita terstruktur (nama tidak dikenal, status karakter berubah tanpa event, timeline berbenturan): belum ada; `canon_names.txt` hanya dipakai pre-check nama baru.
- Pemeriksaan JSON/format metadata di semua file ops: parsial.
- Laporan validasi batch yang dihimpun dalam satu format (error/warning/info): belum ada; keluaran tersebar.
- Pemeriksaan konsistensi `models.json`/dokumen terhadap kebijakan single-agent: belum ada.

## 7. Kelemahan story memory (Verified)
- Memory = file markdown (`state.md`, `debts.md`, `secrets.md`, `threads.md`, `timeline.md`, `twists-*.md`, `summaries.md` plus arsip). Retrieval (`memory_retrieve.py`) berbasis kecocokan nama kanon di baris outline N..N+2, nomor bab di tabel plant/feed, dan ringkasan lama yang berbagi ≥2 nama; anggaran 3.000 karakter, entri yang tidak muat dicatat file:baris.
- Tidak ada indeks terstruktur (karakter, event, relasi, konflik, misteri, foreshadowing), tidak ada provenance, tidak ada FTS. Tes retrieval hanya pada fixture (2/2 dan 3/3 ditemukan, Measured; bukan ukuran recall di 850 bab).
- Tidak ada rolling arc summary; ringkasan lama dipindah ke arsip dan hanya tersentuh retrieval nama.
- SQLite dengan FTS5 tersedia di lingkungan ini (sqlite 3.53.1, Verified), jadi tidak butuh dependensi baru. Belum ada bukti bahwa FTS5 diperlukan atau cukup di skala 850 bab.

## 8. Risiko kualitas cerita
Pengurangan context bisa menimbulkan: plot hole karena debts/secrets terpotong, lupa foreshadowing, nama/relasi tidak konsisten, pengulangan adegan. Pencegah yang sudah ada: tangga reveal-ladder, first-use, pre-pass pengulangan 5-kata, critic per 10 bab, tes lossless State/Debts/Secrets. Yang kurang: pelacak foreshadowing/misteri terstruktur, benchmark kualitas narasi (tidak ada), dan self-review ringkas per bab (critic baru per 10 bab). Dengan critic = sesi yang sama dengan penulis, tidak ada pemeriksa independen (Verified dari locked setting 13).

## 9. Rekomendasi optimasi
1. Selaraskan semua dokumen dan `models.json` dengan single-agent; tambah tes penegak (Stage 1).
2. Tambah anggaran context yang terukur dan log ukuran per pemanggilan; pecah style profile menjadi inti (selalu) dan bagian situasional (hanya bila relevan: fight, armor, romance) tanpa menghapus aturan permanen (Stage 2). Perlu persetujuan owner bila memotong aturan gaya yang dikunci (locked setting 12).
3. Validator Python berbasis data terstruktur dengan keluaran ERROR/WARNING/INFO (Stage 3).
4. Checklist self-review ringkas per bab + klasifikasi risiko di Python, kompatibel dengan critic per 10 bab (Stage 4).
5. Indeks SQLite/FTS5 turunan dari markdown (Stage 5), diuji vs retrieval saat ini sebelum dipakai.
6. Usage log yang memisahkan reported/manual/estimated; laporan biaya per bab dan proyeksi 850 bab hanya setelah ada data aktual (Stage 6).

## 10. Prioritas implementasi
P1 Stage 1 (risiko rendah, kontradiksi dokumen). P2 Stage 3 (validator, 0 token, aman). P3 Stage 2 dan 5 (ubah cara context diambil; perlu benchmark). P4 Stage 4 dan 6.

## 11. File yang akan diubah
Stage 1: `engine/models.json` (hanya field `mode` dan teks `rule`/`where`, bukan model/tier/concurrency angka), `AGENTS.md`, `docs/ARCHITECTURE.md`, `engine/batch-writer-prompt.md`, `engine/batch-critic-prompt.md`, `engine/sop.md`, `engine/PORTABILITY.md`, `tools/test_tools.py`, tool baru `tools/policy_check.py`.
Stage berikutnya: `tools/context_pack.py`, `tools/memory_retrieve.py`, `tools/usage_log.py`, `tools/verify_batch.py`, tool baru (validator, indeks SQLite), dokumen `docs/`.

## 12. File yang tidak boleh diubah
- Isi `novels/*/chapters/` (bab selesai), `story/bible/*`, outline, brief, state, ringkasan (canon).
- Pengaturan terkunci: nilai model dan tier, `concurrency.max_agents_per_job`, ukuran batch 5, critic per 10 bab, target kata, jadwal OFF, provider.
- Pembatasan konten (tanpa seksual/ecchi/harem) dan locked settings 1-13 di `AGENTS.md`.
Catatan: `engine/models.json` bertanda LOCKED. Permintaan owner pada tugas ini secara eksplisit meminta menonaktifkan konfigurasi delegate "tanpa mengubah model utama maupun tier model". Saya membaca itu sebagai izin mengubah hanya field `mode` dan teks kata "spawn". Jika owner tidak setuju, hentikan di Stage 1.

## 13. Baseline metrik yang berhasil dikumpulkan (Measured)
- Pack statis 32.195 karakter; delta batch-start 20.792; delta incremental 19.264.
- Fixture A/B: 76.406 vs 52.285 karakter (31,6% lebih kecil).
- Tes: ALL TESTS PASSED; CI PR #6 success.
- Bab: 25, ~55.115 kata.
- Panggilan jaringan ke provider dari repo: 0.

## 14. Informasi yang belum dapat diukur
- Token input/output/cache aktual dan biaya aktual: **Not available**. Tidak ada `ops/usage.jsonl` dan host tidak mengekspos usage ke repo. Penghematan biaya aktual tidak dapat dibuktikan sampai data itu ada.
- Jumlah revisi/retry per bab, jumlah tahap per bab: Not available (hanya estimasi desain di `PERFORMANCE_BASELINE.md`).
- Kualitas narasi sebelum/sesudah: Not tested (belum ada benchmark blind).
- Recall retrieval di skala ratusan bab: Not tested.
- Perbedaan model opus vs sonnet per peran: tidak dapat dipilih di sesi tunggal.

## Temuan sampingan (tidak diubah, perlu keputusan owner)
- `novels/*/story/bible/state.md` masih memuat kata "rank 8" untuk Eden, sedangkan canon baru menghapus level/rank. Konten novel, tidak disentuh.
- `docs/OPTIMIZATION_CHANGELOG.md` sudah ada (Phase Two). Dokumen akhir akan menambah bagian baru, bukan menimpa.
