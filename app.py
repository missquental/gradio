import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import textwrap

# --------------------------------------------------
# Contoh fungsi generate_image
# Ganti isi fungsi ini dengan model AI kamu
# --------------------------------------------------
def generate_image(prompt: str):
    img = Image.new("RGB", (512, 512), color="white")
    draw = ImageDraw.Draw(img)
    
    # Membungkus teks agar tidak keluar dari gambar
    wrapped_text = textwrap.fill(prompt, width=30)
    
    # Mencoba menggunakan font default atau fallback ke font sederhana
    try:
        # Di beberapa sistem mungkin tidak ada font default
        draw.text((20, 20), wrapped_text, fill="black")
    except:
        # Fallback jika font tidak tersedia
        draw.text((20, 20), wrapped_text, fill="black")
    
    return img

# --------------------------------------------------
# Streamlit App
# --------------------------------------------------
st.set_page_config(page_title="🎨 Your Fancy Image Generator", layout="wide")

# Header dengan markdown
st.markdown("# 🎨 Your Fancy Image Generator")
st.markdown("---")

# Membuat layout dengan kolom
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Prompt Input")
    prompt = st.text_area(
        "Masukkan deskripsi gambar:",
        placeholder="Contoh: A beautiful sunset over mountains...",
        height=100,
        key="prompt_input"
    )
    
    generate_btn = st.button(
        "✨ Generate Image",
        type="primary",
        use_container_width=True
    )
    
    # Info box
    st.info("💡 Masukkan deskripsi gambar yang ingin Anda hasilkan, lalu klik tombol 'Generate Image'")

with col2:
    st.markdown("### 🖼️ Hasil Gambar")
    
    # Placeholder untuk gambar
    image_placeholder = st.empty()
    
    # Jika tombol diklik dan prompt tidak kosong
    if generate_btn:
        if prompt.strip():
            with st.spinner("🎨 Sedang membuat gambar..."):
                try:
                    generated_image = generate_image(prompt)
                    image_placeholder.image(generated_image, caption=f"Gambar untuk: {prompt}", use_column_width=True)
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {str(e)}")
        else:
            st.warning("⚠️ Silakan masukkan deskripsi gambar terlebih dahulu!")
    
    # Jika belum ada gambar yang di-generate
    if not generate_btn or not prompt.strip():
        # Menampilkan placeholder image
        placeholder_img = Image.new("RGB", (512, 512), color="#f0f2f6")
        draw = ImageDraw.Draw(placeholder_img)
        draw.text((200, 250), "🖼️ Hasil Gambar", fill="gray")
        image_placeholder.image(placeholder_img, caption="Belum ada gambar", use_column_width=True)

# Footer
st.markdown("---")
st.markdown("💻 Dibuat dengan Streamlit | Ganti fungsi `generate_image` dengan model AI Anda sendiri")
