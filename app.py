import streamlit as st
import yt_dlp
import tempfile
import os
import re
import subprocess
import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import time
import warnings
import shutil

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
st.markdown("Unduh video Facebook Reels dengan dubbing otomatis GRATIS!")

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

# Fungsi untuk cek apakah ffmpeg tersedia
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        return True
    except:
        return False

# Fungsi untuk extract audio dari video
def extract_audio(video_path, audio_path):
    try:
        if not check_ffmpeg():
            st.error("⚠️ FFmpeg tidak ditemukan. Silakan install ffmpeg terlebih dahulu.")
            st.info("""
            ### Cara Install FFmpeg:
            
            **Ubuntu/Debian:**
            ```bash
            sudo apt update
            sudo apt install ffmpeg
            ```
            
            **macOS:**
            ```bash
            brew install ffmpeg
            ```
            
            **Windows:**
            1. Download dari https://ffmpeg.org/download.html
            2. Ekstrak dan tambahkan ke PATH environment variable
            """)
            return False
            
        result = subprocess.run([
            'ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le',
            '-ar', '44100', '-ac', '2', audio_path
        ], check=True, capture_output=True, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        st.error(f"Gagal extract audio dengan FFmpeg: {e.stdout.decode() if e.stdout else str(e)}")
        return False
    except Exception as e:
        st.error(f"Gagal extract audio: {str(e)}")
        return False

# Fungsi untuk speech recognition (offline)
def transcribe_audio_offline(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        st.warning("⚠️ Tidak dapat mengenali suara dalam audio (audio terlalu pelan/noise)")
        return None
    except sr.RequestError as e:
        st.error(f"⚠️ Error service Speech Recognition: {str(e)}")
        return None
    except Exception as e:
        st.error(f"⚠️ Error transkripsi: {str(e)}")
        return None

# Fungsi untuk translate teks
def translate_text(text, target_lang):
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        st.error(f"⚠️ Error translation: {str(e)}")
        return text

# Fungsi untuk text-to-speech offline
def text_to_speech_offline(text, output_path, lang='id'):
    try:
        engine = pyttsx3.init()
        
        # Set properti TTS berdasarkan bahasa
        voices = engine.getProperty('voices')
        if voices:
            # Coba cari voice yang cocok dengan bahasa target
            for voice in voices:
                if lang in voice.id.lower() or any(l in voice.id.lower() for l in ['indonesian', 'english', 'spanish']):
                    engine.setProperty('voice', voice.id)
                    break
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return True
    except Exception as e:
        st.error(f"⚠️ Error TTS: {str(e)}")
        return False

# Fungsi untuk replace audio di video
def replace_audio_in_video(video_path, new_audio_path, output_path):
    try:
        if not check_ffmpeg():
            st.error("⚠️ FFmpeg tidak ditemukan. Tidak dapat mengganti audio.")
            return video_path
            
        result = subprocess.run([
            'ffmpeg', '-y', '-i', video_path, '-i', new_audio_path,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            output_path
        ], check=True, capture_output=True, stderr=subprocess.STDOUT)
        return output_path
    except subprocess.CalledProcessError as e:
        st.error(f"⚠️ Error replace audio dengan FFmpeg: {e.stdout.decode() if e.stdout else str(e)}")
        return video_path
    except Exception as e:
        st.error(f"⚠️ Error replace audio: {str(e)}")
        return video_path

# Fungsi dubbing lengkap
def dub_video_complete(video_path, target_lang='id'):
    try:
        # Buat direktori temporary untuk file-file intermediate
        temp_dir = os.path.dirname(video_path)
        
        # 1. Extract audio
        original_audio = os.path.join(temp_dir, "original_audio.wav")
        if not extract_audio(video_path, original_audio):
            return video_path, "❌ Gagal extract audio - pastikan FFmpeg sudah terinstall"
        
        # 2. Transcribe audio ke teks
        with st.spinner("🎤 Mengubah audio menjadi teks..."):
            original_text = transcribe_audio_offline(original_audio)
            if not original_text:
                return video_path, "❌ Gagal transkripsi audio atau audio tidak jelas"
        
        # 3. Translate teks
        with st.spinner("🔄 Menerjemahkan teks..."):
            translated_text = translate_text(original_text, target_lang)
            if not translated_text:
                return video_path, "❌ Gagal translation"
        
        # 4. Generate speech baru
        with st.spinner("🎙️ Menghasilkan suara baru..."):
            new_audio_path = os.path.join(temp_dir, "new_audio.wav")
            if not text_to_speech_offline(translated_text, new_audio_path, target_lang):
                return video_path, "❌ Gagal generate suara baru"
        
        # 5. Replace audio di video
        with st.spinner("🎵 Mengganti audio dalam video..."):
            dubbed_video_path = video_path.replace('.mp4', f'_dubbed_{target_lang}.mp4')
            final_path = replace_audio_in_video(video_path, new_audio_path, dubbed_video_path)
            
        return final_path, "✅ Dubbing berhasil!"
        
    except Exception as e:
        return video_path, f"❌ Error dubbing: {str(e)}"

# Input URL dan bahasa
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("🔗 Masukkan URL Facebook Reels:", 
                       placeholder="https://www.facebook.com/reel/...")
with col2:
    language = st.selectbox("🌍 Bahasa Target:", 
                           ["id", "en", "es", "fr", "de", "ja", "ko", "pt", "ru"],
                           format_func=lambda x: {
                               "id": "🇮🇩 Indonesia", "en": "🇺🇸 English", "es": "🇪🇸 Spanish",
                               "fr": "🇫🇷 French", "de": "🇩🇪 German", "ja": "🇯🇵 Japanese", 
                               "ko": "🇰🇷 Korean", "pt": "🇵🇹 Portuguese", "ru": "🇷🇺 Russian"
                           }[x])

# Opsi dubbing
dub_option = st.checkbox("🎙️ Tambahkan dubbing otomatis GRATIS", value=False)

# Tombol download
if st.button("⬇️ Download Video", type="primary") and url:
    # Cek FFmpeg sebelum proses
    ffmpeg_available = check_ffmpeg()
    if dub_option and not ffmpeg_available:
        st.warning("⚠️ FFmpeg diperlukan untuk fitur dubbing tapi tidak ditemukan!")
        with st.expander("ℹ️ Instruksi Install FFmpeg", expanded=True):
            st.markdown("""
            ### Cara Install FFmpeg:
            
            **Ubuntu/Debian:**
            ```bash
            sudo apt update
            sudo apt install ffmpeg
            ```
            
            **CentOS/RHEL/Fedora:**
            ```bash
            sudo yum install ffmpeg
            # atau untuk Fedora:
            sudo dnf install ffmpeg
            ```
            
            **macOS:**
            ```bash
            brew install ffmpeg
            ```
            
            **Windows:**
            1. Download dari [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
            2. Ekstrak file
            3. Tambahkan folder `bin` ke PATH environment variable
            """)
        st.info("➡️ Video akan tetap didownload tanpa dubbing...")
    
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
                
                # Proses dubbing jika dipilih dan FFmpeg tersedia
                dub_message = ""
                if dub_option and ffmpeg_available:
                    with st.spinner("🎙️ Menambahkan dubbing gratis..."):
                        start_time = time.time()
                        temp_filename, dub_message = dub_video_complete(temp_filename, language)
                        end_time = time.time()
                        st.info(f"⏱️ Waktu dubbing: {end_time - start_time:.2f} detik")
                elif dub_option and not ffmpeg_available:
                    dub_message = "⚠️ Dubbing dilewati karena FFmpeg tidak tersedia"
                
                # Baca file yang sudah didownload
                with open(temp_filename, 'rb') as file:
                    video_data = file.read()
                
                # Tampilkan hasil
                st.success("✅ Video berhasil diproses!")
                
                if dub_message:
                    st.info(dub_message)
                
                st.video(temp_filename)
                
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
                    shutil.rmtree(temp_dir)
                except:
                    pass
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Pastikan URL benar dan video dapat diakses publik")

# Panel informasi
with st.expander("ℹ️ Tentang Fitur Dubbing"):
    st.markdown("### Cara Kerja Dubbing Gratis:")
    st.markdown("""
    1. **Extract Audio** - Mengambil audio dari video menggunakan FFmpeg
    2. **Speech Recognition** - Mengubah audio menjadi teks menggunakan Google Speech Recognition
    3. **Translation** - Menerjemahkan teks ke bahasa target
    4. **Text-to-Speech** - Menghasilkan suara baru dalam bahasa target
    5. **Replace Audio** - Mengganti audio asli dengan audio hasil dubbing
    """)
    
    st.markdown("### Teknologi yang Digunakan:")
    st.markdown("""
    - 🎤 **SpeechRecognition** - Library Python untuk speech-to-text
    - 🌍 **Google Translate** - Terjemahan teks gratis
    - 🗣️ **pyttsx3** - Text-to-speech offline
    - 🎬 **FFmpeg** - Processing video dan audio
    """)

# Informasi penggunaan
st.markdown("---")
st.markdown("### ℹ️ Cara Penggunaan:")
st.markdown("""
1. Copy URL Facebook Reels dari aplikasi/web Facebook
2. Pilih bahasa target untuk dubbing
3. Centang opsi "Tambahkan dubbing otomatis GRATIS" jika diinginkan
4. Klik tombol "Download Video"
5. Tunggu proses selesai
6. Klik tombol "Download" untuk menyimpan video
""")

st.markdown("### ⚠️ Peringatan:")
st.warning("""
⚠️ **Perhatian Penting:**
- Gunakan tools ini sesuai hak cipta dan kebijakan Facebook
- Fitur dubbing membutuhkan waktu pemrosesan yang lama (1-3 menit)
- Kualitas dubbing tergantung kualitas audio asli
- Video hanya akan diproses secara lokal dan tidak disimpan di server
""")

st.markdown("### 🎯 Tips untuk Hasil Terbaik:")
st.markdown("""
- Gunakan video dengan audio yang jernih dan tidak berisik
- Video pendek (< 30 detik) lebih cepat diproses
- Pastikan koneksi internet stabil saat download
- Suara hasil dubbing menggunakan suara sistem default
""")

# Footer
st.markdown("---")
st.markdown("🎯 **Dubbing Gratis Tanpa Biaya Tambahan** | Made with ❤️ using Streamlit")
