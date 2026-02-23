# [cite_start]Stabilita a kvalita regulačního obvodu [cite: 1]

## 1. Základní principy a význam stability
* [cite_start]Nejdůležitější podmínkou pro správnou činnost regulačních obvodů je jejich stabilita. [cite: 4]
* [cite_start]Regulační obvod je stabilní, jestliže se při libovolné změně vstupní veličiny po odeznění přechodového děje výstupní veličina ustálí na nové hodnotě. [cite: 5] 
* [cite_start]Nestabilní systémy nejčastěji kmitají nebo se překlápí do jednoho nebo druhého mezního stavu. [cite: 6]
* [cite_start]Takovéto obvody neplní funkci regulace a navíc mohou poškodit regulovanou soustavu. [cite: 7]
* [cite_start]U lineárních systémů nezávisí stabilita regulačního pochodu na velikosti ani na průběhu vstupních veličin. [cite: 10]
* [cite_start]Stabilita regulačního obvodu závisí pouze na přenosových vlastnostech jeho členů, zejména u obvodů s uzavřenou ZV smyčkou. [cite: 8]
* [cite_start]K vyšetřování stability slouží kritéria stability. [cite: 11]

## 2. Matematický základ a póly přenosu
* [cite_start]V regulačním obvodu mohou být jednotlivé členy stabilní i nestabilní, ale ve výsledku musí být uzavřený regulační obvod vždy stabilní. [cite: 15]
* Obecný tvar přenosu uzavřeného obvodu:
  [cite_start]$$G_p = \frac{b_mp^m + b_{m-1}p^{m-1} + \dots + b_1p + b_0}{a_np^n + a_{n-1}p^{n-1} + \dots + a_1p + a_0}$$ [cite: 16, 17]
* [cite_start]Kořeny jmenovatele ($p_1, p_2 \dots p_n$) se nazývají póly a mohou být reálné i komplexní. [cite: 20]
* [cite_start]**Nutná a postačující podmínka stability:** Všechny kořeny jmenovatele přenosu uzavřeného obvodu musí ležet v záporné polorovině komplexní roviny. [cite: 26]
* [cite_start]To znamená, že pokud jsou reálné kořeny, musí být záporné, a u komplexních kořenů musí být reálné části záporné a nesmí být ani nulové. [cite: 27]
* [cite_start]Okamžitě můžeme o (ne)stabilitě rozhodnout podle tvaru polynomu jmenovatele $A(p)$: [cite: 28]
  * [cite_start]Je-li polynom $A(p)$ maximálně 2. stupně a jsou-li všechny jeho koeficienty kladné, je systém stabilní. [cite: 29]
  * [cite_start]Nejsou-li všechny koeficienty polynomu $A(p)$ kladné nebo některý člen chybí, je systém nestabilní. [cite: 30]
  * [cite_start]Je-li polynom vyššího než 2. stupně a všechny koeficienty jsou kladné, nelze určit (ne)stabilitu a je potřeba buď vyřešit kořeny polynomu nebo použít některé kritérium stability. [cite: 31]

## 3. Kritéria stability

### A. Nyquistovo kritérium
* [cite_start]Jedná se o grafické a kmitočtové kritérium. [cite: 80, 81]
* [cite_start]Používá se nejčastěji, protože slouží nejen k ověření stability, ale již při návrhu regulačního obvodu udává vzdálenost od meze stability. [cite: 82]
* [cite_start]Lze jej použít i na obvody s dopravním zpožděním. [cite: 83]
* [cite_start]Stabilitu zjišťuje na základě změřených frekvenčních charakteristik otevřené smyčky (ta musí být stabilní). [cite: 84, 85]
* [cite_start]Uzavřený regulační obvod je stabilní, probíhá-li frekvenční charakteristika jeho otevřené smyčky vpravo od bodu $-1+0j$. [cite: 91]
* [cite_start]Obvod je nestabilní, je-li bod $-1+0j$ charakteristikou „obklíčen“. [cite: 92] 
* [cite_start]Obvod je na mezi stability, prochází-li právě bodem $-1+0j$. [cite: 93]

### B. Michajlovovo-Leonhardovo kritérium
* [cite_start]Grafické kritérium, které vychází z jmenovatele přenosu uzavřeného regulačního obvodu, za $p$ se dosadí $j\omega$. [cite: 244, 245, 246]
* [cite_start]Křivka se vynese v komplexní rovině a získá se tzv. hodograf (Michajlova křivka). [cite: 247]
* [cite_start]Nehodí se pro obvody s dopravním zpožděním. [cite: 248]
* [cite_start]Obvod je stabilní, jestliže křivka pro $0 < \omega < \infty$ začíná na reálné ose a projde postupně proti směru hodinových ručiček $n$ kvadrantů, kde $n$ je stupeň polynomu charakteristické rovnice daného přenosu. [cite: 249]

### C. Hurwitzovo kritérium
* [cite_start]Algebraické kritérium vycházející z charakteristické rovnice. [cite: 267, 268, 269]
* [cite_start]Poskytuje pouze informaci o tom, zda je obvod stabilní či nestabilní, a nehodí se pro obvody s dopravním zpožděním. [cite: 270, 271]
* [cite_start]**Podmínky nutné:** Všechny koeficienty charakteristické rovnice musejí být nenulové kladné. [cite: 278]
* [cite_start]**Podmínky postačující:** Všechny Hurwitzovy subdeterminanty $H_i$ odpovídající prvkům na hlavní diagonále Hurwitzovy matice $H$ musejí být $> 0$. [cite: 279]
* [cite_start]Stačí kontrolovat subdeterminanty: $H_2 > 0, H_3 > 0, \dots, H_{n-1} > 0$. [cite: 283, 284]

### D. Routh-Schurovo kritérium
* [cite_start]Algebraické kritérium, které se dá použít i jako test aperiodicity (nekmitavosti). [cite: 310, 311, 312]
* [cite_start]Princip spočívá v postupném snižování stupně charakteristické rovnice na 2. stupeň. [cite: 313]
* [cite_start]Všechny členy jsou kladné $\rightarrow$ systém je stabilní. [cite: 314]
* [cite_start]Všechny členy jsou kladné nebo nulové $\rightarrow$ systém je na mezi stability. [cite: 315]
* [cite_start]Členy jsou opačných znamének $\rightarrow$ systém je nestabilní. [cite: 316]