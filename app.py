import streamlit as st
import yt_dlp
import tempfile
import os
import re

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
    # Batasi panjang nama file (200 karakter untuk aman)
    if len(filename) > 200:
        filename = filename[:200]
    # Ganti spasi dengan underscore
    filename = filename.replace(' ', '_')
    return filename or "video"  # default nama jika kosong

# Input URL dan bahasa
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("🔗 Masukkan URL Facebook Reels:", 
                       placeholder="https://www.facebook.com/reel/...")
with col2:
    language = st.selectbox("🌍 Bahasa Target:", 
                           ["id", "en", "es", "fr", "de", "ja", "ko", "pt", "ru", "zh"],
                           format_func=lambda x: {
                               "id": "Indonesia", "en": "English", "es": "Spanish",
                               "fr": "French", "de": "German", "ja": "Japanese", 
                               "ko": "Korean", "pt": "Portuguese", "ru": "Russian",
                               "zh": "Chinese"
                           }[x])

# Opsi dubbing (placeholder untuk fitur future)
dub_option = st.checkbox("🎙️ Tambahkan dubbing otomatis (Coming Soon)", value=False, disabled=True)
st.caption("ℹ️ Fitur dubbing memerlukan setup API terpisah")

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
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video')
                
                # Sanitasi nama file
                safe_title = sanitize_filename(title)
                
                # Buat file temporary
                temp_dir = tempfile.mkdtemp()
                temp_filename = os.path.join(temp_dir, f"{safe_title}.mp4")
                
                # Update konfigurasi untuk download ke file temporary
                ydl_opts.update({
                    'outtmpl': temp_filename,
                })
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    ydl_download.download([url])
                
                # Baca file yang sudah didownload
                with open(temp_filename, 'rb') as file:
                    video_data = file.read()
                
                # Tampilkan hasil
                st.success("✅ Video berhasil diproses!")
                
                if dub_option:
                    st.info("⚠️ Fitur dubbing akan tersedia dalam update berikutnya")
                
                st.video(temp_filename)
                
                st.download_button(
                    label="💾 Download Video",
                    data=video_data,
                    file_name=f"{safe_title}_{language}.mp4",
                    mime="video/mp4"
                )
                
                # Bersihkan file temporary
                try:
                    os.remove(temp_filename)
                    os.rmdir(temp_dir)
                except:
                    pass
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Pastikan URL benar dan video dapat diakses publik")

# Bagian penjelasan fitur dubbing
with st.expander("🎙️ Tentang Fitur Dubbing Otomatis"):
    st.markdown("### Fitur Dubbing akan mencakup:")
    st.markdown("""
    1. **Speech Recognition**: Mengubah audio menjadi teks
    2. **Translation**: Menerjemahkan teks ke bahasa target
    3. **Voice Synthesis**: Menghasilkan suara baru dalam bahasa target
    4. **Audio Replacement**: Mengganti audio asli dengan dubbing baru
    """)
    
    st.markdown("### Teknologi yang akan digunakan:")
    st.markdown("""
    - Google Cloud Speech-to-Text API
    - Google Translate API  
    - Google Text-to-Speech API
    - FFmpeg untuk processing video
    """)

# Informasi penggunaan
st.markdown("---")
st.markdown("### ℹ️ Cara Penggunaan:")
st.markdown("""
1. Copy URL Facebook Reels dari aplikasi/web Facebook
2. Pilih bahasa target (untuk penamaan file)
3. Klik tombol "Download Video"
4. Tunggu proses selesai
5. Klik tombol "Download" untuk menyimpan video
""")

st.markdown("### ⚠️ Peringatan:")
st.warning("""
- Gunakan tools ini sesuai hak cipta dan kebijakan Facebook
- Beberapa video mungkin tidak bisa diunduh karena pembatasan akses
- Video hanya akan diproses secara lokal dan tidak disimpan di server
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
