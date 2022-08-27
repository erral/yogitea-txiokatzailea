# YogiTea mezu-txiokatzailea

YogiTea infusio boltsetan datozen testuak euskarara automatikoki itzuli eta txiokatzeko tresna.

YogiTea mezuen jatorria nik kudeatzen dudan Google Kalkulu orri baten dago, ez dizut kalkulu horretarako sarbiderik emango nahiz eta bere identifikadorea kodean bertan dagoen.

Scripta Googleren kalkulu orrietara sartzeko adibide gisa ere erabili daiteke. Horretarako Googleren APIa erabiltzeko aplikazio bat sortu behar da, kredentzialak sortu eta berauek `credentials.json` izeneko fitxategi baten deskargatu.

## Twitterren txiokatu

Twitterren txiokatzeko Twitteren APIa erabiltzen da, beraz Twitterren kontu bat izan behar duzu, bertan aplikazio bat sortu eta bere kredentzialak `credentials.twitter.json` izeneko fitxategian gordeta izan behar dituzu. Bere edukia honelakoa izan behar da:

```json
{
  "API_KEY": "XXXXXXXXXXXXXXXXXXXXXX",
  "API_SECRET": "XXXXXXXXXXXXXXXXXXXXXX",
  "BEARER_TOKEN": "AAAAAAAAAAAAAXXXXXXXXXXXXXXXXXXXXXX",
  "ACCESS_TOKEN_KEY": "XXXXXXXXXXXXXXXXXXXXXX",
  "ACCESS_TOKEN_SECRET": "XXXXXXXXXXXXXXXXXXXXXX"
}
```

## Mastodonen tooteatu

Mastodonen tooteatzeko ere zure Mastodon instantzian aplikazio bat sortu behar duzu eta bertako hiru gakoak dituen JSON fitxategi bat sortu karpeta honetan `credentials.mastodon.json` izenarekin. Bere edukia horrelakoa izan behar da:

```json
{
  "CLIENT_ID": "XXXXXXXXXXXXXXXXXXXXXX",
  "CLIENT_SECRET": "XXXXXXXXXXXXXXXXXXXXXX",
  "ACCESS_TOKEN": "XXXXXXXXXXXXXXXXXXXXXX"
}
```

Lizentzia: GPLv3
