# Etap 3 - określenie celu i zakresu prac, uruchomienie narzędzi

## Zestawienie najlepszej znalezionej oraz najlepszej możliwej strategii
### Znaleziona
![](best_strategy.png)

### Możliwa
![](best_possible_strategy.png)

Najlepsza znaleziona strategia dała rezultat równy ~0.07439% optymalnej strategii

## Cele i zakres prac
- Stworzenie generatora strategii inwestycyjnych opierającego się o algorytmy optymalizacyjne inspirowane biologicznie.
- Dopracowanie modelu reprezentacji strategii, uwzględniającego punkty z akapitu ["Rozwój obecnego algorytmu" Etapu 2](../2/README.md#rozwój-obecnego-algorytmu). Szczególną uwagę chcemy zwrócić na analizę wykorzystywanych metryk (korelacja atrybutów, eliminacja mało wartościowych metryk itd.). Docelowo chcielibyśmy uzyskać zbiór kilkuset metryk, poprzez wielokrotne wykorzystanie tych samych wskaźników, ale z różnymi parametrami.
- Usprawnienie funkcji kosztu tak, aby uwzględniała punkty z akapitu ["Urzeczywistnić algorytm" Etapu 2](../2/README.md#rozwój-obecnego-algorytmu). 
- Porównanie algorytmów dostępnych w bibliotece DEAP, czyli EA i CMA-ES.
