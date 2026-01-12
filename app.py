import streamlit as st
import yt_dlp
import tempfile
import os
import re
import time
from io import BytesIO
import warnings

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

# Fungsi untuk download video dengan yt-dlp
def download_video(url):
    try:
        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '-',  # Output ke stdout
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Dapatkan info video dulu
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            
            # Sanitasi nama file
            safe_title = sanitize_filename(title)
            
            # Download video ke memory
            video_buffer = BytesIO()
            
            # Update config untuk download ke buffer
            ydl_opts.update({
                'outtmpl': '-'  # Output ke stdout
            })
            
            # Download video
            ydl.download([url])
            
            return video_buffer.getvalue(), safe_title, "✅ Video berhasil diproses!"
            
    except Exception as e:
        raise Exception(f"Gagal download video: {str(e)}")

# Input URL
url = st.text_input("🔗 Masukkan URL Facebook Reels:", 
                   placeholder="https://www.facebook.com/reel/...")

# Tombol download
if st.button("⬇️ Download Video", type="primary") and url:
    try:
        with st.spinner("🔄 Memproses video..."):
            # Konfigurasi yt-dlp
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Dapatkan info video
                with st.spinner("🔍 Mengambil informasi video..."):
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'video')
                    duration = info.get('duration', 'N/A')
                    
                # Sanitasi nama file
                safe_title = sanitize_filename(title)
                
                # Buat file temporary
                temp_dir = tempfile.mkdtemp()
                temp_filename = os.path.join(temp_dir, f"{safe_title}.mp4")
                
                # Update konfigurasi untuk download ke file temporary
                ydl_opts.update({
                    'outtmpl': temp_filename,
                })
                
                with st.spinner(f"📥 Downloading video... ({duration}s)"):
                    ydl.download([url])
                
                # Baca file yang sudah didownload
                with open(temp_filename, 'rb') as file:
                    video_data = file.read()
                
                # Tampilkan hasil
                st.success("✅ Video berhasil diproses!")
                
                # Preview video jika ukuran memungkinkan
                if len(video_data) < 50 * 1024 * 1024:  # < 50MB
                    st.video(temp_filename)
                else:
                    st.info("📹 Video terlalu besar untuk preview (tetap bisa didownload)")
                
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
        - Pastikan URL adalah Facebook Reels yang valid
        - Video harus bersifat publik
        - Coba refresh halaman dan ulangi
        - Gunakan URL langsung dari browser, bukan dari share
        """)

# Panel informasi
with st.expander("ℹ️ Cara Menggunakan"):
    st.markdown("### Langkah-langkah:")
    st.markdown("""
    1. **Buka Facebook** dan cari Reels yang ingin diunduh
    2. **Klik tombol Share** pada Reels
    3. **Pilih "Copy Link"** atau "Salin Tautan"
    4. **Paste URL** di kotak input di atas
    5. **Klik tombol "Download Video"**
    6. **Tunggu proses selesai**
    7. **Klik tombol "Download"** untuk menyimpan video
    """)
    
    st.markdown("### Contoh URL yang Valid:")
    st.code("https://www.facebook.com/reel/1234567890123456/", language="text")

# FAQ Section
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

# Informasi sistem
st.markdown("---")
st.markdown("### ⚠️ Peringatan:")
st.warning("""
- Gunakan tools ini sesuai hak cipta dan kebijakan Facebook
- Video hanya akan diproses secara lokal dan tidak disimpan di server
- Beberapa video mungkin tidak bisa diunduh karena pembatasan akses
""")

st.markdown("### 🎯 Tips:")
st.markdown("""
- Pastikan URL adalah Reels Facebook yang publik
- Video dengan durasi pendek biasanya lebih cepat diproses
- Gunakan koneksi internet yang stabil untuk download
""")

# Footer
st.markdown("---")
st.markdown(" Made with ❤️ using Streamlit | Facebook Reels Downloader")
