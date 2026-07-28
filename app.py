from __future__ import annotations

import re
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup


# ============================================================
# SAYFA AYARLARI
# ============================================================

st.set_page_config(
    page_title="BIST 500 Tarayıcı",
    page_icon="📈",
    layout="wide",
)

st.title("📈 BIST Dipten Dönüş Tarayıcı")
st.caption(
    "Borsa İstanbul hisselerini toplu olarak tarar, güncel olmayan "
    "verileri eler ve dipten dönüş ihtimali güçlü olanları puanlar."
)


# ============================================================
# YEDEK BIST HİSSE LİSTESİ
# ============================================================

YEDEK_HISSELER = """
A1CAP ACSEL ADEL ADESE ADGYO AFYON AGESA AGHOL AGROT AGYO
AHGAZ AKBNK AKCNS AKEUR AKFGY AKFIS AKFYE AKGRT AKMGY AKSA
AKSEN AKSGY AKSUE AKYHO ALARK ALBRK ALCAR ALCTL ALCHE ALFAS
ALGYO ALKA ALKIM ALMAD ALTNY ALVES ANELE ANGORA ANGEN ANHYT
ANSGR ARASE ARCLK ARDYZ ARENA ARMDA ARSAN ARTMS ARZUM ASELS
ASGYO ASTOR ASUZU ATAGY ATAKP ATATP ATEKS ATLAS ATSYH AVGYO
AVHOL AVOD AVPGY AYCES AYES AYGAZ AZTEK BAGFS BAKAB BALAT
BALSU BANVT BARMA BASCM BERA BEYAZ BFREN BIENY BIGCH BIGEN
BIMAS BINBN BINHO BIOEN BIZIM BJKAS BLCYT BMSCH BMSCL BNTAS
BOBET BORLS BOSSA BRISA BRKO BRKVY BRLSM BRMEN BRSAN BRYAT
BSOKE BTCIM BUCIM BURCE BURVA BVSAN BYDNR CANTE CASA CATES
CCOLA CELHA CEMAS CEMTS CEOEM CGCAM CIMSA CLEBI CMBTN CMENT
CONSE COSMO CRDFA CRFSA CUSAN CVKMD CWENE DAGHL DAGI DAPGM
DARDL DCTTR DENGE DERHL DERIM DESA DESPC DEVA DGATE DGGYO
DGNMO DIRIT DITAS DMRGD DMSAS DNISI DOAS DOBUR DOCO DOFER
DOGUB DOHOL DOKTA DURDO DURKN DYOB DZGYO EBEK ECILC ECZYT
EDATA EDIP EFOR EGEEN EGEGY EGGUB EGPRO EGSER EKGYO EKIZ
EKSUN ELITE EMKEL ENERY ENJSA ENKAI EPLAS ERBOS ERCB EREGL
ERSU ESCAR EUPWR EUYO EYGYO FADE FENER FLAP FMIZP FONET
FORMT FORTE FRIGO FROTO GARAN GARFA GEDIK GEDZA GENIL GENTS
GEREL GESAN GLBMD GLRYH GLYHO GMTAS GOKNR GOLTS GOODY GOZDE
GRNYO GRSEL GRTRK GSDDE GSDHO GSRAY GUBRF GUNDG GWIND GZNMI
HALKB HATEK HATSN HEDEF HEKTS HKTM HUBVC HUNER HURGZ ICUGS
IDGYO IEYHO IHAAS IHEVA IHGZT IHLAS IHLGM IHYAY IMASM INDES
INFO INGRM INTEM INVEO INVES ISATR ISBIR ISBTR ISCTR ISDMR
ISFIN ISGSY ISGYO ISKPL ISMEN ISSEN ISYAT IZELM IZFAS IZMDC
JANTS KAPLM KAREL KARSN KARTN KATMR KAYSE KBORU KCAER KCHOL
KENT KERVN KERVT KFEIN KGYO KIMMR KLGYO KLKIM KLMSN KLNMA
KLRHO KLSER KLSYN KMPUR KNFRT KOCMT KONKA KONTR KOPOL KORDS
KOTON KOZAA KOZAL KRDMA KRDMB KRDMD KRGYO KRONT KRPLS KRSTL
KRTEK KRVGD KSTUR KTLEV KTSKR KUTPO KUYAS KZBGY KZGYO LIDER
LIDFA LILAK LINK LKMNH LMKDC LOGO LRSHO LUKSK LYDHO MAALT
MACKO MAGEN MAKIM MANAS MARBL MARKA MARTI MAVI MEDTR MEGAP
MEPET MERCN MERIT MERKO METRO METUR MGROS MHRGY MIATK MIPAZ
MMCAS MNDRS MNDTR MOBTL MOGAN MPARK MRSHL MSGYO MTRKS MZHLD
NATEN NETAS NIBAS NTGAZ NTHOL NUGYO NUHCM OBAMS OBASE ODAS
ODINE OLMK ONCSM ORCAY ORGE ORMA OYAKC OYAYO OZATD OZKGY
OZRDN OZSUB PAGYO PAMEL PASEU PATEK PCILT PEHOL PENGD PENTA
PETKM PETUN PGSUS PINSU PKART PLTUR PNLSN PNSUT POLHO POLTK
PRDGS PRKAB PRKME PRZMA PSDTC QNBFB QNBFL QUAGR RALYH RAYSG
REEDR RNPOL RODRG RTALB RYGYO RYSAS SAFKR SAHOL SAMAT SANKO
SARKY SASA SAYAS SDTTR SEGYO SEKFK SEKUR SELEC SELGD SELVA
SEYKM SILVR SISE SKBNK SKTAS SKYLP SMART SMRTG SNGYO SNICA
SNKRN SODSN SOKE SOKM SRVGY SUMAS SURGY SUWEN TACTR TATEN
TATGD TAVHL TBORG TCELL TDGYO TEKTU TERA TETMT TEZOL TGSAS
THYAO TIRE TLMAN TMPOL TMSN TNZTP TOASO TRCAS TRGYO TRILC
TSGYO TSKB TSPOR TTKOM TTRAK TUCLK TUKAS TUPRS TURGG TURSG
UFUK ULAS ULUFA ULUSE ULKER UNLU USAK VAKBN VAKFN VAKKO
VANGD VBTYZ VERTU VERUS VESBE VESTL VKFYO VKGYO YAPRK
YATAS YAYLA YEOTK YESIL YGGYO YGYO YKBNK YONGA YUNSA YYAPI
YYLGD ZEDUR ZOREN ZRGYO
""".split()


# ============================================================
# KAP'TAN GÜNCEL HİSSE LİSTESİ
# ============================================================

@st.cache_data(ttl=21600, show_spinner=False)
def kap_hisselerini_getir() -> tuple[list[str], str]:
    """
    KAP tablosunun ilk sütunundaki gerçek hisse kodlarını almaya çalışır.
    Başarısız olursa yedek listeyi döndürür.
    """
    url = "https://kap.org.tr/tr/bist-sirketler"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 Version/17.0 Mobile Safari/604.1"
        )
    }

    try:
        cevap = requests.get(url, headers=headers, timeout=25)
        cevap.raise_for_status()

        soup = BeautifulSoup(cevap.text, "html.parser")
        bulunanlar: set[str] = set()

        # Sayfadaki her kelimeyi değil, tablo satırlarının ilk hücresini kullan.
        for satir in soup.select("tr"):
            hucreler = satir.find_all(["td", "th"])
            if not hucreler:
                continue

            ilk_hucre = hucreler[0].get_text(" ", strip=True).upper()
            ilk_hucre = re.sub(r"\s+", " ", ilk_hucre)

            if re.fullmatch(r"[A-Z0-9]{4,6}", ilk_hucre):
                bulunanlar.add(ilk_hucre)

        # KAP yapısı değişirse, yedek listedeki kodlarla kesişim kullan.
        if len(bulunanlar) < 300:
            sayfa_metni = soup.get_text(" ", strip=True).upper()
            adaylar = set(re.findall(r"\b[A-Z][A-Z0-9]{3,5}\b", sayfa_metni))
            bulunanlar = adaylar.intersection(set(YEDEK_HISSELER))

        if len(bulunanlar) >= 300:
            return sorted(bulunanlar), "KAP güncel listesi"

    except Exception:
        pass

    return sorted(set(YEDEK_HISSELER)), "Yedek BIST listesi"


# ============================================================
# GÖSTERGELER
# ============================================================

def rsi_hesapla(kapanis: pd.Series, periyot: int = 14) -> pd.Series:
    fark = kapanis.diff()
    yukselis = fark.clip(lower=0)
    dusus = -fark.clip(upper=0)

    ort_yukselis = yukselis.ewm(
        alpha=1 / periyot,
        adjust=False,
        min_periods=periyot,
    ).mean()

    ort_dusus = dusus.ewm(
        alpha=1 / periyot,
        adjust=False,
        min_periods=periyot,
    ).mean()

    rs = ort_yukselis / ort_dusus.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def atr_hesapla(
    yuksek: pd.Series,
    dusuk: pd.Series,
    kapanis: pd.Series,
    periyot: int = 14,
) -> pd.Series:
    onceki_kapanis = kapanis.shift(1)

    true_range = pd.concat(
        [
            yuksek - dusuk,
            (yuksek - onceki_kapanis).abs(),
            (dusuk - onceki_kapanis).abs(),
        ],
        axis=1,
    ).max(axis=1)

    return true_range.ewm(
        alpha=1 / periyot,
        adjust=False,
        min_periods=periyot,
    ).mean()


def cmf_hesapla(
    yuksek: pd.Series,
    dusuk: pd.Series,
    kapanis: pd.Series,
    hacim: pd.Series,
    periyot: int = 20,
) -> pd.Series:
    fiyat_araligi = (yuksek - dusuk).replace(0, np.nan)

    para_carpani = (
        ((kapanis - dusuk) - (yuksek - kapanis))
        / fiyat_araligi
    )

    para_hacmi = para_carpani.fillna(0) * hacim

    return (
        para_hacmi.rolling(periyot).sum()
        / hacim.rolling(periyot).sum().replace(0, np.nan)
    )


def obv_hesapla(kapanis: pd.Series, hacim: pd.Series) -> pd.Series:
    yon = np.sign(kapanis.diff()).fillna(0)
    return (yon * hacim).cumsum()


# ============================================================
# VERİ TEMİZLEME
# ============================================================

def veriyi_temizle(veri: pd.DataFrame) -> pd.DataFrame:
    if veri is None or veri.empty:
        return pd.DataFrame()

    gerekli = ["Open", "High", "Low", "Close", "Volume"]

    if not all(sutun in veri.columns for sutun in gerekli):
        return pd.DataFrame()

    veri = veri[gerekli].copy()

    for sutun in gerekli:
        veri[sutun] = pd.to_numeric(veri[sutun], errors="coerce")

    veri = veri.dropna(subset=["Open", "High", "Low", "Close"])
    veri["Volume"] = veri["Volume"].fillna(0)

    veri = (
        veri[~veri.index.duplicated(keep="last")]
        .sort_index()
    )

    return veri


# ============================================================
# VERİ GÜNCELLİĞİ
# ============================================================

def veri_eski_mi(son_zaman: pd.Timestamp, zaman_dilimi: str) -> bool:
    """
    Hafta sonunu yanlışlıkla eski veri saymamak için iş günü farkını kullanır.
    """
    try:
        son = pd.Timestamp(son_zaman)

        if son.tzinfo is not None:
            son = son.tz_convert("Europe/Istanbul")

        bugun = pd.Timestamp.now(tz="Europe/Istanbul").date()
        son_tarih = son.date()

        if son_tarih > bugun:
            return False

        is_gunu_farki = int(
            np.busday_count(
                np.datetime64(son_tarih),
                np.datetime64(bugun),
            )
        )

        if zaman_dilimi in ["1 Saat", "4 Saat"]:
            return is_gunu_farki > 2

        return is_gunu_farki > 5

    except Exception:
        return True


# ============================================================
# 4 SAATLİK MUM OLUŞTURMA
# ============================================================

def dort_saatlik_yap(veri: pd.DataFrame) -> pd.DataFrame:
    if veri.empty:
        return veri

    tum_parcalar = []

    for _, gun in veri.groupby(veri.index.date):
        gun = gun.sort_index().copy()

        if gun.empty:
            continue

        grup = np.arange(len(gun)) // 4

        birlesmis = gun.groupby(grup).agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )

        zamanlar = []

        for grup_no in sorted(set(grup)):
            grup_satirlari = gun.iloc[np.where(grup == grup_no)[0]]
            zamanlar.append(grup_satirlari.index[0])

        birlesmis.index = pd.DatetimeIndex(zamanlar)
        tum_parcalar.append(birlesmis)

    if not tum_parcalar:
        return pd.DataFrame()

    return pd.concat(tum_parcalar).sort_index()


# ============================================================
# TOPLU VERİ İNDİRME
# ============================================================

@st.cache_data(ttl=300, show_spinner=False)
def grup_verisi_indir(
    semboller: tuple[str, ...],
    zaman_dilimi: str,
) -> pd.DataFrame:
    yahoo_sembolleri = [f"{sembol}.IS" for sembol in semboller]

    if zaman_dilimi in ["1 Saat", "4 Saat"]:
        period = "60d"
        interval = "1h"
    else:
        period = "1y"
        interval = "1d"

    return yf.download(
        tickers=yahoo_sembolleri,
        period=period,
        interval=interval,
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
        timeout=30,
    )


def toplu_veriden_hisseyi_ayir(
    toplu_veri: pd.DataFrame,
    sembol: str,
) -> pd.DataFrame:
    if toplu_veri is None or toplu_veri.empty:
        return pd.DataFrame()

    yahoo_sembol = f"{sembol}.IS"

    try:
        if isinstance(toplu_veri.columns, pd.MultiIndex):
            birinci_seviye = (
                toplu_veri.columns.get_level_values(0).unique().tolist()
            )
            ikinci_seviye = (
                toplu_veri.columns.get_level_values(1).unique().tolist()
            )

            if yahoo_sembol in birinci_seviye:
                hisse_verisi = toplu_veri[yahoo_sembol].copy()
            elif yahoo_sembol in ikinci_seviye:
                hisse_verisi = toplu_veri.xs(
                    yahoo_sembol,
                    axis=1,
                    level=1,
                ).copy()
            else:
                return pd.DataFrame()
        else:
            hisse_verisi = toplu_veri.copy()

        return veriyi_temizle(hisse_verisi)

    except Exception:
        return pd.DataFrame()


# ============================================================
# HİSSE ANALİZİ
# ============================================================

def hisseyi_analiz_et(
    sembol: str,
    veri: pd.DataFrame,
    zaman_dilimi: str,
    min_puan: int,
    hacim_carpani: float,
    min_toparlanma: float,
    min_hacim_tl: float,
    veri_guncelligini_kontrol_et: bool = True,
) -> tuple[dict | None, str | None]:

    if zaman_dilimi == "4 Saat":
        veri = dort_saatlik_yap(veri)

    if veri.empty or len(veri) < 55:
        return None, "Yetersiz veri"

    if (
        veri_guncelligini_kontrol_et
        and veri_eski_mi(veri.index[-1], zaman_dilimi)
    ):
        return None, "Eski veri"

    veri = veri.copy()

    veri["EMA7"] = veri["Close"].ewm(span=7, adjust=False).mean()
    veri["EMA21"] = veri["Close"].ewm(span=21, adjust=False).mean()
    veri["EMA50"] = veri["Close"].ewm(span=50, adjust=False).mean()
    veri["RSI"] = rsi_hesapla(veri["Close"], 14)

    veri["ATR"] = atr_hesapla(
        veri["High"],
        veri["Low"],
        veri["Close"],
        14,
    )

    veri["HacimOrt20"] = veri["Volume"].rolling(20).mean()
    veri["OBV"] = obv_hesapla(veri["Close"], veri["Volume"])

    veri["CMF"] = cmf_hesapla(
        veri["High"],
        veri["Low"],
        veri["Close"],
        veri["Volume"],
        20,
    )

    veri["MACD"] = (
        veri["Close"].ewm(span=12, adjust=False).mean()
        - veri["Close"].ewm(span=26, adjust=False).mean()
    )

    veri["MACDSinyal"] = veri["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    veri = veri.dropna().copy()

    if len(veri) < 3:
        return None, "Yetersiz veri"

    son = veri.iloc[-1]
    onceki = veri.iloc[-2]

    fiyat = float(son["Close"])
    acilis = float(son["Open"])
    yuksek = float(son["High"])
    dusuk = float(son["Low"])
    hacim = float(son["Volume"])

    if fiyat <= 0:
        return None, "Geçersiz fiyat"

    hacim_tl = fiyat * hacim

    if hacim_tl < min_hacim_tl:
        return None, "Düşük hacim"

    ema7 = float(son["EMA7"])
    ema21 = float(son["EMA21"])
    ema50 = float(son["EMA50"])

    rsi = float(son["RSI"])
    onceki_rsi = float(onceki["RSI"])

    atr = float(son["ATR"])
    cmf = float(son["CMF"])
    hacim_ort = float(son["HacimOrt20"])

    hacim_orani = hacim / hacim_ort if hacim_ort > 0 else 0

    son_gun = veri.index[-1].date()
    gun_verisi = veri[pd.Index(veri.index.date) == son_gun]

    if gun_verisi.empty:
        return None, "Yetersiz veri"

    gun_acilis = float(gun_verisi.iloc[0]["Open"])
    gun_dusuk = float(gun_verisi["Low"].min())
    gun_yuksek = float(gun_verisi["High"].max())

    gunluk_degisim = ((fiyat / gun_acilis) - 1) * 100
    dipten_toparlanma = ((fiyat / gun_dusuk) - 1) * 100
    zirveye_uzaklik = ((fiyat / gun_yuksek) - 1) * 100

    # Gerçek gün içi satış baskısı:
    # Günün açılışından gün içi en düşüğe kadar olan hareket.
    gun_ici_dusus = ((gun_dusuk / gun_acilis) - 1) * 100

    mum_araligi = yuksek - dusuk
    mum_govdesi = abs(fiyat - acilis)

    govde_orani = (
        mum_govdesi / mum_araligi
        if mum_araligi > 0
        else 0
    )

    alt_fitil = min(acilis, fiyat) - dusuk

    alt_fitil_orani = (
        alt_fitil / mum_araligi
        if mum_araligi > 0
        else 0
    )

    atr_yuzde = (atr / fiyat) * 100

    # --------------------------------------------------------
    # KOŞULLAR
    # --------------------------------------------------------

    satis_baskisi = gun_ici_dusus <= -1.5
    dipten_donus = dipten_toparlanma >= min_toparlanma
    hacimli = hacim_orani >= hacim_carpani
    yesil_mum = fiyat > acilis

    guclu_govde = (
        yesil_mum
        and govde_orani >= 0.45
    )

    alt_fitil_var = alt_fitil_orani >= 0.25

    rsi_donusu = (
        30 <= rsi <= 68
        and rsi > onceki_rsi
    )

    ema7_ustu = fiyat > ema7
    ema21_ustu = fiyat > ema21

    ema21_geri_alindi = (
        fiyat > ema21
        and float(onceki["Close"]) <= float(onceki["EMA21"])
    )

    # Önceki sürümde fiyat EMA50'nin çok üstündeyken de "yakın" sayılıyordu.
    ema50_yakin = abs(fiyat - ema50) / fiyat <= 0.035

    obv_yukseliyor = float(son["OBV"]) > float(onceki["OBV"])
    cmf_olumlu = cmf > 0

    macd_gucleniyor = (
        float(son["MACD"]) > float(onceki["MACD"])
    )

    macd_sinyal_ustu = (
        float(son["MACD"]) > float(son["MACDSinyal"])
    )

    onceki_tepe_kirildi = fiyat > float(onceki["High"])
    atr_uygun = 0.7 <= atr_yuzde <= 5.0

    # --------------------------------------------------------
    # PUAN
    # Aynı hareketi ölçen benzer koşulların ağırlığı azaltıldı.
    # --------------------------------------------------------

    puan = 0
    nedenler: list[str] = []

    def puan_ekle(sart: bool, deger: int, neden: str) -> None:
        nonlocal puan
        if sart:
            puan += deger
            nedenler.append(neden)

    puan_ekle(satis_baskisi, 8, "Gün içi satış baskısı")
    puan_ekle(dipten_donus, 10, "Dipten toparlanma")
    puan_ekle(hacimli, 12, "Hacim artışı")
    puan_ekle(yesil_mum, 8, "Yeşil mum")
    puan_ekle(guclu_govde, 6, "Güçlü gövde")
    puan_ekle(alt_fitil_var, 6, "Dipten alım")
    puan_ekle(rsi_donusu, 8, "RSI dönüşü")
    puan_ekle(ema7_ustu, 5, "EMA7 üstü")
    puan_ekle(ema21_ustu, 4, "EMA21 üstü")
    puan_ekle(ema21_geri_alindi, 5, "EMA21 geri alındı")
    puan_ekle(ema50_yakin, 4, "EMA50 yakın")
    puan_ekle(obv_yukseliyor, 5, "OBV yükseliyor")
    puan_ekle(cmf_olumlu, 5, "CMF olumlu")
    puan_ekle(macd_gucleniyor, 5, "MACD güçleniyor")
    puan_ekle(macd_sinyal_ustu, 4, "MACD sinyal üstü")
    puan_ekle(onceki_tepe_kirildi, 5, "Önceki tepe kırıldı")
    puan_ekle(atr_uygun, 4, "ATR uygun")

    puan = min(puan, 100)

    # --------------------------------------------------------
    # SİNYAL SINIFLANDIRMASI
    # --------------------------------------------------------

    asiri_uzamis = (
        rsi >= 70
        or gunluk_degisim >= 7
        or dipten_toparlanma >= 8
    )

    donus_teyidi = (
        ema21_ustu
        or ema21_geri_alindi
        or (
            macd_sinyal_ustu
            and cmf > 0
        )
    )

    temel_al_sartlari = (
        dipten_donus
        and hacimli
        and yesil_mum
        and ema7_ustu
        and rsi <= 68
        and gunluk_degisim < 7
        and dipten_toparlanma < 8
        and donus_teyidi
    )

    guclu_al_sartlari = (
        temel_al_sartlari
        and cmf > 0
        and ema21_ustu
        and hacim_orani >= max(hacim_carpani, 1.25)
    )

    erken_al_sartlari = (
        35 <= rsi <= 60
        and rsi > onceki_rsi
        and fiyat > ema7
        and yesil_mum
        and 0.7 <= dipten_toparlanma <= 5
        and gunluk_degisim < 4
        and hacim_orani >= 1.05
        and cmf > -0.05
        and macd_gucleniyor
    )

    if asiri_uzamis:
        sinyal = "GEÇ KALINDI"
    elif puan >= 84 and guclu_al_sartlari:
        sinyal = "GÜÇLÜ AL"
    elif (
        puan >= min_puan
        and temel_al_sartlari
        and cmf > -0.10
    ):
        sinyal = "AL"
    elif erken_al_sartlari:
        sinyal = "ERKEN AL"
        nedenler.append("Erken dönüş yapısı")
    elif puan >= max(min_puan - 10, 0):
        sinyal = "İZLE"
    else:
        sinyal = "ZAYIF"

    # Stop hem ATR'yi hem de gün içi dönüş dibini dikkate alır.
    atr_stop = fiyat - atr * 1.2
    dip_stop = gun_dusuk - atr * 0.2
    stop = max(min(atr_stop, dip_stop), 0)

    hedef1 = fiyat + atr * 1.5
    hedef2 = fiyat + atr * 2.5

    return {
        "Sembol": sembol,
        "Sinyal": sinyal,
        "Puan": int(puan),
        "Fiyat": round(fiyat, 2),
        "Gün İçi %": round(gunluk_degisim, 2),
        "Dipten %": round(dipten_toparlanma, 2),
        "Zirveye %": round(zirveye_uzaklik, 2),
        "Gün İçi Dip %": round(gun_ici_dusus, 2),
        "RSI": round(rsi, 1),
        "Hacim x": round(hacim_orani, 2),
        "Hacim TL": round(hacim_tl, 0),
        "EMA7": round(ema7, 2),
        "EMA21": round(ema21, 2),
        "EMA50": round(ema50, 2),
        "CMF": round(cmf, 3),
        "ATR %": round(atr_yuzde, 2),
        "Stop": round(stop, 2),
        "Hedef 1": round(hedef1, 2),
        "Hedef 2": round(hedef2, 2),
        "Neden": ", ".join(nedenler),
        "Son Mum": veri.index[-1].strftime("%d.%m.%Y %H:%M"),
    }, None


# ============================================================
# YAN MENÜ
# ============================================================

# ============================================================
# BACKTEST
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def backtest_verisi_indir(
    sembol: str,
    zaman_dilimi: str,
    gunluk_yil: int,
) -> pd.DataFrame:
    yahoo_sembol = f"{sembol}.IS"

    if zaman_dilimi in ["1 Saat", "4 Saat"]:
        period = "60d"
        interval = "1h"
    else:
        period = f"{gunluk_yil}y"
        interval = "1d"

    veri = yf.download(
        tickers=yahoo_sembol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
        timeout=30,
    )

    if veri is None or veri.empty:
        return pd.DataFrame()

    if isinstance(veri.columns, pd.MultiIndex):
        try:
            if yahoo_sembol in veri.columns.get_level_values(0):
                veri = veri[yahoo_sembol].copy()
            elif yahoo_sembol in veri.columns.get_level_values(1):
                veri = veri.xs(
                    yahoo_sembol,
                    axis=1,
                    level=1,
                ).copy()
        except Exception:
            return pd.DataFrame()

    return veriyi_temizle(veri)


def maksimum_dusus_hesapla(getiriler: pd.Series) -> float:
    if getiriler.empty:
        return 0.0

    sermaye = (1 + getiriler.fillna(0) / 100).cumprod()
    zirve = sermaye.cummax()
    dusus = (sermaye / zirve - 1) * 100

    return float(dusus.min())


def backtest_calistir(
    semboller: list[str],
    zaman_dilimi: str,
    gunluk_yil: int,
    min_puan: int,
    hacim_carpani: float,
    min_toparlanma: float,
    min_hacim_tl: float,
    sinyal_turleri: list[str],
    bekleme_mumu: int,
    hedef_atr: float,
    stop_atr: float,
    maliyet_yuzde: float,
) -> tuple[pd.DataFrame, list[str]]:
    """
    Sinyal kapanışta oluşur, işlem bir sonraki mumun açılışında başlar.
    Aynı mumda hem stop hem hedef görülürse ihtiyatlı biçimde stop önce sayılır.
    Aynı hissede önceki işlem kapanmadan yeni işlem açılmaz.
    """
    islemler: list[dict] = []
    veri_alinamayanlar: list[str] = []

    ilerleme = st.progress(0)
    durum = st.empty()

    for sira, sembol in enumerate(semboller, start=1):
        durum.info(
            f"Backtest: {sembol} · {sira}/{len(semboller)}"
        )

        try:
            ham_veri = backtest_verisi_indir(
                sembol,
                zaman_dilimi,
                gunluk_yil,
            )
        except Exception:
            ham_veri = pd.DataFrame()

        if ham_veri.empty:
            veri_alinamayanlar.append(sembol)
            ilerleme.progress(sira / len(semboller))
            continue

        veri = (
            dort_saatlik_yap(ham_veri)
            if zaman_dilimi == "4 Saat"
            else ham_veri.copy()
        )

        if len(veri) < 80:
            veri_alinamayanlar.append(sembol)
            ilerleme.progress(sira / len(semboller))
            continue

        son_cikis_indeksi = -1
        ilk_indeks = 60
        son_indeks = len(veri) - bekleme_mumu - 1

        for i in range(ilk_indeks, max(ilk_indeks, son_indeks)):
            if i <= son_cikis_indeksi:
                continue

            gecmis = veri.iloc[:i + 1].copy()

            sonuc, _ = hisseyi_analiz_et(
                sembol=sembol,
                veri=gecmis,
                zaman_dilimi="1 Gün" if zaman_dilimi == "1 Gün" else zaman_dilimi,
                min_puan=min_puan,
                hacim_carpani=hacim_carpani,
                min_toparlanma=min_toparlanma,
                min_hacim_tl=min_hacim_tl,
                veri_guncelligini_kontrol_et=False,
            )

            if sonuc is None:
                continue

            sinyal = str(sonuc["Sinyal"])

            if sinyal not in sinyal_turleri:
                continue

            giris_indeksi = i + 1

            if giris_indeksi >= len(veri):
                continue

            giris = float(veri.iloc[giris_indeksi]["Open"])

            if not np.isfinite(giris) or giris <= 0:
                continue

            atr_degeri = (
                float(sonuc["ATR %"])
                / 100
                * float(sonuc["Fiyat"])
            )

            if not np.isfinite(atr_degeri) or atr_degeri <= 0:
                continue

            stop_fiyati = max(giris - stop_atr * atr_degeri, 0)
            hedef_fiyati = giris + hedef_atr * atr_degeri

            son_bakis = min(
                giris_indeksi + bekleme_mumu - 1,
                len(veri) - 1,
            )

            cikis_indeksi = son_bakis
            cikis_fiyati = float(veri.iloc[son_bakis]["Close"])
            cikis_nedeni = "Süre sonu"

            for j in range(giris_indeksi, son_bakis + 1):
                mum = veri.iloc[j]

                stop_goruldu = float(mum["Low"]) <= stop_fiyati
                hedef_goruldu = float(mum["High"]) >= hedef_fiyati

                # Aynı mumda ikisi de görülürse stop önce kabul edilir.
                if stop_goruldu:
                    cikis_indeksi = j
                    cikis_fiyati = stop_fiyati
                    cikis_nedeni = "Stop"
                    break

                if hedef_goruldu:
                    cikis_indeksi = j
                    cikis_fiyati = hedef_fiyati
                    cikis_nedeni = "Hedef"
                    break

            brut_getiri = ((cikis_fiyati / giris) - 1) * 100
            net_getiri = brut_getiri - maliyet_yuzde

            islemler.append(
                {
                    "Sembol": sembol,
                    "Sinyal": sinyal,
                    "Puan": int(sonuc["Puan"]),
                    "Sinyal Tarihi": veri.index[i].strftime(
                        "%d.%m.%Y %H:%M"
                    ),
                    "Giriş Tarihi": veri.index[giris_indeksi].strftime(
                        "%d.%m.%Y %H:%M"
                    ),
                    "Çıkış Tarihi": veri.index[cikis_indeksi].strftime(
                        "%d.%m.%Y %H:%M"
                    ),
                    "Giriş": round(giris, 4),
                    "Stop": round(stop_fiyati, 4),
                    "Hedef": round(hedef_fiyati, 4),
                    "Çıkış": round(cikis_fiyati, 4),
                    "Çıkış Nedeni": cikis_nedeni,
                    "Beklenen Mum": bekleme_mumu,
                    "Tutulan Mum": (
                        cikis_indeksi - giris_indeksi + 1
                    ),
                    "Brüt Getiri %": round(brut_getiri, 2),
                    "Net Getiri %": round(net_getiri, 2),
                }
            )

            son_cikis_indeksi = cikis_indeksi

        ilerleme.progress(sira / len(semboller))

    ilerleme.empty()
    durum.empty()

    return pd.DataFrame(islemler), veri_alinamayanlar


# ============================================================
# YAN MENÜ VE UYGULAMA MODU
# ============================================================

hisse_listesi, liste_kaynagi = kap_hisselerini_getir()

with st.sidebar:
    st.header("⚙️ Uygulama")

    uygulama_modu = st.radio(
        "Çalışma modu",
        ["Canlı Tarama", "Backtest"],
        index=0,
    )

    st.info(
        f"Liste kaynağı: {liste_kaynagi}\n\n"
        f"Bulunan sembol: {len(hisse_listesi)}"
    )

    if uygulama_modu == "Canlı Tarama":
        tarama_turu = st.selectbox(
            "Tarama listesi",
            ["Tüm BIST", "İlk 100 hisse", "Özel liste"],
            index=0,
        )

        zaman_dilimi = st.selectbox(
            "Zaman dilimi",
            ["1 Saat", "4 Saat", "1 Gün"],
            index=0,
            key="tarama_zaman",
        )

        min_puan = st.slider(
            "Minimum AL puanı",
            min_value=40,
            max_value=90,
            value=70,
            step=5,
            key="tarama_min_puan",
        )

        hacim_carpani = st.slider(
            "Minimum hacim çarpanı",
            min_value=0.5,
            max_value=4.0,
            value=1.2,
            step=0.1,
            key="tarama_hacim",
        )

        min_toparlanma = st.slider(
            "Dipten minimum toparlanma",
            min_value=0.5,
            max_value=10.0,
            value=1.0,
            step=0.1,
            format="%.1f%%",
            key="tarama_toparlanma",
        )

        min_hacim_milyon = st.slider(
            "Minimum mum hacmi",
            min_value=0,
            max_value=100,
            value=3,
            step=1,
            format="%d milyon TL",
            key="tarama_min_hacim",
        )

        grup_boyutu = st.select_slider(
            "İndirme grup büyüklüğü",
            options=[20, 30, 40, 50],
            value=40,
        )

        gosterim_sayisi = st.slider(
            "Ekranda gösterilecek sonuç",
            min_value=10,
            max_value=200,
            value=50,
            step=10,
        )

        sadece_al = st.checkbox(
            "Sadece alım sinyallerini göster",
            value=True,
        )

        ozel_liste = st.text_area(
            "Özel hisse listesi",
            value="GEREL, ASTOR, MIATK, PATEK, FORTE",
            height=120,
            disabled=tarama_turu != "Özel liste",
        )

        calistir = st.button(
            "🔍 Taramayı Başlat",
            type="primary",
            use_container_width=True,
        )

    else:
        zaman_dilimi = st.selectbox(
            "Backtest zaman dilimi",
            ["1 Saat", "4 Saat", "1 Gün"],
            index=2,
            key="backtest_zaman",
        )

        backtest_sembol_metni = st.text_area(
            "Backtest hisseleri",
            value="GOZDE, TKFEN, MGROS, EREGL, GEREL",
            height=120,
            help="En fazla 10 sembol kullanılması önerilir.",
        )

        gunluk_yil = st.slider(
            "Günlük veri geçmişi",
            min_value=1,
            max_value=5,
            value=2,
            step=1,
            format="%d yıl",
            disabled=zaman_dilimi != "1 Gün",
        )

        sinyal_turleri = st.multiselect(
            "Test edilecek sinyaller",
            ["GÜÇLÜ AL", "AL", "ERKEN AL"],
            default=["GÜÇLÜ AL", "AL", "ERKEN AL"],
        )

        min_puan = st.slider(
            "Backtest minimum AL puanı",
            min_value=40,
            max_value=90,
            value=70,
            step=5,
            key="backtest_min_puan",
        )

        hacim_carpani = st.slider(
            "Backtest hacim çarpanı",
            min_value=0.5,
            max_value=4.0,
            value=1.2,
            step=0.1,
            key="backtest_hacim",
        )

        min_toparlanma = st.slider(
            "Backtest dipten toparlanma",
            min_value=0.5,
            max_value=10.0,
            value=1.0,
            step=0.1,
            format="%.1f%%",
            key="backtest_toparlanma",
        )

        min_hacim_milyon = st.slider(
            "Backtest minimum mum hacmi",
            min_value=0,
            max_value=100,
            value=3,
            step=1,
            format="%d milyon TL",
            key="backtest_min_hacim",
        )

        bekleme_mumu = st.slider(
            "İşlemde en fazla beklenecek mum",
            min_value=2,
            max_value=30,
            value=10,
            step=1,
        )

        hedef_atr = st.slider(
            "Hedef ATR katsayısı",
            min_value=0.5,
            max_value=5.0,
            value=1.5,
            step=0.1,
        )

        stop_atr = st.slider(
            "Stop ATR katsayısı",
            min_value=0.5,
            max_value=5.0,
            value=1.2,
            step=0.1,
        )

        maliyet_yuzde = st.slider(
            "Toplam işlem maliyeti",
            min_value=0.0,
            max_value=1.0,
            value=0.20,
            step=0.05,
            format="%.2f%%",
            help="Alış ve satışın toplam komisyon/kayma varsayımıdır.",
        )

        calistir = st.button(
            "🧪 Backtest Başlat",
            type="primary",
            use_container_width=True,
        )

    if st.button(
        "🔄 Önbelleği temizle",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.success("Önbellek temizlendi.")


# ============================================================
# CANLI TARAMA
# ============================================================

if uygulama_modu == "Canlı Tarama":
    if not calistir:
        kolon1, kolon2, kolon3 = st.columns(3)

        kolon1.metric("Taranabilir hisse", len(hisse_listesi))
        kolon2.metric("Varsayılan zaman", "1 Saat")
        kolon3.metric("Varsayılan AL puanı", "70")

        st.info(
            "Sol menüden ayarları seçip "
            "**Taramayı Başlat** düğmesine bas."
        )

        st.subheader("Algoritmanın aradığı hareket")

        st.write(
            """
            **Gün içi satış baskısı → dipten alım → hacim artışı →  
            RSI dönüşü → EMA teyidi → para akışının güçlenmesi**
            """
        )

        st.warning(
            "Tüm BIST taraması birkaç dakika sürebilir. "
            "Tarama bitene kadar sayfayı kapatma."
        )

    else:
        if tarama_turu == "Tüm BIST":
            taranacaklar = hisse_listesi
        elif tarama_turu == "İlk 100 hisse":
            taranacaklar = hisse_listesi[:100]
        else:
            taranacaklar = [
                kod.strip().upper().replace(".IS", "")
                for kod in re.split(r"[,;\s]+", ozel_liste)
                if kod.strip()
            ]

        taranacaklar = [
            kod
            for kod in taranacaklar
            if re.fullmatch(r"[A-Z0-9]{4,6}", kod)
        ]
        taranacaklar = list(dict.fromkeys(taranacaklar))

        if not taranacaklar:
            st.error("Taranacak hisse bulunamadı.")
            st.stop()

        st.write(f"**{len(taranacaklar)} aday sembol taranacak.**")

        ilerleme = st.progress(0)
        durum = st.empty()
        sonuc_alani = st.empty()

        sonuclar: list[dict] = []
        veri_alinamayanlar: list[str] = []
        eski_veriler: list[str] = []
        yetersiz_veriler: list[str] = []
        dusuk_hacimliler: list[str] = []

        baslangic = time.time()

        gruplar = [
            taranacaklar[i:i + grup_boyutu]
            for i in range(0, len(taranacaklar), grup_boyutu)
        ]

        tamamlanan = 0

        for grup_no, grup in enumerate(gruplar, start=1):
            durum.info(
                f"Grup {grup_no}/{len(gruplar)} indiriliyor… "
                f"Tamamlanan: {tamamlanan}/{len(taranacaklar)}"
            )

            try:
                toplu_veri = grup_verisi_indir(
                    tuple(grup),
                    zaman_dilimi,
                )
            except Exception:
                toplu_veri = pd.DataFrame()

            for sembol in grup:
                try:
                    hisse_verisi = toplu_veriden_hisseyi_ayir(
                        toplu_veri,
                        sembol,
                    )

                    if hisse_verisi.empty:
                        veri_alinamayanlar.append(sembol)
                    else:
                        sonuc, hata = hisseyi_analiz_et(
                            sembol=sembol,
                            veri=hisse_verisi,
                            zaman_dilimi=zaman_dilimi,
                            min_puan=min_puan,
                            hacim_carpani=hacim_carpani,
                            min_toparlanma=min_toparlanma,
                            min_hacim_tl=(
                                min_hacim_milyon * 1_000_000
                            ),
                        )

                        if sonuc is not None:
                            sonuclar.append(sonuc)
                        elif hata == "Eski veri":
                            eski_veriler.append(sembol)
                        elif hata == "Düşük hacim":
                            dusuk_hacimliler.append(sembol)
                        else:
                            yetersiz_veriler.append(sembol)

                except Exception:
                    veri_alinamayanlar.append(sembol)

                tamamlanan += 1
                ilerleme.progress(
                    min(
                        int(
                            tamamlanan
                            / len(taranacaklar)
                            * 100
                        ),
                        100,
                    )
                )

            sonuc_alani.caption(
                f"Şu ana kadar {len(sonuclar)} "
                "güncel ve geçerli analiz bulundu."
            )

            time.sleep(0.5)

        ilerleme.empty()
        durum.empty()
        sonuc_alani.empty()

        gecen_sure = time.time() - baslangic

        if not sonuclar:
            st.error(
                "Güncel ve geçerli sonuç bulunamadı. "
                "Önbelleği temizleyip yeniden dene."
            )
            st.stop()

        tablo = pd.DataFrame(sonuclar)

        sinyal_sirasi = {
            "GÜÇLÜ AL": 1,
            "AL": 2,
            "ERKEN AL": 3,
            "İZLE": 4,
            "GEÇ KALINDI": 5,
            "ZAYIF": 6,
        }

        tablo["_sira"] = (
            tablo["Sinyal"]
            .map(sinyal_sirasi)
            .fillna(9)
        )

        tablo = (
            tablo
            .sort_values(
                by=["_sira", "Puan", "Hacim x", "Dipten %"],
                ascending=[True, False, False, False],
            )
            .drop(columns="_sira")
            .reset_index(drop=True)
        )

        guclu_al_sayisi = int(
            (tablo["Sinyal"] == "GÜÇLÜ AL").sum()
        )
        al_sayisi = int(
            (tablo["Sinyal"] == "AL").sum()
        )
        erken_al_sayisi = int(
            (tablo["Sinyal"] == "ERKEN AL").sum()
        )
        gec_kalindi_sayisi = int(
            (tablo["Sinyal"] == "GEÇ KALINDI").sum()
        )

        kolon1, kolon2, kolon3, kolon4, kolon5 = st.columns(5)

        kolon1.metric("Geçerli analiz", len(tablo))
        kolon2.metric("Güçlü AL", guclu_al_sayisi)
        kolon3.metric("AL", al_sayisi)
        kolon4.metric("Erken AL", erken_al_sayisi)
        kolon5.metric("Geç kalındı", gec_kalindi_sayisi)

        st.caption(
            f"Aday: {len(taranacaklar)} · "
            f"Veri alınamadı: {len(set(veri_alinamayanlar))} · "
            f"Eski veri: {len(set(eski_veriler))} · "
            f"Yetersiz veri: {len(set(yetersiz_veriler))} · "
            f"Düşük hacim: {len(set(dusuk_hacimliler))}"
        )

        st.success(
            f"Tarama {gecen_sure / 60:.1f} dakikada tamamlandı. "
            f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

        if sadece_al:
            ekran_tablosu = tablo[
                tablo["Sinyal"].isin(
                    ["GÜÇLÜ AL", "AL", "ERKEN AL"]
                )
            ].copy()
        else:
            ekran_tablosu = tablo.copy()

        ekran_tablosu = ekran_tablosu.head(gosterim_sayisi)

        if ekran_tablosu.empty:
            st.warning(
                "Seçilen şartlara uygun alım sinyali bulunamadı."
            )
        else:
            st.subheader(
                f"📊 En güçlü {len(ekran_tablosu)} sonuç"
            )

            st.dataframe(
                ekran_tablosu,
                use_container_width=True,
                hide_index=True,
                height=650,
                column_config={
                    "Puan": st.column_config.ProgressColumn(
                        "Puan",
                        min_value=0,
                        max_value=100,
                        format="%d",
                    ),
                    "Fiyat": st.column_config.NumberColumn(
                        "Fiyat",
                        format="₺ %.2f",
                    ),
                    "Gün İçi %": st.column_config.NumberColumn(
                        "Gün İçi %",
                        format="%.2f%%",
                    ),
                    "Dipten %": st.column_config.NumberColumn(
                        "Dipten %",
                        format="%.2f%%",
                    ),
                    "Zirveye %": st.column_config.NumberColumn(
                        "Zirveye %",
                        format="%.2f%%",
                    ),
                    "Gün İçi Dip %": st.column_config.NumberColumn(
                        "Gün İçi Dip %",
                        format="%.2f%%",
                    ),
                    "Hacim x": st.column_config.NumberColumn(
                        "Hacim x",
                        format="%.2fx",
                    ),
                    "Hacim TL": st.column_config.NumberColumn(
                        "Hacim TL",
                        format="₺ %.0f",
                    ),
                    "Stop": st.column_config.NumberColumn(
                        "Stop",
                        format="₺ %.2f",
                    ),
                    "Hedef 1": st.column_config.NumberColumn(
                        "Hedef 1",
                        format="₺ %.2f",
                    ),
                    "Hedef 2": st.column_config.NumberColumn(
                        "Hedef 2",
                        format="₺ %.2f",
                    ),
                },
            )

        csv_tumu = tablo.to_csv(
            index=False,
            sep=";",
            decimal=",",
        ).encode("utf-8-sig")

        st.download_button(
            "📥 Tüm sonuçları CSV indir",
            data=csv_tumu,
            file_name=(
                "bist_tarama_"
                + datetime.now().strftime("%Y%m%d_%H%M")
                + ".csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

        for baslik, liste in [
            ("Veri alınamayan semboller", veri_alinamayanlar),
            ("Eski verisi olan semboller", eski_veriler),
            ("Yetersiz verisi olan semboller", yetersiz_veriler),
            (
                "Minimum hacmin altında kalan semboller",
                dusuk_hacimliler,
            ),
        ]:
            if liste:
                with st.expander(
                    f"{baslik}: {len(set(liste))}"
                ):
                    st.write(", ".join(sorted(set(liste))))


# ============================================================
# BACKTEST EKRANI
# ============================================================

else:
    if not calistir:
        st.subheader("🧪 Sinyal Backtesti")

        st.write(
            """
            Backtest, geçmişte oluşan **GÜÇLÜ AL, AL ve ERKEN AL**
            sinyallerini inceler. Sinyal mumunun kapanışından sonra,
            işlemi bir sonraki mumun açılışında başlatır.
            """
        )

        st.info(
            "Saatlik ve 4 saatlik testte son 60 günlük veri; "
            "günlük testte seçilen yıl kadar veri kullanılır."
        )

        st.warning(
            "Backtest geçmiş performansı ölçer; gelecekte aynı "
            "sonucun gerçekleşeceğini garanti etmez."
        )

    else:
        semboller = [
            kod.strip().upper().replace(".IS", "")
            for kod in re.split(
                r"[,;\s]+",
                backtest_sembol_metni,
            )
            if kod.strip()
        ]

        semboller = [
            kod
            for kod in semboller
            if re.fullmatch(r"[A-Z0-9]{4,6}", kod)
        ]
        semboller = list(dict.fromkeys(semboller))[:10]

        if not semboller:
            st.error("Backtest için geçerli sembol girilmedi.")
            st.stop()

        if not sinyal_turleri:
            st.error("En az bir sinyal türü seç.")
            st.stop()

        baslangic = time.time()

        islemler, veri_alinamayanlar = backtest_calistir(
            semboller=semboller,
            zaman_dilimi=zaman_dilimi,
            gunluk_yil=gunluk_yil,
            min_puan=min_puan,
            hacim_carpani=hacim_carpani,
            min_toparlanma=min_toparlanma,
            min_hacim_tl=min_hacim_milyon * 1_000_000,
            sinyal_turleri=sinyal_turleri,
            bekleme_mumu=bekleme_mumu,
            hedef_atr=hedef_atr,
            stop_atr=stop_atr,
            maliyet_yuzde=maliyet_yuzde,
        )

        gecen_sure = time.time() - baslangic

        if islemler.empty:
            st.warning(
                "Bu ayarlarda geçmiş sinyal bulunamadı. "
                "Puanı, hacim çarpanını veya minimum hacmi azalt."
            )
            if veri_alinamayanlar:
                st.write(
                    "Veri alınamayanlar: "
                    + ", ".join(veri_alinamayanlar)
                )
            st.stop()

        net = islemler["Net Getiri %"]
        kazananlar = net[net > 0]
        kaybedenler = net[net <= 0]

        basari_orani = (
            len(kazananlar) / len(islemler) * 100
        )

        hedef_orani = (
            (islemler["Çıkış Nedeni"] == "Hedef").mean()
            * 100
        )

        toplam_getiri = (
            (1 + net / 100).prod() - 1
        ) * 100

        kar_faktoru = (
            kazananlar.sum()
            / abs(kaybedenler.sum())
            if not kaybedenler.empty
            and abs(kaybedenler.sum()) > 0
            else np.inf
        )

        maksimum_dusus = maksimum_dusus_hesapla(net)

        k1, k2, k3, k4, k5 = st.columns(5)

        k1.metric("İşlem", len(islemler))
        k2.metric("Kazanma oranı", f"%{basari_orani:.1f}")
        k3.metric("Hedefe ulaşma", f"%{hedef_orani:.1f}")
        k4.metric("Ortalama net", f"%{net.mean():.2f}")
        k5.metric("Bileşik sonuç", f"%{toplam_getiri:.2f}")

        k6, k7, k8, k9 = st.columns(4)

        k6.metric("Medyan net", f"%{net.median():.2f}")
        k7.metric(
            "Kâr faktörü",
            "∞" if np.isinf(kar_faktoru) else f"{kar_faktoru:.2f}",
        )
        k8.metric("Maksimum düşüş", f"%{maksimum_dusus:.2f}")
        k9.metric(
            "Ortalama tutma",
            f"{islemler['Tutulan Mum'].mean():.1f} mum",
        )

        st.success(
            f"Backtest {gecen_sure:.1f} saniyede tamamlandı."
        )

        st.subheader("Bileşik getiri eğrisi")

        getiri_egrisi = (
            (1 + net / 100).cumprod() - 1
        ) * 100

        grafik = pd.DataFrame(
            {
                "Bileşik Getiri %": getiri_egrisi.values
            }
        )

        st.line_chart(grafik)

        st.subheader("Sinyal türüne göre sonuç")

        sinyal_ozeti = (
            islemler
            .groupby("Sinyal", as_index=False)
            .agg(
                İşlem=("Net Getiri %", "size"),
                Kazanma_Oranı=(
                    "Net Getiri %",
                    lambda seri: (seri > 0).mean() * 100,
                ),
                Ortalama_Net=("Net Getiri %", "mean"),
                Medyan_Net=("Net Getiri %", "median"),
            )
        )

        sinyal_ozeti = sinyal_ozeti.rename(
            columns={
                "Kazanma_Oranı": "Kazanma Oranı %",
                "Ortalama_Net": "Ortalama Net %",
                "Medyan_Net": "Medyan Net %",
            }
        )

        st.dataframe(
            sinyal_ozeti.round(2),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("İşlem ayrıntıları")

        st.dataframe(
            islemler,
            use_container_width=True,
            hide_index=True,
            height=650,
            column_config={
                "Giriş": st.column_config.NumberColumn(
                    "Giriş",
                    format="₺ %.4f",
                ),
                "Stop": st.column_config.NumberColumn(
                    "Stop",
                    format="₺ %.4f",
                ),
                "Hedef": st.column_config.NumberColumn(
                    "Hedef",
                    format="₺ %.4f",
                ),
                "Çıkış": st.column_config.NumberColumn(
                    "Çıkış",
                    format="₺ %.4f",
                ),
                "Brüt Getiri %": st.column_config.NumberColumn(
                    "Brüt Getiri %",
                    format="%.2f%%",
                ),
                "Net Getiri %": st.column_config.NumberColumn(
                    "Net Getiri %",
                    format="%.2f%%",
                ),
            },
        )

        csv_backtest = islemler.to_csv(
            index=False,
            sep=";",
            decimal=",",
        ).encode("utf-8-sig")

        st.download_button(
            "📥 Backtest işlemlerini CSV indir",
            data=csv_backtest,
            file_name=(
                "bist_backtest_"
                + datetime.now().strftime("%Y%m%d_%H%M")
                + ".csv"
            ),
            mime="text/csv",
            use_container_width=True,
        )

        if veri_alinamayanlar:
            st.warning(
                "Veri alınamayan veya yetersiz geçmişi olanlar: "
                + ", ".join(veri_alinamayanlar)
            )

        st.caption(
            "Varsayım: Sinyal kapanışta oluşur, giriş bir sonraki "
            "mumun açılışındadır. Aynı mumda hedef ve stop birlikte "
            "görülürse stop önce kabul edilir. Sonuçlara işlem "
            "maliyeti düşülmüştür."
        )


st.divider()

st.caption(
    "Yatırım tavsiyesi değildir. Fiyat verileri gecikmeli, eksik "
    "veya hatalı olabilir. Tarama ve backtest sonuçları grafik "
    "üzerinden doğrulanmalıdır."
)
