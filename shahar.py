# -*- coding: utf-8 -*-
"""
Amaliy 9 — shahar muhiti va Contract Net dvigateli (faqat standart kutubxona)
Taqsimlangan tizimlar | 60610400 — Dasturiy injiniring

BU FAYLNI OʻZGARTIRMANG.

Bu yerda muhit bor: shahar, buyurtmalar oqimi va vaqt. Agentlar esa
sizning faylingizda yoziladi.

Muhit har bir yangi buyurtma uchun Contract Net protokolini oʻtkazadi:
    1) hamma agentga cfp yuboradi      -> agent.taklif(...)
    2) takliflarni yigʻadi             -> son yoki None (rad etish)
    3) eng kichik taklifni tanlaydi    -> agent.qabul(...)
    4) natijani qayd etadi

Simulyatsiya urugʻ (seed) bilan ishlaydi: bir xil urugʻ — bir xil
buyurtmalar oqimi. Shuning uchun ikki yechimni halol solishtirish mumkin.
"""

import math
import random
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

OLCHAM = 100.0          # shahar tomoni (shartli birlik)
QADAM = 0.5             # simulyatsiya qadami, soniya
TEZLIK = 6.0            # kuryer tezligi, birlik/soniya
SABR = 90.0             # buyurtma shuncha kutgach xizmatsiz deb belgilanadi
QAYTA = 3.0             # biriktirilmagan buyurtma uchun CFP shuncha soniyada qayta yuboriladi

# hududlar: (x0, y0, x1, y1, buyurtma oqimi — sekundiga)
HUDUDLAR = [
    ('Markaz',   0.0,  0.0, 50.0, 50.0, 0.58),
    ('2-hudud', 50.0,  0.0, 100.0, 50.0, 0.32),
    ('3-hudud',  0.0, 50.0, 50.0, 100.0, 0.18),
    ('Chekka',  50.0, 50.0, 100.0, 100.0, 0.10),
]


def masofa(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def hudud_raqami(x, y):
    for i, h in enumerate(HUDUDLAR):
        if h[1] <= x < h[3] and h[2] <= y < h[4]:
            return i
    return 0


class Buyurtma(object):
    def __init__(self, nom, x, y, t0):
        self.nom = nom
        self.x = x
        self.y = y
        self.t0 = t0            # qachon paydo boʻldi
        self.egasi = None       # qaysi agent oldi
        self.t_qabul = None     # qachon biriktirildi
        self.t_cfp = -1e9       # oxirgi CFP qachon yuborilgan
        self.t_yetkazildi = None

    @property
    def hudud(self):
        return hudud_raqami(self.x, self.y)

    def __repr__(self):
        return '<%s (%.0f, %.0f)>' % (self.nom, self.x, self.y)


class AgentAsosi(object):
    """Kuryer agentining asosi. Siz shundan meros olasiz.

    Muhit sizdan ikki narsani soʻraydi:
        taklif(b, vaqt)  — bu buyurtmani olasizmi va qanchaga?
                           son qaytarsangiz — taklif (kichik = yaxshi),
                           None qaytarsangiz — rad etish.
        qabul(b, vaqt)   — taklifingiz yutdi, buyurtma sizniki.

    Ixtiyoriy:
        bosh_vaqtda(vaqt, shahar) — navbatingiz boʻsh boʻlganda
                                    chaqiriladi (proaktivlik uchun).
    """

    SIGIM = 3               # navbatda koʻpi bilan nechta buyurtma

    def __init__(self, nom, x, y):
        self.nom = nom
        self.x = x
        self.y = y
        self.navbat = []        # qoʻlidagi buyurtmalar
        self.masofa = 0.0       # bosib oʻtgan yoʻl
        self.bajardi = 0        # yetkazilgan buyurtmalar soni
        self.rad_etdi = 0
        self.maqsad = None      # proaktiv harakat nuqtasi (ixtiyoriy)

    # ------------------------------------------------ agent qarorlari
    def taklif(self, b, vaqt):
        raise NotImplementedError('taklif() funksiyasini yozing')

    def qabul(self, b, vaqt):
        self.navbat.append(b)

    def bosh_vaqtda(self, vaqt, shahar):
        return None

    # ------------------------------------------------ yordamchilar
    def oxirgi_nuqta(self):
        """Navbatdagi oxirgi buyurtma joyi (yoki hozirgi joy)."""
        if self.navbat:
            o = self.navbat[-1]
            return (o.x, o.y)
        return (self.x, self.y)

    def yetib_borish(self, b):
        """Navbatni hisobga olib, shu buyurtmagacha boriladigan masofa."""
        x, y = self.oxirgi_nuqta()
        return masofa(x, y, b.x, b.y)

    @property
    def yuk(self):
        return len(self.navbat)

    def __repr__(self):
        return '<%s yuk=%d bajardi=%d>' % (self.nom, self.yuk, self.bajardi)


class Shahar(object):
    """Muhit: vaqt, buyurtmalar oqimi va Contract Net protokoli."""

    def __init__(self, agentlar, urugh=1, davomiylik=300.0,
                 markazlashgan=False, jurnal=False):
        self.agentlar = agentlar
        self.urugh = urugh
        self.davomiylik = davomiylik
        self.markazlashgan = markazlashgan   # True -> “eng yaqini” usuli
        self.jurnal = jurnal
        self.vaqt = 0.0
        self.navbat = []        # biriktirilmagan buyurtmalar
        self.yetkazilgan = []
        self.xizmatsiz = []
        self.hisoblagich = 0
        self.cfp_soni = 0
        self.taklif_soni = 0
        self.xabar_soni = 0
        self.tolov = {}         # agent nomi -> toʻlangan haq (auktsion uchun)

    # ------------------------------------------------ buyurtma oqimi
    def _yangi_buyurtmalar(self, rnd):
        for i, h in enumerate(HUDUDLAR):
            if rnd.random() < h[5] * QADAM:
                self.hisoblagich += 1
                x = h[1] + rnd.random() * (h[3] - h[1])
                y = h[2] + rnd.random() * (h[4] - h[2])
                b = Buyurtma('#%d' % (400 + self.hisoblagich), x, y, self.vaqt)
                self.navbat.append(b)

    # ------------------------------------------------ Contract Net
    def _biriktirish(self):
        qoldi = []
        for b in self.navbat:
            if self.vaqt - b.t_cfp < QAYTA:
                qoldi.append(b)
                continue
            b.t_cfp = self.vaqt
            if self.markazlashgan:
                gholib = self._eng_yaqini(b)
                narx = None
            else:
                gholib, narx = self._contract_net(b)
            if gholib is None:
                if self.vaqt - b.t0 > SABR:
                    self.xizmatsiz.append(b)
                else:
                    qoldi.append(b)
                continue
            b.egasi = gholib
            b.t_qabul = self.vaqt
            gholib.qabul(b, self.vaqt)
            if narx is not None:
                self.tolov[gholib.nom] = self.tolov.get(gholib.nom, 0.0) + narx
            if self.jurnal:
                print('  %6.1f s  %s -> %s%s'
                      % (self.vaqt, b.nom, gholib.nom,
                         '' if narx is None else '  (haq %.1f)' % narx))
        self.navbat = qoldi

    def _contract_net(self, b):
        """CFP yuboriladi, takliflar yigʻiladi, eng kichigi yutadi."""
        self.cfp_soni += 1
        self.xabar_soni += len(self.agentlar)       # cfp
        takliflar = []
        for a in self.agentlar:
            t = a.taklif(b, self.vaqt)
            self.xabar_soni += 1                    # propose yoki refuse
            if t is None:
                a.rad_etdi += 1
            else:
                takliflar.append((float(t), a))
                self.taklif_soni += 1
        if not takliflar:
            return (None, None)
        takliflar.sort(key=lambda p: p[0])
        self.xabar_soni += len(takliflar)           # accept + reject
        gholib = takliflar[0][1]
        # ikkinchi narx (Vickrey): agar agent VICKREY=True deb belgilangan boʻlsa
        if getattr(gholib, 'VICKREY', False) and len(takliflar) > 1:
            narx = takliflar[1][0]
        else:
            narx = takliflar[0][0]
        return (gholib, narx)

    def _eng_yaqini(self, b):
        """Markazlashgan usul: markaz hamma agentning joyini biladi."""
        eng, ed = None, 1e18
        for a in self.agentlar:
            if a.yuk >= a.SIGIM:
                continue
            d = masofa(a.x, a.y, b.x, b.y)
            if d < ed:
                ed, eng = d, a
        return eng

    # ------------------------------------------------ harakat
    def _harakat(self):
        for a in self.agentlar:
            if a.navbat:
                tg = a.navbat[0]
                d = masofa(a.x, a.y, tg.x, tg.y)
                qadam = TEZLIK * QADAM
                if d <= qadam:
                    a.masofa += d
                    a.x, a.y = tg.x, tg.y
                    a.navbat.pop(0)
                    a.bajardi += 1
                    tg.t_yetkazildi = self.vaqt
                    self.yetkazilgan.append(tg)
                else:
                    a.x += (tg.x - a.x) / d * qadam
                    a.y += (tg.y - a.y) / d * qadam
                    a.masofa += qadam
            else:
                nuqta = a.bosh_vaqtda(self.vaqt, self)
                if nuqta:
                    tx, ty = nuqta
                    d = masofa(a.x, a.y, tx, ty)
                    qadam = TEZLIK * QADAM
                    if d > 0.1:
                        k = min(qadam, d)
                        a.x += (tx - a.x) / d * k
                        a.y += (ty - a.y) / d * k
                        a.masofa += k

    # ------------------------------------------------ ishga tushirish
    def ishga_tushir(self):
        rnd = random.Random(self.urugh)
        while self.vaqt < self.davomiylik:
            self._yangi_buyurtmalar(rnd)
            self._biriktirish()
            self._harakat()
            self.vaqt += QADAM
        # qolgan biriktirilmaganlar ham xizmatsiz hisoblanadi
        self.xizmatsiz.extend(self.navbat)
        self.navbat = []
        return self.natijalar()

    # ------------------------------------------------ oʻlchovlar
    def natijalar(self):
        kutishlar = [b.t_yetkazildi - b.t0 for b in self.yetkazilgan]
        bajarganlar = [a.bajardi for a in self.agentlar]
        o = sum(bajarganlar) / float(len(bajarganlar)) if bajarganlar else 0.0
        if o > 0:
            sd = math.sqrt(sum((v - o) ** 2 for v in bajarganlar)
                           / len(bajarganlar))
            notekis = sd / o
        else:
            notekis = 0.0
        return {
            'yetkazildi': len(self.yetkazilgan),
            'xizmatsiz': len(self.xizmatsiz),
            'jami_buyurtma': self.hisoblagich,
            'ortacha_kutish': (sum(kutishlar) / len(kutishlar)
                               if kutishlar else 0.0),
            'maks_kutish': max(kutishlar) if kutishlar else 0.0,
            'umumiy_masofa': sum(a.masofa for a in self.agentlar),
            'notekislik': notekis,
            'xabarlar': self.xabar_soni,
            'cfp': self.cfp_soni,
            'takliflar': self.taklif_soni,
        }

    def agent_jadvali(self):
        return [[a.nom, a.bajardi, a.rad_etdi, round(a.masofa, 1),
                 hudud_nomi(a.x, a.y)] for a in self.agentlar]

    def hudud_taqsimoti(self):
        """Har bir hududda nechta agent turibdi."""
        son = [0] * len(HUDUDLAR)
        for a in self.agentlar:
            son[hudud_raqami(a.x, a.y)] += 1
        return son


def hudud_nomi(x, y):
    return HUDUDLAR[hudud_raqami(x, y)][0]


# ======================================================================
#  CHOP ETISH YORDAMCHILARI
# ======================================================================

def sarlavha(matn):
    print('')
    print('=' * 72)
    print(' ' + matn)
    print('=' * 72)


def jadval_chop(bosh, qatorlar):
    if not qatorlar:
        qatorlar = [['—'] * len(bosh)]
    k = [max(len(str(bosh[i])),
             max([len(str(q[i])) for q in qatorlar] or [0])) + 2
         for i in range(len(bosh))]
    chiziq = '  ' + '-' * sum(k)
    print('  ' + ''.join(str(bosh[i]).ljust(k[i]) for i in range(len(bosh))))
    print(chiziq)
    for q in qatorlar:
        print('  ' + ''.join(str(q[i]).ljust(k[i]) for i in range(len(q))))
    print(chiziq)


def natija_chop(nom, n):
    """Bitta tajriba natijasini jadval koʻrinishida chiqaradi."""
    jadval_chop(['Koʻrsatkich', nom], [
        ['Yetkazilgan buyurtma', n['yetkazildi']],
        ['Xizmatsiz qolgan', n['xizmatsiz']],
        ['Oʻrtacha kutish, s', '%.1f' % n['ortacha_kutish']],
        ['Eng uzun kutish, s', '%.1f' % n['maks_kutish']],
        ['Umumiy masofa', '%.0f' % n['umumiy_masofa']],
        ['Yuk notekisligi', '%.3f' % n['notekislik']],
        ['Xabarlar soni', n['xabarlar']],
    ])


def qiyos_chop(natijalar):
    """natijalar: [(nom, natija), ...] — yonma-yon jadval."""
    nomlar = [n for n, _ in natijalar]
    qatorlar = [
        ['Yetkazilgan'] + [str(r['yetkazildi']) for _, r in natijalar],
        ['Xizmatsiz'] + [str(r['xizmatsiz']) for _, r in natijalar],
        ['Oʻrtacha kutish, s'] + ['%.1f' % r['ortacha_kutish'] for _, r in natijalar],
        ['Eng uzun kutish, s'] + ['%.1f' % r['maks_kutish'] for _, r in natijalar],
        ['Umumiy masofa'] + ['%.0f' % r['umumiy_masofa'] for _, r in natijalar],
        ['Yuk notekisligi'] + ['%.3f' % r['notekislik'] for _, r in natijalar],
        ['Xabarlar soni'] + [str(r['xabarlar']) for _, r in natijalar],
    ]
    jadval_chop(['Koʻrsatkich'] + nomlar, qatorlar)


def agentlar_yarat(sinf, n, urugh=7):
    """n ta agentni shahar boʻylab tasodifiy joylashtiradi."""
    rnd = random.Random(urugh)
    out = []
    for i in range(n):
        out.append(sinf('K%d' % (i + 1),
                        rnd.random() * OLCHAM, rnd.random() * OLCHAM))
    return out
