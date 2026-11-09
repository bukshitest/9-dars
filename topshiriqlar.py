# -*- coding: utf-8 -*-
"""
=======================================================================
 AMALIY 9 — TOPSHIRIQLAR
 Koʻp agentli tizim: kuryerlar va Contract Net
=======================================================================
 Sakkizta topshiriq.

 QANDAY ISHLATILADI
   1. Quyidagi TOPSHIRIQ qatoriga oʻz raqamingizni yozing (1 dan 8 gacha)
   2. Shu topshiriqning sinfida TODO yozilgan joyni toʻldiring
   3. Ctrl+S bosing, soʻng Run tugmasini bosing

 Namuna masala alohida faylda:  namuna.py
 Shahar muhiti shahar.py da; uni OʻZGARTIRMANG.
=======================================================================
"""

from shahar import (AgentAsosi, Shahar, agentlar_yarat, masofa,
                    HUDUDLAR, hudud_raqami,
                    sarlavha, jadval_chop, natija_chop, qiyos_chop)

# >>>>>>>>>>>>>>>>>>>>>>  SHU YERNI OʻZGARTIRING  <<<<<<<<<<<<<<<<<<<<<
TOPSHIRIQ = 1
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

URUGH = 1               # buyurtmalar oqimi urugʻi — OʻZGARTIRMANG
KURYERLAR = 8
DAVOMIYLIK = 300.0      # soniya


# ======================================================================
#  1-TOPSHIRIQ
#  Berilgan: 100x100 shahar, 300 soniyalik buyurtmalar oqimi.
#  Talab:    Kuryer agenti buyurtmagacha boradigan masofani taklif
#            qilsin. Navbati toʻla boʻlsa rad etsin.
#            Kuryerlar sonini 4, 8 va 16 qilib natijalarni solishtiring.
# ======================================================================
class Agent1(AgentAsosi):

    def taklif(self, b, vaqt):
        # TODO 1: navbat toʻla boʻlsa None qaytaring
        #         (shart:  self.yuk >= self.SIGIM)
        # TODO 2: aks holda self.yetib_borish(b) qiymatini qaytaring
        return None


def topshiriq_1():
    sarlavha('1-TOPSHIRIQ.  Masofa boʻyicha taklif')
    q = []
    for n in (4, 8, 16):
        r = Shahar(agentlar_yarat(Agent1, n), urugh=URUGH,
                   davomiylik=DAVOMIYLIK).ishga_tushir()
        q.append([n, r['yetkazildi'], r['xizmatsiz'],
                  '%.1f' % r['ortacha_kutish'],
                  '%.0f' % r['umumiy_masofa'],
                  '%.3f' % r['notekislik'], r['xabarlar']])
    jadval_chop(['Kuryer', 'Yetkazildi', 'Xizmatsiz', 'Oʻrt. kutish',
                 'Masofa', 'Notekislik', 'Xabarlar'], q)


# ======================================================================
#  2-TOPSHIRIQ
#  Berilgan: 8 ta kuryer, baho funksiyasi = masofa + navbat jazosi.
#  Talab:    Kuryerning navbat sigʻimini (SIGIM) 1, 2, 3 va 5 qilib
#            oʻzgartiring. Sigʻim qaysi qiymatdan keyin natijaga
#            taʼsir qilmay qoʻyishini aniqlang.
# ======================================================================
class Agent2(AgentAsosi):

    JAZO = 22.0

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        # TODO: self.yetib_borish(b) ga self.yuk * self.JAZO ni qoʻshing
        return None


def topshiriq_2():
    sarlavha('2-TOPSHIRIQ.  Navbat sigʻimi')
    q = []
    for sigim in (1, 2, 3, 5):
        class Sinov(Agent2):
            SIGIM = sigim
        r = Shahar(agentlar_yarat(Sinov, KURYERLAR), urugh=URUGH,
                   davomiylik=DAVOMIYLIK).ishga_tushir()
        q.append([sigim, r['yetkazildi'], r['xizmatsiz'],
                  '%.1f' % r['ortacha_kutish'], '%.1f' % r['maks_kutish'],
                  '%.0f' % r['umumiy_masofa'], '%.3f' % r['notekislik']])
    jadval_chop(['SIGIM', 'Yetkazildi', 'Xizmatsiz', 'Oʻrt. kutish',
                 'Eng uzun', 'Masofa', 'Notekislik'], q)


# ======================================================================
#  3-TOPSHIRIQ
#  Berilgan: 8 ta kuryer.
#  Talab:    Agent buyurtmagacha boradigan masofa CHEGARA dan katta
#            boʻlsa rad etsin. CHEGARA = 100, 40, 25 va 15 uchun
#            oʻlchang. Xizmatsiz buyurtmalar qaysi qiymatdan boshlab
#            paydo boʻlishini aniqlang.
# ======================================================================
class Agent3(AgentAsosi):

    CHEGARA = 100.0

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        d = self.yetib_borish(b)
        # TODO: d qiymati self.CHEGARA dan katta boʻlsa None qaytaring
        return d


def topshiriq_3():
    sarlavha('3-TOPSHIRIQ.  Rad etish chegarasi')
    q = []
    for chegara in (100.0, 40.0, 25.0, 15.0):
        class Sinov(Agent3):
            CHEGARA = chegara
        sh = Shahar(agentlar_yarat(Sinov, KURYERLAR), urugh=URUGH,
                    davomiylik=DAVOMIYLIK)
        r = sh.ishga_tushir()
        rad = sum(a.rad_etdi for a in sh.agentlar)
        q.append(['%.0f' % chegara, r['yetkazildi'], r['xizmatsiz'], rad,
                  '%.1f' % r['ortacha_kutish'],
                  '%.0f' % r['umumiy_masofa']])
    jadval_chop(['CHEGARA', 'Yetkazildi', 'Xizmatsiz', 'Rad etishlar',
                 'Oʻrt. kutish', 'Masofa'], q)


# ======================================================================
#  4-TOPSHIRIQ
#  Berilgan: smena 300 soniya davom etadi.
#  Talab:    Agent smenaning OXIRGI 60 soniyasida UZOQ dan uzoq
#            buyurtmalarni rad etsin (uyiga yaqin tugatishi uchun).
#            UZOQ = cheksiz, 40, 25 va 15 uchun oʻlchang.
#  Eslatma:  taklif() ga vaqt argumenti keladi — joriy soniya.
# ======================================================================
class Agent4(AgentAsosi):

    JAZO = 22.0
    OXIR = 60.0             # smenaning oxirgi necha soniyasi
    UZOQ = 1e9              # shundan uzoq buyurtma rad etiladi

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        d = self.yetib_borish(b)
        # TODO: agar  vaqt > DAVOMIYLIK - self.OXIR  VA  d > self.UZOQ
        #       boʻlsa, None qaytaring
        return d + self.yuk * self.JAZO


def topshiriq_4():
    sarlavha('4-TOPSHIRIQ.  Smena oxirida uzoq buyurtmani rad etish')
    q = []
    for uzoq in (1e9, 40.0, 25.0, 15.0):
        class Sinov(Agent4):
            UZOQ = uzoq
        sh = Shahar(agentlar_yarat(Sinov, KURYERLAR), urugh=URUGH,
                    davomiylik=DAVOMIYLIK)
        r = sh.ishga_tushir()
        rad = sum(a.rad_etdi for a in sh.agentlar)
        q.append(['cheksiz' if uzoq > 1e8 else '%.0f' % uzoq,
                  r['yetkazildi'], r['xizmatsiz'], rad,
                  '%.1f' % r['ortacha_kutish'],
                  '%.0f' % r['umumiy_masofa']])
    jadval_chop(['UZOQ', 'Yetkazildi', 'Xizmatsiz', 'Rad etishlar',
                 'Oʻrt. kutish', 'Masofa'], q)


# ======================================================================
#  5-TOPSHIRIQ
#  Berilgan: bir xil agentlar va bir xil buyurtmalar oqimi.
#  Talab:    Ikki rejimni solishtiring:
#              markazlashgan=False — agentlar taklif beradi
#              markazlashgan=True  — markaz eng yaqinini oʻzi tanlaydi
#            Qaysi usul yaxshiroq ishlashini va buning narxini aniqlang.
# ======================================================================
class Agent5(AgentAsosi):

    JAZO = 22.0

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        # TODO: masofa + yuk jazosi
        return None


def topshiriq_5():
    sarlavha('5-TOPSHIRIQ.  Markazlashgan va taqsimlangan')
    n1 = Shahar(agentlar_yarat(Agent5, KURYERLAR), urugh=URUGH,
                davomiylik=DAVOMIYLIK, markazlashgan=False).ishga_tushir()
    n2 = Shahar(agentlar_yarat(Agent5, KURYERLAR), urugh=URUGH,
                davomiylik=DAVOMIYLIK, markazlashgan=True).ishga_tushir()
    qiyos_chop([('Contract Net', n1), ('Markazlashgan', n2)])


# ======================================================================
#  6-TOPSHIRIQ
#  Berilgan: 4 ta halol va 4 ta yolgʻonchi kuryer bitta shaharda.
#            Halol rost masofani aytadi, yolgʻonchi uni 0,6 ga
#            koʻpaytirib aytadi.
#  Talab:    Ikki toʻlov qoidasini solishtiring:
#              VICKREY = True  — gʻolibga IKKINCHI eng yaxshi taklif
#                                boʻyicha haq toʻlanadi
#              VICKREY = False — gʻolibga oʻz taklifi boʻyicha
#            Yolgʻon gapirish foyda keltiradimi — aniqlang.
# ======================================================================
class Halol(AgentAsosi):
    VICKREY = True

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        # TODO: rost qiymat — self.yetib_borish(b)
        return None


class Yolgonchi(AgentAsosi):
    VICKREY = True
    KOEF = 0.6

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        # TODO: rost qiymatni self.KOEF ga koʻpaytiring
        return None


def topshiriq_6():
    sarlavha('6-TOPSHIRIQ.  Vickrey auktsioni')
    for vick in (True, False):
        class H(Halol):
            VICKREY = vick

        class Y(Yolgonchi):
            VICKREY = vick

        halollar = agentlar_yarat(H, 4)
        yolgonchilar = agentlar_yarat(Y, 4, urugh=11)
        for i, a in enumerate(yolgonchilar):
            a.nom = 'Y%d' % (i + 1)
        hamma = halollar + yolgonchilar

        sh = Shahar(hamma, urugh=URUGH, davomiylik=DAVOMIYLIK)
        sh.ishga_tushir()

        print('')
        print('  --- %s' % ('IKKINCHI NARX (Vickrey)' if vick
                            else 'BIRINCHI NARX'))
        q = []
        for a in hamma:
            haq = sh.tolov.get(a.nom, 0.0)
            foyda = haq - a.masofa
            q.append([a.nom, 'halol' if isinstance(a, H) else 'yolgʻonchi',
                      a.bajardi, '%.0f' % a.masofa, '%.0f' % haq,
                      '%.0f' % foyda,
                      '%.1f' % (foyda / a.bajardi if a.bajardi else 0.0)])
        jadval_chop(['Agent', 'Turi', 'Bajardi', 'Masofa', 'Olgan haq',
                     'Foyda', 'Bitta buyurtmaga'], q)


# ======================================================================
#  7-TOPSHIRIQ
#  Berilgan: shahar toʻrtta hududga boʻlingan.
#  Talab:    Agent faqat OʻZI TURGAN HUDUDDAGI buyurtmalarni olsin,
#            boshqa hududdagilarni rad etsin. Shu cheklov bilan va
#            usiz natijalarni solishtiring.
#  Eslatma:  agentning hududi — hudud_raqami(self.x, self.y)
#            buyurtmaning hududi — b.hudud
# ======================================================================
class Agent7(AgentAsosi):

    JAZO = 22.0
    QATIY = True            # hudud cheklovi yoqilganmi

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        if self.QATIY:
            # TODO: agentning hududi buyurtmaning hududiga teng
            #       boʻlmasa, None qaytaring
            pass
        return self.yetib_borish(b) + self.yuk * self.JAZO


def topshiriq_7():
    sarlavha('7-TOPSHIRIQ.  Hududga biriktirish')
    q = []
    for qatiy in (False, True):
        class Sinov(Agent7):
            QATIY = qatiy
        r = Shahar(agentlar_yarat(Sinov, KURYERLAR), urugh=URUGH,
                   davomiylik=DAVOMIYLIK).ishga_tushir()
        q.append(['bor' if qatiy else 'yoʻq', r['yetkazildi'],
                  r['xizmatsiz'], '%.1f' % r['ortacha_kutish'],
                  '%.0f' % r['umumiy_masofa'],
                  '%.3f' % r['notekislik'], r['xabarlar']])
    jadval_chop(['Hudud cheklovi', 'Yetkazildi', 'Xizmatsiz',
                 'Oʻrt. kutish', 'Masofa', 'Notekislik', 'Xabarlar'], q)


# ======================================================================
#  8-TOPSHIRIQ
#  Berilgan: 16 ta kuryer. bosh_vaqtda() agentning navbati boʻsh
#            boʻlganda chaqiriladi va (x, y) nuqtasini qaytarsa, agent
#            oʻsha tomonga siljiydi.
#  Talab:    Agent eng koʻp buyurtma chiqadigan hudud markaziga borsin.
#            Soʻng shu qoidaga tuzatish kiriting: hududdagi agentlar
#            soni uning jozibadorligini kamaytirsin (SALBIY = True).
#            Ikki holatda kuryerlar qayerda toʻplanishini oʻlchang.
# ======================================================================
class Agent8(AgentAsosi):

    JAZO = 22.0
    SALBIY = False

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        return self.yetib_borish(b) + self.yuk * self.JAZO

    def bosh_vaqtda(self, vaqt, shahar):
        taqsimot = shahar.hudud_taqsimoti()
        eng, eng_joziba = None, -1.0
        for i, h in enumerate(HUDUDLAR):
            joziba = h[5]                  # shu hududdagi buyurtma oqimi
            if self.SALBIY:
                son = taqsimot[i]
                # TODO 1: joziba ni (1.0 + son) ga boʻling
                pass
            if joziba > eng_joziba:
                eng_joziba, eng = joziba, i
        h = HUDUDLAR[eng]
        # TODO 2: shu hududning markazini qaytaring:
        #         ((h[1] + h[3]) / 2,  (h[2] + h[4]) / 2)
        return None


def topshiriq_8():
    sarlavha('8-TOPSHIRIQ.  Hududlarga oʻzi taqsimlanish')
    q = []
    for salbiy in (False, True):
        class Sinov(Agent8):
            SALBIY = salbiy
        sh = Shahar(agentlar_yarat(Sinov, 16), urugh=URUGH,
                    davomiylik=DAVOMIYLIK)
        r = sh.ishga_tushir()
        q.append(['bor' if salbiy else 'yoʻq'] +
                 [str(t) for t in sh.hudud_taqsimoti()] +
                 ['%.1f' % r['ortacha_kutish'], '%.1f' % r['maks_kutish'],
                  '%.0f' % r['umumiy_masofa']])
    jadval_chop(['Salbiy aloqa'] + [h[0] for h in HUDUDLAR] +
                ['Oʻrt. kutish', 'Eng uzun', 'Masofa'], q)


# ======================================================================
def main():
    print('')
    print('#' * 72)
    print('#  AMALIY 9 — TOPSHIRIQ %d' % TOPSHIRIQ)
    print('#  %d kuryer, urugʻ %d, %.0f soniya'
          % (KURYERLAR, URUGH, DAVOMIYLIK))
    print('#' * 72)

    funk = {1: topshiriq_1, 2: topshiriq_2, 3: topshiriq_3,
            4: topshiriq_4, 5: topshiriq_5, 6: topshiriq_6,
            7: topshiriq_7, 8: topshiriq_8}.get(TOPSHIRIQ)
    if funk is None:
        print('  TOPSHIRIQ 1 dan 8 gacha boʻlishi kerak.')
        return
    funk()

    print('')
    print('=' * 72)
    print(' TUGADI.')
    print('=' * 72)


if __name__ == '__main__':
    main()
