import sqlite3
import os

# ─── VERİTABANI YOLU ────────────────────────
klasor = os.path.dirname(os.path.abspath(__file__))
DB_YOLU = os.path.join(klasor, "maden.db")

# ─── TABLOLARI OLUŞTUR ──────────────────────
def veritabani_baslat():
    baglanti = sqlite3.connect(DB_YOLU)
    imleç = baglanti.cursor()

    imleç.execute("""
        CREATE TABLE IF NOT EXISTS vardiyalar (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih           TEXT,
            vardiya         TEXT,
            sorumlu         TEXT,
            toplam_ton      REAL,
            toplam_km       REAL,
            toplam_yakit    REAL
        )
    """)

    imleç.execute("""
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE,
            sifre         TEXT,
            rol           TEXT
        )
    """)

    imleç.execute("""
        INSERT OR IGNORE INTO kullanicilar (kullanici_adi, sifre, rol)
        VALUES (?, ?, ?)
    """, ("abc", "123", "admin"))

    imleç.execute("""
        CREATE TABLE IF NOT EXISTS araclar (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            vardiya_id      INTEGER,
            plaka           TEXT,
            sofor           TEXT,
            durum           TEXT,
            tur             INTEGER,
            ton             REAL,
            km              REAL,
            yakit_maliyet   REAL,
            FOREIGN KEY (vardiya_id) REFERENCES vardiyalar(id)
        )
    """)

    baglanti.commit()
    baglanti.close()
    print("✅ Veritabanı hazır!")

# ─── VARDİYA KAYDET ─────────────────────────
def vardiya_kaydet(vardiya_verisi):
    baglanti = sqlite3.connect(DB_YOLU)
    imleç = baglanti.cursor()

    imleç.execute("""
        INSERT INTO vardiyalar (tarih, vardiya, sorumlu, toplam_ton, toplam_km, toplam_yakit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        vardiya_verisi["tarih"],
        vardiya_verisi["vardiya"],
        vardiya_verisi["sorumlu"],
        vardiya_verisi["toplam_ton"],
        vardiya_verisi["toplam_km"],
        vardiya_verisi["toplam_yakit_maliyet"]
    ))

    vardiya_id = imleç.lastrowid

    for arac in vardiya_verisi["araclar"]:
        imleç.execute("""
            INSERT INTO araclar (vardiya_id, plaka, sofor, durum, tur, ton, km, yakit_maliyet)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vardiya_id,
            arac["plaka"],
            arac["sofor"],
            arac["durum"],
            arac["tur"],
            arac["ton"],
            arac["km"],
            arac["yakit_maliyet"]
        ))

    baglanti.commit()
    baglanti.close()

# ─── GÜNLÜK ÖZET ────────────────────────────
def gunluk_ozet(tarih):
    baglanti = sqlite3.connect(DB_YOLU)
    imleç = baglanti.cursor()

    imleç.execute("""
        SELECT vardiya, toplam_ton, toplam_yakit
        FROM vardiyalar
        WHERE tarih = ?
        ORDER BY id
    """, (tarih,))

    satirlar = imleç.fetchall()
    baglanti.close()
    return satirlar

# ─── HAFTALIK ÖZET ──────────────────────────
def haftalik_ozet():
    baglanti = sqlite3.connect(DB_YOLU)
    imleç = baglanti.cursor()

    imleç.execute("""
        SELECT tarih, SUM(toplam_ton), SUM(toplam_yakit)
        FROM vardiyalar
        GROUP BY tarih
        ORDER BY tarih
    """)

    satirlar = imleç.fetchall()
    baglanti.close()
    return satirlar

# ─── KULLANICI KONTROL ───────────────────────
def kullanici_kontrol(kullanici_adi, sifre):
    baglanti = sqlite3.connect(DB_YOLU)
    imleç = baglanti.cursor()

    imleç.execute("""
        SELECT * FROM kullanicilar
        WHERE kullanici_adi = ? AND sifre = ?
    """, (kullanici_adi, sifre))

    kullanici = imleç.fetchone()
    baglanti.close()

    if kullanici:
        return True
    else:
        return False
    
# ─── TEST ───────────────────────────────────
if __name__ == "__main__":
    veritabani_baslat()

    baglanti = sqlite3.connect(DB_YOLU)
    imleç = baglanti.cursor()

    imleç.execute("SELECT COUNT(*) FROM vardiyalar")
    print("Vardiya sayısı: " + str(imleç.fetchone()[0]))

    imleç.execute("SELECT COUNT(*) FROM araclar")
    print("Araç kaydı sayısı: " + str(imleç.fetchone()[0]))

    imleç.execute("SELECT tarih, vardiya, toplam_ton FROM vardiyalar LIMIT 5")
    print("\nİlk 5 kayıt:")
    for satir in imleç.fetchall():
        print(satir)

    baglanti.close()