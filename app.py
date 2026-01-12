import streamlit as st
import yt_dlp
import tempfile
import os
import re
import time
import warnings
from io import BytesIO

# Suppress warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Facebook Reels Downloader",
    page_icon="🎥",
    layout="centered"
)

# Judul aplikasi
st.title("📥 Facebook Reels Downloader")
st.markdown("Unduh video Facebook Reels dengan mudah!")

# Fungsi untuk sanitasi nama file
def sanitize_filename(filename):
    # Hapus karakter ilegal
    filename = re.sub(r'[^\w\-_\. ]', '', filename)
    # Batasi panjang nama file (150 karakter untuk aman)
    if len(filename) > 150:
        filename = filename[:150]
    # Ganti spasi dengan underscore
    filename = filename.replace(' ', '_')
    return filename or "video"  # default nama jika kosong

# Fungsi untuk validasi URL Facebook
def validate_facebook_url(url):
    facebook_patterns = [
        r'facebook\.com/reel/',
        r'facebook\.com/watch/',
        r'fb\.watch/',
        r'facebook\.com/.*/videos/'
    ]
    
    for pattern in facebook_patterns:
        if re.search(pattern, url):
            return True
    return False

# Fungsi download video dengan error handling yang lebih baik
def download_reels_video(url):
    try:
        # Validasi URL dulu
        if not validate_facebook_url(url):
            raise Exception("URL tidak valid. Harus berupa URL Facebook Reels/Video")
        
        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': False,
            'verbose': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Dapatkan info video
                info = ydl.extract_info(url, download=False)
                
                # Debug info
                if not isinstance(info, dict):
                    raise Exception("Format info tidak valid dari yt-dlp")
                
                # Ambil informasi dasar
                title = info.get('title', 'video') if isinstance(info, dict) else 'video'
                duration = info.get('duration', 0) if isinstance(info, dict) else 0
                
                # Sanitasi nama file
                safe_title = sanitize_filename(str(title))
                
                # Buat file temporary
                temp_dir = tempfile.mkdtemp()
                temp_filename = os.path.join(temp_dir, f"{safe_title}.mp4")
                
                # Update konfigurasi untuk download ke file temporary
                ydl_opts.update({
                    'outtmpl': temp_filename,
                })
                
                # Download video
                ydl_download = yt_dlp.YoutubeDL(ydl_opts)
                ydl_download.download([url])
                
                return temp_filename, safe_title, int(duration), temp_dir
                
            except Exception as extract_error:
                # Coba format alternatif
                ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]'
                try:
                    ydl_alt = yt_dlp.YoutubeDL(ydl_opts)
                    ydl_alt.download([url])
                    return temp_filename, safe_title, int(duration), temp_dir
                except:
                    raise Exception(f"Gagal ekstrak info video: {str(extract_error)}")
            
    except Exception as e:
        raise Exception(f"Gagal download video: {str(e)}")

# Input URL
url = st.text_input("🔗 Masukkan URL Facebook Reels:", 
                   placeholder="https://www.facebook.com/reel/...")

# Tombol download
if st.button("⬇️ Download Video", type="primary") and url:
    try:
        with st.spinner("🔄 Memproses video..."):
            # Download video
            temp_filename, safe_title, duration, temp_dir = download_reels_video(url)
            
            # Baca file yang sudah didownload
            with open(temp_filename, 'rb') as file:
                video_data = file.read()
            
            # Tampilkan hasil
            st.success("✅ Video berhasil diproses!")
            
            # Preview video jika ukuran memungkinkan
            if len(video_data) < 50 * 1024 * 1024:  # < 50MB
                st.video(temp_filename)
            else:
                st.info("📹 Video terlalu besar untuk preview")
            
            # Info video
            if duration > 0:
                st.info(f"🎬 Durasi: {duration//60}:{duration%60:02d} | 📝 Judul: {safe_title}")
            else:
                st.info(f"📝 Judul: {safe_title}")
            
            st.download_button(
                label="💾 Download Video",
                data=video_data,
                file_name=f"{safe_title}.mp4",
                mime="video/mp4"
            )
            
            # Bersihkan file temporary
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("""
        💡 Tips mengatasi error:
        - Pastikan URL adalah Facebook Reels/Video yang valid dan publik
        - Coba refresh halaman dan ulangi
        - Gunakan URL langsung dari browser (bukan dari aplikasi share)
        - Video harus dapat diputar secara publik
        
        📝 Contoh URL yang valid:
        • https://www.facebook.com/reel/1234567890123456/
        • https://www.facebook.com/username/videos/1234567890123456/
        """)

# Panel informasi
with st.expander("ℹ️ Cara Menggunakan"):
    st.markdown("### Langkah-langkah:")
    st.markdown("""
    1. **Buka Facebook** di browser dan cari Reels/Video yang ingin diunduh
    2. **Klik tombol Share** pada video
    3. **Pilih "Copy Link"** atau salin URL dari address bar
    4. **Paste URL** di kotak input di atas
    5. **Klik tombol "Download Video"**
    6. **Tunggu proses selesai**
    7. **Klik tombol "Download"** untuk menyimpan video
    """)
    
    st.markdown("### Contoh URL yang Valid:")
    st.code("""
https://www.facebook.com/reel/1234567890123456/
https://www.facebook.com/username/videos/1234567890123456/
https://fb.watch/abc123/
    """, language="text")

# Troubleshooting
with st.expander("🔧 Troubleshooting"):
    st.markdown("### Video Tidak Bisa Diunduh?")
    st.markdown("""
    ✅ **Pastikan:**
    - Video bersifat publik (tidak privat)
    - URL adalah video Facebook yang valid
    - Video dapat diputar di browser
    
    ❌ **Tidak bisa untuk:**
    - Video live streaming
    - Video yang dilindungi DRM
    - Video yang dihapus
    - Video dari grup privat
    """)
    
    st.markdown("### Error Umum:")
    st.markdown("""
    • **"string indices must be integers"** - Biasanya karena URL tidak valid
    • **"Unable to extract"** - Video tidak dapat diakses publik
    • **"No Media found"** - Video sudah dihapus atau diprivat
    """)

# FAQ
with st.expander("❓ Pertanyaan Umum"):
    st.markdown("### Apakah ini legal?")
    st.markdown("✅ Ya, selama video bersifat publik dan digunakan untuk keperluan pribadi.")
    
    st.markdown("### Kenapa video tidak bisa diunduh?")
    st.markdown("""
    ❌ Kemungkinan penyebab:
    - Video bersifat privat
    - Video dilindungi hak cipta
    - URL tidak valid
    - Video dihapus oleh pengguna
    - Video memerlukan login
    """)
    
    st.markdown("### Apakah video disimpan di server?")
    st.markdown("🔒 Tidak, semua proses dilakukan secara lokal dan video tidak disimpan.")

# Peringatan penting
st.markdown("---")
st.markdown("### ⚠️ Peringatan:")
st.warning("""
⚠️ **Perhatian Penting:**
- Gunakan tools ini sesuai hak cipta dan kebijakan Facebook
- Video hanya akan diproses secara lokal dan tidak disimpan di server
- Beberapa video mungkin tidak bisa diunduh karena pembatasan akses
- Jangan gunakan untuk konten yang dilindungi hak cipta
""")

st.markdown("### 🎯 Tips untuk Hasil Terbaik:")
st.markdown("""
- Gunakan URL video yang bersifat publik
- Video dengan durasi pendek lebih cepat diproses
- Pastikan koneksi internet stabil saat download
- Coba beberapa kali jika gagal pertama kali
""")

# Footer
st.markdown("---")
st.markdown(" Made with ❤️ using Streamlit | Facebook Reels Downloader")
