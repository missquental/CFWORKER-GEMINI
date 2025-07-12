# 🚀 Streamlit Blog Management + Cloudflare Worker

Sistem manajemen blog lengkap yang menggunakan Streamlit sebagai dashboard admin dan Cloudflare Worker sebagai hosting blog.

## ✨ Fitur

### Dashboard Streamlit
- 🔐 **Autentikasi Cloudflare** - Input Account ID dan API Token
- 📝 **Manajemen Post** - Tambah, edit, hapus postingan
- 🚀 **Deploy Otomatis** - Deploy ke Cloudflare Worker dengan satu klik
- 📤 **Export/Import** - Backup dan restore data postingan
- 📱 **Responsive UI** - Interface yang mobile-friendly

### Blog Cloudflare Worker
- ⚡ **Super Cepat** - Hosting di edge network Cloudflare
- 🎨 **Design Modern** - UI yang clean dan professional
- 📱 **Responsive** - Optimal di semua device
- 🔍 **SEO Friendly** - Meta tags dan struktur yang proper

## 🛠️ Setup

### 1. Persiapan Cloudflare
1. Daftar/login ke [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Catat **Account ID** (ada di sidebar kanan bawah)
3. Buat **API Token** di [Profile > API Tokens](https://dash.cloudflare.com/profile/api-tokens)
   - Template: "Custom token"
   - Permissions: 
     - `Account - Cloudflare Workers:Edit`
     - `Zone - Zone Settings:Read` (opsional)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard
```bash
streamlit run streamlit_dashboard.py
```

### 4. Konfigurasi
1. Buka dashboard Streamlit
2. Masukkan Account ID dan API Token Cloudflare
3. Pilih subdomain untuk worker (misal: `blog-namaid`)
4. Klik "Connect"

## 📋 Cara Penggunaan

### Mengelola Postingan
1. Pilih menu "📋 Kelola Post"
2. Klik "➕ Tambah Post Baru"
3. Isi form dengan detail postingan:
   - **Judul**: Judul postingan
   - **ID Post**: Identifier unik (contoh: `tutorial-react`)
   - **Penulis**: Nama penulis
   - **Tanggal**: Tanggal posting
   - **Excerpt**: Ringkasan singkat
   - **Konten**: Isi postingan (mendukung HTML)
4. Klik "💾 Simpan Post"

### Deploy ke Cloudflare Worker
1. Pilih menu "🚀 Deploy"
2. Review daftar postingan yang akan di-deploy
3. Klik "🚀 Deploy Sekarang"
4. Tunggu hingga proses selesai
5. Blog akan live di `https://[subdomain].workers.dev`

### Backup Data
1. Pilih menu "⚙️ Settings"
2. Klik "📥 Export Posts" untuk download backup
3. Gunakan "📤 Import Posts" untuk restore data

## 🏗️ Struktur File

```
├── streamlit_dashboard.py  # Dashboard utama Streamlit
├── worker.js              # Template Cloudflare Worker
├── wrangler.toml          # Konfigurasi Cloudflare
├── requirements.txt       # Dependencies Python
└── README.md             # Dokumentasi
```

## 🎨 Kustomisasi

### Mengubah Tema Blog
Edit bagian CSS di dalam `worker.js`:
```javascript
const HTML_TEMPLATE = `
<style>
  /* Custom CSS di sini */
</style>
`;
```

### Menambah Fitur Worker
Edit fungsi `handleRequest()` di `worker.js` untuk menambah endpoint baru.

### Kustomisasi Dashboard
Modifikasi `streamlit_dashboard.py` untuk menambah fitur admin.

## 🔧 API Endpoints

Blog worker menyediakan endpoint berikut:

- `GET /` - Halaman beranda dengan daftar post
- `GET /post/{id}` - Halaman detail post
- `GET /api/posts` - API untuk mendapatkan semua posts (JSON)

## 🚨 Troubleshooting

### Error "Invalid API Token"
- Pastikan API Token memiliki permission `Cloudflare Workers:Edit`
- Cek Account ID sudah benar

### Worker tidak bisa diakses
- Tunggu 1-2 menit setelah deploy untuk propagasi DNS
- Pastikan subdomain belum digunakan

### Posts tidak muncul
- Cek format JSON posts di dashboard
- Pastikan deploy berhasil tanpa error

## 📝 Tips

1. **ID Post** harus unik dan URL-friendly (contoh: `tutorial-react-hooks`)
2. **Konten** mendukung HTML untuk formatting (gunakan `<br>` untuk line break)
3. **Deploy ulang** setiap kali ada perubahan postingan
4. **Backup** data secara berkala menggunakan fitur export

## 🤝 Kontribusi

Feel free untuk fork, modify, dan submit pull request untuk improvement!

## 📄 License

MIT License - Feel free to use and modify as needed.

---

Dibuat dengan ❤️ menggunakan Streamlit dan Cloudflare Worker
