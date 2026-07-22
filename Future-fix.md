# Future fix


While at it, also check if we have support for fetching query_string for requests, and if we dont lets fix that too.


---


Legg inn Jitter i task runs (cronjobs)



---


Remove one of the fixes for HTTP method:

Hva tror du er mest performant av de to her alternativene?

Denne:
https://github.com/Defendinary/future/commit/7096b8830ffbcdbad7ac5c2bc8c6d1348c167135#diff-7553b9050b5c45bfd8783d6a93043ca31f36d99233bc75e2c0b27162784ff29d

eller:
https://github.com/Defendinary/future/commit/e468fa39cc1c8dbe3458e34744d8b861b1298ba0#diff-7553b9050b5c45bfd8783d6a93043ca31f36d99233bc75e2c0b27162784ff29dR363-R374
https://github.com/Defendinary/future/commit/e468fa39cc1c8dbe3458e34744d8b861b1298ba0#diff-c4ce3fa17516da2284f72332d24e9754a2da9c9f2758aa365a51b52f1fbdd4e6


Hadde glemt jeg allerede hadde laget en fiks for det, så nå er det dobbeltsjekk
Nyeste fixen er 2. hvor jeg la til logikken i route.match når man matcher path, så sjekker den bare method først
Istetenfor at det gjøres senere, slik som i 1.

Nic [pwn.],  — 3/20/26, 4:54 PM

---

Og et annet spørsmål: Ser på å implementere session og cookie greier litt mer integrert i rammeverket. Lurer nesten på å lage det som en Middleware man selektivt kan velge å bruke? Thoughts? Er det mandatory å ha i core eller går det greit som en middleware?
Er jo ikke noe vits å tvinge inn i core og sjekke for cookies hvis man ikke planlegger å bruke det anyways (?)

Nic [pwn.],  — 3/20/26, 5:35 PM
ChatGPT sier det er textbook middleware. Men den sier også at core burde "provide a clean mutation API (request.session[...]), men at session logikken er middleware. 

starR — 3/20/26, 10:57 PM
Vil jo tippr .2 er raskest. Kan du ikke benchmarke?
Cookies lager du bare støtte for i headers om du ikke har det. Ville laget det som en eget object. Det å sjekke og bruke en cookie er en middleware ting. Må selff huske å inkludere cookies i header når det er i bruk da.
Hva skal du med sessions? 

starR — 3/20/26, 11:04 PM
Bruk msgspec for alt av json encoding/decoding og "datamodeller" ( msgspec.Struct)
Du har masse gains på å ikke bruke built-in json i python

Nic [pwn.],  — 3/21/26, 12:10 AM
Trenger det vel egentlig ikke, nei. Var for å teste OpenIdConnect middlewaren jeg har jobbet med med Future, så man kan logge inn med Azure AD. Det bruker sessions, men kan sikkert skrive rundt det men å gjøre cookie settingen manuelt
Var derfor jeg kom på: burde Future ha støtte for det? Kan jo løse det med å sette cookies og lese dem igjen, men tenkte mer built-in
Får ikke testet mer atm. Har ikke hatt internett på flere timer. Telia styrer med noe

starR — 3/21/26, 12:23 AM
veldig rart om de bruker sessions synes jeg. Må jo være cookies med jwt? eller bare jwt?

Nic [pwn.],  — 3/21/26, 1:05 AM
Storer bare user object i session, som blir satt som cookie
Var bare om jeg skulle implementere at man kan:
request.session["user"] = user_data

og at når du får respons, så returnerer den Set-Cookie: user=userdata
Men kan jo bare gjøre det med headerne manuelt. Må ikke ha request.session satt.
Men om man hadde implementert request.session greiene så hadde rammeverket ordnet det automatisk når du brukte request.session, slik som i Flask etc.
At man slipper å sette headerne
