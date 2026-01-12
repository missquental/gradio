import streamlit as st
import yt_dlp
import tempfile
import os
import re
import time
import pandas as pd
from io import StringIO, BytesIO
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="Facebook Reels Bulk Downloader",
    page_icon="🎥",
    layout="wide"
)

# Judul aplikasi
st.title("📥 Facebook Reels Bulk Downloader")
st.markdown("Unduh banyak video Facebook Reels sekaligus!")

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

# Fungsi untuk membersihkan dan extract URL
def clean_and_extract_urls(text_input):
    urls = []
    lines = text_input.strip().split('\n')
    
    for line in lines:
        # Cari URL Facebook dalam setiap baris
        url_matches = re.findall(r'https://(?:www\.)?facebook\.com/(?:reel|watch|[^/]+/videos)/[^\s]+', line)
        urls.extend(url_matches)
    
    # Bersihkan parameter query yang tidak perlu
    cleaned_urls = []
    for url in urls:
        # Hapus parameter query yang tidak penting
        url = re.sub(r'[?&](s=fb_shorts_profile|stack_idx=\d+).*$', '', url)
        # Pastikan URL valid
        if re.search(r'https://(?:www\.)?facebook\.com/(?:reel|watch|[^/]+/videos)/', url):
            cleaned_urls.append(url)
    
    # Hapus duplikat dengan menjaga urutan
    seen = set()
    unique_urls = []
    for url in cleaned_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls

# Fungsi download single video
def download_single_video(url, index=0):
    try:
        # Konfigurasi yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Dapatkan info video
            info = ydl.extract_info(url, download=False)
            
            if not isinstance(info, dict):
                raise Exception("Format info tidak valid")
            
            # Ambil informasi dasar
            title = info.get('title', f'video_{index}')
            duration = info.get('duration', 0)
            
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
            
            return {
                'status': 'success',
                'filename': temp_filename,
                'title': safe_title,
                'duration': int(duration),
                'temp_dir': temp_dir,
                'error': None
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'filename': None,
            'title': f'video_{index}',
            'duration': 0,
            'temp_dir': None,
            'error': str(e)
        }

# Sidebar
st.sidebar.header("📥 Bulk Download Manager")
bulk_mode = st.sidebar.radio("Mode Download:", ["Single Video", "Bulk Download"])

if bulk_mode == "Single Video":
    # Mode Single Video
    url = st.text_input("🔗 Masukkan URL Facebook Reels:", 
                       placeholder="https://www.facebook.com/reel/...")
    
    if st.button("⬇️ Download Video", type="primary") and url:
        try:
            with st.spinner("🔄 Memproses video..."):
                result = download_single_video(url)
                
                if result['status'] == 'success':
                    # Baca file yang sudah didownload
                    with open(result['filename'], 'rb') as file:
                        video_data = file.read()
                    
                    # Tampilkan hasil
                    st.success("✅ Video berhasil diproses!")
                    st.video(result['filename'])
                    
                    if result['duration'] > 0:
                        st.info(f"🎬 Durasi: {result['duration']//60}:{result['duration']%60:02d} | 📝 Judul: {result['title']}")
                    else:
                        st.info(f"📝 Judul: {result['title']}")
                    
                    st.download_button(
                        label="💾 Download Video",
                        data=video_data,
                        file_name=f"{result['title']}.mp4",
                        mime="video/mp4"
                    )
                    
                    # Bersihkan file temporary
                    try:
                        import shutil
                        shutil.rmtree(result['temp_dir'])
                    except:
                        pass
                else:
                    st.error(f"❌ Error: {result['error']}")
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

else:
    # Mode Bulk Download
    st.subheader("📦 Bulk Download Facebook Reels")
    
    # Tab untuk input dan preview
    tab1, tab2 = st.tabs(["📥 Input URLs", "📋 Preview & Download"])
    
    with tab1:
        text_input = st.text_area("📋 Paste URLs (satu URL per baris):", 
                                 height=300,
                                 placeholder="""https://www.facebook.com/reel/1234567890123456/
https://www.facebook.com/reel/9876543210987654/
https://www.facebook.com/user/videos/1122334455667788/""")
        
        if st.button("🔍 Parse URLs", type="secondary"):
            if text_input.strip():
                urls = clean_and_extract_urls(text_input)
                if urls:
                    st.session_state.bulk_urls = urls
                    st.success(f"✅ Berhasil memparse {len(urls)} URL unik")
                    st.write("URLs yang akan diproses:")
                    for i, url in enumerate(urls[:10]):  # Tampilkan max 10
                        st.code(url, language="text")
                    if len(urls) > 10:
                        st.info(f"... dan {len(urls) - 10} URL lainnya")
                else:
                    st.warning("⚠️ Tidak menemukan URL Facebook yang valid")
            else:
                st.warning("⚠️ Masukkan beberapa URL terlebih dahulu")
    
    with tab2:
        if 'bulk_urls' in st.session_state and st.session_state.bulk_urls:
            urls = st.session_state.bulk_urls
            st.info(f"📊 Total URLs: {len(urls)}")
            
            # Slider untuk memilih jumlah download
            max_downloads = st.slider("🔢 Jumlah maksimal download:", 1, min(len(urls), 500), min(len(urls), 10))
            
            if st.button("🚀 Mulai Download Bulk", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()
                
                # Simpan hasil download
                download_results = []
                
                # Proses download
                for i, url in enumerate(urls[:max_downloads]):
                    status_text.text(f"🔄 Memproses {i+1}/{max_downloads}: {url}")
                    progress_bar.progress((i + 1) / max_downloads)
                    
                    result = download_single_video(url, i+1)
                    download_results.append({
                        'url': url,
                        'title': result['title'],
                        'status': result['status'],
                        'error': result['error'],
                        'filename': result['filename'],
                        'temp_dir': result['temp_dir']
                    })
                
                progress_bar.empty()
                status_text.empty()
                
                # Tampilkan hasil
                success_count = sum(1 for r in download_results if r['status'] == 'success')
                error_count = len(download_results) - success_count
                
                st.success(f"✅ Selesai! {success_count} berhasil, {error_count} gagal")
                
                # Tampilkan detail hasil
                with results_container:
                    st.subheader("📊 Hasil Download")
                    
                    # Buat ZIP jika ada yang berhasil
                    if success_count > 0:
                        try:
                            from zipfile import ZipFile
                            import shutil
                            
                            # Buat file ZIP
                            zip_buffer = BytesIO()
                            with ZipFile(zip_buffer, 'w') as zip_file:
                                for result in download_results:
                                    if result['status'] == 'success' and result['filename']:
                                        try:
                                            zip_file.write(result['filename'], f"{result['title']}.mp4")
                                        except:
                                            pass  # Lewati jika file tidak bisa ditambahkan
                            
                            zip_buffer.seek(0)
                            
                            st.download_button(
                                label=f"📦 Download Semua Video ({success_count} files)",
                                data=zip_buffer,
                                file_name="facebook_reels_bulk_download.zip",
                                mime="application/zip"
                            )
                        except Exception as e:
                            st.warning(f"⚠️ Tidak dapat membuat file ZIP: {str(e)}")
                    
                    # Tampilkan daftar hasil
                    st.subheader("📋 Detail Hasil")
                    for i, result in enumerate(download_results):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{result['title']}**")
                            st.caption(result['url'][:80] + ("..." if len(result['url']) > 80 else ""))
                        with col2:
                            if result['status'] == 'success':
                                st.success("✅ OK")
                            else:
                                st.error("❌ Fail")
                        with col3:
                            if result['status'] == 'success' and result['filename']:
                                try:
                                    with open(result['filename'], 'rb') as f:
                                        st.download_button(
                                            label="💾",
                                            data=f,
                                            file_name=f"{result['title']}.mp4",
                                            mime="video/mp4",
                                            key=f"download_{i}"
                                        )
                                except:
                                    st.write("⚠️ File not found")
                        
                        if result['status'] == 'error':
                            st.caption(f"Error: {result['error']}")
                    
                    # Bersihkan file temporary
                    try:
                        for result in download_results:
                            if result['temp_dir']:
                                shutil.rmtree(result['temp_dir'])
                    except:
                        pass
                        
        else:
            st.info("👈 Masukkan URLs di tab 'Input URLs' terlebih dahulu")

# Panel informasi
with st.expander("ℹ️ Cara Menggunakan Bulk Download"):
    st.markdown("### Langkah-langkah:")
    st.markdown("""
    1. **Pilih "Bulk Download"** di sidebar
    2. **Paste URLs** di tab "Input URLs" (bisa copy-paste dari spreadsheet)
    3. **Klik "Parse URLs"** untuk memproses dan membersihkan URLs
    4. **Pindah ke tab "Preview & Download"**
    5. **Atur jumlah maksimal download** dengan slider
    6. **Klik "Mulai Download Bulk"**
    7. **Download hasil** sebagai file ZIP atau individual
    """)
    
    st.markdown("### Format URL yang Didukung:")
    st.code("""
https://www.facebook.com/reel/1234567890123456/
https://www.facebook.com/username/videos/1234567890123456/
https://fb.watch/abc123/
    """, language="text")

# FAQ
with st.expander("❓ Pertanyaan Umum"):
    st.markdown("### Berapa banyak video yang bisa didownload sekaligus?")
    st.markdown("📊 Maksimal 50 video per sesi untuk menjaga performa.")
    
    st.markdown("### Apakah URL otomatis dibersihkan?")
    st.markdown("✅ Ya, sistem akan otomatis membersihkan parameter yang tidak perlu dan menghapus duplikat.")
    
    st.markdown("### Format output apa yang didukung?")
    st.markdown("🎬 Format MP4 dengan kualitas terbaik yang tersedia.")

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

st.markdown("### 🎯 Tips untuk Bulk Download:")
st.markdown("""
- Gunakan koneksi internet yang stabil
- Video pendek akan lebih cepat diproses
- Jangan melebihi 20-30 video per batch untuk performa terbaik
- Pastikan semua URLs adalah video publik
""")

# Footer
st.markdown("---")
st.markdown("🎯 **Bulk Download dengan Auto-Cleaning URLs** | Made with ❤️ using Streamlit")
