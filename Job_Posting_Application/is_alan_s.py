import streamlit as st
import pyodbc
import pandas as pd

with open("son_giris.txt", mode='r') as dosya:
    ana_kullanici_ad = dosya.read()

conn_str = f'DRIVER={{SQL Server}};SERVER={'DESKTOP-HU58BL8\\SQLEXPRESS'};DATABASE={'yazilim_sinama'};Trusted_Connection=yes'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
sorgu = f"SELECT * FROM isler WHERE proje_verildi_mi = 'False' AND proje_sahibi !='{ana_kullanici_ad}' "
cursor.execute(sorgu)
ilanlar = []
for row in cursor.fetchall():
    ilanlar.append({
        'başlık': row.proje_basligi,
        'açıklama': row.proje_aciklamasi,
        'ücret': row.proje_butce,
        'son_tarih':row.proje_tarihi,
        'sahibi':row.proje_sahibi,
        'ID':row.proje_ID
    })

def main():
    query2 = f"SELECT para FROM kullanicilar WHERE kullanici_adi = '{ana_kullanici_ad}'"
    result = cursor.execute(query2).fetchone()
    cuzdan = result[0] 
    if cuzdan != None:
        st.markdown(f'<div style="position: absolute; top: 2px; right: 10px; color: green; font-size: 24px;">{cuzdan}TL</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="position: absolute; top: 2px; right: 10px; color: green; font-size: 24px;">0.00TL</div>', unsafe_allow_html=True)

    st.header(f"Merhaba {ana_kullanici_ad}")
    st.write(" ")
    secenekler = ["İlan Ara", "Aldığın işler"]
    secim = st.sidebar.selectbox("Menü", secenekler)

    if secim == "İlan Ara":
        ilan_arama()
    elif secim == "Aldığın işler":
        aldıgın_isler()

def aldıgın_isler():
    conn = pyodbc.connect(conn_str)
    query = f"SELECT * FROM isler WHERE projeyi_alan = '{ana_kullanici_ad}' AND proje_verildi_mi = 'True'"
    df = pd.read_sql(query, conn)
    selected_data = df['proje_basligi'].unique()
    selected_value = st.selectbox('Seçiniz', selected_data)
    if selected_value:
        st.write(" ")
        st.write('Proje Başlığı: ', selected_value)
        if not df.empty:
            selected_info1 = df[df['proje_basligi'] == selected_value]['proje_aciklamasi'].values[0]
            selected_info2 = df[df['proje_basligi'] == selected_value]['proje_tarihi'].values[0]
            basvuru_id = df[df['proje_basligi'] == selected_value]['proje_ID'].values[0]
            proje_veren = df[df['proje_basligi'] == selected_value]['proje_sahibi'].values[0]
            query2 = f"SELECT mail FROM kullanicilar WHERE kullanici_adi = '{proje_veren}'"
            result = cursor.execute(query2).fetchone()
            patron_maili = result[0]
            query3 = f"SELECT teklif FROM basvuranlar WHERE basvuran_ismi = '{ana_kullanici_ad}' AND proje_ID = '{basvuru_id}'"
            result = cursor.execute(query3).fetchone()
            teklif_fiyati = result[0]

            st.write('Proje açıklaması: ', selected_info1)
            st.write('Proje bitince alacağınız ücret: ', teklif_fiyati,'TL')
            st.write('Proje son tarihi: ', selected_info2)
            st.write('Projeyi veren: ', proje_veren)
            st.write('Proje gelişmelerini ve ilerlemelerini bildirmek için ulaşacağınız mail adresi: ', patron_maili)

    else:
        st.write("")
        st.subheader("Alınmış iş yok.")


def ilan_arama():
    arama_metni = st.text_input('İş Ara:', key='arama_metni')
    
    filtrelenen_ilanlar = filtrele_ilanlar(arama_metni, ilanlar)
    if not filtrelenen_ilanlar:
        st.subheader("Henüz bir ilan verilmedi.")

    for ilan in filtrelenen_ilanlar:
        st.write(" ")
        st.write("-----------------------------------------------------------------")
        st.write(" ")
        st.write(f"## {ilan['başlık']}")
        st.write(f"Açıklama: {ilan['açıklama']}")
        st.write(f"Bütçe: {ilan['ücret']}TL")
        st.write(f"Son tarihi {ilan['son_tarih']}")
        st.write(f"İşi veren: {ilan['sahibi']}")

        teklif = st.number_input(f"Başvuru Teklifi (TL)", key=f"teklif_{ilan['ID']}",max_value=ilan['ücret'])

        if st.button(f"Hemen başvur.",key=f"{ilan['ID']}"):
            if teklif:
                basvurmak(ilan['ID'],ana_kullanici_ad,teklif)
            else:
                st.error("Teklif vermeden başvuramazsınız!")

def basvuran_var_mi(basvuran_mi,basvuru_id):
    conn = None
    cursor = None
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = f"SELECT * FROM basvuranlar WHERE proje_ID = {basvuru_id} AND basvuran_ismi = '{basvuran_mi}'"
    result = cursor.execute(query).fetchone()
    conn.close()
    return result is not None

def basvurmak(basvuruID,basvuran,teklifi):
    conn_str = f'DRIVER={{SQL Server}};SERVER={'DESKTOP-HU58BL8\\SQLEXPRESS'};DATABASE={'yazilim_sinama'};Trusted_Connection=yes'
    try:
        conn = None
        cursor = None

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        if not basvuran_var_mi(basvuran,basvuruID):

            query = "INSERT INTO basvuranlar (proje_ID,basvuran_ismi,teklif) VALUES (?,?,?)"
            cursor.execute(query, (basvuruID,basvuran,teklifi ))
            conn.commit()
            st.success("Başvurunuz alındı!")
        
        else:
            st.error("Bu ilana zaten başvurdunuz.")
    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")

    finally:
        cursor.close()
        conn.close()

def filtrele_ilanlar(arama_metni, ilanlar):
    if not arama_metni:
        return ilanlar
    else:
        filtrelenen_ilanlar = []
        for ilan in ilanlar:
            if arama_metni.lower() in ilan['başlık'].lower() or arama_metni.lower() in ilan['açıklama'].lower():
                filtrelenen_ilanlar.append(ilan)
        return filtrelenen_ilanlar

if __name__ == '__main__':
    main()