# Task0057 — Ownership del journal e lifecycle sequenziale

## Metadata e risultato

Data2026-10-15, Europe/Rome. Stato:
`completed_software_only_streaming_session_lifecycle_repair`; readiness
`requires_fresh_bounded_operational_authorization`; operational readiness e P4
false. Base effettiva pulita: main/origin/main,
`5e64b42a34fb7f2e09d9d657f1070e1025744c8f`, indice vuoto, Task0056 committato,
memoria1.51→1.52. Nessuna modifica preesistente, prova remota/push/CI o Git automatico.
Le basi storiche0055/0056 non vengono riscritte. Il
[prompt effettivo](../prompts/0057-streaming-session-lifecycle-repair.md) è stato
copiato integralmente e questo handoff inizializzato prima dell'implementazione.

## Difetto riprodotto e correzione

La regressione usa un file generato realmente posseduto: snapshot dei fd del caso,
oggetto Journal, prima scrittura differita, `emergency_release`, seconda
pubblicazione tramite lo stesso oggetto. Riproduce esattamente
`QuotaError: Unregistered diagnostic descriptor`; la prova precedente alla
correzione, con hash sorgente e registrazioni osservate, è conservata. Spostare
solo l'oggetto fuori dal loop non sarebbe bastato: il fd nasceva dopo lo snapshot.

Il nuovo `pilot54.candidate_session` è **lo stesso loop chiamato dal controller
operativo e dalle sessioni generate**. Apre/registra un solo journal prima di
qualsiasi snapshot del caso; verifica la stessa identità dopo ogni cleanup e lo
chiude nel finalizer di sessione. Nessun journal sostitutivo per AE, copia del
controller, esenzione dei leak del caso o modifica del runtime CPU/thread/tracker.
La registrazione originale e device/inode vengono verificati prima di scrivere o
chiudere: un fd numericamente riutilizzato non può colpire un altro file. Close
sicuro/idempotente, setup parziale e scritture corte/fallite restano controllati.
Un reader riceve ora `None` per header corto/lunghezza zero/CRC o JSON invalido,
invece di tentare il parsing di una pubblicazione incompleta.

Il journal di sessione e heartbeat/tracker del subject hanno durata superiore ai
casi. Ring, mapping, record, output, campioni, semafori e child appartengono al caso;
la cleanup reale li ritira indipendentemente da diagnostica/mutex. Il finalizer del
journal non aspetta acknowledgement. I contesti0057 sono immutabili, distinti da
P4, limitati alla nuova radice generata e privi di fallback verso originali.

## Qualifica sul sorgente finale

Bundle finale40pin:
`142d9e0130a5310921c59c0d3ed57f762ed08ebaea5143fa9540d9f0b3cbdfe7`.
**Un gruppo, tutte12aspettative core e tutte3sessioni passate**, nessuna modifica
sorgente durante/dopo, secondo gruppo non utilizzato. Runtime CPU e politica
joint80MiB sono byte-identici alla base, quindi nessun bootstrap aggiuntivo.
Le classi effettive PCA/AE creano artifact artificiali e li caricano con
from_artifact/score; dataset stand-in rigoroso, full700feature, gate m1…8 e
reference differiti nella shape/ordine realizzati, nessun file HDF.

| Sessione generata | Risultato workload | Journal e aspettativa software |
| --- | --- | --- |
| Normale PCA→AE |61/64completati ciascuno;3rifiuti contention ciascuno; tutti gate e61reference ciascuno | Stesso fd5/inode66030287 prima/dopo entrambi i cleanup;1open/1close; pass |
| Fault PCA primo read stream |2submitted/admitted,1failed e1queued,0completed;25unresolved/37future; AE64non tentate | Fault esatto prima del ritorno raw, stop AE, cleanup/reap e1close; pass, sessione invalida |
| Fault AE pre-worker | PCA60/64con4rifiuti/59gruppi referenziati; AE0worker/payload/t0 | Osservazione tracker valida10272768B/joint42336256B conservata con failure di pubblicazione;1close; pass, sessione invalida |

Normale: generazioni journal0→707dopo PCA→708prima AE→1103dopo AE→1104finale.
Fault: generazioni finali312/390; sempre una sola apertura e chiusura per sessione.
Tutti i set fd iniziali vengono ripristinati;336verifiche nomi SemLock assenti,
nessun leak child osservato. Nel fault PCA il consumer è terminato forzatamente e
reaped: una richiesta raw/row è incerta e la chiamata di close finale del secondo
handle stand-in non è osservata. Non si inventano ritorno, drain o lifecycle normale.
Questi fault passano le aspettative software, non l'accettazione del workload.

12core+5candidati =17dispatch sottostanti; le3righe sessione non sono altri casi
numerici.944offerte pianificate comprendono560core+384sessioni;880offerte sono
configurate ai dispatch effettivi,64AE restano non tentate dopo il primo fault.
Il CSV ha21righe:12core,3confini di sessione,6candidati compresa AE non tentata.
Non sommare denominatori di sessione e candidato.

## Attività positiva e diagnostica

Core: lower bounds446read/444feature-score aritmetici/443reference rows e444servizi
completati; torn work rimane sconosciuto. Sessioni serializzate:294intenti raw/
687righe richieste,293ritorni/686righe,293feature calls/686righe;
**530public calls/1120score rows/4480Booleans**, inclusi237reference/434righe.
Quattro load artificiali membership/golden/modello,2creator+4loaded models,
28file serializzati/189810B. Setup deduplicato128feature calls/righe;0optimizer,
0HDF. Otto aperture stand-in,7close espliciti e1close finale non osservato.
Le4maschere non sono4eventi. Gli stessi64input artificiali riutilizzati non
costituiscono nuovi eventi indipendenti o misura scientifica.

Append evento1446campioni/**1superamento50µs**, massimo69.125µs nel PCA normale;
batch4311/**0superamenti200µs**, massimo51.791µs. Tutti conservati, con costi/cicli
inclusivi; nessuna sottrazione overhead o ottimizzazione/confronto recorder.
Task0052 mantiene i suoi5superamenti e l'esito parziale/negativo.
Latenza da intended offer massima3.030375ms PCA e2.495333ms AE nella sessione
normale, n61ciascuno;0miss illustrativi100ms fra completati. Nessuna latenza
imputata a reject/future/unresolved, nessun p99produzione o throughput fisico.

## Limiti e verifiche

Unica radice nuova ignorata `data/task0057-validation/session-lifecycle`;
ledger immutabile **511voci/30182464B entro33554432B**, prima della regressione,
test e nativo. Include entrambi i gruppi possibili, fixture deduplicate per
candidato/gruppo, snapshot, campioni, fault, report/receipt e copie curate
simultanee. Nessuna cancellazione di prove per recuperare quota o reset per finestra.
Byte logici, blocchi regolari allocati e alias mapping sono distinti nel summary;
metadata/kernel ignoti. Fd≤16, mapping≤3/143360B,21SemLock per caso attivo,
cap albero26; backing kernel non dedotto da wrapper o RSS.

Inviluppo nativo2gruppi/24core/6sessioni/36dispatch/3840offerte massimo,5s/core,
20s/sessione,280scomplessivi invariati. Un gruppo osservato **14.973123708s**
dal lancio/import subject a report/finalizer/exit/reap; **18.973123708s** includendo
4sriservati separatamente alla receipt observer. Non è un timer autoreferenziale
che include l'ultima scrittura propria. Exit0/reaped/gruppo assente, nessun forced
subject cleanup; gap esterno max8.710542ms sotto250ms. Sessioni6.516399625,
1.895271209 e2.311176333s, ciascuna entro20s. Curation statica successiva separata.

Picchi byte: outer28622848, inner32063488, tracker16826368, producer30064640,
consumer377061376; joint max48889856 e charge conservativo inclusa riserva outer
499662848 entro512MiB. Ruoli restano48+80joint+64+1024, aggregate1216MiB;
charge resident512MiB aggiuntivo. Picchi sovrapposti/non simultanei, non RAM unica.
Originali target heap8MiB/native workspace512MiB e threading decoder effettivo
rimangono non attribuiti/non provati. Buffer numerici posseduti≤8MiB, container e
registrazioni limitati; query CPU supportate e identità rimangono quelle qualificate.

148aspettative focalizzate/compatibilità distinte hanno osservazioni passate;
279esecuzioni pure,276pass/3failure conservate. Primo giro137pass/2failure
(header corto e vecchio mockfd senza inode); secondo129pass/1failure prima di
creare file perché directory vuota già esistente; verifica corretta1pass,
compatibilità record9pass. Rerun selettivi, nessuna falsa dichiarazione di rerun
completo dei test file. Lint/format passano; JSON, CSV, aritmetica/offerte,
source bundle, link locali e anchor storici verificati. I15check nativi hanno
copertura completa dello stesso sorgente finale. Nessun caso nativo parte dai test.

## Storia e prossima decisione

**Zero nuovo lavoro operativo**: custody/hash raw, HDF/metadata, array originali,
artifact congelati e frozen public inference0. È distinto dal positivo storico
Task0056:2custody/5816520818B, PCA63/64,207raw/features,174public342score rows/
1368Booleans, tutti gate+63reference.0056rimane parziale/fallito/P4consumato,
AE reale senza worker/payload;0054resta fallito/consumato con la propria distinta
custody5816520818B. Nessun retry/reset/nuova acquisizione/scienza.

Preservati0055startup,0053v2,0052negativo,0049chiusuraCPU/synthetic,0036unresolved,
0034gate,YES/YES/YES,particle192/192consumati/deferral canonico,0024export accettato
versus0025performance fallita, tutti gli esiti e nessun MPS corrente. Nessuna
utilità/efficienza fisica/causalità nonlineare/conferma indipendente/detector readiness
o affiliazione ufficiale CERN/esperimento segue da queste prove software.

Prossima decisione consigliata: una **nuova autorizzazione AE-only** stretta può
colmare la parity/resource integration reale AE mancante. Ripetere PCA è necessario
solo per una distinta domanda sperimentale/controller che richieda una nuova
sessione doppia; non per sostituire il PCA valido o fabbricare un confronto
accoppiato fra versioni. P4 rimane non concesso,24×768/840s non concesso e nessun
Task0058 viene lanciato.

Consegna: [report](../development-streaming-session-lifecycle.md),
[spec](../../configs/streaming/development_streaming_session_lifecycle_v1.json),
[CSV](../../results/tables/final/task0057-streaming-session-lifecycle-cases.csv),
[summary](../../results/tables/final/task0057-streaming-session-lifecycle-summary.json).
README/indice/memoria aggiornati in loco. Tutti gli anchor0056 coincidono;
i documenti/config/risultati/prompt/handoff storici restano byte-identici.

## Git manuale

Task0056 è già nel base5e64b42a: nessuna dipendenza uncommitted da separare.
Escludere interamente diagnostica/fixture/data/artifact/ambienti e altro lavoro;
selezionare solo i21percorsi Task0057 elencati nella consegna finale, dopo review
anche dei nuovi file. Eseguire manualmente status/diff, staging selettivo, review
staged, Conventional Commit `fix(streaming): preserve session journal across candidate cleanup`
e push `origin main`. Nessuno staging/commit/push è stato eseguito da Codex.
