# CityScramble 🎮

Ein 2D Top-Down Arena Brawler Spiel in Python mit Pygame.

## Features

### Singleplayer
- 🎯 Top-down Shooter Gameplay
- 🤖 KI-Gegner mit Upgrades
- 🔫 5 verschiedene Waffen (Pistole, Shotgun, Machinegun, Grenade Launcher, Rifle)
- 💪 Waffenupgrade-System
- 🎨 Charakter- und Munitionsfarben (inkl. Rainbow-Animation)
- 💀 Kill-Animationen (Blumen, Blutfleck, Grabstein)
- 🗺️ Mini-Map (käuflich im Spezial-Shop)
- 🏢 Zerstörbare Gebäude

### Multiplayer (1vs1)
- 🌐 Netzwerk-basiertes Multiplayer
- 🔗 Room-Code System für einfaches Matchmaking
- ⚖️ Alle Waffen auf Level 20 für faire Matches
- 🚫 Keine KI-Gegner im 1vs1
- 🔄 Automatische State-Wiederherstellung nach Match

### Shop-System
- Waffen-Upgrades (Feuerrate, Schaden, Spawn-Rate)
- Charakter-Farben (11 Farben inkl. Regenbogen)
- Munitions-Farben
- Kill-Animationen
- Spezial-Items (Mini-Map)

## Installation

```bash
# Repository klonen
git clone https://github.com/GM-2010/CityScramble.git
cd CityScramble

# Abhängigkeiten installieren
pip install pygame-ce

# Spiel starten
python main.py
```

## Steuerung

- **Bewegung**: WASD oder Pfeiltasten
- **Schießen**: Linke Maustaste
- **Gebäude zerstören**: Rechte Maustaste (10 Treffer pro Gebäude)

## Multiplayer spielen

1. Spieler 1: Klicke auf "1vs1 ONLINE" → "SPIEL HOSTEN"
2. Teile den 6-stelligen Room-Code mit deinem Gegner
3. Spieler 2: "1vs1 ONLINE" → "SPIEL BEITRETEN" → Code eingeben
4. Match startet automatisch!

## Projektstruktur

```
city_scramble_python/
├── main.py              # Hauptspiel-Logik, Menüs, Shops
├── sprites.py           # Spieler, Gegner, Projektile, Animationen
├── network.py           # Multiplayer Netzwerk-Modul
├── settings.py          # Spiel-Konfiguration
├── Background.mp3       # Match-Musik
├── start.mp3            # Menü-Musik
└── sound2.mp3           # Zusätzlicher Sound-Layer
```

## Technische Details

- **Engine**: Pygame CE 2.5+
- **Python**: 3.8+
- **Multiplayer**: Socket-basierter Relay-Server
- **Persistenz**: JSON-basierte Save-Datei

## Lizenz

Dieses Projekt ist Open Source.
