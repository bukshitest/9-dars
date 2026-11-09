# -*- coding: utf-8 -*-
"""
=======================================================================
 AMALIY 9 — NAMUNA YECHIM
 “Baho funksiyasi va yuk muvozanati”
=======================================================================
 Bu fayl — ANDOZA. Qolgan topshiriqlarni xuddi shu koʻrinishda yozing:

     1) har bir variant alohida agent sinfi
     2) hammasi BIR XIL urugʻda sinaladi
     3) natija — jadval, matn emas
     4) xulosa oʻlchangan raqamga tayanadi

 Raqamlarni oʻylab topmang: jadvalga faqat dastur chiqargan qiymatni
 yozing.
=======================================================================
"""

from shahar import (AgentAsosi, Shahar, agentlar_yarat,
                    sarlavha, jadval_chop, qiyos_chop)

URUGH = 1               # bir xil buyurtmalar oqimi — halol qiyos uchun
KURYERLAR = 8
DAVOMIYLIK = 300.0      # soniya


# ----------------------------------------------------------------------
#  1-variant: faqat masofa
# ----------------------------------------------------------------------
class FaqatMasofa(AgentAsosi):
    """Agent faqat “men qancha yurishim kerak” degan savolga qaraydi."""

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None                  # navbat toʻla — rad etaman
        return self.yetib_borish(b)


# ----------------------------------------------------------------------
#  2-variant: masofa + yuk jazosi
# ----------------------------------------------------------------------
class MasofaVaYuk(AgentAsosi):
    """Agent navbati uzun boʻlsa, taklifini ataylab yomonlashtiradi.

    Shu bitta qoʻshimcha hadning taʼsirini oʻlchaymiz.
    """

    JAZO = 22.0                          # bitta navbatdagi buyurtma narxi

    def taklif(self, b, vaqt):
        if self.yuk >= self.SIGIM:
            return None
        return self.yetib_borish(b) + self.yuk * self.JAZO


# ----------------------------------------------------------------------
#  Bitta tajriba
# ----------------------------------------------------------------------
def tajriba(sinf, nom):
    agentlar = agentlar_yarat(sinf, KURYERLAR)
    sh = Shahar(agentlar, urugh=URUGH, davomiylik=DAVOMIYLIK)
    natija = sh.ishga_tushir()
    return natija, sh


# ----------------------------------------------------------------------
#  (a) Ikki baho funksiyasini solishtirish
# ----------------------------------------------------------------------
def a_qadam():
    sarlavha('(a)  Ikki baho funksiyasi bir xil buyurtmalar oqimida')
    n1, sh1 = tajriba(FaqatMasofa, 'Faqat masofa')
    n2, sh2 = tajriba(MasofaVaYuk, 'Masofa + yuk')
    qiyos_chop([('Faqat masofa', n1), ('Masofa + yuk', n2)])
    return n1, n2, sh1, sh2


# ----------------------------------------------------------------------
#  (b) Yuk agentlar boʻyicha qanday taqsimlandi
# ----------------------------------------------------------------------
def b_qadam(sh1, sh2):
    sarlavha('(b)  Har bir kuryer nechta buyurtma bajardi')
    q = []
    for a1, a2 in zip(sh1.agentlar, sh2.agentlar):
        q.append([a1.nom, a1.bajardi, a2.bajardi, a2.bajardi - a1.bajardi])
    jadval_chop(['Kuryer', 'Faqat masofa', 'Masofa + yuk', 'Farq'], q)

    v1 = [a.bajardi for a in sh1.agentlar]
    v2 = [a.bajardi for a in sh2.agentlar]
    jadval_chop(['Koʻrsatkich', 'Faqat masofa', 'Masofa + yuk'],
                [['Eng koʻp bajargan', max(v1), max(v2)],
                 ['Eng kam bajargan', min(v1), min(v2)],
                 ['Farq (maks − min)', max(v1) - min(v1), max(v2) - min(v2)]])
    return v1, v2


# ----------------------------------------------------------------------
#  (c) JAZO qiymatini tanlash
# ----------------------------------------------------------------------
def c_qadam():
    sarlavha('(c)  JAZO qiymati natijaga qanday taʼsir qiladi')
    q = []
    for jazo in (0.0, 5.0, 12.0, 22.0, 40.0, 80.0):
        class Sinov(MasofaVaYuk):
            JAZO = jazo
        agentlar = agentlar_yarat(Sinov, KURYERLAR)
        sh = Shahar(agentlar, urugh=URUGH, davomiylik=DAVOMIYLIK)
        n = sh.ishga_tushir()
        q.append([('%.0f' % jazo), n['yetkazildi'], n['xizmatsiz'],
                  '%.1f' % n['ortacha_kutish'],
                  '%.0f' % n['umumiy_masofa'],
                  '%.3f' % n['notekislik']])
    jadval_chop(['JAZO', 'Yetkazildi', 'Xizmatsiz', 'Oʻrt. kutish',
                 'Masofa', 'Notekislik'], q)
    return q


# ----------------------------------------------------------------------
#  Xulosa
# ----------------------------------------------------------------------
def xulosa(n1, n2, v1, v2, q):
    sarlavha('XULOSA')
    dk = n2['ortacha_kutish'] - n1['ortacha_kutish']
    dm = n2['umumiy_masofa'] - n1['umumiy_masofa']
    dn = n2['notekislik'] - n1['notekislik']

    print('  1. Ikkala variant ham bir xil buyurtmalar oqimida sinaldi')
    print('     (urugʻ = %d, %d kuryer, %.0f soniya). Shuning uchun farq'
          % (URUGH, KURYERLAR, DAVOMIYLIK))
    print('     tasodifga emas, baho funksiyasiga bogʻliq.')
    print('')
    print('  2. Yuk jazosi qoʻshilgach notekislik %.3f dan %.3f ga tushdi '
          '(%+.3f).' % (n1['notekislik'], n2['notekislik'], dn))
    print('     Eng koʻp va eng kam bajargan kuryer orasidagi farq %d tadan'
          % (max(v1) - min(v1)))
    print('     %d taga qisqardi.' % (max(v2) - min(v2)))
    print('')
    print('  3. Buning narxi bor: umumiy masofa %+.0f birlikka oʻzgardi,'
          % dm)
    print('     oʻrtacha kutish esa %+.1f soniyaga. Agent eng yaqin'
          % dk)
    print('     buyurtmani emas, baʼzan uzoqrogʻini oladi — chunki')
    print('     yaqinroq turgan kuryerning navbati toʻlgan.')
    print('')
    print('  4. JAZO oshgani sari notekislik kamayadi, lekin masofa')
    print('     oʻsadi. Jadvaldan koʻrinadiki, JAZO = 0 boʻlganda')
    print('     notekislik %s, JAZO = 80 boʻlganda %s.'
          % (q[0][5], q[-1][5]))
    print('     Demak bitta “eng yaxshi” qiymat yoʻq — bu muvozanat.')
    print('')
    print('  5. Eng muhimi: markaz hech qanday qoida oʻzgartirmadi.')
    print('     Faqat agentning ichki baho funksiyasi oʻzgardi va butun')
    print('     tizimning xatti-harakati boshqacha boʻldi. Koʻp agentli')
    print('     tizimda boshqaruv ana shu yerda — agentning ichida.')


def main():
    print('')
    print('#' * 72)
    print('#  NAMUNA YECHIM')
    print('#  Baho funksiyasi va yuk muvozanati')
    print('#  %d kuryer, urugʻ %d, %.0f soniya'
          % (KURYERLAR, URUGH, DAVOMIYLIK))
    print('#' * 72)

    n1, n2, sh1, sh2 = a_qadam()
    v1, v2 = b_qadam(sh1, sh2)
    q = c_qadam()
    xulosa(n1, n2, v1, v2, q)

    print('')
    print('=' * 72)
    print(' NAMUNA TUGADI.')
    print('=' * 72)


if __name__ == '__main__':
    main()
