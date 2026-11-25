# Single-Agent Architecture

Status: Stage 1 selesai (2026-11-25). Aturan sumber: AGENTS.md locked setting 13 (tidak ada sub-agent, permanen).

## Prinsip
- Satu AI utama (sesi host) mengerjakan semua pekerjaan kreatif. Tidak ada sub-agent, delegasi, atau AI paralel.
- Peran (development editor, writer, canon keeper, critic, managing editor, rewrite) adalah TAHAP KERJA yang dijalankan berurutan oleh AI yang sama, satu per satu, di bawah lock global (`tools/lock.py`).
- Pekerjaan deterministik berada di `tools/*.py` (0 token, stdlib saja).
- Repo tidak berisi klien model; tidak ada panggilan jaringan ke provider.

## Alur satu batch (inline)
1. `engine_state.py next` lalu `lock.py acquire write`.
2. Tahap penulis: konteks via `context_pack.py`, tulis bab, pembukuan canon per bab, commit per bab.
3. `lock.py release`, `verify_batch.py A-B` (cek teknis, tanpa AI).
4. Tahap critic per 10 bab (pengaturan terkunci): `prepass.py` dulu, lalu pemeriksaan naskah dan patch kecil; audit di dalam run critic pada bab 10/20/30.
5. `save.py`, `engine_state.py next`.

## Batas yang jujur
Penulis dan critic adalah sesi yang sama. Tidak ada pemeriksa independen; kualitas pemeriksaan bergantung pada `prepass.py`, `verify_batch.py` dan checklist tertulis. Ini konsekuensi aturan owner, bukan bug.

## Penegakan
- `engine/models.json`: field `mode` memakai `inline-stage` (nilai lama untuk delegasi sudah dihapus); model, tier, dan `max_agents_per_job` tidak diubah.
- `tools/policy_check.py` gagal (exit 1) bila konfigurasi menyuruh delegasi atau dokumen instruksi menyuruh memulai agent. Dijalankan di CI dan di `tools/test_tools.py`.
- Pemeriksa bekerja per klausa (dipecah di titik, titik koma, tanda hubung dan kata kontras seperti but/tetapi/namun). Klausa yang memuat istilah terlarang hanya lolos bila itu larangan murni: kata larangan (never/not/jangan/tidak pernah, dan lain-lain) tepat di depannya atau "is never/not" tepat di belakangnya. Kata pengecualian atau kewajiban (except, unless, kecuali, forget to, lupa, must, wajib) menggagalkan klausa. Diuji dengan kalimat adversarial (Inggris, Indonesia, campuran).
- Keterbatasan: pemeriksa memakai kata kunci, bukan pemahaman bahasa. Kalimat yang menyuruh delegasi dengan kata lain yang tidak ada di daftar tidak terdeteksi. Dokumen historis (AUDIT_REPORT, PERFORMANCE_BASELINE, OPTIMIZATION_*, decisions.md) tidak dipindai.
