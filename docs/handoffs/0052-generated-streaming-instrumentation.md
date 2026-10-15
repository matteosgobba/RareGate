# Task0052 — Riparazione e caratterizzazione della strumentazione streaming generata

## Metadati e decisione

Data: 2026-10-15, Europe/Rome. Fase: software/processi con input esclusivamente generati. Stato **`partial_generated_streaming_instrumentation_characterization`**; strumentazione **`sampled_limits_exceeded`**; readiness **`requires_final_source_revalidation_and_instrumentation_storage_clock_budget_decision`**. Non si usa lo stato completed: rimangono verifiche native obbligatorie sulla versione finale e lacune nel conto globale di spazio/tempo. Nessuna accettazione operativa.

Base effettiva: `main`, HEAD `2f59ae1fafd77455b001393482a5bea84ddb1fc8`, upstream locale `origin/main`, ahead/behind 0/0, 700 file tracciati, albero/indice inizialmente puliti. Task0051 è committato; Task0050 `3521c8f6…` e Task0049 `42ab4458…` restano storici. Non è stato verificato un remoto aggiornato, push o CI. Nessuna modifica preesistente da attribuire a Task0052. Memoria1.46→1.47 aggiornata in loco; le basi storiche restano inalterate. Nessuno staging/commit/push eseguito.

**Decisione:** mantenere la revisione limitata del recorder come codice da rivedere, conservare l'esito negativo del criterio50µs e fermare l'espansione delle prove. Cinque append evento eleggibili del candidato superano50.000ns, massimo103.041ns. I2.935 append batch eleggibili non superano200.000ns, massimo50.541ns. Le soglie non sono state alzate. Il confronto isolato favorevole non basta a certificare il costo della strumentazione nel percorso streaming.

## Obiettivo, istruzioni e confine

Il prompt effettivo è salvato integralmente in [0052](../prompts/0052-generated-streaming-instrumentation.md), copiato dall'allegato utente. L'handoff iniziale è stato creato prima del lavoro sostanziale. Letti protocollo di sviluppo, README, memoria e indice, protocollo/spec0050, report/config/summary/handoff0051, moduli streaming e test focalizzati; nessun AGENTS applicabile trovato nei percorsi pertinenti.

I tre anchor0051 corrispondono a15.687/8.211/80.200byte e agli SHA256 forniti. Il [riepilogo](../../results/tables/final/task0052-streaming-instrumentation-summary.json) lega dieci input storici a percorso/dimensione/hash e ne verifica i byte finali. Non sono stati riaperti gli artefatti ignorati0051. Il baseline usa soltanto `protocol.py` e `records.py` del commit fissato,21.228byte, package isolato con SHA verificati: nessuna copia completa del repository o import ambiguo del codice corrente.

P4 rimane **non concesso**. Zero nuovo lavoro operativo su raw/HDF/hash raw, membership/golden/feature/score/fingerprint reali, artefatti/import di modelli, inferenza pubblica/congelata, ricostruzione, training/ottimizzazione/calibrazione/scienza/acquisizione. Nessun HDF, nemmeno generato; niente timing vector/replay/controller storico, survey di dispositivi/processi estranei, installazione, privilegio o prenotazione. Il lavoro numerico generato, i record e le osservazioni temporali/processuali sono invece positivi. Nessun Task0053 o campagna fisica24casi è stato lanciato.

## Modifica e significato delle misure

Versione `0052.1`: `Store.write` valida/codifica in uno scratch512B riusabile, azzera ogni byte, calcola CRC attraverso una memoryview e pubblica tutti512B nel file mappato condiviso. Il baseline allocava bytearray/sliceCRC/bytes e usava pwrite. Rimangono identici formato/versione, validità null/zero, campi riservati, CRC/canonicalità, intenti/ritorni/output e capacità. La validazione precede la pubblicazione; un errore di codifica non modifica il record precedente. Un record lacerato è invalido: non si recupera una vecchia versione per inventare un completamento.

Descriptor64B, ring12.288B,64crediti inclusivi, FIFO/B8/timeout1ms, sorgente simbolica e quattro confronti stretti di forma effettiva sono conservati. Solo input/stub generati, nessun codec/provider operativo. Mapping e pwrite senza fsync/flush esplicito danno evidenza di visibilità rispetto al crash di processo, non durabilità a perdita di alimentazione.

Il timer append resta quello0051: prima di Store.write fino al ritorno, comprendendo validazione, encoding, allocazioni interne, CRC e pubblicazione. Statistiche e campioni osservatori seguono; non vengono sottratti. Il timer osservatore include il primo campione scritto, mentre il secondo non può misurare ricorsivamente la propria scrittura. Il suo costo resta nel ciclo e nella vita del processo. I cicli completi offerta e batch comprendono tutta la strumentazione, ma anche controllo trasporto e lavoro generato: sono involucri diagnostici inclusivi, non una misura isolata di overhead. Ogni batch ha m e numero di aggiornamenti realizzati. Inizializzazione/page touch, fasi, output, finalizzazione e cleanup sono osservati separatamente; code path e confini esatti sono nella [spec](../../configs/streaming/development_streaming_instrumentation_v1.json).

Ogni finestra salva prospetticamente ordine/casi/configurazione/hash prima dei figli. La consegna preserva tutte e quattro le versioni, anche i preventivi inesatti, e aggiunge una correzione statica esplicita. Nessun confine viene ristretto dopo aver visto un costo lento.

## Confronti e tutti i tentativi

Tre coppie complete AB/BA/AB; A0051 fissato, B candidato. Ogni lato:256append evento+256batch su128record, due aggiornamenti per record, m1. File nuovi azzerati; entrambi i lati leggono prima65.536B/file; B aggiunge map/touch4KiB/scratch durante l'inizializzazione. Nessun warm-up append, purge o cache fredda dichiarata. Le differenze comprendono queste storie e l'ordine sullo stesso host, non identificano causalmente il solo pwrite.

Nelle tre coppie valide, A:768campioni/kind, massimi16.042/20.917ns e zero superamenti; B non supera le soglie nel confronto isolato. Le mediane B sono inferiori alle A nei dodici gruppi confrontabili, senza aggregare quantili. Il successivo percorso streaming ha comunque i cinque superamenti evento: due intenti in capacity (max59.833ns), un intento57.208ns, una risoluzione60.750ns e un miss103.041ns nella contesa. I quantili CSV usano interpolazione lineare `(n−1)p`, separati per caso/versione/lato/ripetizione/operazione/stadio/m/aggiornamenti. Conteggi, somme/media/mediana/p95/p99/max/superamenti sono conservati anche per tentativi non eleggibili.

| Tentativi globali | Versione e risultato |
| --- | --- |
|1|A iniziale completa256+256append; wrapper di cleanup riceve un intero invece della funzione clock. Campioni recuperati dal summary del worker; lifecycle finale sconosciuto, confronto incompleto. Due superamenti evento A, max483.666ns, conservati separatamente.|
|2–7|v2, tre coppie complete AB/BA/AB, controlli byte/accounting passano.|
|8|v2, normal500 invalido:512slot per campioni produttore insufficienti per`5N+7`. Conservati98completamenti,4rifiuti contesa e lavoro irrisolto/futuro; nessuna sostituzione silenziosa.|
|9–14|v3, buffer produttore768slot; normal500/2500/5000, capacity, contention e morte prima del ritorno passano.|
|15|v3, post-return non raggiunto: snapshot iniziale produttore perde la gara col polling supervisore; tentativo invalido conservato.|
|16–20|v4 finale, attesa snapshot limitata50ms prima delle offerte; cinque casi passano: post-return, post-output+proprietario mutex morto, secondo avvio fallito, pubblicazione lacerata, pubblicazione fallita+overflow+errori diagnostici cleanup.|

Tre difetti di correttezza hanno controlli deterministici specifici. Sono stati corretti entro il margine totale; nessuna ricerca di prestazioni o nuova quota.20invocazioni consumate,17controlli attesi passano,3fallimenti non cancellati. Le quattro coppie consentite sono consumate: una parziale+tre complete;1.792append evento e1.792batch nei recorder (≤2.048/kind). Nessun'altra prova nativa segue.

## Copertura finale, workload ed accounting

I cinque casi v4 hanno8offerte ciascuno a500/s, orizzonte16ms. Post-return conserva ritorno senza feature; post-output conserva C=1 e poi termina tenendo il vero mutex, da cui cleanup indipendente. Il caso lacerato copia256byte e invalidaCRC prima dell'exit75: accounting/stadi/tempi restano null/invalidi. Pubblicazione fallita genera OSError prima della copia; il preflight native imposta temporaneamente failed=MAX e verifica che overflow non liberi crediti, ripristina e termina failed. Dopo reaping si corrompe pending sotto vero mutex: Ring._invariant fallisce nello snapshot di cleanup. Journal già chiuso, snapshot e errore diagnostico dopo close non impediscono unlink/reaping. Non sono processi normali né esperimenti fisici validi.

Copertura finale completa della matrice **assente**: normal500/2500/5000, capacity, contention e pre-return legano v3. Startup riparato è osservato nei guasti v4; la matrice normale non è stata rieseguita sul bundle finale. Il recorder/encoder è byte-identico al percorso delle coppie, ma questo non trasforma il vecchio bundle in un test completo del nuovo. Lo stato resta parziale.

Workload totale696offerte artificiali configurate:128 nel fallimento8 +528 nella finestra v3 +40finali; recorder zero offerte. Ogni invocazione≤128. In v3, con128offerte:500/s→126C/2contese;2500/s→126C/2contese;5000/s→121C/6contese/1miss. Capacity96→64C/30overflow/2contese, con46deadline illustrative100ms mancate; contesa32→31rifiuti/1miss/0C. Il risultato sfavorevole rimane osservazione, non motivo per ritentare. Rate e latenza stub non sono costi HDF/modelli o rate LHC.

Da12report con record validi (su13tentativi streaming), limiti inferiori:298intenti read/538righe restituite,295feature+score/536righe,294reference/535righe,536C/2.144Booleani primari. Stadi del run lacerato sconosciuti, non0. Il ledger recorder896presentazioni simboliche resta separato dai servizi streaming; test numerici generati sono ulteriori. Identità per cutoff O=U+M+S; S=J+Rcap+Rcont+A; A=Qring+Qstaged+active+C+F+K. Le quattro maschere non sono quattro eventi; i falsi completano servizio. Code/attivi/irrisolti e tempi mancanti restano espliciti.

## Risorse, clock, limiti

Binary peak streaming a128: ring12.288 +event/batch131.072 +fasi49.152 +output1.536 +campioni49.152/262.144 =505.344B. Ogni Store ha512B scratch e map≤65.536B; il supervisore mappa entrambi in riconciliazione. File/mapping alias non raddoppiano i payload. Recorder/lato:131.072+66.048=197.120B; testo baseline21.228B+pycache, pre-read65.536B, temporanei encoding≤1.536B. Output12B/row, buffer numerici generati stimati34.080B, framing/copie e parsing/JSON/list cardinality nella spec. Heap Python e workspace nativo non sono provati entro le quote0050.

Diagnostici ignorati effettivi8.218.819B al momento dell'aggregazione, entro16MiB; inventario finale nel summary. La revisione statica ha rilevato che il preventivo15.218.688B ometteva report duplicati e più riepiloghi di finestra: già aggiungere20copie×131.072B dà17.840.128B. I guard di spazio sono per finestra, non cumulativi fra versioni. Questo è un prerequisito P2 concreto, non una prova di budget generale o un superamento effettivamente osservato.

Gli elapsed salvati sommano3.727670291s **prima** delle scritture aggregate finali e fuori dagli import CLI; non costituiscono la durata cumulativa completa richiesta120s. I guard post-write operano per finestra, ma manca la registrazione inclusiva fra finestre: ulteriore P3. Maggiore intervallo invocazione catturato462.491416ms; cleanup max32.378ms; gap monitor21.774541ms. Non si inventa il costo dei tail o del cleanup iniziale fallito. RSS streaming campionato: produttore25.231.360B, consumer34.062.336B, supervisore28.655.616B; massimo somma stesso run87.801.856B. Limiti esterni64/1024/128MiB, totale1216MiB, workspace nativo512MiB restano quote, non prova di fattibilità reale.

Audit oggetti effettivi:1mutex+4Events=21SemLocks; scopi start produttore/start consumer/stop/barriera guasto, creati dal supervisore, condivisi spawn, lifetime del fixture, finalizer/tracker per nomi. Recorder1Event=5SemLocks. Non è stata rimossa una primitiva necessaria né introdotta Queue/Pipe/atomica non provata. Backing65.536B **non dimostrato**: occorre attribuzione OS/runtime o decisione esplicita sulla definizione della quota; sizeof/count/RSS non bastano.

Clock servizio: mach_absolute_time via perf_counter_ns, risoluzione dichiarata41,6667ns, monotono/non regolabile. Supervisione mach_continuous_time/timebase; risoluzione continua non misurata. Bracket di fase/ruolo supportano soltanto confronto limitato dello stesso host, senza uguaglianza/offset calibrati o validità operativa del scheduler. Nessuna sottrazione overhead, percentile di produzione o inferenza di indipendenza dai riusi finiti.

## Verifiche e prossima decisione separata

96test focalizzati passano (82fondazione+14nuovi casi), lint/format passano; layout/CRC indipendenti, pinned encoder bidirezionale, null/reserved, accounting/overflow/uncertainty, cleanup, capacità osservatore e gara avvio. Solo i due file pertinenti raccolti, nessuna suite storica completa/matrice modello/native. I sette run focalizzati (91/91/91/92/94/95/96test) includono56subprocess Python di audit import/help/errori, otto/run: nessun fixture IPC, mapping o backend numerico avviato da questi audit. Sono contabilizzati separatamente dalle20istanze di fixture generate, non presentati come processi inesistenti. JSON/CSV, aritmetica, hash storici, link locali, diff e indice sono ricontrollati staticamente; dettagli nel summary. Nessuna modifica comportamentale dopo v4: solo documentazione/config correzione statica dichiarata.

P1 conserva controlli deterministici e native parziale; P2 ha backingSemLock/Python/native/modelli/decoder/cache/thread e inventario globale aperti; P3 ha limiti di logging, clock e finalizzazione inclusiva; P4non concesso. Il prossimo passo è **una revisione separata dell'architettura/budget della strumentazione, con contabilità globale corretta e un nuovo piano generato limitato per le verifiche finali mancanti**, prima di considerare integrazione HDF/modelli. Nessuna soglia/architettura futura è adottata ora, nessun Task0053 avviato.

CPU/sintetico0049 rimane chiuso; Task0036 `unresolved_no_acquisition`, gate0034, YES/YES/YES permanente, particle192/192consumato/deferral canonico, tutti gli esiti storici, export0024accettato/performance0025fallita e nessun claim MPS corrente sono invariati. Nessuna conclusione su strict-tail, efficienza fisica, causalità della non linearità o prontezza detector. Ricerca indipendente, senza affiliazione ufficiale CERN/esperimento implicita.

## File e Git manuale

Modifiche vive: init/records/fixture/supervision/transport, nuovi instrumentation/characterization, entrypoint e test; spec/report/CSV/summary/prompt/handoff e tre documenti condivisi. Artefatti ignorati sotto `data/task0052-validation/` esclusi. Gli input storici0050/0051 restano invariati; nessuna modifica Task0049 preesistente da includere, essendo già committata. I link e le identità sono nel report/summary. Il commit risultante non esiste ancora.

Da eseguire soltanto manualmente, dopo revisione:

```sh
git status --short --branch
git diff --check
git diff -- README.md docs/project-memory.md docs/handoffs/README.md src/latenttrigger/streaming
git ls-files --others --exclude-standard
git add -- README.md docs/project-memory.md docs/handoffs/README.md \
  src/latenttrigger/streaming/__init__.py src/latenttrigger/streaming/records.py \
  src/latenttrigger/streaming/fixture.py src/latenttrigger/streaming/supervision.py \
  src/latenttrigger/streaming/transport.py src/latenttrigger/streaming/instrumentation.py \
  src/latenttrigger/streaming/characterization.py scripts/characterize_development_streaming.py \
  tests/test_development_streaming_instrumentation.py \
  configs/streaming/development_streaming_instrumentation_v1.json \
  docs/development-streaming-instrumentation.md \
  docs/prompts/0052-generated-streaming-instrumentation.md \
  docs/handoffs/0052-generated-streaming-instrumentation.md \
  results/tables/final/task0052-streaming-instrumentation-cases.csv \
  results/tables/final/task0052-streaming-instrumentation-summary.json
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "fix(streaming): characterize generated recorder limits"
git push origin main
```
