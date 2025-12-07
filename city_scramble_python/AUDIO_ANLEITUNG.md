# Hintergrundmusik für City Scramble

## 🎵 Was wurde implementiert?

Das Spiel spielt jetzt automatisch einen Hintergrund-Sound (Drum-Loop) in einer Endlosschleife ab.

## 📁 Audio-Datei einrichten

### Schritt 1: Audio-Datei besorgen

Sie benötigen eine Schlagzeug-Loop-Datei. Sie können:

1. **Kostenlose Drum-Loops herunterladen** von:
   - [Freesound.org](https://freesound.org/) - Royalty-free Sounds
   - [ccMixter](https://ccmixter.org/) - Creative Commons Musik
   - [Incompetech](https://incompetech.com/) - Royalty-free Musik

2. **Nach Suchbegriffen suchen** wie:
   - "drum loop"
   - "hip hop beat"
   - "rock drum loop"
   - "electronic drum pattern"

### Schritt 2: Datei vorbereiten

1. Laden Sie eine Drum-Loop-Datei herunter (unterstützte Formate: `.mp3`, `.wav`, `.ogg`)
2. **Benennen Sie die Datei um** zu: `drum_loop.mp3` (oder `.wav` bzw. `.ogg`)
3. **Platzieren Sie die Datei** in das Verzeichnis: `d:\Gaming Coding\city_scramble_python\`

### Schritt 3: Anpassen (Optional)

Falls Sie einen anderen Dateinamen oder ein anderes Format verwenden möchten, ändern Sie in `main.py` (Zeile ~105):

```python
self.background_music_file = "drum_loop.mp3"  # Ihr Dateiname hier
```

## 🔊 Lautstärke anpassen

Die Lautstärke ist standardmäßig auf 50% eingestellt. Um sie zu ändern, bearbeiten Sie in `main.py` (Zeile ~109):

```python
pygame.mixer.music.set_volume(0.5)  # Werte: 0.0 (stumm) bis 1.0 (max)
```

Beispiele:
- `0.3` = 30% Lautstärke (leiser)
- `0.7` = 70% Lautstärke (lauter)
- `1.0` = 100% Lautstärke (maximum)

## 🎮 Musik-Steuerung im Spiel

### Musik pausieren/fortsetzen
Sie können folgende Tastenkombinationen hinzufügen (optional):
- **M-Taste**: Musik ein/aus (muss noch implementiert werden)

### Automatisches Verhalten
- Die Musik startet **automatisch beim Spielstart**
- Die Musik läuft in **Endlosschleife** (Loop)
- Bei jedem neuen Spiel wird geprüft, ob die Musik noch läuft

## ⚠️ Fehlerbehebung

### "Konnte Musik nicht laden"
**Problem**: Die Audio-Datei wurde nicht gefunden

**Lösung**:
1. Überprüfen Sie, ob `drum_loop.mp3` (oder Ihr Dateiname) im richtigen Verzeichnis liegt
2. Stellen Sie sicher, dass der Dateiname **exakt übereinstimmt** (Groß-/Kleinschreibung beachten!)
3. Versuchen Sie ein anderes Format (.wav statt .mp3)

### Musik spielt nicht ab
**Problem**: pygame.mixer wurde nicht korrekt initialisiert

**Lösung**:
- Starten Sie das Spiel neu
- Überprüfen Sie, ob pygame installiert ist: `pip install pygame`

### Musik ist zu laut/leise
**Problem**: Lautstärke muss angepasst werden

**Lösung**: Siehe "Lautstärke anpassen" oben

## 📋 Unterstützte Audio-Formate

- ✅ **MP3** (.mp3) - Empfohlen, kleine Dateigröße
- ✅ **WAV** (.wav) - Höchste Qualität, große Dateigröße
- ✅ **OGG** (.ogg) - Gute Kompression

## 🎼 Empfohlene Drum-Loop-Eigenschaften

Für optimales Spielerlebnis:
- **Tempo**: 100-140 BPM (Schläge pro Minute)
- **Länge**: 2-8 Sekunden (nahtlose Loop)
- **Stil**: Hip-Hop, Rock, Electronic - je nach Vorliebe
- **Qualität**: Mindestens 128 kbps (für MP3)

## 📝 Beispiel: Schnellstart

1. Gehen Sie zu [Freesound.org](https://freesound.org/search/?q=drum+loop&f=&s=score+desc)
2. Suchen Sie nach "drum loop" und filtern Sie nach "CC0" (gemeinfrei)
3. Laden Sie einen Loop herunter
4. Benennen Sie ihn um zu `drum_loop.mp3`
5. Verschieben Sie ihn nach `d:\Gaming Coding\city_scramble_python\`
6. Starten Sie das Spiel!

---

**Viel Spaß mit Ihrer neuen Hintergrundmusik! 🥁🎵**
