import unittest
from io import StringIO
from unittest.mock import patch
from is_alan_s import filtrele_ilanlar, basvuran_var_mi, basvurmak

class TestYourScript(unittest.TestCase):

    def test_filtrele_ilanlar(self):
        # Filtreleme işlevini test etme
        ilanlar = [
            {'başlık': 'Test Başlık', 'açıklama': 'Test Açıklama'},
            {'başlık': 'Başka Bir Başlık', 'açıklama': 'Başka Bir Açıklama'}
        ]
        filtered = filtrele_ilanlar('Test', ilanlar)
        self.assertEqual(len(filtered), 1)  # 'Test' kelimesiyle eşleşen bir ilan olmalı

    def test_basvuran_var_mi(self):
        # Başvuranın varlığını kontrol etme
        result = basvuran_var_mi("TestKisi", 500)  # Test amaçlı bir ID ile test ediyoruz
        self.assertFalse(result)  # Başvuran yoksa False dönmeli


if __name__ == "__main__":
    unittest.main()
