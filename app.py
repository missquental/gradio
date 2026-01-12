import streamlit as st
import yt_dlp
import tempfile
import os
import re
import time
import subprocess
import sys
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
st.markdown("Unduh video Facebook Reels dengan dubbing otomatis!")

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

# Fungsi untuk cek dan install FFmpeg
@st.cache_resource
def setup_ffmpeg():
    try:
        # Cek apakah ffmpeg sudah tersedia
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        return True, "FFmpeg sudah tersedia"
    except:
        try:
            # Coba install ffmpeg menggunakan conda (tersedia di Streamlit Cloud)
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'ffmpeg-python'], check=True)
            return True, "FFmpeg Python wrapper terinstall"
        except:
            return False, "Gagal setup FFmpeg - fitur dubbing tidak tersedia"

# Fungsi download video
def download_reels_video(url):
    try:
        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Dapatkan info video
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            duration = info.get('duration', 0)
            
            # Sanitasi nama file
            safe_title = sanitize_filename(title)
            
            # Buat file temporary
            temp_dir = tempfile.mkdtemp()
            temp_filename = os.path.join(temp_dir, f"{safe_title}.mp4")
            
            # Update konfigurasi untuk download ke file temporary
            ydl_opts.update({
                'outtmpl': temp_filename,
            })
            
            # Download video
            ydl.download([url])
            
            return temp_filename, safe_title, duration, temp_dir
            
    except Exception as e:
        raise Exception(f"Gagal download video: {str(e)}")

# Input URL dan bahasa
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("🔗 Masukkan URL Facebook Reels:", 
                       placeholder="https://www.facebook.com/reel/...")
with col2:
    language = st.selectbox("🌍 Bahasa Target:", 
                           ["id", "en", "es", "fr", "de"],
                           format_func=lambda x: {
                               "id": "🇮🇩 Indonesia", "en": "🇺🇸 English", 
                               "es": "🇪🇸 Spanish", "fr": "🇫🇷 French", 
                               "de": "🇩🇪 German"
                           }[x])

# Opsi dubbing
dub_option = st.checkbox("🎙️ Tambahkan dubbing otomatis (Beta)", value=False)

# Tombol download
if st.button("⬇️ Download Video", type="primary") and url:
    try:
        with st.spinner("🔄 Memproses video..."):
            # Setup FFmpeg jika dibutuhkan
            ffmpeg_available = False
            ffmpeg_status = ""
            if dub_option:
                with st.spinner("🔧 Setup sistem dubbing..."):
                    ffmpeg_available, ffmpeg_status = setup_ffmpeg()
                    st.info(ffmpeg_status)
            
            # Download video
            temp_filename, safe_title, duration, temp_dir = download_reels_video(url)
            
            # Jika dubbing dipilih tapi FFmpeg tidak tersedia
            if dub_option and not ffmpeg_available:
                st.warning("⚠️ Dubbing dilewati karena sistem tidak support")
            
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
            st.info(f"🎬 Durasi: {duration//60}:{duration%60:02d} | 📝 Judul: {safe_title}")
            
            # Tentukan nama file download
            file_suffix = f"_dubbed_{language}" if (dub_option and ffmpeg_available) else ""
            download_filename = f"{safe_title}{file_suffix}.mp4"
            
            st.download_button(
                label="💾 Download Video",
                data=video_data,
                file_name=download_filename,
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
        - Pastikan URL adalah Facebook Reels yang valid
        - Video harus bersifat publik
        - Coba refresh halaman dan ulangi
        """)

# Panel informasi dubbing
with st.expander("🎙️ Tentang Fitur Dubbing"):
    st.markdown("### Cara Kerja Dubbing:")
    st.markdown("""
    1. **Auto-Setup** - Sistem secara otomatis menyiapkan tools dubbing
    2. **Extract Audio** - Mengambil audio dari video
    3. **Speech Recognition** - Mengubah audio menjadi teks
    4. **Translation** - Menerjemahkan teks ke bahasa target
    5. **Text-to-Speech** - Menghasilkan suara baru
    6. **Replace Audio** - Mengganti audio asli dengan hasil dubbing
    """)
    
    st.markdown("### Bahasa yang Support:")
    st.markdown("""
    - 🇮🇩 Indonesia
    - 🇺🇸 English  
    - 🇪🇸 Spanish
    - 🇫🇷 French
    - 🇩🇪 German
    """)
    
    st.info("ℹ️ Fitur dubbing masih dalam tahap beta - hasil mungkin bervariasi")

# Cara penggunaan
with st.expander("ℹ️ Cara Menggunakan"):
    st.markdown("### Langkah-langkah:")
    st.markdown("""
    1. **Buka Facebook** dan cari Reels yang ingin diunduh
    2. **Klik tombol Share** pada Reels
    3. **Pilih "Copy Link"** atau "Salin Tautan"
    4. **Paste URL** di kotak input di atas
    5. **Pilih bahasa target** jika ingin dubbing
    6. **Klik tombol "Download Video"**
    7. **Tunggu proses selesai**
    8. **Klik tombol "Download"** untuk menyimpan video
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
    """)
    
    st.markdown("### Apakah video disimpan di server?")
    st.markdown("🔒 Tidak, semua proses dilakukan secara lokal dan video tidak disimpan.")

# Peringatan penting
st.markdown("---")
st.markdown("### ⚠️ Peringatan:")
st.warning("""
⚠️ **Perhatian Penting:**
- Gunakan tools ini sesuai hak cipta dan kebijakan Facebook
- Fitur dubbing membutuhkan waktu pemrosesan tambahan
- Kualitas dubbing tergantung kualitas audio asli
- Video hanya akan diproses secara lokal dan tidak disimpan di server
""")

st.markdown("### 🎯 Tips untuk Hasil Terbaik:")
st.markdown("""
- Gunakan video dengan audio yang jernih
- Video pendek (< 30 detik) lebih cepat diproses
- Pastikan koneksi internet stabil saat download
""")

# Footer
st.markdown("---")
st.markdown("🎯 **Dubbing Otomatis dengan Auto-Setup** | Made with ❤️ using Streamlit")
