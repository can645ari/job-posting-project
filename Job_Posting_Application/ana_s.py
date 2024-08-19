import streamlit as st
import subprocess
import pyautogui
import pyodbc
import re
import time

dosya_adı = "son_giris.txt"
conn_str = f'DRIVER={{SQL Server}};SERVER={'DESKTOP-HU58BL8\\SQLEXPRESS'};DATABASE={'yazilim_sinama'};Trusted_Connection=yes'

def main():
    st.title("Hoşgeldiniz!")
    selection2 = st.sidebar.radio("Ne yapmak istiyorsunuz? ", ["Giriş Yap", "Kayıt ol"])
    if selection2 == "Giriş Yap":
        giris_ekrani()
    elif selection2 == "Kayıt ol":
        kayit_ekrani()

def giris_baglanti(username, password):
    conn = None
    cursor = None
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = f"SELECT * FROM kullanicilar WHERE kullanici_adi = '{username}' AND sifre = '{password}'"
    result = cursor.execute(query).fetchone()
    conn.close()
    return result is not None

def giris_ekrani():
    is_veren_mi= True
    selection1 = st.radio("Giriş yapacağınız hesap türünü seçin: ", ["İş Arayan", "İş Veren"])
    if selection1 == "İş Arayan":
        is_veren_mi = False
    elif selection1 == "İş Veren":
        is_veren_mi = True

    if is_veren_mi == True:
       st.subheader("İş Veren Girişi")
    elif is_veren_mi == False:
        st.subheader("İş Arayan Girişi ")

    username = st.text_input("Kullanıcı Adı", key="job_seeker_username")
    password = st.text_input("Şifre", type="password", key="job_seeker_password")

    if st.button("Giriş"):
        if username and password:
            if giris_baglanti(username, password):
                st.success("Başarıyla giriş yaptınız!")
                with open(dosya_adı, mode='w') as dosya:
                    dosya.write(username)
                if is_veren_mi:
                    subprocess.Popen(["cmd.exe", "/c", "streamlit run is_veren_s.py"])
                    time.sleep(1)
                    pyautogui.hotkey("ctrl","F5")
                else:
                    subprocess.Popen(["cmd.exe", "/c", "streamlit run is_alan_s.py"])
                    time.sleep(1)
                    pyautogui.hotkey("ctrl","F5")

            else:
                st.error("Giriş başarısız. Lütfen kullanıcı adı ve şifrenizin doğruluğunu kontrol edin.")
        else:
            st.error("Giriş başarısız. Lütfen boş alan bırakmayın.")


def kullaniciyi_kaydet(first_name, last_name,user_name,password ,email):
    try:
        conn = None
        cursor = None

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        query = "INSERT INTO kullanicilar (isim, soyisim,kullanici_adi,sifre,mail) VALUES (?, ?, ?, ?,?)"
        cursor.execute(query, (first_name, last_name,user_name,password, email))
        conn.commit()

        st.success("Tebrikler! Başarıyla Kayıt Oldunuz.")
        time.sleep(1)
        pyautogui.hotkey("ctrl","F5")

    except Exception as e:
        st.error(f"Hata oluştu: {str(e)}")

    finally:
        cursor.close()
        conn.close()

def kayit_var_mi(user_name):
    conn = None
    cursor = None
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    query = f"SELECT * FROM kullanicilar WHERE kullanici_adi = '{user_name}'"
    result = cursor.execute(query).fetchone()
    conn.close()
    return result is not None

def kayit_ekrani():
    st.subheader("Lütfen kayıt için gerekli bilgileri giriniz.")
    first_name = st.text_input("Ad", key="registration_first_name")
    last_name = st.text_input("Soyad", key="registration_last_name")
    user_name = st.text_input("Kullanıcı Adı", key="registration_user_name")
    password = st.text_input("Şifre", key="registration_password")
    email = st.text_input("E-posta", key="registration_email")

    if st.button("Kayıt Ol"):
        if not kayit_var_mi(user_name):
            if first_name and last_name and user_name and password and email:
                if first_name.isalpha() and last_name.isalpha() and not user_name.isdigit() and not password.isdigit():
                    if len(first_name)>=3 and len(last_name)>=3 and len(user_name)>=3 and len(password)>=3 and len(email)>=3:
                        if email_kontrol(email):
                            kullaniciyi_kaydet(first_name, last_name,user_name ,password, email)
                        else:
                            st.error("Başarısız deneme! Lütfen doğru formatta bir email giriniz.")
                    else:
                        st.error("Başarısız deneme! Girilen hiçbir bilgi 3 karakterden kısa olamaz.")
                else: st.error("Başarısız deneme! Ad ve soyad değerleri sadece harflerden oluşmalı, kullanıcı adı ile şifre ise sadece sayılardan oluşmamalı Bunlara dikkat ediniz.")
            else:
                st.error("Başarısız deneme! Lütfen boş alan bırakmamaya özen gösteriniz.")
        else:
            st.error("Başarısız deneme! Bu kullanıcı adı zaten kayıtlı.")


def email_kontrol(email):
    pattern = r'^\S+@\S+\.\S+$'
    return re.match(pattern, email) is not None


if __name__ == "__main__":
    main()