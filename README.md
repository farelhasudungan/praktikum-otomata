# Tugas Praktikum — Teori Bahasa & Automata

> Mata Kuliah: **Teori Bahasa & Automata (Otomata)**  
> Institusi: **Institut Teknologi Sepuluh Nopember (ITS)**  
> Semester: **4**

Repository ini berisi tiga program Python berbasis GUI (Tkinter) untuk tugas praktikum mata kuliah Teori Bahasa & Automata.

---

## Daftar Program

| File | Tugas | Deskripsi Singkat |
|------|-------|-------------------|
| `TugasW2.py` | Praktikum #1 | Tokenizer / Lexical Analyzer |
| `TugasW3.py` | Praktikum #2 | FSM (Finite State Machine) Simulator |
| `TugasW7_PDA.py` | Praktikum PDA | NPDA / Pushdown Automata Simulator |

---

## Prasyarat

- **Python 3.x** (disarankan Python 3.8+)
- **Tkinter** — sudah termasuk dalam instalasi standar Python di Windows & macOS. Untuk Linux:
  ```bash
  sudo apt-get install python3-tk
  ```
- Tidak memerlukan library eksternal tambahan (hanya menggunakan modul bawaan: `re`, `tkinter`, `math`, `dataclasses`, `collections`).

---

## TugasW2.py — Tokenizer Analyzer

### Deskripsi

Program ini melakukan **analisis leksikal (tokenisasi)** terhadap source code. Setiap token yang ditemukan akan diklasifikasikan ke dalam salah satu kategori berikut:

| Kategori | Deskripsi | Contoh | Warna |
|----------|-----------|--------|-------|
| **Reserved Word** | Kata kunci bahasa pemrograman | `if`, `else`, `for`, `while`, `return`, `int`, `float`, `void`, dll. | Biru |
| **Variable** | Identifier / nama variabel | `x`, `count`, `myVar` | Hitam |
| **Math** | Operator matematika & angka | `+`, `-`, `*`, `/`, `=`, `<`, `>`, `42`, `3.14` | Hijau |
| **Symbol** | Simbol / tanda baca | `(`, `)`, `{`, `}`, `;`, `,`, `#` | Ungu |
| **Unknown** | Token yang tidak dikenali | — | Merah |

### Cara Menjalankan

```bash
python TugasW2.py
```

### Cara Menggunakan

1. **Tulis atau tempel** kode program pada kotak input.
2. Atau klik **"Load File"** untuk memuat file dari disk.
3. Klik **"Analyze"** untuk menjalankan tokenisasi.
4. Hasil analisis token akan tampil di bagian bawah dengan warna sesuai kategori.
5. Klik **"Clear"** untuk mengosongkan semua input dan output.

### Alur Kerja Program

```
Source Code → Tokenisasi (regex) → Klasifikasi Token → Output (berwarna)
```

1. **Tokenisasi** — Menggunakan regex untuk memecah input menjadi token: identifier/keyword, angka (integer & float), dan simbol tunggal.
2. **Klasifikasi** — Setiap token dicek secara berurutan:
   - Apakah termasuk *reserved word*?
   - Apakah berupa angka atau operator matematika?
   - Apakah termasuk simbol?
   - Apakah berupa identifier/variabel?
   - Jika tidak cocok semua → *Unknown*
3. **Output** — Ditampilkan dalam format `token -> kategori` dengan pewarnaan.

---

## TugasW3.py — FSM Simulator

### Deskripsi

Program ini mensimulasikan sebuah **Deterministic Finite Automaton (DFA)** yang menerima bahasa:

```
L = { x ∈ (0+1)⁺ | karakter terakhir x = 1  ∧  x tidak memiliki substring "00" }
```

Dengan kata lain, string biner **diterima** jika dan hanya jika:
- String **tidak kosong** (minimal 1 karakter)
- Hanya terdiri dari karakter `0` dan `1`
- **Karakter terakhir adalah `1`**
- **Tidak mengandung substring `"00"`**

### Definisi FSM

| State | Deskripsi | Tipe |
|-------|-----------|------|
| **S** | Start — belum membaca input | Start state |
| **A** | Baru membaca `0`, menunggu `1` | Normal state |
| **B** | Baru membaca `1` | Accept state |
| **C** | Dead state — ditemukan `00` | Trap/dead state |

#### Tabel Transisi

| State | Input `0` | Input `1` |
|-------|-----------|-----------|
| S | A | B |
| A | C | B |
| B | A | B |
| C | C | C |

### Cara Menjalankan

```bash
python TugasW3.py
```

### Cara Menggunakan

1. **Masukkan string biner** (contoh: `101`, `0101`, `00`) pada kotak input.
2. Klik **"▶ Analyze"** untuk langsung melihat hasil (diterima/ditolak).
3. Klik **"⏵ Step-by-Step"** untuk melihat animasi langkah demi langkah perpindahan state.
4. Gunakan tombol **Quick Test** di bagian bawah untuk menguji contoh string yang sudah disediakan.
5. Klik **"✕ Clear"** untuk mengosongkan.

### Fitur

| Fitur | Deskripsi |
|-------|-----------|
| **Diagram FSM interaktif** | Visualisasi diagram state pada canvas, dengan highlight state aktif |
| **Tabel transisi** | Menampilkan setiap langkah transisi secara detail |
| **Mode animasi** | Menjalankan simulasi langkah demi langkah dengan delay 600ms |
| **Quick Test** | Tombol contoh string (diterima dan ditolak) untuk pengujian cepat |
| **Validasi input** | Mendeteksi karakter tidak valid dan string kosong |

### Contoh Pengujian

| Input | Hasil | Alasan |
|-------|-------|--------|
| `1` | Diterima | Berakhir `1`, tidak ada `00` |
| `01` | Diterima | Berakhir `1`, tidak ada `00` |
| `101` | Diterima | Berakhir `1`, tidak ada `00` |
| `0101` | Diterima | Berakhir `1`, tidak ada `00` |
| `0` | Ditolak | Karakter terakhir bukan `1` |
| `00` | Ditolak | Mengandung substring `00` |
| `100` | Ditolak | Mengandung substring `00` |
| `010010` | Ditolak | Mengandung substring `00` |

---

## TugasW7_PDA.py - PDA Simulator

### Deskripsi

Program ini mensimulasikan **Pushdown Automata (PDA)** secara umum. Pengguna dapat memilih preset bahasa, mengedit definisi PDA, memasukkan string, lalu melihat apakah string tersebut **Accepted** atau **Rejected** melalui trace dan visualisasi interaktif.

Simulator menggunakan pencarian BFS sehingga dapat menangani **NPDA** dengan transisi nondeterministik dan transisi epsilon (`eps`).

### Preset PDA

| Preset | Contoh Accepted | Contoh Rejected |
|--------|-----------------|-----------------|
| `L = { a^n b^n / n >= 1 }` | `ab`, `aabb`, `aaabbb` | `aab`, `abb`, `ba` |
| `Balanced Parentheses` | `()`, `(())`, `(()())` | `(()`, `())(` |
| `PPT 7 - wXw^R` | `X`, `aXa`, `abXba` | `aXb`, `abXab`, `aba` |
| `Palindrome {a,b}` | `a`, `aa`, `aba`, `abba` | `ab`, `aab`, `abab` |

### Cara Menjalankan

```bash
python TugasW7_PDA.py
```

### Cara Self-Test

```bash
python TugasW7_PDA.py --test
```

### Fitur

| Fitur | Deskripsi |
|-------|-----------|
| **Preset PDA** | Memuat contoh PDA yang siap diuji |
| **Visualisasi interaktif** | Menampilkan graph state, transisi aktif, input tape, stack, dan operasi aktif sesuai preset yang dipilih |
| **Editor definisi** | Mengubah states, alphabet, stack alphabet, start state, final states, dan acceptance mode |
| **Editor transisi** | Menambah, menghapus, dan mengupdate transisi PDA |
| **Mode Analyze** | Menampilkan hasil akhir Accepted atau Rejected secara langsung |
| **Mode Step-by-step** | Menampilkan trace konfigurasi PDA satu per satu sambil menyorot visualisasi |
| **Validasi input** | Menolak simbol input yang tidak ada pada alphabet |
| **Batas simulasi** | Mencegah program macet akibat epsilon-loop |

---

## Cara Menjalankan (Umum)

```bash
# Clone / download repository, lalu masuk ke direktori
cd "Otomata"

# Jalankan Tokenizer Analyzer
python TugasW2.py

# Jalankan FSM Simulator
python TugasW3.py

# Jalankan PDA Simulator
python TugasW7_PDA.py
```

> **Catatan:** Program GUI (Tkinter) harus dijalankan di lingkungan yang mendukung tampilan grafis (desktop), bukan di terminal SSH tanpa X-forwarding.

---

## Struktur Direktori

```
Otomata/
├── README.md          ← Dokumentasi ini
├── TugasW2.py         ← Tokenizer / Lexical Analyzer
├── TugasW3.py         ← FSM Simulator
└── TugasW7_PDA.py    ← PDA Simulator
```

---

## Lisensi

Proyek ini dibuat untuk keperluan akademik mata kuliah Teori Bahasa & Automata di Institut Teknologi Sepuluh Nopember (ITS).
