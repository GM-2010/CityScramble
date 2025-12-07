# City Scramble - Spielkonzept

## 1. Grundmechanik & Ziel
*   **Genre**: 2D Top-Down Arena Brawler.
*   **Dauer**: Jede Runde dauert exakt 3:00 Minuten.
*   **Siegbedingung**: Der Charakter mit dem höchsten zugefügten Gesamtschaden am Ende der 3 Minuten gewinnt.
*   **Eliminierung/Respawn**: Wird ein Charakter eliminiert (Lebenspunkte auf Null), respawnt er nach 10 Sekunden in seiner Startbasis. Der gesamte zugerichtete Schaden wird kumulativ bis zum Rundenende gezählt.
*   **Waffenwechsel**: Waffen werden in Kisten auf dem Feld gefunden. Eine neu aufgenommene Waffe ersetzt die aktuell getragene Waffe sofort.

## 2. Visueller Stil & Umgebung
*   **Perspektive**: Starre Vogelperspektive (Top-Down).
*   **Grafikstil**: Moderner, klarer Cartoon-Stil. Helle Farben, klare Linienführung.
*   **Arena**: Eine städtische Arena (z.B. belebter Marktplatz). Die Karte enthält statische Hindernisse (z.B. Bauzäune, Bänke), die die Bewegungswege blockieren. Es gibt keine zerstörbaren Objekte oder Umgebungsschäden.
*   **Einstiegsszenario**:
    > "Willkommen in 'City Scramble'! Die Stadtverwaltung hat angekündigt, das gesamte Stadtzentrum zu sanieren. Nun liegt es an dir und deinem Gegenspieler, in 3 Minuten des Chaos zu beweisen, wer der wahre Beherrscher der Straße ist. Wer den meisten Schaden anrichtet, gewinnt das Recht auf das Revier! Wähle deinen Kämpfer und eliminiere die Konkurrenz!"

## 3. Die 5 Charaktere und Spezialfähigkeiten
Jeder Charakter hat eine einzigartige Kombination aus Tempo/Rüstung und eine spezielle, waffenunabhängige Fähigkeit (auf Cooldown).

| Charakter | Rüstung/Tempo | Spielstil-Fokus | Spezialfähigkeit (Taste Q) |
| :--- | :--- | :--- | :--- |
| **Der Flitzer** | Gering / Sehr Hoch | Hit-and-Run | **Aktivierbarer Dash**: Führt einen kurzen Sprint aus, währenddessen er für 1 Sekunde unverwundbar ist. (Cooldown: 15s). |
| **Der Tank** | Sehr Hoch / Gering | Hält lange durch | **Schild-Modus**: Reduziert eingehenden Schaden für 3 Sekunden um 50%. Verringert die eigene Geschwindigkeit währenddessen um 30%. (Cooldown: 20s). |
| **Der Allrounder** | Mittel / Mittel | Ausgeglichen | **Waffen-Boost**: Halbiert die Cooldowntime der aktuell getragenen Waffe für 5 Sekunden. (Cooldown: 25s). |
| **Der Jäger** | Mittel / Hoch | Distanz | **Scharfschuss**: Erhöht die Schussreichweite aller Waffen um 20% und die Geschossgeschwindigkeit für 8 Sekunden. (Cooldown: 20s). |
| **Die Falle** | Mittel / Mittel | Kontrollzone | **Platzierbare Mine**: Legt eine unsichtbare Mine. Bei Auslösung wird der Gegner für 2 Sekunden betäubt (Stunned). (Cooldown: 30s). |

## 4. Waffen-Balancing (Schadenswerte)
Der zugerichtete Schaden wird als Punktwert für den Gesamtsieg gezählt.

| Waffe | Typ | Max. Munition | Schaden pro Treffer (Punkte) | Feuerrate (Cooldown) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseballschläger** | Nahkampf | Unbegrenzt | 10 | Sehr schnell (0.5 Sek.) |
| **Pistole** | Fernkampf | 8 Schuss | 20 | Schnell (0.8 Sek.) |
| **Schrotflinte** | Fernkampf | 4 Schuss | 35 (hoher Streuschaden) | Langsam (2.0 Sek.) |
| **Bumerang** | Wurf | 3 Schuss | 15 (kann zweimal treffen, max 30) | Mittel (1.5 Sek.) |
| **Giftflasche** | Fläche | 2 Schuss | 5 pro Sekunde (Schaden über Zeit) | Langsam (3.0 Sek.) |
| **Explosionsbombe** | Wurf (Fläche) | 1 Schuss | 50 (hoher Flächenschaden) | Sehr Langsam (4.0 Sek.) |

## 5. KI-Strategien (Künstliche Intelligenz)
Die KI muss ihren Spielstil an ihren gewählten Charakter anpassen. Sie soll Waffen gemäß ihrer Rolle priorisieren (z.B. Der Tank bevorzugt Nahkampf/Schrotflinte, Der Jäger bevorzugt Pistole/Bumerang) und die Spezialfähigkeit strategisch nutzen.

## 6. Steuerung
*   **Bewegung**: WASD / Pfeiltasten
*   **Angriff/Waffe benutzen**: Leertaste
*   **Spezialfähigkeit**: Q
*   **Waffe aufheben**: E
