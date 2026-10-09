# Projektstatus: CMS Unsicher

Stand: 9. Oktober 2026

## Ziel

Ein absichtlich verwundbares CMS für autorisierte Sicherheitsübungen. Die Anwendung soll später auf einer eigenen VM auf einem Proxmox-VE-Server laufen und über eine Subdomain hinter einem Nginx-Reverse-Proxy erreichbar sein. SSH, FTP und weitere Übungsdienste sollen später über separate Portweiterleitungen erreichbar werden. Die Serverkonfiguration erfolgt in einem späteren Schritt direkt auf dem Server.

## Was umgesetzt wurde

- Eine lokale `.venv` mit Python 3.13.5 erstellt. Alle Python-Abhängigkeiten wurden ausschließlich in dieser Umgebung installiert.
- Flask 3.1.2 und Waitress 3.0.2 über `requirements.txt` eingebunden.
- `app.py` mit SQLite-Datenbank, automatischer Erstinitialisierung und Demo-Daten erstellt.
- Login, Logout, Beitragssuche, Beitragserstellung, Beitragslöschung, Benutzerprofile und Adminübersicht umgesetzt.
- Deutsche HTML-Vorlagen und ein responsives dunkles Layout erstellt.
- Einen `/health`-Endpunkt für die Erreichbarkeitsprüfung eingerichtet.
- Start über Waitress eingerichtet; Standardadresse ist `127.0.0.1:8000`. Adresse und Port lassen sich über `CMS_HOST` und `CMS_PORT` einstellen.
- `.gitignore` für virtuelle Umgebung, Datenbank, Python-Cache und `.env` erstellt.
- Einrichtung, Demo-Zugänge, Übungsschwachstellen und Hinweise zum späteren Betrieb in `README.md` dokumentiert.

## Bewusst eingebaute Schwachstellen

- SQL-Injection in Login und Beitragssuche.
- Gespeichertes XSS durch ungefilterte HTML-Beitragsinhalte.
- IDOR: angemeldete Benutzer können fremde Profile und private Notizen lesen.
- Fehlende Rollenprüfung bei Adminübersicht und Beitragslöschung.
- Fehlender CSRF-Schutz und Beitragslöschung über GET.
- Klartextpasswörter und schwache Demo-Zugangsdaten.
- Fest hinterlegter Sitzungsschlüssel.
- Deaktiviertes `HttpOnly` bei Sitzungscookies.

Die Schwachstellen sind beabsichtigte Übungsziele. Ausschließlich fiktive Daten verwenden.

## Was geprüft wurde

Mit dem Python-Interpreter der `.venv` wurden zwei automatisierte Tests ausgeführt; beide waren erfolgreich:

1. Normaler Ablauf: Health-Endpunkt, Startseite, Zugriff ohne Anmeldung, falsches Passwort, Demo-Anmeldung, Beitragserstellung, Suche und Logout.
2. Übungsfunktionen: SQL-Injection beim Login und bei der Suche, fremdes Profil, Adminzugriff als normaler Benutzer, ungefilterte Skriptinhalte und Beitragslöschung.

Die Tests verwenden eine temporäre Datenbank. Sie führen keine Browser-Skripte aus; die XSS-Prüfung bestätigt, dass Skriptinhalt ungefiltert im HTML erscheint.

Eine visuelle Browserprüfung und ein Test auf dem Zielserver stehen noch aus. Die Tests belegen keine öffentliche Erreichbarkeit. Ein dauerhaft laufender Server wurde nicht eingerichtet.

## Lokaler Start

Im Projektordner unter Windows:

```powershell
.\.venv\Scripts\python.exe app.py
```

Anschließend `http://127.0.0.1:8000` öffnen. Die Datenbank wird beim ersten regulären Start in `instance/cms.sqlite3` angelegt.

| Benutzer | Passwort | Rolle |
| --- | --- | --- |
| admin | admin123 | admin |
| demo | demo123 | user |

Tests erneut ausführen:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Was noch gemacht werden muss

### Proxmox und Netzwerk

- Eigene VM und Betriebssystem für das Labor bereitstellen.
- VM in ein isoliertes Netz/VLAN setzen und Zugriff auf Proxmox-Verwaltung, produktive Systeme und interne Netze sperren.
- Ausgehende Netzwerkverbindungen passend zum Labor begrenzen.
- Sauberen VM-Snapshot und einen Rücksetzungsablauf vorbereiten.

### Anwendung auf dem Server

- Projektdateien auf die VM übertragen; die Windows-`.venv` nicht mitkopieren.
- Zuerst eine neue Linux-`.venv` mit `python3 -m venv .venv` erstellen und anschließend mit deren Interpreter die Abhängigkeiten installieren.
- Eigenen Dienstbenutzer, Dateirechte und einen systemd-Dienst für den automatischen Start einrichten.
- Bind-Adresse und Port entsprechend dem Standort des Nginx-Proxys festlegen. Bei einem getrennten Proxy den Anwendungsport nur für diesen Proxy freigeben.
- Anwendung auf dem Server starten und Login, Beiträge, Datenbankpersistenz und Neustarts prüfen.

### Subdomain und Nginx

- Konkrete Subdomain und DNS-Ziel festlegen.
- Nginx-Reverse-Proxy zur VM konfigurieren.
- TLS-Zertifikat und HTTPS konfigurieren.
- Erforderliche HTTP-/HTTPS-Portweiterleitungen und Firewallregeln einrichten.
- Erreichbarkeit über die Subdomain und Proxy-Verhalten prüfen.

### Weitere Angriffsflächen

- Gemeinsam festlegen, welche SSH-, FTP- und weiteren Dienste als Übungsziele dienen sollen und welche Schwachstellen gewünscht sind.
- Diese Dienste später direkt auf dem Server konfigurieren.
- Separate Portweiterleitungen und Firewallregeln für die ausgewählten Dienste einrichten und prüfen.

SSH-/FTP-Dienste, Portweiterleitungen, DNS, Nginx, TLS, VM und systemd wurden bisher nicht konfiguriert.

### Abschließende Prüfung

- Layout und Bedienung im Browser prüfen, einschließlich kleiner Bildschirmgrößen.
- XSS-Ausführung mit einem harmlosen Demonstrationsskript im Browser verifizieren.
- Übungsziele auf der Zielumgebung erneut prüfen.
- Netzwerkisolation, Logs und Rücksetzung auf den sauberen Snapshot testen.
- Tatsächliche Serveradressen, Ports, Startbefehle und Rücksetzungsablauf nach der Einrichtung dokumentieren.

## Wichtige Dateien

| Datei | Zweck |
| --- | --- |
| `app.py` | Flask-Anwendung, Datenbank und Start über Waitress |
| `requirements.txt` | Direkte Python-Abhängigkeiten |
| `templates/` | HTML-Seiten |
| `static/style.css` | Gestaltung |
| `tests/test_app.py` | Automatisierte Funktions- und Schwachstellenprüfungen |
| `README.md` | Einrichtung und Bedienung |
| `PROJEKTSTATUS.md` | Übergabe und offene Aufgaben |
