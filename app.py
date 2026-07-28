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
    "Borsa İstanbul hisselerini toplu olarak tarar ve "
    "dipten dönüş ihtimali güçlü olanları puanlar."
)


# ============================================================
# YEDEK BIST HİSSE LİSTESİ
# KAP listesi alınamazsa bu liste kullanılır.
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
UFUK ULAS ULUFA ULUSE ULKER ULUSE UNLU USAK VAKBN VAKFN
VAKKO VANGD VBTYZ VERTU VERUS VESBE VESTL VKFYO VKGYO YAPRK
YATAS YAYLA YEOTK YESIL YGGYO YGYO YKBNK YONGA YUNSA YYAPI
YYLGD ZEDUR ZOREN ZRGYO
""".split()


# ============================================================
# KAP'TAN GÜNCEL HİSSE LİSTESİ
# ============================================================

@st.cache_data(ttl=21600, show_spinner=False)
def kap_hisselerini_getir() -> tuple[list[str], str]:
    """
    KAP BIST şirketleri sayfasından hisse kodlarını almaya çalışır.
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
        cevap = requests.get(
            url,
            headers=headers,
            timeout=25,
        )
        cevap.raise_for_status()

        soup = BeautifulSoup(cevap.text, "html.parser")

        bulunanlar: set[str] = set()

        # Sayfadaki görünen metinlerden sembol yakalama
        for metin in soup.stripped_strings:
            metin = metin.strip().upper()

            if re.fullmatch(r"[A-Z0-9]{4,6}", metin):
                bulunanlar.add(metin)

        # Linklerin içindeki kodlardan yakalama
        for link in soup.find_all("a", href=True):
            yazi = link.get_text(" ", strip=True).upper()

            for kod in re.findall(
                r"\b[A-Z][A-Z0-9]{3,5}\b",
                yazi,
            ):
                bulunanlar.add(kod)

        # Hisse sembolüne benzemeyen genel kelimeler
        yasakli = {
            "KAP",
            "BIST",
            "SIRKET",
            "ŞİRKET",
            "ISTANBUL",
            "İSTANBUL",
            "ANKARA",
            "BURSA",
            "IZMIR",
            "İZMİR",
            "DENET",
            "KPMG",
            "PRICE",
            "EMAIL",
            "PHONE",
            "LOGIN",
            "INDEX",
            "HTTPS",
        }

        bulunanlar = {
            kod
            for kod in bulunanlar
            if kod not in yasakli
            and 4 <= len(kod) <= 6
            and kod[0].isalpha()
        }

        # KAP'tan gerçekçi büyüklükte liste geldiyse kullan
        if len(bulunanlar) >= 350:
            return sorted(bulunanlar), "KAP güncel listesi"

    except Exception:
        pass

    return sorted(set(YEDEK_HISSELER)), "Yedek BIST listesi"


# ============================================================
# GÖSTERGELER
# ============================================================

def rsi_hesapla(
    kapanis: pd.Series,
    periyot: int = 14,
) -> pd.Series:
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

    para_hacmi = para_carpani * hacim

    return (
        para_hacmi.rolling(periyot).sum()
        / hacim.rolling(periyot).sum().replace(0, np.nan)
    )


def obv_hesapla(
    kapanis: pd.Series,
    hacim: pd.Series,
) -> pd.Series:
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
        veri[sutun] = pd.to_numeric(
            veri[sutun],
            errors="coerce",
        )

    veri = veri.dropna(
        subset=["Open", "High", "Low", "Close"]
    )

    veri["Volume"] = veri["Volume"].fillna(0)

    veri = veri[
        ~veri.index.duplicated(keep="last")
    ].sort_index()

    return veri


# ============================================================
# 4 SAATLİK MUM OLUŞTURMA
# ============================================================

def dort_saatlik_yap(
    veri: pd.DataFrame,
) -> pd.DataFrame:
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
            grup_satirlari = gun.iloc[
                np.where(grup == grup_no)[0]
            ]
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
    yahoo_sembolleri = [
        f"{sembol}.IS"
        for sembol in semboller
    ]

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
                toplu_veri.columns
                .get_level_values(0)
                .unique()
                .tolist()
            )

            ikinci_seviye = (
                toplu_veri.columns
                .get_level_values(1)
                .unique()
                .tolist()
            )

            if yahoo_sembol in birinci_seviye:
                hisse_verisi = toplu_veri[yahoo_sembol].copy()

            elif yahoo_sembol in ikinci_seviye:
                hisse_verisi = (
                    toplu_veri
                    .xs(
                        yahoo_sembol,
                        axis=1,
                        level=1,
                    )
                    .copy()
                )

            else:
                return pd.DataFrame()

        else:
            # Grupta tek sembol kaldıysa normal sütun gelebilir
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
) -> dict | None:
    if zaman_dilimi == "4 Saat":
        veri = dort_saatlik_yap(veri)

    if veri.empty or len(veri) < 55:
        return None

    veri = veri.copy()

    veri["EMA7"] = veri["Close"].ewm(
        span=7,
        adjust=False,
    ).mean()

    veri["EMA21"] = veri["Close"].ewm(
        span=21,
        adjust=False,
    ).mean()

    veri["EMA50"] = veri["Close"].ewm(
        span=50,
        adjust=False,
    ).mean()

    veri["RSI"] = rsi_hesapla(
        veri["Close"],
        14,
    )

    veri["ATR"] = atr_hesapla(
        veri["High"],
        veri["Low"],
        veri["Close"],
        14,
    )

    veri["HacimOrt20"] = (
        veri["Volume"].rolling(20).mean()
    )

    veri["OBV"] = obv_hesapla(
        veri["Close"],
        veri["Volume"],
    )

    veri["CMF"] = cmf_hesapla(
        veri["High"],
        veri["Low"],
        veri["Close"],
        veri["Volume"],
        20,
    )

    veri["MACD"] = (
        veri["Close"].ewm(
            span=12,
            adjust=False,
        ).mean()
        -
        veri["Close"].ewm(
            span=26,
            adjust=False,
        ).mean()
    )

    veri["MACDSinyal"] = veri["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    veri = veri.dropna().copy()

    if len(veri) < 3:
        return None

    son = veri.iloc[-1]
    onceki = veri.iloc[-2]

    fiyat = float(son["Close"])
    acilis = float(son["Open"])
    yuksek = float(son["High"])
    dusuk = float(son["Low"])
    hacim = float(son["Volume"])

    if fiyat <= 0:
        return None

    hacim_tl = fiyat * hacim

    if hacim_tl < min_hacim_tl:
        return None

    ema7 = float(son["EMA7"])
    ema21 = float(son["EMA21"])
    ema50 = float(son["EMA50"])

    rsi = float(son["RSI"])
    onceki_rsi = float(onceki["RSI"])

    atr = float(son["ATR"])
    cmf = float(son["CMF"])

    hacim_ort = float(son["HacimOrt20"])

    hacim_orani = (
        hacim / hacim_ort
        if hacim_ort > 0
        else 0
    )

    son_gun = veri.index[-1].date()

    gun_verisi = veri[
        pd.Index(veri.index.date) == son_gun
    ]

    if gun_verisi.empty:
        return None

    gun_acilis = float(gun_verisi.iloc[0]["Open"])
    gun_dusuk = float(gun_verisi["Low"].min())
    gun_yuksek = float(gun_verisi["High"].max())

    gunluk_degisim = (
        (fiyat / gun_acilis) - 1
    ) * 100

    dipten_toparlanma = (
        (fiyat / gun_dusuk) - 1
    ) * 100

    zirveye_uzaklik = (
        (fiyat / gun_yuksek) - 1
    ) * 100

    mum_araligi = yuksek - dusuk
    mum_govdesi = abs(fiyat - acilis)

    govde_orani = (
        mum_govdesi / mum_araligi
        if mum_araligi > 0
        else 0
    )

    alt_fitil = (
        min(acilis, fiyat) - dusuk
    )

    alt_fitil_orani = (
        alt_fitil / mum_araligi
        if mum_araligi > 0
        else 0
    )

    atr_yuzde = (
        atr / fiyat
    ) * 100

    # --------------------------------------------------------
    # KOŞULLAR
    # --------------------------------------------------------

    satis_baskisi = (
        -10 <= gunluk_degisim <= 2
    )

    dipten_donus = (
        dipten_toparlanma
        >= min_toparlanma
    )

    hacimli = (
        hacim_orani >= hacim_carpani
    )

    yesil_mum = fiyat > acilis

    guclu_govde = (
        yesil_mum
        and govde_orani >= 0.45
    )

    alt_fitil_var = (
        alt_fitil_orani >= 0.25
    )

    rsi_donusu = (
        25 <= rsi <= 68
        and rsi > onceki_rsi
    )

    ema7_ustu = fiyat > ema7
    ema21_ustu = fiyat > ema21

    ema21_geri_alindi = (
        fiyat > ema21
        and float(onceki["Close"])
        <= float(onceki["EMA21"])
    )

    ema50_yakin = (
        fiyat >= ema50 * 0.97
    )

    obv_yukseliyor = (
        float(son["OBV"])
        > float(onceki["OBV"])
    )

    cmf_olumlu = cmf > 0

    macd_gucleniyor = (
        float(son["MACD"])
        > float(onceki["MACD"])
    )

    macd_sinyal_ustu = (
        float(son["MACD"])
        > float(son["MACDSinyal"])
    )

    onceki_tepe_kirildi = (
        fiyat > float(onceki["High"])
    )

    atr_uygun = (
        0.7 <= atr_yuzde <= 10
    )

    # --------------------------------------------------------
    # PUAN
    # --------------------------------------------------------

    puan = 0
    nedenler = []

    if satis_baskisi:
        puan += 7
        nedenler.append("Satış baskısı")

    if dipten_donus:
        puan += 18
        nedenler.append("Dipten toparlanma")

    if hacimli:
        puan += 15
        nedenler.append("Hacim artışı")

    if yesil_mum:
        puan += 5
        nedenler.append("Yeşil mum")

    if guclu_govde:
        puan += 9
        nedenler.append("Güçlü gövde")

    if alt_fitil_var:
        puan += 5
        nedenler.append("Dipten alım")

    if rsi_donusu:
        puan += 10
        nedenler.append("RSI dönüşü")

    if ema7_ustu:
        puan += 5
        nedenler.append("EMA7 üstü")

    if ema21_ustu:
        puan += 5
        nedenler.append("EMA21 üstü")

    if ema21_geri_alindi:
        puan += 5
        nedenler.append("EMA21 geri alındı")

    if ema50_yakin:
        puan += 3
        nedenler.append("EMA50 yakın")

    if obv_yukseliyor:
        puan += 4
        nedenler.append("OBV yükseliyor")

    if cmf_olumlu:
        puan += 4
        nedenler.append("CMF olumlu")

    if macd_gucleniyor:
        puan += 3
        nedenler.append("MACD güçleniyor")

    if macd_sinyal_ustu:
        puan += 3
        nedenler.append("MACD sinyal üstü")

    if onceki_tepe_kirildi:
        puan += 2
        nedenler.append("Önceki tepe kırıldı")

    if atr_uygun:
        puan += 2
        nedenler.append("ATR uygun")

    puan = min(puan, 100)

    if puan >= 82:
        sinyal = "GÜÇLÜ AL"
    elif puan >= min_puan:
        sinyal = "AL"
    elif puan >= min_puan - 10:
        sinyal = "İZLE"
    else:
        sinyal = "ZAYIF"

    stop = max(
        fiyat - atr * 1.2,
        0,
    )

    hedef1 = fiyat + atr * 1.5
    hedef2 = fiyat + atr * 2.5

    return {
        "Sembol": sembol,
        "Sinyal": sinyal,
        "Puan": int(puan),
        "Fiyat": round(fiyat, 2),
        "Günlük %": round(gunluk_degisim, 2),
        "Dipten %": round(dipten_toparlanma, 2),
        "Zirveye %": round(zirveye_uzaklik, 2),
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
        "Son Mum": veri.index[-1].strftime(
            "%d.%m.%Y %H:%M"
        ),
    }


# ============================================================
# YAN MENÜ
# ============================================================

hisse_listesi, liste_kaynagi = kap_hisselerini_getir()

with st.sidebar:
    st.header("⚙️ Tarama Ayarları")

    st.info(
        f"Liste kaynağı: {liste_kaynagi}\n\n"
        f"Bulunan sembol: {len(hisse_listesi)}"
    )

    tarama_turu = st.selectbox(
        "Tarama listesi",
        [
            "Tüm BIST",
            "İlk 100 hisse",
            "Özel liste",
        ],
        index=0,
    )

    zaman_dilimi = st.selectbox(
        "Zaman dilimi",
        [
            "1 Saat",
            "4 Saat",
            "1 Gün",
        ],
        index=0,
    )

    min_puan = st.slider(
        "Minimum AL puanı",
        min_value=40,
        max_value=90,
        value=65,
        step=5,
    )

    hacim_carpani = st.slider(
        "Minimum hacim çarpanı",
        min_value=0.5,
        max_value=4.0,
        value=1.2,
        step=0.1,
    )

    min_toparlanma = st.slider(
        "Dipten minimum toparlanma",
        min_value=0.5,
        max_value=10.0,
        value=1.0,
        step=0.1,
        format="%.1f%%",
    )

    min_hacim_milyon = st.slider(
        "Minimum mum hacmi",
        min_value=0,
        max_value=100,
        value=2,
        step=1,
        format="%d milyon TL",
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
        "Sadece AL sinyallerini göster",
        value=True,
    )

    ozel_liste = st.text_area(
        "Özel hisse listesi",
        value="GEREL, ASTOR, MIATK, PATEK, FORTE",
        height=120,
        disabled=tarama_turu != "Özel liste",
    )

    tara = st.button(
        "🔍 Taramayı Başlat",
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
# ANA SAYFA
# ============================================================

if not tara:
    kolon1, kolon2, kolon3 = st.columns(3)

    kolon1.metric(
        "Taranabilir hisse",
        len(hisse_listesi),
    )

    kolon2.metric(
        "Varsayılan zaman",
        "1 Saat",
    )

    kolon3.metric(
        "Varsayılan AL puanı",
        "65",
    )

    st.info(
        "Sol menüden **Tüm BIST** seçiliyken "
        "**Taramayı Başlat** düğmesine bas."
    )

    st.subheader("Algoritmanın aradığı hareket")

    st.write(
        """
        **Sert satış veya gün içi baskı → dipten alım → hacim artışı →  
        RSI dönüşü → EMA seviyelerinin geri alınması → para girişinin güçlenmesi**
        """
    )

    st.warning(
        "500 civarı hisse taraması birkaç dakika sürebilir. "
        "Tarama bitene kadar sayfayı kapatma."
    )

else:
    if tarama_turu == "Tüm BIST":
        taranacaklar = hisse_listesi

    elif tarama_turu == "İlk 100 hisse":
        taranacaklar = hisse_listesi[:100]

    else:
        taranacaklar = [
            kod.strip()
            .upper()
            .replace(".IS", "")
            for kod in re.split(
                r"[,;\s]+",
                ozel_liste,
            )
            if kod.strip()
        ]

    taranacaklar = list(
        dict.fromkeys(taranacaklar)
    )

    if not taranacaklar:
        st.error("Taranacak hisse bulunamadı.")
        st.stop()

    st.write(
        f"**{len(taranacaklar)} hisse taranacak.**"
    )

    ilerleme = st.progress(0)
    durum = st.empty()
    sonuc_alani = st.empty()

    sonuclar = []
    veri_alinamayanlar = []

    baslangic = time.time()

    gruplar = [
        taranacaklar[i:i + grup_boyutu]
        for i in range(
            0,
            len(taranacaklar),
            grup_boyutu,
        )
    ]

    tamamlanan = 0

    for grup_no, grup in enumerate(
        gruplar,
        start=1,
    ):
        durum.info(
            f"Grup {grup_no}/{len(gruplar)} indiriliyor… "
            f"Toplam tamamlanan: {tamamlanan}/{len(taranacaklar)}"
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
                    sonuc = hisseyi_analiz_et(
                        sembol=sembol,
                        veri=hisse_verisi,
                        zaman_dilimi=zaman_dilimi,
                        min_puan=min_puan,
                        hacim_carpani=hacim_carpani,
                        min_toparlanma=min_toparlanma,
                        min_hacim_tl=(
                            min_hacim_milyon
                            * 1_000_000
                        ),
                    )

                    if sonuc is not None:
                        sonuclar.append(sonuc)

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
            f"Şu ana kadar {len(sonuclar)} geçerli sonuç bulundu."
        )

        time.sleep(0.5)

    ilerleme.empty()
    durum.empty()
    sonuc_alani.empty()

    gecen_sure = time.time() - baslangic

    if not sonuclar:
        st.error(
            "Geçerli sonuç bulunamadı. Yahoo Finance geçici olarak "
            "veri göndermemiş olabilir. Önbelleği temizleyip yeniden dene."
        )
        st.stop()

    tablo = pd.DataFrame(sonuclar)

    sinyal_sirasi = {
        "GÜÇLÜ AL": 1,
        "AL": 2,
        "İZLE": 3,
        "ZAYIF": 4,
    }

    tablo["_sira"] = tablo["Sinyal"].map(
        sinyal_sirasi
    )

    tablo = (
        tablo
        .sort_values(
            by=[
                "_sira",
                "Puan",
                "Hacim x",
                "Dipten %",
            ],
            ascending=[
                True,
                False,
                False,
                False,
            ],
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

    izle_sayisi = int(
        (tablo["Sinyal"] == "İZLE").sum()
    )

    kolon1, kolon2, kolon3, kolon4 = st.columns(4)

    kolon1.metric(
        "Taranan",
        len(taranacaklar),
    )

    kolon2.metric(
        "Güçlü AL",
        guclu_al_sayisi,
    )

    kolon3.metric(
        "AL",
        al_sayisi,
    )

    kolon4.metric(
        "İzle",
        izle_sayisi,
    )

    st.success(
        f"Tarama {gecen_sure / 60:.1f} dakikada tamamlandı. "
        f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )

    if sadece_al:
        ekran_tablosu = tablo[
            tablo["Sinyal"].isin(
                ["GÜÇLÜ AL", "AL"]
            )
        ].copy()
    else:
        ekran_tablosu = tablo.copy()

    ekran_tablosu = ekran_tablosu.head(
        gosterim_sayisi
    )

    if ekran_tablosu.empty:
        st.warning(
            "Seçilen şartlara uygun AL sinyali bulunamadı. "
            "Minimum AL puanını 60'a veya hacim çarpanını 1,0'a düşür."
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
                "Günlük %": st.column_config.NumberColumn(
                    "Günlük %",
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
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Tüm sonuçları CSV indir",
        data=csv_tumu,
        file_name=(
            "bist_500_tarama_"
            + datetime.now().strftime("%Y%m%d_%H%M")
            + ".csv"
        ),
        mime="text/csv",
        use_container_width=True,
    )

    if veri_alinamayanlar:
        with st.expander(
            f"Veri alınamayan semboller: "
            f"{len(set(veri_alinamayanlar))}"
        ):
            st.write(
                ", ".join(
                    sorted(
                        set(veri_alinamayanlar)
                    )
                )
            )


st.divider()

st.caption(
    "Yatırım tavsiyesi değildir. Fiyat verileri gecikmeli, "
    "eksik veya hatalı olabilir. Sinyaller gerçekleşmeden "
    "önce mutlaka grafik üzerinden kontrol edilmelidir."
)
