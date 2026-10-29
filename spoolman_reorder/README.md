# Spoolman Reorder Upgrade

Home-Assistant-App von OrbitNestLab auf Basis von Spoolman 0.27.0
(bed3f14ee77a3a571d31b14215d54b0b88a7519c), mit einer Nachbestellansicht direkt in v2.
Die Oberfläche ist auf Deutsch und Englisch verfügbar.

## Testinstallation

Repository hinzufügen: https://github.com/OrbitNestLab/spoolman-reorder-upgrade

Die App verwendet standardmäßig Port 7913. Das bestehende Spoolman kann auf
7912 weiterlaufen. Die neue App speichert unter ihrem eigenen /data/spoolman.
In den Optionen kann import_from_app einmalig auf den Slug der vorhandenen
Spoolman-App gesetzt werden. Deren app_config/spoolman.db wird ausschließlich
lesend mit der SQLite-Backup-Funktion kopiert. Der Import läuft nur, solange
die neue App noch keine Datenbank besitzt. Vor einem Fehler wird keine
halbe Kopie als gültige Datenbank abgelegt.

Die Kopie ist ein Zeitpunktstand. Änderungen durch HaspelSync werden weiter
in der ursprünglichen App gespeichert und erscheinen nicht automatisch in
der Testkopie. Vor einer produktiven Umstellung muss erneut sauber kopiert
und die URL der Verbraucher kontrolliert werden.

## Nachbestellen

Unter /reorder lassen sich Gramm-Schwelle, ungeöffneter Mindestvorrat und
Bestellmenge unabhängig voneinander speichern. Auch 0 g ist gültig.
Einzelne Profile können abweichende Regeln erhalten. Die Regeln verwenden
die bestehende Settings-Tabelle; es gibt keine neue Bestandsmigration.

Nicht archivierte Rollen werden pro Hersteller, Material, Name,
Farbe und Ausführung zusammengezählt. Unbekannte Gewichte blockieren
automatische Vorschläge. Nur wirklich unbenutzte volle Rollen zählen
als Reserve; konfigurierte Lagerorte helfen bei fehlenden Datumsangaben.
Bei ausreichender Reserve erfolgt kein Vorschlag. Mindestvorrat 0
deaktiviert die Nachbestellung für die betreffende Regel.

Der optionale Bambu-EU-Katalog enthält 33 Produkte und 259 Varianten zum
Stand 29.10.2026. Varianten-ID, SKU, Farbe, Gewicht und Refill/mit Spule
sind getrennt erhalten. Ein versehentlich mitgeführter PTFE-Verbinder
wurde entfernt. Neue Produkte und Verfügbarkeit erfordern eine
erneute Katalogabfrage. Der generische Kern enthält keine Bambu-Daten.

Exakte Bambu-Refill-Zuordnungen können vorgeschlagen und anschließend
gespeichert werden. Für andere Verpackungen und nicht eindeutig passende
Artikel steht die Katalogauswahl oder manuelle Variantennummer bereit.
Shopify-IDs und Artikel-SKUs sind unterschiedliche Kennungen; der
Warenkorb benötigt die numerische Shopify-Varianten-ID.

Ein Warenkorb-Link öffnet einen vorbereiteten Warenkorb, ändert keinen
Bestand und löst weder Kauf noch Zahlung aus. Fehlende Zuordnungen
werden angezeigt und im Link ausgelassen. Einzelne Produktlinks helfen
beim Prüfen. Lagerverfügbarkeit muss im Shop geprüft werden.

### Aktuelle Einschränkung beim Bambu-Shop

Am 29.10.2026 wurde der konkrete Multi-Item-Link anonym per HTTP geprüft:
Die EU-Shop-Oberfläche antwortet auf /cart/VARIANT:QTY mit HTTP 404.
Die zugehörige myshopify.com-Adresse liefert zwar eine Warenkorbseite,
leitet aber per JavaScript zur Bambu-Startseite um. Ein alternativer
Checkout-Aufruf war per API nicht verlässlich erreichbar.
Deshalb ist für Bambu derzeit kein direkter Warenkorb freigegeben.
Die Shop-Adresse bleibt leer; die Artikelzuordnungen und Produktlinks
bleiben verwendbar. Eine erfolgreiche HTTP-Antwort alleine gilt nicht
als bestätigter Warenkorb. Für andere kompatible Shopify-Shops bleibt
die generische Permalink-Funktion verfügbar.

## API und Tests

- GET /api/v1/reorder: erforderliche Bestellungen
- GET /api/v1/reorder?include_sufficient=true: alle aktiven Profile
- GET /api/v1/reorder/cart: kombinierter Link mit ausgeschlossenen Profilen
- GET /api/v1/reorder/catalog: optionaler Katalog
- GET/POST /api/v1/setting/reorder_defaults
- GET/POST /api/v1/setting/reorder_profiles
- GET/POST /api/v1/setting/reorder_stock
- GET/POST /api/v1/setting/reorder_providers

Der Body eines Settings-POST ist wie bei Spoolman üblich ein
JSON-kodierter String. Beispiel für die Gramm-Schwelle:
`"{\"threshold_g\":0,\"unopened_min\":1,\"order_qty\":1}"`

upstream.patch enthält die Änderungen gegen den exakten Basis-Commit.
Die Tests erstellen eine temporäre SQLite-Datenbank. Geprüft werden
Grenzwerte, Reserven, Duplikate, ungültige Einstellungen, sichere
Warenkorb-URLs und Persistenz mit einem neuen API-Client.

## Rollback

Test-App stoppen. Die ursprüngliche App und deren Daten bleiben erhalten.
Eine produktive Umschaltung auf Port 7912 ist ein eigener, nachgelagerter
Schritt nach dem Funktionstest. Kein Backup muss für diesen Test
zurückgespielt werden.

## Lizenz / Upstream

Spoolman stammt von Donkie und steht unter MIT. Die Originaldateien und
deren Lizenz bleiben im Basis-Image erhalten. Die generischen Änderungen
in upstream.patch sind ebenfalls MIT und sollen nach Review gegen den
aktuellen Donkie/Spoolman-Stand portiert werden. Die HA-Verpackung und
der optionale Provider-Katalog werden separat gepflegt.
