#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = u'Maxime DIVO'
__copyright__ = u'Copyright 2015, Maxime DIVO'
__credits__ = [u'Maxime DIVO']

__license__ = u'GPL v3'
__version__ = u'0.1.2'
__maintainer__ = u'Maxime DIVO'
__email__ = u'maxime.divo@gmail.com'
__status__ = u'Development'

"""
NOTE:


"""

""" Import """
import math as m

""" Constantes """
# Conducteur
PH1 = 0
PH2 = 1
PH3 = 2
N = 3
PE = 4

# Rho (Résistivitées)
CUIVRE = 18.51 # 18,51 mΩ. mm² / m
ALUMINIUM = 29.41 # 29,41 mΩ. mm² / m

RHO_0 = 0
RHO_1 = 1
RHO_2 = 2
RHO_3 = 3

COS_PHI = 0.8
SIN_PHI = 0.6

# SOURCES
S_TRANS = 1000.
UN = 400.
UCC_MAX = 0.06 # /!\ Str > 630kVA -> 6% / Str <= 630kVA -> 4%
UCC_MIN = 0.04 # /!\ Str > 630kVA -> 6% / Str <= 630kVA -> 4%
M = 1.05
CMAX = 1.05
CMIN = 0.95

COEF_RQ = 0.100
COEF_XQ = 0.995

COEF_RT = 0.31
COEF_XT = 0.95

IKa = 3. #kA
SKQ_DEFVAL = 250000.

# Protections
FUSIBLE = 1
DISJONCTEUR = 2

gG = 4.
aM = 4.55

B = 5.
C = 10.
D = 20.

""" Fonctions"""
def courant_neutre(i=list([0,0,0,0])):
    return ((i[PH1] + i[PH2] * m.cos(-2 * m.pi / 3) + i[PH3] * m.cos(2 * m.pi / 3)) ** 2 +\
           (i[PH2] * m.sin( -2 * m.pi / 3) + i[PH3] * m.sin(2 * m.pi / 3)) ** 2) ** 0.5

def add(x, y):
    return x + y

def rotation_phase(ph):
    ph = int(ph)
    ph += 1
    if 0 < ph <= 3:
        return ph
    else:
        return 1
        
""" Base class"""

class Item(object):
    """
    Classe de base décrivant un élément d'un arbre
    """
    def __init__(self, parent=None):
        super(Item, self).__init__();
        self.parent = parent
        self.index_1 = None
        self.index_2 = None
        self.level = None
        self._tree = None
    
    def count_childs(self):
        return int((self.index_2 - self.index_1 - 1) / 2)
    
    def __repr__(self):
        return u'An tree item'
    
    def __str__(self):
        return self.__repr__()
    
    @property
    def tree(self):
        if self._tree is None:
            return Tree()
        else:
            return self._tree

    @tree.setter
    def tree(self, value):
        self._tree = value
    
        
class Tree(list):
    """
    Classe de base décrivant une arborescence
    """
    def __init__(self):
        super(Tree, self).__init__()
            
    def __repr__(self):
        return self.print_()
    
    def __str__(self):
        return self.__repr__()
    
    def __create_root(self):
        return Item(self)
    
    def print_(self):
        txt =u''
        for child in self.root_items:
            txt += self.__print(child)
        return txt
    
    def __print(self, item=None, index=0):
        txt = u'%s+%s (%i)\n' % (self.__tab(index, u' '), item, item.level)
        index += 1
        for child in self.direct_childs_of(item):
            txt += self.__print(child, index)
        index -= 1
        return txt
    
    def __tab(self, nb_tab, char=u'\t'):
        out = u''
        for i in range(nb_tab):
            out += char
        return out
    
    def index(self):
        index = 0
        level = 0
        for child in self.root_items:
            index, level = self.__index(child, index, level)
    
    def __index(self, item=None, index=0, level=0):
        item.index_1 = index
        item.level = level
        index += 1
        level += 1
        for child in self.direct_childs_of(item):
            index, level = self.__index(child, index, level)
        item.index_2 = index
        index += 1
        level -= 1
        return index, level
        
    def direct_childs_of(self, parent):
        return filter(lambda item: item.parent == parent, self)
        
    def count_direct_childs_of(self, parent):
        return len(filter(lambda item: item.parent == parent, self))
        
    def count_childs_intersecs(self, parent):
        counter = 0
        count = self.count_direct_childs_of(parent)
        if count > 0:
            counter = count - 1
        return self._count_intersecs(self.direct_childs_of(parent), counter) 
    
    def _count_intersecs(self, child_list, counter):
        for child in child_list:
            count = self.count_direct_childs_of(child)
            if count > 0:
                counter += count - 1
            counter = self._count_intersecs(self.direct_childs_of(child), counter)
        return counter
    
    def childs_of(self, parent):
        self.index()
        return filter(lambda item: item.index_1 > parent.index_1 and item.index_2 < parent.index_2, self)
        
    def parents_of(self, child):
        self.index()
        return filter(lambda item: item.index_1 < child.index_1 and item.index_2 > child.index_2, self)
    
    def append(self, item):
        if isinstance(item, Item):
            item.tree = self
            super(Tree, self).append(item)
            self.index()
        else:
            raise ValueError(u'Item must be a <class Item> instance.')

    def remove(self, item):
        super(Tree, self).remove(item)
        self.index()

    """
    --------------
    Les propriétés
    --------------
    """
    @property
    def root_items(self):
        return self.direct_childs_of(self)


""" Job class"""

# Les consommateurs

class Ouvrage(Item):
    """
    Classe décrivant un ouvrage
    """
    def __init__(self, mnemonique=u'Ouvrage', parent=None):
        super(Ouvrage, self).__init__(parent);
        self.mnemonique = mnemonique
        self.recepteurs = list()
        self.recepteurs.append(Recepteur())
        self.conducteur = Conducteur(self, u'%s.c1' % mnemonique)
    
    def __repr__(self):
        return u'Ouvrage \'{0}\' (DU%={1:.2f}% Ikmin={2:.3f}kA Rph-n={3:.1f}mOhm Xph-n={4:.1f}mOhm)'.format(self.mnemonique, self.dub[PH1]/2.30, self.ikmin, self.source.rs + self.rcphn(RHO_1), self.source.xs + self.xcphn())
    
    @property
    def source(self):
        return self.tree.parent.source
    
    @property
    def ib(self):
        ib = list([0.,0.,0.,0.]) # (PH1, PH2, PH3, N)
        d = self.tree.d
        for recept in self.recepteurs:
            ib[recept.ph] += recept.ib * d
        ib[N] = courant_neutre(ib)
        return ib
    
    @property
    def ia(self):
        d = self.tree.d
        ia = list([0.,0.,0.,0.]) # (PH1, PH2, PH3, N)
        for recept in self.recepteurs:
            ia[recept.ph] += recept.ia * d
        ia[N] = courant_neutre(ia)
        return ia
    
    @property
    def dub(self): #Chute de tension en régime stabilisé au niveau de l'ouvrage
        du = self.conducteur.dub
        for parent in self.tree.parents_of(self):
            du = map(add, du, parent.conducteur.dub)
        return du
        
    @property
    def dua(self): #Chute de tension en régime transitoire au niveau de l'ouvrage
        du = self.conducteur.dua
        for parent in self.tree.parents_of(self):
            du = map(add, du, parent.conducteur.dua)
        return du
    
    def rcphn(self, rho=0, phase=PH1):
        rc = self.conducteur.rcph(rho, phase) + self.conducteur.rcn(rho)
        for parent in self.tree.parents_of(self):
            rc += parent.conducteur.rcph(rho, phase) + parent.conducteur.rcn(rho)
        return rc
    
    def xcphn(self):
        xc = self.conducteur.xc * 2
        for parent in self.tree.parents_of(self):
            xc += parent.conducteur.xc * 2
        return xc
    
    @property
    def ikmin(self):
        rho = self.tree.protection.rho
        rc = self.rcphn(rho)
        xc = self.xcphn()
        return self.source.ikmin(rc, xc)

        
class Recepteur(object):
    """
    Classe décrivant un récepteur
    """
    def __init__(self, mnemonique=u'Récepteur 1'):
        super(Recepteur, self).__init__();
        self.mnemonique = mnemonique
        self.ib = 1.4
        self.ia = 2.3
        self.cosfi = 0.8
        self.ph = PH1 #phase de raccordement
        self.type = u'SHP250W Ferromagnetique'
    
    def __repr__(self):
        return u'Récepteur \'%s\' (%s)' % (self.mnemonique, self.type)
    
    def __str__(self):
        return self.__repr__()


class Conducteur(object):
    """
    Classe décrivant un Conducteur électrique
    """
    def __init__(self, parent=None, mnemonique=u'Conducteur'):
        super(Conducteur, self).__init__()
        self.mnemonique = mnemonique
        self.parent = parent
        self.longueur = 20. # 20 m
        self.rho0 = CUIVRE
        self.is_isolant_pvc = False
        self.reactance_l = 0.08 # 0,08 mΩ / m
        self.s = list([0.,0.,0.,0.,0.])
        self.s[PH1] = 6. # 6 mm²
        self.s[PH2] = 6. # 6 mm²
        self.s[PH3] = 6. # 6 mm²
        self.s[N] = 6. # 6 mm²
        self.s[PE] = 6. # 6 mm²
        self.conducteurs = list([0.,0.,0.,0.,0.])
        self.conducteurs[PH1] = True
        self.conducteurs[PH2] = True
        self.conducteurs[PH3] = True
        self.conducteurs[N] = True
        self.conducteurs[PE] = True
 
        self.famille = u'U1000R2V'
    
    def __repr__(self):
        return u'Conducteur \'%s\' (%s) Rc=%1.2fmOhms' % (self.mnemonique, self.type, self.rcph(RHO_1)+self.rcn(RHO_1))
    
    def __str__(self):
        return self.__repr__()
    
    def is_conforme(self):
        if all(map(lambda x: x/2.30 <= 3, self.parent.dub))\
        and all(map(lambda x: x/2.30 <= 10, self.parent.dua)):
            return True
        else:
            return False
    
    def rcph(self, n_rho, phase):
        if n_rho == RHO_0:
            return self.rho0 / self.s[phase] * self.longueur
        elif n_rho == RHO_1:
            return self.rho1 / self.s[phase] * self.longueur
        elif n_rho == RHO_2:
            return self.rho2 / self.s[phase] * self.longueur
    
    def rcn(self, n_rho):
        if n_rho == RHO_0:
            return self.rho0 / self.s[N] * self.longueur
        elif n_rho == RHO_1:
            return self.rho1 / self.s[N] * self.longueur
        elif n_rho == RHO_2:
            return self.rho2 / self.s[N] * self.longueur
            
    def rpe(self, n_rho):
        if n_rho == RHO_0:
            return self.rho0 / self.s[PE] * self.longueur
        elif n_rho == RHO_1:
            return self.rho1 / self.s[PE] * self.longueur
        elif n_rho == RHO_2:
            return self.rho2 / self.s[PE] * self.longueur
        elif n_rho == RHO_3:
            return self.rho3 / self.s[PE] * self.longueur
    
    def zcph(self, rho, phase):
        return (self.rcph(rho, phase) * COS_PHI + self.xc * SIN_PHI)

    def zcn(self, rho):
        return (self.rcn(rho) * COS_PHI + self.xc * SIN_PHI)
    
    @property
    def nb_conduc(self):
        return len(filter(lambda x: x, self.conducteurs))
    
    @property
    def descr(self):
        lettre = u'x'
        if self.conducteurs[PE]:
            lettre = u'G'
        return u'{0}{1}{2}'.format(self.nb_conduc, lettre, self.s[PH1])
    
    @property
    def type(self):
        lettre = u'x'
        if self.conducteurs[PE]:
            lettre = u'G'
        return u'{0} {1}'.format(self.famille, self.descr)
    
    @property
    def xc(self):
        return self.reactance_l * self.longueur
    
    @property
    def rho1(self):
        if self.is_isolant_pvc:
            return 1.2 * self.rho0
        else:
            return 1.28 * self.rho0
            
    @property
    def rho2(self):
        if self.is_isolant_pvc:
            return 1.38 * self.rho0
        else:
            return 1.6 * self.rho0
        
    @property
    def rho3(self):
        if self.is_isolant_pvc:
            return 1.30 * self.rho0
        else:
            return 1.48 * self.rho0
    
    @property
    def ib(self): #Courant en régime stabilisé dans le conducteur
        ib = self.parent.ib
        for child in self.parent.tree.childs_of(self.parent):
            ib = map(add, ib, child.ib)
        ib[N] = courant_neutre(ib)
        return ib
    
    @property
    def ia(self): #Courant en régime transitoire dans le conducteur
        ia = self.parent.ia
        for child in self.parent.tree.childs_of(self.parent):
            ia = map(add, ia, child.ia)
        ia[N] = courant_neutre(ia)
        return ia
    
    @property
    def dub(self): #Chute de tension en régime stabilisé dans le conducteur
        du = list([0.,0.,0.,0.])
        i = self.ib
        def test(i):
            if i > 0: return 1
            else: return 0
        du[N] = 0
        du[PH1] = (self.zcph(RHO_1, PH1) * i[PH1] + self.zcn(RHO_1) * i[N]) * test(i[PH1]) / 1000
        du[PH2] = (self.zcph(RHO_1, PH2) * i[PH2] + self.zcn(RHO_1) * i[N]) * test(i[PH2]) / 1000
        du[PH3] = (self.zcph(RHO_1, PH3) * i[PH3] + self.zcn(RHO_1) * i[N]) * test(i[PH3]) / 1000
        return du
        
    @property
    def dua(self): #Chute de tension en régime transitoire dans le conducteur
        du = list([0.,0.,0.,0.])
        i = self.ia
        def test(i):
            if i > 0: return 1
            else: return 0
        du[N] = 0
        du[PH1] = (self.zcph(RHO_1, PH1) * i[PH1] + self.zcn(RHO_1) * i[N]) * test(i[PH1]) / 1000
        du[PH2] = (self.zcph(RHO_1, PH2) * i[PH2] + self.zcn(RHO_1) * i[N]) * test(i[PH2]) / 1000
        du[PH3] = (self.zcph(RHO_1, PH3) * i[PH3] + self.zcn(RHO_1) * i[N]) * test(i[PH3]) / 1000
        return du

        
# Les Sources
        
class Source(object):
    """
    Classe de base pour une source d'alimentation
    """
    def __init__(self, mnemonique=u'Source'):
        super(Source, self).__init__();
        self.u_n = UN 
        self.c_max = CMAX
        self.c_min = CMIN
        self.m = M
    
    def __repr__(self):
        return u'Une source'
    
    def __str__(self):
        return self.__repr__()
    
    def ikmin(self, rc=0, xc=0):
        r = self.rs + rc
        x = self.xs + xc
        return (self.c_min * self.m * self.u0) / ((r ** 2 + x ** 2) ** .5)
    
    def ikmax(self, num=1):
        return None
    
    @property
    def u0(self):
        return self.u_n / (3 ** .5 )
        
    @property
    def zs(self):
        return (self.rs ** 2 + self.xs ** 2) ** .5
    
    @property
    def rs(self):
        return None
        
    @property
    def xs(self):
        return None


class BrchSurveille(Source):
    """
    Classe décrivant un branchement surveillé alimenté par un Transformateur HT/BT
    - Transformateur -> Zs + Zt + Zq
    """
    def __init__(self, mnemonique=u'Conducteur'):
        super(BrchSurveille, self).__init__();
        self.s = S_TRANS
        self.skq = SKQ_DEFVAL
        self._ucc = None
        conducteur = Conducteur()
        conducteur.s_ph = 240.
        conducteur.s_n = 95.
        conducteur.count_ph = 3
        conducteur.longueur = 15.
        conducteur.rho0 = 29.41 # 29,41 mΩ. mm² / m
        conducteur.is_isolant_pvc = True
        conducteur.cablette = False
        conducteur.type = u'H1 XDV-AR 3x240+95²'
        conducteur.conducteur_amont = conducteur
    
    def __repr__(self):
        return u'Transformateur \'%s\' (%s)' % (u'', u'')
    
    @property
    def zq(self):
        return (self.m * self.un) ** 2 / self.skq
    
    @property
    def rq(self):
        return self.zq * COEF_RQ
        
    @property
    def xq(self):
        return self.zq * COEF_XQ
        
    @property
    def zt(self):
        return (self.m * self.un) ** 2 / self.s * self.ucc / 100
    
    @property
    def rt(self):
        return self.zt * COEF_RT
        
    @property
    def xt(self):
        return self.zt * COEF_XT
        
    @property
    def zs(self):
        return (self.rs ** 2 + self.xs ** 2) ** .5
    
    @property
    def rs(self):
        return self.rt + self.rq + self.conducteur.rcph(0) + self.conducteur.rcn(0)
        
    @property
    def xs(self):
        return self.xt + self.xq + self.conducteur.xc * 2
    
    @property
    def ikmax(self):
        return (self.c_max * self.m * self.u0) / self.zs
        
    @property
    def ucc(self):
        if self._ucc is None:
            if self.s > 630:
                return UCC_MAX
            else:
                return UCC_MIN
        else:
            return self._ucc
    
    @ucc.setter
    def ucc(self, value):
        self._ucc = value


class BrchLimite(Source):
    """
    Classe décrivant un branchement limité (<=36kVA - Tarif Bleu)
    Branchement limité -> Ika (3000A)
    """
    def __init__(self, mnemonique=u'Branchement Limite'):
        super(BrchLimite, self).__init__();
        self.u_n = UN
        self.s = S_TRANS
        self.ikmax = IKa #3kA (Voir C14-100 et C17-200 titre 7)
        
    @property
    def zs(self):
        return self.u0 / self.ikmax
    
    @property
    def rs(self):
        return self.zs * COEF_RQ
        
    @property
    def xs(self):
        return self.zs * COEF_XQ
    
    def __repr__(self):
        return u'Branchement Limite \'%s\' (%s)' % (u'', u'')
        

# Depart / Protection
        
class Depart(Tree):
    def __init__(self, parent, mnemonique=u'Depart'):
        super(Depart, self).__init__()
        self.mnemonique = mnemonique
        self.d = 1.2 # Coefficient de reserve
        parent.append(self)
        self._parent = parent
        self.protection = Disjoncteur()
        self.nb = 0
        
    def __create_root(self):
        return Ouvrage(self)
    
    def __repr__(self):
        return u'Depart \'%s\'\n%s' % (self.mnemonique, self.print_())
        
    def end_line(self):
        return filter(lambda item: item.index_1 == item.index_2 - 1, self)
    
    def is_conforme(self):
        if self.ia[PH1] > self.protection.inom:
            return False
        elif self.ia[PH2] > self.protection.inom:
            return False
        elif self.ia[PH3] > self.protection.inom:
            return False
        else:
            return True
    
    @property
    def ib(self):
        ib = list([0.,0.,0.,0.]) # (PH1, PH2, PH3, N)
        for child in self.direct_childs_of(self):
            ib = map(add, ib, child.conducteur.ib)
        ib[N] = courant_neutre(ib)
        return ib
        
    @property
    def ia(self):
        ia = list([0.,0.,0.,0.]) # (PH1, PH2, PH3, N)
        for child in self.direct_childs_of(self):
            ia = map(add, ia, child.conducteur.ia)
        ia[N] = courant_neutre(ia)
        return ia
           
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, value):
        if isinstance(value, Armoire):
            self._parent = value
        else:
            raise ValueError(u'Parent must be a <class Armoire> instance.')

    
class Protection(object):
    """
    Classe de base pour les protections
    """
    def __init__(self, mnemonique=u'Protection'):
        super(Protection, self).__init__();
        self.mnemonique = mnemonique
        self.type = 0 #1 => disjoncteur / 2 => fusible
        self.inom = 0.
        self.rho = None
    
    def __repr__(self):
        return u'Une Protection'
    
    def __str__(self):
        return self.__repr__()
        
    @property
    def property(self):
        return None


class Disjoncteur(Protection):
    """
    Classe décrivant un disjoncteur
    """
    def __init__(self, mnemonique=u'Protection'):
        super(Disjoncteur, self).__init__();
        self.type = DISJONCTEUR
        self.inom = 10.
        self.courbe = B
        self.rho = RHO_1
        self.is_diff = False
        self.idn = .3
    
    def __repr__(self):
        return u'Une Protection'
        
    @property
    def imag(self):
        return self.inom * courbe(self.courbe)


class Fusible(Protection):
    """
    Classe décrivant un fusible
    """
    def __init__(self, mnemonique=u'Protection'):
        super(Fusible, self).__init__();
        self.type = FUSIBLE
        self.inom = 0.
        self.courbe = gG
        self.rho = RHO_2
    
    def __repr__(self):
        return u'Une Protection'
        
           
# Commande
class Armoire(list):
    """
    Classe de base pour les protections
    """
    def __init__(self, mnemonique=u'Armoire'):
        super(Armoire, self).__init__();
        self.mnemonique = mnemonique
        self.source = BrchLimite()
            
    def __repr__(self):
        return u'Une commande'
    
    def __str__(self):
        return self.__repr__()
    
    def append(self, depart):
        if isinstance(depart, Depart):
            depart.parent = self
            super(Armoire, self).append(depart)
        else:
            raise ValueError(u'Child must be a <class Depart> instance.')
           
           
if __name__ == u'__main__':
    commande = Armoire()
    tree = Depart(commande)
    
    it0 = Ouvrage(u'1', tree)
    tree.append(it0)
    
    last = it0
    ph = 1
    for i in range(14):
        it = Ouvrage(u'%i'%(i+2), last)
        for recept in it.recepteurs:
            recept.ph = ph
            ph = rotation_phase(ph)
        tree.append(it)
        last = it
    print it0.conducteur
    
    print tree
    
    for item in tree.root_items:
        print u' \tPH1\tPH2\tPH3\tN'
        print u''
        print u'Ib\t{0[1]:.2f}A\t{0[2]:.2f}A\t{0[3]:.2f}A\t{0[0]:.2f}A'.format(item.conducteur.ib)
        print u'Ia\t{0[1]:.2f}A\t{0[2]:.2f}A\t{0[3]:.2f}A\t{0[0]:.2f}A'.format(item.conducteur.ia)
        print u''
    for it in tree.end_line():
        print u'Chute de tension : \'%s\'' % it
        print u'DUb\t{0[1]:.2f}%\t{0[2]:.2f}%\t{0[3]:.2f}%\t-'.format(map(lambda x: x/2.30, it.dub))
        print u'DUa\t{0[1]:.2f}%\t{0[2]:.2f}%\t{0[3]:.2f}%\t-'.format(map(lambda x: x/2.30, it.dua))
    