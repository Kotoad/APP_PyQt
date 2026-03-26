# Operační zesilovače (OZ) – Souhrn a zapojení

## 1. Vlastnosti operačních zesilovačů
* **Ideální OZ**:
  * [cite_start]Dosahuje nekonečného napěťového zesílení[cite: 4].
  * [cite_start]Má nulové zkreslení[cite: 4].
  * [cite_start]Má nulový šum[cite: 4].
  * [cite_start]Vykazuje nulový fázový posun[cite: 4].
  * *Doplněná informace:* Ideální OZ má navíc nekonečný vstupní odpor (neodebírá absolutně žádný proud) a nulový výstupní odpor (dokáže dodat libovolně velký proud bez poklesu napětí).

## 2. Parametry reálného OZ
[cite_start]**Statické parametry**[cite: 8]:
* [cite_start]**Vstupní napěťová nesymetrie (Input offset voltage)**[cite: 10]:
  * [cite_start]Její hodnota se pohybuje v řádech milivoltů (mV)[cite: 11].
  * [cite_start]Představuje napětí nutné ke kompenzaci rozdílu vstupních tranzistorů[cite: 11, 12].
  * [cite_start]Tato hodnota je závislá na teplotě[cite: 13].
* [cite_start]**Vstupní klidový proud**[cite: 14]:
  * [cite_start]Typická velikost se pohybuje kolem 10 nA[cite: 15].
* [cite_start]**Vstupní proudová nesymetrie**[cite: 16].
* [cite_start]**Činitel potlačení součtového signálu**[cite: 17]:
  * *Doplněná informace:* Tento parametr (často označovaný jako CMRR) popisuje schopnost zesilovače potlačit signál nebo šum, který je přiveden současně na invertující i neinvertující vstup.

[cite_start]**Dynamické parametry**[cite: 18]:
* [cite_start]**Rychlost přeběhu (Slew rate)**[cite: 18, 19]:
  * *Doplněná informace:* Udává se ve V/µs a definuje, jak rychle je OZ schopen změnit napětí na svém výstupu při skokové změně na vstupu.
* [cite_start]**Frekvenční charakteristika**[cite: 20]:
  * *Doplněná informace:* Určuje frekvenční rozsah (šířku pásma), ve kterém OZ dokáže efektivně zesilovat signál bez útlumu.

---

## [cite_start]3. Základní aplikace a zapojení OZ [cite: 21]

### [cite_start]A. Napěťové zesilovače [cite: 22]

[cite_start]**Invertující zapojení** [cite: 23]


[Image of inverting operational amplifier circuit diagram]

* [cite_start]Obrací fázi vstupního signálu o 180°[cite: 23].
* [cite_start]Zapojení využívá rezistory R1 a R2[cite: 25, 44].
* Napěťové zesílení se řídí vztahem:
  [cite_start]$$A = -\frac{R_2}{R_1}$$ [cite: 33]
* [cite_start]Pokud je odpor R1 roven odporu R2, funguje obvod jako přesný invertor[cite: 34].
* [cite_start]Na invertujícím vstupu se vytváří tzv. virtuální nula[cite: 28].

[cite_start]**Neinvertující zapojení** [cite: 47]


[Image of non-inverting operational amplifier circuit diagram]

* Fáze signálu zůstává zachována.
* Napěťové zesílení je definováno vztahem:
  [cite_start]$$A_u = 1 + \frac{R_2}{R_1}$$ [cite: 59]

[cite_start]**Napěťový sledovač** [cite: 62]


[Image of operational amplifier voltage follower circuit diagram]

* Výstupní napětí je shodné se vstupním.
* *Doplněná informace:* Obvod má napěťové zesílení rovno jedné. Slouží primárně k oddělení obvodů – má obrovský vstupní odpor (nezatěžuje zdroj signálu) a velmi nízký výstupní odpor (dokáže budit další obvody).

### B. Komparátory

[cite_start]**Komparátor bez hystereze** [cite: 73]


[Image of operational amplifier comparator circuit diagram]

* Slouží k porovnání dvou napěťových úrovní A a B.
* [cite_start]Pokud je úroveň A vyšší než B (A > B), výstup se překlopí do kladného maxima (+V)[cite: 79].
* [cite_start]Pokud je úroveň B vyšší než A (B > A), výstup se překlopí do záporného maxima (-V)[cite: 79].
* *Doplněná informace:* Nevýhodou tohoto zapojení je, že pokud na vstupu leží zašuměný signál přesně na úrovni reference, výstup může nekontrolovatelně zakmitávat.

[cite_start]**Komparátor s hysterezí (Schmittův klopný obvod)** [cite: 91]

* [cite_start]Využívá rezistory R1 a R2 k vytvoření zpětné vazby[cite: 95, 96].
* [cite_start]Tím vznikají dvě různé rozhodovací úrovně – jedna pro překlopení nahoru (X) a druhá pro překlopení dolů (Y)[cite: 98, 100].
* [cite_start]Hranice pro překlopení se počítají z referenčního napětí (Uref) a děliče tvořeného odpory R1 a R2[cite: 94, 104].
* *Doplněná informace:* Právě tato "mezera" mezi úrovněmi (hystereze) efektivně eliminuje zakmitávání způsobené šumem v signálu.

### C. Matematické a další funkční obvody

[cite_start]**Součtový zesilovač** [cite: 106]


[Image of summing operational amplifier circuit diagram]

* Součtový zesilovač dokáže sečíst více přivedených napětí.
* Součet se řídí vztahem (pokud jsou odpory stejné):
  [cite_start]$$-(U_1 + U_2) = U_{out}$$ [cite: 124]
* [cite_start]Pro reálné zapojení se na neinvertující vstup často připojuje paralelní kombinace všech odporů z větve invertujícího vstupu[cite: 113].

[cite_start]**Integrační zesilovač (Millerův)** [cite: 115]


[Image of operational amplifier integrator circuit diagram]

* [cite_start]Jako zpětnovazební prvek nepoužívá rezistor, ale kondenzátor C[cite: 138].
* Na výstupu vzniká matematický integrál vstupního napětí podle času:
  [cite_start]$$U_c = \frac{1}{C} \int i dt$$ [cite: 125]
* Strmost průběhu na výstupu je určena časovou konstantou obvodu:
  [cite_start]$$\tau = R \cdot C$$ [cite: 127]

[cite_start]**Operační usměrňovač** [cite: 129]

* [cite_start]Používá se pro usměrňování velmi malých signálů[cite: 129].
* [cite_start]Obvod obsahuje zpětnou vazbu s diodou D[cite: 130].
* *Doplněná informace:* Běžná usměrňovací dioda potřebuje k otevření alespoň 0,6 V až 0,7 V, což menší signály odřízne. Umístěním diody do zpětnovazební smyčky operačního zesilovače se tento úbytek téměř vyruší, čímž získáme "ideální diodu", která spolehlivě usměrní i milivoltové průběhy.