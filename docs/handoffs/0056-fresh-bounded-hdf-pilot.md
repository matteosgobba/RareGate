# Task0056 — Nuovo pilot HDF ristretto sullo startup riparato

## Metadati e decisione

2026-10-15, Europe/Rome. Stato **`partial_failed_development_hdf_pilot_v2`**;
qualifica generata dichiarata **16/16 pass sul sorgente finale**, accettazione
pilot/readiness operativa **false**. La nuova sessione P4 è consumata. PCA ha
completato un run reale valido; il tentativo supervisore AE è fallito prima di
avviare entrambi i worker. Nessun repair/retry o modifica sorgente/config dopo
l'attivazione. Nessun secondo gruppo generato o Task0057.

Base effettiva pulita: `main`, upstream `origin/main`, HEAD
`6ca5c347d77061cfb34a9cdd5656253c2aa4d73e`, indice vuoto, riferimenti locali0/0,
memoria1.50→1.51. Task0055 era stato committato dopo il planning: nessuna sua
modifica pendente da attribuire a0056 o separare per hunk. Il suo base storico
0dd42ee7 resta. Nessuna verifica fresca di remoto/push/CI e nessun Git automatico.
[Prompt effettivo](../prompts/0056-fresh-bounded-hdf-pilot.md) e handoff iniziale
salvati prima del lavoro sostanziale. Letti istruzioni/living context, evidenza
curata0055, metodo/spec0054, contratto v2 e sorgenti pertinenti. Nessun vecchio
journal ignorato o controller operativo storico riaperto/eseguito.

## Cosa è cambiato prima dell'attivazione

Nuovo `PilotContext56` immutabile: task/root/prompt/bundle/ruolo/budget e receipt
16check verificati prima del payload. `FixtureContext56` è un tipo distinto e
limitato ai file generati posseduti. I vecchi helper di lifecycle ricevono il
contesto esplicito; non viene copiato il controller, impersonato0054, modificato
un grant/config storico o monkeypatchato un provider. `RuntimeSession` e politica
joint inner+owned-tracker80MiB rimangono gli stessi qualificati in0055. Bootstrap,
help/error e API generate restano senza permesso operativo/fallback.

L'ispezione statica ha trovato che i13file piccoli per candidato richiedono
320.343B(PCA)/377.025B(AE), oltre262.144B. Nuovo envelope esplicito393.216B,
con totale applicativo derivato7.444.432B entro8MiB. Il primo test NPY ha rilevato
una vista non posseduta da `np.load(BytesIO(...))`: ora il loader condiviso valida
forma/tipo esatti e produce una copia C posseduta. Nessuna coercizione tollerante,
fit o modifica a feature/scaler/modelli/threshold. Errori startup e post-service
conservano separatamente fase, errore primario/report e budget. Le verifiche byte
piccole iniziali/finali sono conteggiate per ruolo; non si dichiarano verificate
le sorgenti dell'altro candidato.

Sorgente/config/prompt finali: **41 pin**, bundle
`38a3031a333eb8532233873675ef8491b3d178a5cb43886f54fdf56402c28614`.
Ancore0055 da17117/34181/281273B e bundle storico27753982… verificati; nove fonti
storiche e loro byte restano preservati. Componenti storici verificati anche nel
commit base; runtime CPU/resource policy non riscritti. Report/config/risultati/
prompt/handoff precedenti invariati.

## Software e fixture generate

**123 test focalizzati finali passati**:22nuovi,57startup,40integrazione precedente,
4pure v2. Tre esecuzioni pure conservate:120con1failure proprietà NPY, poi122e123
pass;365esecuzioni/364pass. Nessun modulo modello caricato nel processo dei test
puri. Un rifiuto preparatorio del limite stringa JSON avviene prima della creazione
file: snapshot living suddiviso in chunk, limite non allargato. Numerica generata
unitaria aggiuntiva, distinta dai conteggi nativi.

Un gruppo congelato:12core+2bootstrap CPU reali source-free+2fixture serializzate,
**16invocazioni /688offerte configurate** su32/4096/240s. Tutte le aspettative
passano; fault iniettati restano workload anormali, con torn/unknown conservati.
Le due fixture usano artifact/from_artifact/score delle classi effettive e un
dataset stand-in rigoroso; zero HDF generati o sorgenti di produzione. Per fixture:
64feature setup singleton,1modello creatore rilasciato+1caricato,14file serializzati,
2handle stand-in,16contesti gate e62/64offerte completate con riferimenti differiti.
Golden ha1024righe di formato,64popolate/poi presentate: i campi lineage artificiali
non sono misure di preparazione/fitting/acquisizione.

Core: minimi439read/436feature-score aritmetici/435reference,436C; torn unknown.
Fixture serializzate:188chain/412righe raw-feature più128feature setup,
344public/680score rows/2720Booleans,2creator+2loader/0optimizer. Due worker CPU
importano librerie vere senza sorgenti/modelli; thread/build supportati.
Append generati, incluse fixture:1322event/3superamenti50µs, max96.417µs;
3601batch/0superamenti200µs, max120.791µs. Nessun benchmark recorder o sottrazione
observer. Il percorso supervisore che riusa lo stesso journal fra due candidati
non era incluso nelle16aspettative: questa lacuna è ora osservata fisicamente.

## Sessione operativa nuova e conteggi

Task0056 è una nuova autorizzazione, non retry di0054. I17originali sono copiati
come identità attese dalla spec immutabile, senza traversare link/byte_pins. Solo
metadata path/type/size prima di P4. Nel pilot: due SHA raw completi da2908260409B,
totale **5816520818B**, hash originale corretto;13ruoli PCA verificati due volte.
I3file AE modello/config/calibrazione restano soltanto attesi, non verificati né
caricati. Membership originale6999caricata una volta, prefix1024ordinato stabile
e golden1024×8originale una volta; payload hash corretti.

| Confine reale | PCA | AE supervisor |
| --- | ---: | ---: |
| Configurate / submitted / admitted / completed |64 /64 /63 /63|64 /0 /0 /0|
| Rejected contention / missed / final pending |1 /0 /0|0 /0 /0,64future|
| Fixed raw calls / rows |32 /144|0 /0|
| Stream raw calls / rows |63 /63|0 /0|
| Tutti raw=feature calls / rows |95 /207|0 /0|
| Fixed golden calls / rows |16 /72|0 /0|
| Realized golden calls / rows |63 /63|0 /0|
| Public calls / score rows / Booleans |174 /342 /1368|0 /0 /0|
| Membership/golden/candidato+threshold loads |1 /1 /1|0 /0 /0|
| HDF opens/closes / schema checks |2 /2 /4|0 /0 /0|

63posizioni raw distinte raggiunte, sempre fra0..63; gate0..7. Richieste1..8,
full700particle/features congelate, PCA6/SSE FP64/strict4, output posseduti. Gate
pre/post esatti a ogni m1..8, due catene raw più un reference golden per shape;
63gruppi stream tutti **m1 con B8 nominale**, ognuno referenziato una volta dopo
drain. Parametri/scaler/input/threshold invariati.4maschere non sono4eventi.
A H:62C+1active; dopo drain63C/252maschere stream, zero pending. Tutto dentro i
limiti prospettici invariati192chain/416righe/352public688score/2752Booleans.

Il trasporto porta descrittori software prima di HDF, non byte evento/rivelatore.
PCA submitted500/s su128ms; output−intended max3.965041ms(n63), producer lag
.369041ms(n64), queue1.951417ms(n63), service2.593542ms(n63). Deadline illustrativa
100ms:0miss fra63completati; nessuna latenza assegnata al rifiuto o alle64offerte
future AE. PCA append128event/756batch:0superamenti, max26.125/72.875µs.
Non sono capacità sostenuta, p99produzione o inferenze da eventi indipendenti.

Custody, pre-gate, golden/reference, modello trattenuto e storia host scaldano
input. A chiuso e B riaperto con1MiB/521slot/w0.75effettivi, nessun rawwarmup su B;
non cold OS cache. Nessun purge/reboot/chiusuraapp/prefetch né confronto causale
cache/trasporto/candidati. Geometria chunk non è conteggio I/O/cache miss.

## Fallimento, risorse e incertezza

AE: osservazione tracker **13156352B**, joint **44711936B**, ritorno96/errno0,
stato observed. Subito dopo: `QuotaError: Unregistered diagnostic descriptor`,
conservato nella `ResourceFailure: Tracker diagnostic publication failed`.
Valore valido sotto soglia, non superamento RSS. Il journal di sessione è aperto
dopo lo snapshot `previous_fds` del caso PCA; `emergency_release` lo chiude e
rimuove da FDS, ma l'oggetto Journal sopravvive. La pubblicazione ready AE sul
descrittore conservato fallisce prima di entrambi i child/t0. È evidenza attuale
più ispezione sorgente, non traceback recuperato0054 o parity failure AE.

PCA worker exit0/close/reap normali; AE worker non avviati. Subject exit1, nessun
forced/watchdog error esterno, subject reaped/group absent e42nomi SemLock pilot
assenti. Chiusura finale del journal obsoleto non certificata separatamente dal
subject: eventuale retirement di processo non sana il lifecycle/reporting fallito.
Nessun repair/retry, seconda suite o sorgente modificato dopo P4.

Ledger **504voci/28631424B entro33554432B**, tutte prove/fixture/source/report/
receipt/emergenze/copie curate simultanee; prenotazioni inutilizzate trattenute,
nessuna cancellazione per recuperare budget. Radice nuova unica ignorata:
`data/task0056-validation/session-v2`. Byte logici e blocchi file allocati distinti
nel summary, metadata/kernel sconosciuti.21SemLock per core,0espliciti CPU/observer,
315nomi complessivi assenti (273generati+42pilot); backing kernel non provato.

Generated subject **14.205127916s**, con4sreserveobserver18.205127916s su240s;
pilot subject **6.633486583s**, con2sreserve8.633486583s su180s. Import/setup,
report, finalizzazione/exit/reap inclusi; receipt fuori subject e riservata, curation
statica successiva separata, non coda temporale inventata. Gap esterni massimi
13.321333/31.797750ms sotto250ms. PCA consumer peak361938944B, producer29933568B,
inner31555584B, tracker16777216B; joint48332800B e carica conservativa490536960B
includendo outer48MiB sotto512MiB. Peak sovrapposti/non simultanei, non RAM unica.
Torch intra/inter1, OpenMP1, Accelerate1/determinismo/rounding0 prima/dopo servizio
PCA passano. Decoder effective unknown; heap Python8MiB/native workspace512MiB
restano target non attribuiti, non provati da RSS.

Le etichette private ereditate `synthetic_stage_counts`, stringa timing fixture e
`event_dataset_values_read:0` del helper metadata sono preservate, ma non sono uno
zero operativo: il PCA usa dati reali e quel0vale per la sola query di metadata.
La curation esplicita l'interpretazione corretta senza cambiare evidenza nativa.

## Consegna e prossima decisione

[Report inglese](../development-hdf-consumer-pilot-v2.md),
[scope congelato](../../configs/streaming/development_hdf_consumer_pilot_v2.json),
[18righe](../../results/tables/final/task0056-development-hdf-pilot-cases.csv),
[summary](../../results/tables/final/task0056-development-hdf-pilot-summary.json).
README/indice/memoria aggiornati in loco a1.51. Qualifica generata positiva e
integrazione PCA reale valida non equivalgono all'accettazione del pilot completo.

Prossima decisione: riparazione **software-only** dell'ownership del journal e
qualifica generata del lifecycle sequenziale supervisore/candidati prima di
qualsiasi nuovo P4. AE reale resta non misurato. Nessuno studio24×768/840s concesso,
nessun Task0057 lanciato. Preservati0054fallito/consumato,0055storico,0053qualificato,
0052parziale-negativo,0049chiusura,0036unresolved,0034gate,YES/YES/YES,particle192/192
consumati/deferral canonico,0024export accettato versus0025performance fallita,
tutti gli esiti e nessun MPS corrente. Nessuna nuova utilità scientifica/efficienza
fisica/causalità nonlineare/conferma indipendente/detector readiness/affiliazione
ufficiale CERN o esperimento.

## Git manuale

Task0055 già committato nel base6ca5c347: nessuna sua modifica pendente da includere
per dipendenza. Solo i21percorsi Task0056 elencati nella consegna vanno selezionati,
dopo review completa anche dei nuovi file. Non includere data/fixture/diagnostica,
modelli, ambienti o altro lavoro; niente `git add .`. Messaggio proposto:
`feat(streaming): wire fresh HDF pilot and record partial outcome`.
Review status/diff, staging selettivo, review staged, commit e push `origin main`
restano manuali. Nessun commit/push/CI Task0056 è stato inventato.
