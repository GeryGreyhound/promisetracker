# Ígéretfigyelő

Politikusok nyomon követése, hogy betartják-e a kapmány igéreteket, vagy nem.

Olvasd el más nyelveken is: [English](README.md)

## Kezdő lépések

Ez a leírás segít elindítani a projektet a saját gépeden fejlszetéshez vagy teszteléshez.

### Előfeltételek

Mindenképp fel kell telepítened ezeket a fejlesztői eszközöket:
- [Python 3](https://www.python.org/) (minimum 3.4)
- [PostgreSQL](https://www.postgresql.org/)

### Telepítés

1. Telepítsd a függőségeket a `pip install -r requirements.txt` paranccsal
2. Másold le az env sablont `cp .env.example .env` majd töltsd ki a hiányzó értékeket
3. Hozz létre egy új adatbázist `createdb igeretfigyelo`
4. Töltsd be a tábla szerkezetet `psql -f db/schema.sql -d igeretfigyelo`
5. Generálj egy minta adatbázist `python db/seeds.py` (ki fog törölni minden eddigi adatot!)

Alapértelmezett felhasználók (email / jelszó):
* admin@example.com / LetMeIn
* editor@example.com / LetMeIn

## Futtatás saját gépen

1. Indítsd el a szervert `python __init__.py`
2. Niysd meg a `127.0.0.1:8080` vagy `localhost:8080` oldalakat
3. Jó munkát a fejlesztéshez :)

## Tesztek futtatása

Nem igazán készültek még automata tesztek :(

### Kód ellenőrzés

Még nincs kód stílus ellenőrzés bekötve :(

## Közreműködés

Kérlek olvasd el a [CONTRIBUTING.hu.md](CONTRIBUTING.hu.md) leírást a részletekért

## License

Nem lett még meghatározva explicit licensz :(
