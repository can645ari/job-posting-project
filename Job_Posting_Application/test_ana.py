import unittest
from ana_s import giris_baglanti, kayit_var_mi, email_kontrol

class TestYourScript(unittest.TestCase):

    def test_giris_baglanti(self):
        # Giriş bağlantısını test etme
        result = giris_baglanti("test_user", "test_password")  # Geçici test kullanıcı bilgileri
        self.assertFalse(result)  # Geçersiz kullanıcı adı ve şifre ile giriş başarısız olmalı

    

    def test_email_kontrol(self):
        # E-posta doğruluğunu kontrol etme
        valid_email = email_kontrol("test@example.com")  # Geçerli bir e-posta adresi
        invalid_email = email_kontrol("testexample.com")  # Geçersiz bir e-posta adresi
        self.assertTrue(valid_email)  # Geçerli bir e-posta True dönmeli
        self.assertFalse(invalid_email)  # Geçersiz bir e-posta False dönmeli

if __name__ == "__main__":
    unittest.main()
