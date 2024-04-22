# Etap 4 - urzeczywistnienie symulacji, analiza metryk

## Urzeczywistnienie symulacji
### Wybór rodzaju ceny
Mamy do dyspozycji ceny:
- open - otwarcie
- high - max w dniu
- low - min w dniu
- close - zamknięcie

Dla high, low nie możemy być pewni czasu, dla którego występują.

Można rozważać `close` jednak nakłada to pewne ograniczenia bo wymaga użycia AHT (After-Hours Trading).

![](standard_vs_aht.png)

Postanowiliśmy więc używać `open`, zakładając, że dokonujemy zakupów tuż po otwarciu sesji. \
Wybraliśmy tą cenę ponieważ tylko dla niej możemy być pewni czasu, dla którego jest aktualna oraz możemy dokonać zakupu bez dodatkowych ograniczeń.

Źródła:
- [Why Don't Stocks Begin Trading at the Previous Day's Closing Price?](https://www.investopedia.com/ask/answers/139.asp)
- [After-Hours Trading](https://www.investopedia.com/terms/a/afterhourstrading.asp)

### Prowizje brokera
Prowizje różnią się między brokerami dlatego wybraliśmy przedstawiciela - Revolut. \
[System opłat](https://help.revolut.com/pl-PL/help/wealth/stocks/trading-stocks/trading-fees/what-fees-will-i-be-charged-for-my-trading/) wygląda następująco:

![](revolut_prowizje.png)

## Analiza metryk
Wykorzystaliśmy korelację Pearson do znalezienia metryk niosących podobne informacje. \
https://www.scribbr.com/statistics/pearson-correlation-coefficient/
