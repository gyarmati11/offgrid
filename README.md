# Deye off-grid dashboard – telepítés

2 × 6 kW párhuzamos Deye (Solarman) + 15 kWh akku + 3 bővíthető sztring.

## Mit kapsz
- **Otthon nézet**: ajánlás-sáv (ma/holnap fogyassz-e), élő értékek, energiafolyam, mai görbe,
  5 napos napelem-előrejelzés vs. várható fogyasztás, összesítő táblázat (ma/hét/hónap/év:
  kWh, önellátás %, megtakarítás Ft, hálózati költség Ft) és időszakválasztós grafikonok.
- **Szerviz nézet**: mindkét inverter részletesen, akku + BMS beállítások, sztringek kihasználtsága,
  hőmérséklet-grafikon (45/55 °C hűtési jelölőkkel), hálózat, munkamód, Time of Use programok,
  életciklus és akku-ciklusszám, diagnosztika, újraindítás megerősítéssel, összes beállítás.
- **Értesítések**: reggeli ajánlás, napközbeni ajánlásváltozás, esti holnapi előrejelzés,
  „akku tele – most fogyassz” (off-gridnél ez elveszett energia lenne), akku alacsony/kritikus, inverter-hiba.

## 1. HACS kártyák
- `apexcharts-card`
- `sunsynk-power-flow-card` (valószínűleg már megvan – a mostani „Deye” kártyád ez)

## 2. Package
1. `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
2. Másold a `packages/deye_offgrid.yaml`-t a `/config/packages/` mappába.
3. Fejlesztői eszközök → YAML → **Konfiguráció ellenőrzése**, majd HA újraindítás.

Első induláskor beállítja az alapértékeket (70,1 Ft/kWh elkerült ár, 36 Ft/kWh vételi ár,
15 kWh, 10 % tartalék). Ezek a Szerviz nézet aljáról bármikor átírhatók.

## 3. Entitásnevek ellenőrzése (FONTOS)
A Solarman/Forecast.Solar entitásneveket a képernyőképek alapján becsültem. Másold be ezt a
**Fejlesztői eszközök → Sablon** mezőbe, és a kimenet alapján javítsd a package-ben a
`# ⚠️` jelölt sorokat (vagy küldd el nekem a kimenetet, és kijavítom):

```jinja
{% for d in ['solarman', 'forecast_solar'] %}
### {{ d }}
{% for e in integration_entities(d) | sort %}{% if e.startswith('sensor.') or e.startswith('binary_sensor.') %}
{{ e }} = {{ states(e) }}{% endif %}{% endfor %}
{% endfor %}
### weather
{% for w in states.weather %}{{ w.entity_id }} {% endfor %}
```

A sztringek forrását (melyik inverter melyik PV bemenete melyik tömb) a `sensor.deye_string_1..3`
`state:` sorában állítsd be.

## 4. HACS elemek
HACS → Frontend (Irányítópult) → telepítsd:
- **Deye Ház Card** – saját kártya, egyéni tárolóként (lásd lent)
- **Bubble Card** – felugró részletes panelek
- **ApexCharts Card** – grafikonok
- **Sunsynk Power Flow Card** – csak a Szerviz nézet klasszikus energiafolyamához

### Deye Ház Card hozzáadása HACS-hoz
1. Töltsd fel a `deye-haz-card` mappa tartalmát egy saját, **nyilvános** GitHub tárolóba
   (pl. `github.com/<felhasználó>/deye-haz-card`), és készíts egy kiadást (Release), pl. `v1.0.0`.
2. HACS → jobb felső ⋮ → **Egyéni tárolók** → URL: a tároló címe, Típus: **Irányítópult (Dashboard)** → Hozzáadás.
3. Keresd meg a „Deye Ház Card”-ot → **Letöltés** → frissítsd a böngészőt.

A 3D képek a kártyával együtt települnek, külön másolni nem kell.

## 4/B. Dashboard
Beállítások → Irányítópultok → **Irányítópult hozzáadása** → Kezdés üresen → megnyitás →
⋮ → Szerkesztés → ⋮ → **Nyers konfigurációs szerkesztő** → illeszd be a `dashboards/deye_dashboard.yaml` tartalmát.
(Az URL tetszőleges – a felugró panelek `#hash` alapon nyílnak, nem függnek tőle.)

Sötét téma (ajánlott): másold a `themes/deye_sotet.yaml`-t a `/config/themes/` mappába, és a `configuration.yaml`-ba:
```yaml
frontend:
  themes: !include_dir_merge_named themes
```
(Bubble Card-ot és témát HACS-ból is lehet telepíteni; a téma nélkül is működik.)

**A ház kártya buborékjai – koppintás = felugró panel, nyomva tartás = előzmény:**

| Buborék | Mutatja | Koppintásra |
|:--|:--|:--|
| ☀️ Napelem | össz. teljesítmény · mai termelés · kihasználtság sáv | **Napelemek** panel |
| Ház / Ny / DK | sztring W · kihasználtság % · napszög ∠ | **Napelemek** panel |
| ∿ Inverterek | összterhelés · legmelegebb inverter °C (hibánál piros, villog) | **Inverterek** panel |
| 🔋 Akku | SOC · ▲ tölt / ▼ merül · idő · SOC sáv (20 % alatt piros) | **Akkumulátor** panel |
| ⌂ Ház | fogyasztás · mai fogyasztás | **Inverterek** panel |
| ⚡ Hálózat | teljesítmény / narancs „Lekapcsolva” | **Hálózat** panel |

Az energiafolyam-vonalak csak akkor mozognak, ha folyik az energia, és **minél nagyobb a teljesítmény, annál gyorsabban**.
Az akku vonala töltéskor az akku felé, merítéskor az inverter felé fut.

## 4/C. Sztring kihasználtság és napszög
Új szenzorok sztringenként (`sensor.deye_string_N_kihasznaltsag`, `sensor.deye_string_N_napszog`):

| Érték | Jelentés |
|:--|:--|
| Kihasználtság % | most / névleges csúcsteljesítmény (`csucs_w`) |
| Arány az összesből | ez a sztring adja a teljes PV hány %-át (attribútum) |
| Várthoz % | most / Forecast.Solar szerint most várt (tartósan alacsony → árnyék, kosz, hiba) |
| Napszög ∠ | a napsugár és a panel felülete közti szög: **90° = merőlegesen éri (ideális)**, 0° = nem éri |
| Beesési szög | a felület normálisához mért szög (= 90° − napszög), attribútum |

A számításhoz a sztring `dolesszog` és `azimut` attribútuma kell (0° = É, 90° = K, 180° = D, 270° = Ny).
A Szerviz nézetben táblázat és két napi grafikon (napszög, kihasználtság) mutatja mindhármat.

A 3D modell az `eszkozok/3d_telek` mappában van (`v2.html` = jelenet, `bake_v2.py` = képek kiégetése;
Python + Playwright kell hozzá). Új képek után másold őket a kártya `dist` mappájába, és adj ki új verziót.

## 5. Új sztring hozzáadása
1. A package-ben másold ki a `Deye string 4` sablont, írd át a forrás entitást és a feliratot.
2. Vedd fel a `group: deye_napelem_sztringek` listába.
3. A PV összteljesítmény, a sztring-táblázat és az előrejelzés automatikusan számol vele.
   (Grafikonra és a power-flow kártyára `pv4_power_189`-ként kézzel kell felvenni.)
   Ha új Forecast.Solar tömböt is felveszel, add hozzá a 4 `Deye előrejelzés …` szenzor összegéhez.

## Hogyan dönt az ajánlás?
- **Várható napi fogyasztás** = utolsó 7 nap átlaga (első napokban a tegnapi érték, ill. 10 kWh).
- **Mai mérleg** = ma még várható napenergia + akku a tartalék felett − mára még hátralévő
  fogyasztás − éjszakai tartalék (alap 35 % = éjféltől napkeltéig).
- **Holnapi mérleg** = holnapi előrejelzés − várható fogyasztás.
- Küszöb (alap 3 kWh) felett „sok”, 0 alatt „hiány”:
  ma sok + holnap hiány → *Ma érdemes fogyasztani*; ma hiány + holnap sok → *Halaszd holnapra*;
  mindkettő sok → *Bőség*; mindkettő hiány → *Takarékos*; akku ≥ 95 % és jóval több nap, mint
  fogyasztás → *Most kapcsolj be nagyfogyasztót*.
- 3–5. nap: időjárás felhőzet alapján becsülve, a holnapi Forecast.Solar értékhez kalibrálva.

## Forint számítás
- **Megtakarítás** = (fogyasztás − hálózati vétel) × elkerült áramár
- **Hálózati költség** = hálózati vétel × vételi ár
- Halmozott számláló, így árváltozáskor a múlt nem íródik át. A statisztika a telepítés
  pillanatától gyűlik (kWh grafikonok szintén).

## Megjegyzések
- A „DC Temperature” −48 °C értéke a Fő inverteren szenzorhiba/nem használt regiszter.
- A `notify.notify` minden eszközre küld; saját telefonra cseréld `notify.mobile_app_<telefon>`-ra.
- Time of Use beállításokat párhuzamos rendszerben a **Fő** (master) inverteren módosítsd.
