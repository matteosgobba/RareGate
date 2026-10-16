# Task0058 — Pilot HDF AE-only: parità reale positiva, esito complessivo parziale

Stato: `partial_bounded_development_ae_hdf_pilot_storage_guard_gap`.
`native_pilot_checks_passed=true`, `real_AE_integration_parity_observed=true`,
`pilot_accepted=false`, prontezza operativa generale falsa. P4 nuovo di Task0058
concesso, attivato e consumato una volta. Nessuna riparazione o ripetizione reale.
Il mancato completamento riguarda il controllo preventivo globale dello storage,
non un fallimento dei gate AE, della custodia o del teardown nativo.

## Base, mandato e fonti

Base effettiva2026-10-15 Europe/Rome: `main`/`origin/main`, HEAD
`65f4522fedfef7e4e584f30de0f24d8626cef08d`, albero pulito e indice vuoto;
Task0057 già committato, nessuna dipendenza preesistente da separare. Chiusura
redazionale2026-10-16; memoria1.52→1.53. Nessuna verifica remota/push/CI, nessuno
staging/commit/push automatico. Il [prompt effettivo](../prompts/0058-bounded-ae-hdf-pilot.md)
autorizza esclusivamente una nuova sessione AE-only, dopo i prerequisiti software.

[Configurazione congelata](../../configs/streaming/development_ae_hdf_pilot_v1.json),
[rapporto inglese](../development-ae-hdf-pilot.md),
[26 righe curate](../../results/tables/final/task0058-development-ae-hdf-pilot-cases.csv)
e [summary](../../results/tables/final/task0058-development-ae-hdf-pilot-summary.json)
sono la consegna. Il bundle finale44pin è
`6cd0fc14666ea54d903ec93882bc756035198bba82d9aecdf4da9289226e6aed`.
Le ancore0057, la policy aritmetica e i componenti qualificati sono conservati;
nessun vecchio payload nativo ignorato è stato riaperto.

Il contesto operativo0058 chiude piano/root/task/ruolo/parent/bundle/ledger/
attivazione; la tupla è solo `("compact-autoencoder-v2",)`. Il piano unico guida
avvio, accettazione e candidati intended/attempted/unattempted nello stesso controller.
Il default storico PCA→AE resta. Le capability generate non possono armare originali
né P4; richieste PCA vengono respinte prima dei worker/accessi. Import/help/errori
non attivano. Restano lo stesso RuntimeSession, core, consumer, policy joint80MiB e
journal eager registrato prima degli snapshot. Runtime e policy risorse non sono
modificati. Nessun modello/runtime alternativo, controller duplicato o monkeypatch.

## Qualificazione software: positiva, con cronologia completa

169 aspettative distinte focalizzate/compatibilità hanno osservazioni passanti
prima del lavoro nativo:411 esecuzioni pure,408pass/3fail, più due errori iniziali
dell'adattatore di logging. Un run completo154call conserva153pass/1fail dovuto
allo stato del test harness; rerun selettivi coprono le correzioni dell'harness e
dell'oracolo. Non sono169 test tutti passati insieme in un unico run senza errori.
Nessun test puro avvia casi nativi o legge originali. Lint/formato focalizzati
passano; la verifica statica finale disabilita la cache.

È stato riservato e usato **un solo gruppo** congelato:12core+3sessioni0057+
1sessioneAE-only nuova, tutte16 le aspettative passano sul medesimo bundle.
18dispatch sottostanti,1008offerte pianificate,944configurate nei dispatch tentati;
64AE restano intenzionalmente non tentate dopo il fault del primo candidato.
Il normale generato completa61/64per candidato, il PCA prima del faultAE63/64,
l'AE-only62/64. Le sessioni iniettate restano workload invalidi: contano come
software check solo per fault/incertezza/cleanup attesi, non come drain normali.
357nomi SemLock assenti a fine verifica.

Lavoro artificiale positivo:388intenti raw/896righe richieste,387catene ritornate/
895feature rows;702public call/1466score rows/5864Booleane,315reference/571righe.
Una richiesta/riga in-flight e una close stand-in restano non osservate nel fault.
Setup separato128feature rows,2modelli creator/2serializzati,5caricamenti tramite
vere classi;28file artificiali189810B,zero optimizer/HDF generati. Core: lower bound
445read/443feature-score aritmetici/441reference rows; lavoro torn non imputato.
Intervallo esterno soggetto17.046331209s+4s riserva observer=21.046331209s entro160s,
include import/report/finalizer/exit/reap. Exit0, nessuna forzatura observer.

## Una sessione reale AE, senza PCA

Allowlist esatta14originali: raw, membership6999, golden1024×8,7lineage,transform,
AE model/config/calibration; esclusi i3PCA. Prima dell'attivazione solo lstat/tipo/
size/link; hash e decodifica effettivi dentro il nuovo pilot. Il consumer carica
una volta membership/golden/AE155parametri/threshold; il supervisor fa solo le due
custodie raw autorizzate. Nessun ProcessedStore, array supplementare, signal/held-out,
fit/training/optimizer/calibrazione/metriche scientifiche/acquisizione/device survey.

64offerte periodiche500/s,128ms, nominalB8, posizioni0…63 senza wrap/priming/
ripetizione/sostituzione. Il trasporto porta descrittori64B prima delle letture HDF,
non byte evento né un detector link. Tutte64sottomesse,0missed,2reject per contention,
0capacity,62ammesse/completate.60gruppi:58m1+2m2. A orizzonte61complete+1active;
`uncertain=1` è flag sovrapposto dell'active, non un altro evento. Dopo drain nessun
queued/active/failed/unresolved.64presentation key uniche.63posizioni raw distinte
tra gate e stream entro l'universo64, senza enumerare ID reali.

HandleA: m1…8, due catene raw complete e una reference golden indipendente per shape;
closeA, release temporanei, reopenB1MiB/521slot/w0 .75 senza warm-up raw. Dopo drain,
reference pubblica golden indipendente per tutti60gruppi, stesso m/ordine, score/
mask byte-exact. Post-gate suB,16contesti pre/post tutti passanti, feature/repeat/
stato congelato invariati. Quattro confronti stretti `score > threshold`, tie false.
Feature complete700particelle,8canaliFP32,score canonicoFP64,nessuna tolleranza allargata.

| Lavoro reale | Effettivo | Massimo |
| --- | ---: | ---: |
| Raw/feature calls e righe | 92 /206 | 96 /208 |
| Public calls /score rows /Booleane | 168 /340 /1360 | 176 /344 /1376 |
| Reference golden calls /righe | 76 /134 | 80 /136 |
| Membership load /record | 1 /6999 | 1 /6999 |
| Golden load /righe | 1 /1024 | 1 /1024 |
| AE load /threshold load | 1 /1 | 1 /1 |
| HDF opens /closes /schema | 2 /2 /4 | 2 /2 /4 |
| Custodia raw pass /byte | 2 /5816520818 | 2 /5816520818 |

Le92catene sono32gate/144righe+60stream/62righe; le76reference sono16gate/72righe+
60stream/62righe. Caricare1024golden non equivale a score1024. Started/returned
coincidono, nessun lavoro finale indovinato. Due hash globali originali completi,
2908260409B ciascuno, SHA5da8fda2… invariato; pre1.379814334s/post1.260952541s.
13piccole fonti377025B verificate due volte754050B; envelope393216B invariato.

## Tempo, risorse, journal e limite globale

Intervallo esterno reale5.729602250s, da prima di import fino a report/finalizer/exit/
reap; +2s riserva receipt=7.729602250s entro180s. Il receipt finale observer è fuori
soggetto e separatamente riservato. Caso2.874322584s, cleanup0.000809s, massimo gap
monitor8.629541ms. Nessun timeout/cap aumentato. Journal uno, aperto prima snapshot,
stesso inode,1close indipendente finale;21SemLock reali assenti, tracker valido.

ConsumerRSS364969984B,producer29851648B,inner29081600B,tracker16809984B,
joint45891584B,outer27918336B,charge conservativo491044864B<512MiB. I guard restano
consumer1024/producer64/inner+tracker80/outer48MiB,aggregato1216MiB. Bound numerico
owned derivato7444432B<8MiB; non prova heapPython8MiB/nativeworkspace512MiB.
Torch intra/inter1,determinismo,OpenMP/Accelerate1 prima/dopo; decoder richiesto1,
effettivo unknown. I picchi RSS di fase sono lifetime, non allocazioni esclusive.

Massimo latenza da offerta prevista5.269708ms su62complete, producerlag1.077750ms
su64,queuewait2.949292ms,jointservice3.582292ms;0miss100ms. Nessuna latenza imputata
ai reject o p99 di produzione. Eventappend128/max36.917µs/0oltre50µs;batch720/
max33µs/0oltre200µs. Generato1578event/5099batch,0exceed. Soglie diagnostiche,
non prova hard real time né cancellazione dei5exceed storici0052.

**Difetto globale:** ledger immutabile366entry/21563584B sotto512entry/32MiB copre
root nuova `data/task0058-validation/ae-pilot-v1`, tentativi/failure/fonti/log/sample/
receipt/temp/copie curate. Ma il formatter ha aggiornato fuori root tre file
`.ruff_cache/0.16.10/`:7260880457088328013=1884B,
3943971463714022594=16988B,4873380995755368680=5252B.
Totale corrente24124B logici/32768B blocchi allocati. Dimensioni precedenti/delta
unknown: si addebita conservativamente l'intera lunghezza corrente. Nessuna
prenotazione prima della crescita, cancellazione o waiver retroattivo. Storage
osservato sotto cap non sana il requisito; kernel/filesystem metadata non misurato.
Il difetto emerge nella curation finale, lavoro nativo già terminato. I receipt
nativi `qualified=true` restano intatti ma non certificano le scritture del formatter.
Nessun retry/riparazione/qualifica dopo P4. Verifiche finali solo statiche/no-cache.

## Interpretazione e decisione finale

Sono positivi e distinti: custodia originale, letture selettive, feature, caricamento
AE, forward pubblico, SSE e decisioni reali; non sono zero operazioni. Alcuni label
legacy dicono synthetic: la summary corregge il campo di interpretazione senza
modificare sorgente congelata/prove. Nessuna sottrazione observer, stima pipeline
senza strumenti o attribuzione causale cache/trasporto. ReopenHDF non significa OS
cache fredda: custodia/gate/golden/model/prior history possono scaldarla.

P1 finale qualificato su16aspettative; P2 attribuzione heap/workspace/thread decoder
parziale; P3 una piccola pipeline strumentata; P4 usato e consumato qui. Non si usa
`completed_bounded_development_ae_hdf_pilot` e il pilot non è accettato nel complesso
per il gap storage. Il risultato reale AE resta osservato e conservato. Default
successivo: consolidare conclusioniv1scientifiche/CPU/sintetiche e fatti separati PCA/
AE, esplicitando questo gap. Correzione futura source-free della cache tooling,
nessun motivo per ripetere inferenza reale solo per quel difetto; nuovi esperimenti
richiedono domanda distinta e autorizzazione separata. Nessun0059/24×768/840s.

0056 resta partial/consumed con PCA valido63/64,207raw/features174public342rows1368
Booleane; non diventa confronto paired né pilot retroattivamente accettato. Restano
0057software,0054failed/consumed e sua custodia,0055startup,0053v2,0052partial-negative,
0049closure,0036unresolved,0034gates,YES/YES/YES,particle192/192consumed/canonical
deferral,0024exportaccepted vs0025performancefailed,noMPS. Nessuna utilità scientifica,
efficienza rare-anomaly, nonlinearitycausale, conferma indipendente, detector readiness
o affiliazione ufficiale CERN/esperimento. Nessun Git automatico; review e staging
manuale solo dei19file0058, esclusi data/model/fixture/cache/diagnostica ignorati.
