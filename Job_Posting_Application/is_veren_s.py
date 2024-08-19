import streamlit as st
import pyodbc
import pyautogui
import time
import pandas as pd
from datetime import datetime

conn_str = f'DRIVER={{SQL Server}};SERVER={'DESKTOP-HU58BL8\\SQLEXPRESS'};DATABASE={'yazilim_sinama'};Trusted_Connection=yes'
with open("son_giris.txt", mode='r') as dosya:
    ana_kullanici_ad = dosya.read()

def main():
    st.header(f"Merhaba {ana_kullanici_ad}")
    secenekler = ["İş Tanımla", "Atanmamış işler", "Atanmış işler"]
    secim = st.sidebar.selectbox("Menü", secenekler)

    if secim == "İş Tanımla":
        is_tanimla()
    elif secim == "Atanmamış işler":
        atanmamis_isler()
    elif secim == "Atanmış işler":
        atanmis_isler()


def isi_kaydet(baslik, aciklama,butce,tarih):
    try:
        conn = None
        cursor = None

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = "INSERT INTO isler (proje_basligi,proje_aciklamasi,proje_butce,proje_tarihi,proje_sahibi,proje_verildi_mi) VALUES (?,?,?,?,?,?)"
        cursor.execute(query, (baslik, aciklama,butce,tarih.strftime("%Y-%m-%d"),ana_kullanici_ad,False))
        conn.commit()
        st.success("Tebrikler! İş başarıyla kaydedildi.")

    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")

def kayit_var_mi(proje_adi):
    conn = None
    cursor = None
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = f"SELECT * FROM isler WHERE proje_basligi = '{proje_adi}'"
    result = cursor.execute(query).fetchone()
    conn.close()
    return result is not None

def is_tanimla():
    st.subheader("İş tanımlamak için gereken bilgileri giriniz.")

    proje_basligi = st.text_input("Proje Başlığı:")
    proje_aciklama = st.text_area("Proje Açıklaması:")
    proje_butce = st.number_input("Proje Bütçesi:")
    proje_zaman = st.date_input("Proje Bitiş Tarihi:",min_value= datetime.now())
    if st.button("Projeyi Kaydet"):
        if proje_basligi and proje_aciklama and proje_butce and proje_zaman:
            if not kayit_var_mi(proje_basligi):
                if not proje_basligi.isdigit() and not proje_aciklama.isdigit():
                    isi_kaydet(proje_basligi, proje_aciklama,proje_butce ,proje_zaman)
                    time.sleep(1)
                    pyautogui.hotkey("ctrl","F5")
                else:
                    st.error("Başarısız deneme! Bu proje zatensistemde var!")
            else:
                st.error("Başarısız deneme! Bu başlık ile bir iş tanımlı!")
        else:
            st.error("Başarısız deneme! Lütfen boş alan bırakmayınız!")

def atanmamis_isler():
    st.subheader("Atanmamış işlerinizi görüntüleyin.")
    conn = pyodbc.connect(conn_str)
    query = f"SELECT * FROM isler WHERE proje_sahibi = '{ana_kullanici_ad}' AND proje_verildi_mi = 'False'"
    df = pd.read_sql(query, conn)
    selected_data = df['proje_basligi'].unique()
    selected_value = st.selectbox('Seçiniz', selected_data)

    if selected_value:
        st.write(" ")
        st.write('Proje Başlığı: ', selected_value)
        if not df.empty:
            selected_info1 = df[df['proje_basligi'] == selected_value]['proje_aciklamasi'].values[0]
            selected_info2 = df[df['proje_basligi'] == selected_value]['proje_butce'].values[0]
            selected_info3 = df[df['proje_basligi'] == selected_value]['proje_tarihi'].values[0]
            basvuru_id = df[df['proje_basligi'] == selected_value]['proje_ID'].values[0]
            st.write('Proje açıklaması: ', selected_info1)
            st.write('Proje bütçesi: ', selected_info2,'TL')
            st.write('Proje son tarihi: ', selected_info3)


        if st.button('Bu projeyi sil'):
            st.success("Proje silindi.")
            tablodan_sil(selected_value,basvuru_id)

        st.write(" ")
        st.header("İşe başvuranlar:")
        basvuran_kisiler=[]
        cursor = conn.cursor()
        sorgu = f"SELECT * FROM basvuranlar WHERE proje_ID = '{basvuru_id}'"
        cursor.execute(sorgu)
        for row in cursor.fetchall():
            basvuran_kisiler.append({
                'kisi':row.basvuran_ismi,
                "teklifi":row.teklif
            })
        if not basvuran_kisiler:
            st.write(" ")
            st.subheader("Henüz kimse işe başvurmadı.")
            
        for basvuran_kisi in basvuran_kisiler:
            st.write("---------------------------------------------------------------------")
            st.write(" ")
            st.write(f"Başvuran kişinin kullanıcı adı: {basvuran_kisi['kisi']}")
            st.write(f"Teklif ettiği fiyat: {basvuran_kisi['teklifi']}TL")
            if st.button(f"{basvuran_kisi['kisi']} adlı kullanıcıya işi ver."):
                    try:
                        cursor.execute(f"UPDATE isler SET projeyi_alan = '{basvuran_kisi['kisi']}' WHERE proje_ID = '{basvuru_id}'")
                        cursor.execute(f"UPDATE isler SET proje_verildi_mi = 'True' WHERE proje_ID = '{basvuru_id}'")
                        conn.commit()
                        st.success("İş verildi.")
                        time.sleep(1)
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Hata: {e}")
            st.write("UYARI!: İşi başvuran kişiye verdikten sonra Email bilginiz karşı tarafa ulaştırılacaktır. İşi alan kişi, iş ile alakalı gelişmeleri oradan bildirecektir.")

    else:
        st.write(" ")
        st.subheader("Atanmamış proje yok.")


def atanmis_isler():
    st.subheader("Atanmış işlerinizi görüntüleyin.")

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = f"SELECT * FROM isler WHERE proje_sahibi = '{ana_kullanici_ad}' AND proje_verildi_mi = 'True'"
    df = pd.read_sql(query, conn)
    selected_data = df['proje_basligi'].unique()
    selected_value = st.selectbox('Seçiniz', selected_data)
    if selected_value:
        st.write(" ")
        st.write('Proje Başlığı: ', selected_value)
        if not df.empty:
            selected_info1 = df[df['proje_basligi'] == selected_value]['proje_aciklamasi'].values[0]
            selected_info2 = df[df['proje_basligi'] == selected_value]['proje_tarihi'].values[0]
            selected_info3 = df[df['proje_basligi'] == selected_value]['projeyi_alan'].values[0]
            basvuru_id = df[df['proje_basligi'] == selected_value]['proje_ID'].values[0]

            query2 = f"SELECT teklif FROM basvuranlar WHERE basvuran_ismi = '{selected_info3}' AND proje_ID = '{basvuru_id}'"
            result = cursor.execute(query2).fetchone()
            teklif_fiyati = result[0]
            st.write('Proje açıklaması: ', selected_info1)
            st.write('Proje son tarihi: ', selected_info2)
            st.write('Projeyi alan kişi: ', selected_info3)
            st.write('İş bitince ödeyeceğiniz fiyat: ', teklif_fiyati,"TL")
    
        if st.button('İş başarısız ise projeyi iptal et.'):
            st.success("Proje iptal edildi.")
            tablodan_sil(selected_value,basvuru_id)

        if st.button('İş başarılı ise parayı aktar.'):
            query3 = f"SELECT teklif FROM basvuranlar WHERE basvuran_ismi = '{selected_info3}' AND proje_ID = '{basvuru_id}'"
            result = cursor.execute(query3).fetchone()
            verilecek_tutar = result[0]
            query4 = f"SELECT para FROM kullanicilar WHERE kullanici_adi = '{selected_info3}'"
            result = cursor.execute(query4).fetchone()
            hesapta_olan = result[0]
            hesaptaki_para = 0
            if hesapta_olan == None:
                hesapta_olan=0
                hesaptaki_para = verilecek_tutar+hesapta_olan
            else:
                hesaptaki_para = verilecek_tutar+hesapta_olan

            cursor.execute(f"UPDATE kullanicilar SET para = '{hesaptaki_para}' WHERE kullanici_adi= '{selected_info3}'")
            conn.commit()
            st.success("Para başarıyla aktarıldı ve proje bitti.")
            tablodan_sil(selected_value,basvuru_id)
    else:
        st.write(" ")
        st.subheader("Atanmış proje yok.")

def tablodan_sil(basligi,id):
        conn = pyodbc.connect(conn_str)
        delete_query = f"DELETE FROM isler WHERE proje_basligi = '{basligi}' AND proje_sahibi = '{ana_kullanici_ad}'"
        cursor = conn.cursor()
        cursor.execute(delete_query)
        delete_query2 = f"DELETE FROM basvuranlar WHERE proje_ID = '{id}'"
        cursor = conn.cursor()
        cursor.execute(delete_query2)
        conn.commit()

        time.sleep(1)
        st.experimental_rerun()


if __name__ == "__main__":
    main()
