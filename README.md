# todo – CLI-Aufgabenverwaltung

Eine einfache Python-CLI-Anwendung zur Verwaltung von Aufgaben. Aufgaben
werden als JSON-Datei unter `~/.todo/tasks.json` gespeichert.

## Technologie-Stack

- **Sprache**: Python 3.10+
- **Framework**: [click](https://click.palletsprojects.com/)
- **Speicherung**: JSON-Datei (`~/.todo/tasks.json`)
- **Testing**: pytest

## Installation

```bash
pip install -e .
```

Damit wird der Befehl `todo` im PATH verfügbar.

## Nutzung

```bash
todo --help
```

### Verfügbare Befehle

| Befehl      | Beschreibung                                  |
|-------------|-----------------------------------------------|
| `add`       | Neue Aufgabe anlegen                          |
| `list`      | Alle Aufgaben tabellarisch anzeigen           |
| `filter`    | Aufgaben nach Status filtern                  |
| `sort`      | Aufgaben sortieren                            |
| `done`      | Aufgabe als erledigt markieren                |
| `remove`    | Aufgabe löschen                               |
| `edit`      | Beschreibung einer Aufgabe ändern             |
| `priority`  | Priorität einer Aufgabe ändern                |
| `due-date`  | Fälligkeitsdatum setzen oder löschen          |
| `search`    | Aufgaben nach Beschreibungstext durchsuchen   |
| `export`    | Aufgaben als JSON exportieren                 |
| `import`    | Aufgaben aus JSON importieren                 |
| `stats`     | Statistiken (Gesamt, Status, Priorität) anzeigen |

### Statistiken

```bash
$ todo stats
Gesamt: 5
Pending: 3
Done: 2

Nach Priorität:
  low: 1
  medium: 2
  high: 2
```

## Tests

```bash
PYTHONPATH=. py -m pytest
```
