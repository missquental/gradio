import streamlit as st

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

st.title("Greeting App")

# Input nama
name = st.text_input("Enter your name:", "")

# Input intensitas
intensity = st.slider("Select intensity:", 1, 10, 1)

# Tombol untuk menjalankan fungsi greet
if st.button("Greet"):
    if name:
        result = greet(name, intensity)
        st.success(result)
    else:
        st.warning("Please enter your name!")

# Menambahkan informasi cara menggunakan app
st.info("Enter your name and select the intensity level, then click 'Greet' button!")
