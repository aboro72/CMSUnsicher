# CMS Unsicher

Absichtlich verwundbares Flask-/SQLite-CMS für autorisierte Sicherheitsübungen mit fiktiven Daten. Python wird ausschließlich über die projektspezifische `.venv` ausgeführt. Die virtuelle Umgebung trennt die Pakete; ihre Python-Version stammt vom Interpreter, mit dem sie erstellt wurde.

## Windows

Die `.venv` ist bereits angelegt. Für eine neue Installation:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Öffnen: http://127.0.0.1:8000

## Linux / spätere Proxmox-VM

Eine Windows-`.venv` nicht auf Linux kopieren, sondern dort neu erstellen:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Waitress dient als HTTP-Server, ohne Flask-Debugger. Standardmäßig lauscht die Anwendung nur auf `127.0.0.1:8000`. Für einen Nginx-Proxy auf einem anderen Host kann später `CMS_HOST` auf die isolierte VM-IP gesetzt werden; `CMS_PORT` legt den Port fest. Firewall-Zugriff auf diesen Port auf den Proxy begrenzen.

Die öffentlich angreifbare VM in einem eigenen VLAN/Netz betreiben, Zugriff auf Proxmox-Verwaltung und interne Netze sperren, ausgehende Verbindungen begrenzen und einen sauberen Snapshot für Rücksetzungen vorhalten. Keine echten Zugangsdaten, geteilten Laufwerke oder produktiven Daten verwenden. TLS endet später am Nginx-Proxy. SSH/FTP, Portweiterleitungen, VM und Nginx sind noch nicht konfiguriert.

## Demo-Konten

| Benutzer | Passwort | Rolle |
| --- | --- | --- |
| admin | admin123 | admin |
| demo | demo123 | user |

## Absichtliche Schwachstellen

- SQL-Injection in Anmeldung und Beitragssuche durch SQL-Stringverkettung.
- Gespeichertes XSS: Beitragsinhalte werden als ungefiltertes HTML dargestellt.
- IDOR: angemeldete Benutzer können fremde Profile und private Notizen abrufen.
- Fehlende Rollenprüfung im Adminbereich und beim Löschen von Beiträgen.
- Fehlender CSRF-Schutz, inklusive Löschen über GET.
- Klartextpasswörter, schwache Demo-Zugangsdaten und fest hinterlegter Sitzungsschlüssel.
- JavaScript kann Sitzungscookies lesen (`HttpOnly` ist deaktiviert).

Dies sind Übungsziele und dürfen bei einer echten Anwendung nicht übernommen werden. SQLite liegt in `instance/cms.sqlite3` und wird beim ersten Start automatisch initialisiert. Zum Zurücksetzen Server stoppen, diese Datei entfernen und neu starten. Alle Beiträge und Änderungen gehen dabei verloren.

## Prüfung

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
