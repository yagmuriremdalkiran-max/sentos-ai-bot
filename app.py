import streamlit as st
import pandas as pd
from openai import OpenAI

# API KEY BURAYA (tırnak içinde)
client = OpenAI(api_key="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")

# Excel dosyasını yükle
file_path = "Ebio_AI_Demo.xlsx"

try:
    products_df = pd.read_excel(file_path, sheet_name="products")
    risk_df = pd.read_excel(file_path, sheet_name="risk_words")
except Exception as e:
    st.error(f"Excel yüklenemedi: {e}")
    st.stop()

st.title("Ebio AI Müşteri Destek Robotu")

question = st.text_area("Müşteri Sorusu")

if st.button("Analiz Et"):

    if not question:
        st.warning("Lütfen soru girin.")
        st.stop()

    q_lower = question.lower()

    # ÜRÜN TESPİT
    matched_product = None

    for _, row in products_df.iterrows():
        aliases = str(row["kısa_adlar"]).lower().split(",")
        for alias in aliases:
            if alias.strip() and alias.strip() in q_lower:
                matched_product = row
                break
        if matched_product is not None:
            break

    # RİSK KONTROL
    risk_flag = False
    for word in risk_df["kelime"]:
        if str(word).lower() in q_lower:
            risk_flag = True
            break

    # EKRANA YAZ
    if matched_product is not None:
        st.success(f"Eşleşen Ürün: {matched_product['ürün_adı']}")
    else:
        st.warning("Ürün tespit edilemedi.")

    if risk_flag:
        st.error("RİSKLİ MESAJ – Manuel kontrol önerilir.")

    # ÜRÜN BİLGİSİ HAZIRLA
    product_info = ""

    if matched_product is not None:
        garanti = matched_product.get("garanti", "Belirtilmemiş")
        teknik = matched_product.get("teknik_özellikler", "Belirtilmemiş")

        product_info = f"""
Marka: {matched_product['marka']}
Ürün: {matched_product['ürün_adı']}
Garanti: {garanti}
Teknik Özellikler: {teknik}
"""

    prompt = f"""
Sen Trendyol, Hepsiburada, N11 ve Beymen için resmi müşteri temsilcisisin.

Kurallar:
- Cevaba mutlaka "Merhaba," ile başla.
- Nazik ve profesyonel dil kullan.
- Emoji kullanma.
- Asla tahmin yapma.
- Sadece verilen Ürün Bilgisi alanındaki verileri kullan.
- Bilgi yoksa "Bu konuda bilgi bulunmamaktadır." yaz.
- Kısa ve net cevap ver.
- Cevabın sonunda iyi günler dile.

Ürün Bilgisi:
{product_info}

Müşteri Sorusu:
{question}
"""

    # AI ÇAĞRISI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        reply = response.choices[0].message.content

        st.subheader("Taslak Cevap:")
        st.write(reply)

    except Exception as e:
        st.error(f"AI HATASI: {e}")
