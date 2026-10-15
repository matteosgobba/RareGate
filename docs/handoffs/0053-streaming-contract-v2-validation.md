# Task0053 — Contratto streaming strumentato v2 e validazione finale

## Metadati e decisione

Data2026-10-15, Europe/Rome. Stato **`completed_generated_streaming_contract_v2_validation`**; qualifica **`generated_software_qualified_under_v2`**. Readiness operativa **false**, P4 **non concesso**. Tutte le12aspettative software passano su un solo bundle finale; nessuna seconda suite, confronto AB/BA o ottimizzazione del recorder. Task0052 resta **partial_generated_streaming_instrumentation_characterization / sampled_limits_exceeded**, con i suoi cinque superamenti evento permanenti.

Base effettiva: main, HEAD `1155e83f8ab99adfbd7bc0044d4128f9e188e278`, upstream locale origin/main, ahead/behind0/0, albero/indice inizialmente puliti,710file tracciati. Task0052 committato; nessuna modifica preesistente da attribuire a0053. Memoria1.47→1.48 aggiornata in loco. Nessuna prova di remoto aggiornato/push/CI; nessuno staging, commit o push eseguito.

La decisione metodologica è esplicita, autorizzata dal prompt e prospettica: si studia **la pipeline di richieste strumentata**, includendo osservazione/controlli e loro stalli. Non si stima una pipeline invisibile senza strumentazione. La revisione è esplorativa e informata dai risultati0052, non conferma indipendente dei vecchi requisiti.

| Prima | Ora, solo qualifica generata v2 |
| --- | --- |
|50µs append evento /200µs batch come gate di validità proposti|Stessi valori come riferimenti diagnostici; ogni superamento/costo rimane. Nessun nuovo limite adattato a103.041µs. Accounting, risorse e lifecycle restano obbligatori.|
|65.536B all-in synchronization backing non provati|Contratto esplicito primitive/lifetime:≤21coreSemLocks,≤26albero attivo; osservatore effettivo0. Backing OS/kernel resta sconosciuto, il vecchio vincolo non è dichiarato soddisfatto.|
|8MiB heap Python /512MiB workspace nativo non attribuiti|Qualifica generata su buffer binari esatti, cardinalità finite e guard RSS; i target di integrazione restano non validati, senza waiver o attribuzione fittizia.|
|Guard spazio per finestra /timestamp prima del report finale|Ledger unico pre-growth per tutti i tentativi e osservatore esterno prima del lancio/import fino a report chiusi/finalizer/uscita/reaping. Ricevuta osservatore separata e riservata.|

## Scope, istruzioni ed evidenza

Prompt effettivo salvato integralmente in [0053](../prompts/0053-streaming-contract-v2-validation.md) e handoff iniziale creato prima del lavoro sostanziale. Letti sviluppo, README, memoria/indice, protocollo/spec0050, report0051, report/config/CSV/summary/handoff0052 e codice/test/entrypoint streaming pertinenti. Nessun AGENTS applicabile nei percorsi interessati. Anchor0052 verificati:20.058/19.836/257.627B, SHA256 esatti del prompt. Nove input storici legati a percorso/dimensione/hash, byte invariati; nessun payload ignorato0051/0052 riaperto. Codice precedente conservato dai commit, non riclassificato come verifica del codice modificato.

Zero accesso operativo a raw/HDF/metadata/hash raw, membership/golden/feature/score/fingerprint reali, artefatti/import di modelli, inferenza pubblica/congelata, ricostruzione, training/optimizer/calibrazione/scienza/acquisizione. Nessun HDF nemmeno generato, timing vector storico, replay, vecchio controller, survey dispositivi/processi estranei, installazione o prenotazione. Il lavoro generato numerico/record/timing/processi è positivo, distinto da questi zeri operativi. Nessuna campagna fisica24casi o Task0054.

## Implementazione e contratto congelato

Versione0053.1. Il recorder0052 con scratch512B/mmap/CRC rimane; la modifica necessaria riguarda creazione/truncate/scritture/close sotto quota, non una nuova ottimizzazione. Restano64Bdescriptor,12.288Bring,64crediti inclusivi, FIFO/B8/oldest1ms, open-loop lag2ms/catch-up4/horizon, record512B/CRC/null/ownership, actual-m e quattro confronti stretti con tiesfalse. Nessuna transizione è eliminata per ridurre i costi. Mapping/pwrite danno osservabilità rispetto al crash di processo, non durabilità a perdita di alimentazione.

Il [contratto risolto](../../configs/protocols/development_streaming_v2.json) lega v1 e dettaglia requisiti cambiati, invarianti, conti/timer e limiti. Mantiene semantiche scientifiche/frozen future,384raw versus1024golden e proposta24×768/840s non eseguita/non concessa. Il backend attuale è soltanto memoria generata1024×3, feature sintetiche e score aritmetico; consumer HDF/modelli reali non implementato. Sourceorder position(k),k0…N−1,N≤128, reset a ogni caso, quindi0…127; riusi non indipendenti. Nessuna cache OS fredda, prefetch, sottrazione overhead o attribuzione causale a trasporto/cache.

I timer append mantengono l'intero Store.write inclusivo di validazione/codifica/CRC/pubblicazione. Statistiche/campioni osservatori seguono; il secondo campione non misura ricorsivamente se stesso ma resta nei cicli/lifetime. Ciclo offerta include costruzione record, intent/resolution e controllo ammissione; ciclo batch include tutti gli aggiornamenti e lavoro generato/output/reference/control. Non sono overhead isolati. Setup/page touch, fasi, quota, GC/probe dei propri nomi, parsing, preflight JSON, serializzazione/close e cleanup rimangono nei conti. Quantili lineari(n−1)p separati per caso/ruolo/operazione/stadio/m/aggiornamenti, con n/somma/media/mediana/p95/p99/max/superamenti. Tail interrotti sconosciuti, non0; campioni e maschere restano nei file binari ignorati.

## Ledger globale e osservatore

Un solo root nuovo `data/task0053-validation/task0053/`. Prima del subject viene salvato un ledger immutabile di **294entry /15.136.928B** per entrambe le possibili suite, sotto **16.777.216B**. Quote inutilizzate restano addebitate: niente cancellazione di evidenza per recuperare budget. Un solo risultato autorevole/caso, niente duplicati producer/consumer/supervisor JSON. Snapshot sorgente/config per suite, manifest, campioni, output, fasi, heartbeat, risultati, emergenze, CSV/JSON e copie curate simultanee sono tutti riservati.

Controlli prima della crescita: pathname dichiarato/canonico, niente symlink/hardlink in scrittura o overwrite di evidenza; dimensione JSON esatta e cardinalità prima di creare il file, chunk limitati, preflight per truncate/pwrite/rename. File corti/falliti restano come evidenza con quota intatta. Coppie temp/final contano entrambe; unlink di ring/guard è retirement di risorse, senza liberare la prenotazione. Cleanup di setup parziale indipendente da journaling/mutex. Dimensioni logiche e blocchi allocati osservati separati; metadata FS/kernel non attribuiti.

Binary per streamingN128:505.344B = ring12.288 +event/batch131.072 +phase49.152 +output1536 +campioni49.152/262.144. Mapping/file alias non raddoppiano il payload; map≤3/143.360B per processo, scratch512B/Store, zero template512B/processo, registryFD diagnostici≤16. Payload numerico generato34.080B; event/batchobjects≤128, sampletuples≤4096/ruolo, righe12/suite24/task, JSON≤24.000nodi/profondità24/dict512/list4096/string65.536char/scalarchunk262.144B. Heap Python e workspace libreria non ricavati da questi conteggi.

Outer48MiB e inner80MiB dividono i128MiB del supervisore; producer64MiB, consumer1024MiB, somma1216MiB. Si impone inoltre una carica residente conservativa sommaRSS≤512MiB, senza chiamarla attribuzione nativa o prova del workspace. Pagine condivise/peak sovrapposti non sono RAM unica. Mutex+4Events sono21SemLocks effettivi; scopi startproducer/startconsumer/stop/barriera guasto, proprietario inner, lifetime un caso. Outer usa0primitive esplicite. Dopo GC si controllano soltanto i propri nomi con sem_open senza create, chiudendo eventuale riferimento; devono essere assenti prima del caso successivo. Tracker e sessione propri devono ritirarsi dopo uscita/reaping; nessun conteggio converte in byte kernel.

L'outer osserva il subject **prima di Popen/import**, poi attende report/finalizzazione/uscita/reaping e assenza della sessione. Ricevuta propria fuori da quel tempo, overhead riservato5s/lancio, non timer auto-referenziale. Ogni lancio≤75s: subject70s, cleanup albero fino72s, restante ricevuta; due lanci≤150s (al massimo120s di casi+15setup+15finalizzazione/osservatore). Monitor primario250ms, heartbeat/report liveness2s, startup7.5s, operation2s/drainprogettato5s, cleanup2s, caso5s. SIGTERM al gruppo permette finally/reaping; SIGKILL è fallback e comporta invalidità/uncertezza, non reaping inventato dei discendenti. Stdio subject prospetticamente DEVNULL, nessuna coda/pipe di eventi o buffer di stampa illimitato; record/exit code/errori limitati sono l'evidenza.

## Prove e risultati nativi effettivi

**120test focalizzati** passano (96precedenti+24nuovi casi), lint/format passano. Layout/CRC/null attesi indipendenti, compatibilità0051/0052, conti globali fra tentativi e controesempio duplicati0052, temp/final simultanei, short/failedwrite, symlink/pathescape, setupfallito/cleanupquota, clock finti per stall di report/finalizer/receipt/start e retirement del gruppo. Un difetto di serializzazione nella ricevuta fake e un import del test sono corretti prima della prima prova nativa; nessun fallimento nativo inatteso. I test non avviano casi di qualifica nativa; audit CLI import/help/errori sono subprocess separati senza IPC/backend generato. Nessuna suite storica completa/matrice modelli.

Bundle unico finale:
`1e015d6d6575e1004c337a1d6d84fec416bbf63ed91e25377e3bf876aed3e03e`.
Manifest completo salvato prima delle prove; sorgenti/config/test/prompt identici dopo e alla consegna. Nessuna modifica comportamentale dopo questa suite.

| Caso | Configurate/C | Esito osservato |
| --- | ---: | --- |
|normal500|128/116|11miss producer+1contesa; slotreuse richiesto osservato|
|normal2500|128/123|2miss+3contese|
|normal5000|128/119|3miss+6contese|
|capacity|96/64|31overflow+1contesa,50deadline100ms illustrative mancate|
|contention|32/0|32contese, drain normale|
|pre-return|8/0|intento read incerto, pending/irrisolti conservati|
|post-return|8/0|1riga ritornata senza feature|
|post-output/mutex morto|8/1|C resta dopo exit74 tenendo il vero mutex|
|secondo start fallito|8/0|0submission, nessun H fittizio; cleanup del producer/oggetto non avviato|
|pubblicazione lacerata|8/unknown|CRC invalido, accounting/stadi null; niente recupero di vecchia versione|
|pubblicazione/cleanup falliti|8/0|OSError/overflow preflight/phase chiuso/counter-snapshot/close gestiti; crediti non liberati anticipatamente|
|observer report/quota|0/0|17B in target16B rifiutati prima della creazione, emergenza limitata e guard chiuso/unlink; ricevuta esterna completa|

12/12aspettative passano:5run drenati validi,7casi deliberatamente invalidi correttamente osservati. Questi ultimi non diventano run normali.560offerte configurate (limite3072), massimo128/caso;12invocazioni (limite24), una suite, seconda non eseguita. Non si rinnova o consuma la quota esaurita0052.

Diagnostica **1.041append evento,10superamenti50µs, massimo963.000ns**; **1.970append batch,4superamenti200µs, massimo2.074.625ns**. Normal500 contribuisce9evento/4batch; post-return1evento in contesto fault. Nessuna sostituzione o soglia adattata. Sono osservazioni della pipeline strumentata v2, senza causa isolata né bound universale. Cicli completi529offerte(max4.352.792ns)/177batch(max12.353.584ns); fasi max3.592.708ns, init53.865.583ns, final324.959ns, output294.166ns. Distribuzioni omogenee e n restano nei risultati.

Conservazione a H/stop O=U+M+S;S=J+Rcap+Rcont+A;A=Qring+Qstaged+X+C+F+K;maschere=4C. Nei cinque casi normali:512configurate=16miss+31overflow+43contese+422C. Nei dieci report streaming riconciliabili, limiti inferiori181readintents/425righe ritornate,178feature/scorecalls/423righe,177reference/422righe,423C/1692Booleani e1688confronti reference. Il run lacerato ha lavoro sconosciuto, non0. Dieci backend generati; ulteriore attività dei test separata. Nessun ID reale o payload operativo nei CSV/summary.

## Tempo/spazio osservati e limiti di claim

Osservazione esterna del subject **3.426913083s**, inclusi import, lavoro, report chiusi, finalizer, uscita/reaping e retirement della propria sessione. Somma intervalli caso3.301730208s, non sostituita al totale esterno. Con5s di overhead observer riservato:8.426913083s addebitati al budget150s; check totale post-ricevuta75s passato. Caso massimo546.627583ms, cleanup32.246750ms, gap inner30.996417ms e outer16.543875ms. Exit0/reaped/gruppo assente, nessuna azione forzata dell'outer.

Il subject produce i propri JSON di caso, CSV e summary di qualifica prima dell'exit. La successiva curation statica di documenti/exports è esterna al programma misurato e riservata separatamente: non viene spacciata per un tail misurato. La ricevuta propria dell'outer è fuori dal tempo subject e addebitata esplicitamente.

Root immediatamente dopo ricevuta:4.645.602B logici; snapshot pre-ricevuta4641467B/4653056B di blocchi nel record immutabile. Conteggio finale root/copie curate nel summary, sotto la stessa riserva15136928B/cap16MiB, con entrambi i piani ancora prenotati. Le copie curate simultanee sono addebitate; dimensioni effettive piccole integrano, non sostituiscono, il ledger pre-growth.

RSS peak catturati producer25.247.744B, consumer33.865.728B, inner27.836.416B, outer23.298.048B; massima somma stesso caso109.903.872B.231nomi propri controllati e assenti,21primitive attive/0outer/cap26. Byte backing65536B restano non provati;8MiBPython e512MiBworkspace reale non certificati. Clock servizio mach_absolute_time/perf_counter_ns e continuo Mach/timebase, bracket propri; unità ns non significano risoluzione1ns, né confronto limitato fra processi prova uguaglianza calibrata o scheduler operativo.

P1 finale generato è qualificato. V2 qualifica il nuovo claim di lifetime/conteggio e buffer/cardinalità/RSS, ma P2cache/decoder/modelli/workspace/thread effettivi e P3operativi restano aperti. P4non concesso. Il prossimo passo è **una decisione separata di integrazione consumer selected-HDF/PCA/AE congelati e verifica risorse/cache/workspace/thread**, con autorizzazione esplicita, mantenendo384raw/1024golden e identità scientifiche. Nessun nuovo benchmark recorder raccomandato di default; nessuna integrazione o Task0054 ora.

CPU/sintetico0049chiuso, Task0036unresolved_no_acquisition, gate0034, YES/YES/YES, particle192/192consumato/deferral canonico, tutti gli esiti storici, export0024accettato/performance0025fallita e nessun claim MPS corrente invariati. Nessuna utilità strict-tail, efficienza fisica, causalità non-lineare, prontezza detector o affiliazione ufficiale CERN/esperimento implicita.

## File, verifica statica e Git manuale

Nuovi quota/validation_v2/entrypoint/test, aggiornamenti mirati a init/fixture/record/sample/transport/supervision, due config v2, contratto/report, prompt/handoff, CSV/summary e tre documenti condivisi. JSON/CSV, manifest sorgenti, aritmetica quota/casi/conservazione, link locali, hash storici, branch/indice/diff controllati staticamente. Dettagli nel summary. Diagnostici ignorati sotto il solo root0053 esclusi dallo staging; nessun altro task lanciato. Nessun commit risultante inventato.

Comandi soltanto manuali dopo revisione:

```sh
git status --short --branch
git diff --check
git diff -- README.md docs/project-memory.md docs/handoffs/README.md src/latenttrigger/streaming
git ls-files --others --exclude-standard
git add -- README.md docs/project-memory.md docs/handoffs/README.md \
  src/latenttrigger/streaming/__init__.py src/latenttrigger/streaming/fixture.py \
  src/latenttrigger/streaming/records.py src/latenttrigger/streaming/instrumentation.py \
  src/latenttrigger/streaming/supervision.py src/latenttrigger/streaming/transport.py \
  src/latenttrigger/streaming/quota.py src/latenttrigger/streaming/validation_v2.py \
  scripts/validate_development_streaming_v2.py tests/test_development_streaming_contract_v2.py \
  configs/protocols/development_streaming_v2.json \
  configs/streaming/development_streaming_validation_v2.json \
  docs/development-streaming-contract-v2.md \
  docs/prompts/0053-streaming-contract-v2-validation.md \
  docs/handoffs/0053-streaming-contract-v2-validation.md \
  results/tables/final/task0053-streaming-contract-validation-cases.csv \
  results/tables/final/task0053-streaming-contract-validation-summary.json
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "feat(streaming): qualify instrumented request contract v2"
git push origin main
```
