# Task0054 — Consumer HDF e pilot limitato: esito parziale/fallito

Data:2026-10-15, Europe/Rome. Stato **`partial_failed_development_hdf_consumer_pilot`**;
qualifica finale **`generated_validation_incomplete`**; readiness operativa e
accettazione del pilot **false**. Il codice di integrazione esiste, ma non è stata
stabilita la parità reale né completata la qualifica generata della revisione finale.

Il [prompt effettivo](../prompts/0054-development-hdf-consumer-pilot.md), salvato
prima del lavoro sostanziale insieme all'handoff iniziale, ha concesso un solo
P4 condizionale per questa sessione. È stato usato e consumato: nessuna ripetizione
reale dopo il fallimento. La proposta24×768/840s resta non concessa. Nessuna
Task0055, installazione, survey dispositivi, controller storico o confronto recorder.

## Base, contratti e implementazione

Verificati main/origin/main, HEAD `2f7ee515396bfda00288bcf0f7285cac15f418ce`,
indice/albero inizialmente puliti, Task0053 committato, memoria1.48→1.49.
Nessuna modifica preesistente da attribuire a0054. Riferimenti locali0/0 non
provano remoto aggiornato, push o CI; nessuno staging/commit/push è eseguito.
Tre anchor0053 corrispondono esattamente a23.488/23.313/258.923B e SHA256 del
prompt. Il manifest iniziale lega12fonti storiche; alla consegna i byte restano
invariati. Le versioni precedenti del codice vivo restano nei commit/snapshot.

Letti istruzioni/sviluppo/README/memoria/indice, disegno0050, contratto/config/
summary/handoff0053, metodi0043/0047, preprocessing/arithmetic e codice rilevante
come testo. Nessun percorso operativo storico o `byte_pins` ricorsivo è stato
eseguito. Il nuovo backend non modifica i guard dei vecchi provider e non
costruisce ProcessedStore. Il gather reale controlla owned FP64[m,2101], layering
senza duplicati per selezione crescente e scatter FIFO di ogni occorrenza. Le
feature usano tutte700particelle con sort/wrap/cast/aggregati/log/scaler congelati;
nessuna vista384, preload, padding, fit o nuovo candidato.

Il manifest chiuso contiene17file originali: raw, membership, golden, sette
metadati lineage, transform e tre JSON per candidato. Hash scientifici/file attesi
copiati dal metodo0047; prima dell'attivazione solo lstat delle dimensioni, non
letture/hash dei payload. Solo il consumer può caricare membership/golden/un
modello e aprire HDF; il supervisore esegue le due custody. Entry/help/errori e API
generate restano isolati. Dopo l'attivazione è stato verificato soltanto il raw;
gli altri16file non hanno raggiunto la verifica dei byte.

Il [report inglese](../development-hdf-consumer-pilot.md), la
[configurazione](../../configs/streaming/development_hdf_consumer_pilot_v1.json),
il [CSV](../../results/tables/final/task0054-development-hdf-consumer-pilot-cases.csv)
e il [summary](../../results/tables/final/task0054-development-hdf-consumer-pilot-summary.json)
sono autosufficienti su denominatori, sorgenti, limiti e incertezze.

## Sessione proposta e attività reale effettiva

PCA→AE, gruppi freschi sequenziali; ciascuno B8/64offerte periodiche500/s,
orizzonte128ms, posizioni del prefisso0…63 senza wrap/priming/replacement. Golden
approvato1024righe resta distinto dal massimo raw storico384 e dalle64di questo
pilot. Gate pre/post m1…8, posizioni0…m−1: due catene raw e un riferimento golden
indipendente per forma. A chiuso, B riaperto con1MiB/521/.75, niente warm-up raw
su B; controllo feature dopo output e un public score golden indipendente per
ogni gruppo realizzato dopo drain. Tutto questo lavoro numerico reale è rimasto
**non eseguito**.

I massimi prospettici erano128offerte,192read/feature calls,416righe raw/feature,
352public calls/688righe scored/2752Booleani,2membership/13998record,
2golden/2048righe,2modelli/threshold set,4handle/8schema check e2custody.
La derivazione usa somma(1…8)=36 e conta separatamente i riferimenti; niente
sostituzione con costi B8 pieni, timing vector o eventi indipendenti inventati.

**Attività reale positiva:** due SHA256 completi del raw, ognuno2.908.260.409B,
totale **5.816.520.818B**, stesso hash originale atteso. Pre1.260091750s,
post1.469026375s. Il consumer PCA ha tentato l'inizializzazione/import numerico,
poi è uscito1 prima di ready. Il suo ultimo checkpoint valido è generazione1,
fase imports, prima delle verifiche/caricamenti payload: tutti i contatori sono0,
nessun inflight. Zero membership/golden/model-artifact loads, selezioni/HDF handle,
feature/public-score/decisioni reali; non è una dichiarazione globale di attività
operativa zero, perché la custody è realmente avvenuta. Il completamento degli
import/thread query non è documentato; non va trasformato in un risultato positivo
né in un falso zero-import.

PCA aveva64offerte configurate, ma t0 non è stato emesso:0offerte effettive,
submission/ammissioni/completamenti0,64future, latenza n=0. AE non tentato.
Supervisore: `Child exited before ready`; producer in attesa terminato/reaped,
consumer exit1/reaped. Cleanup34.581916ms, ring assente e21nomi propri assenti.
Outer non ha forzato il gruppo; exit1 osservato, reaping e assenza sessione
confermati. Durata esterna **6.016954667s** inclusiva di import/report/finalizer/
uscita/reaping. Nessuna parità, throughput o latenza raw-to-decision misurata.

La precisa eccezione di inizializzazione non è conservata. La revisione statica ha
identificato un errore certo nel codice: SHA del testo Torch confrontato con SHA
della stringa JSON canonica storica. È una spiegazione plausibile, non un traceback
osservato. Il codice finale0054.2 corregge la rappresentazione e conserva errori
iniziali con cleanup indipendente; **non è stato rieseguito sui dati reali**.
La fonte originale del pilot0054.1 rimane congelata nel relativo snapshot.

## Qualifica generata e secondo fallimento

Prima del pilot, il bundle
`57345476109c91e4be63cb1b8d5e6e8f8d698666cb4414da555e27af9a67816c`
passa12/12aspettative generate:560offerte configurate,5run normali e7guasti
intenzionali verificati, esterno3.600960167s. I guasti attesi non diventano run
normali. Limiti inferiori conservati:433righe read,431feature/score aritmetici,
430reference,431C/1724Booleani primari. Il torn e l'inizializzazione non osservata
restano incerti. Test stand-in separati, nessun HDF generato.

Dopo la correzione, unico secondo bundle
`2ce73ba6149ea6cdb66605352cd44e268d7c86e5526239f23ffa043970b815f1`:
**40test focalizzati passano**, ma la suite nativa si ferma al primo normal500
prima di t0. Messaggio `Own tracker16MiB allowance within inner80MiB`.
Il predicato richiede0<RSS≤16MiB: il valore fallito non è conservato, quindi non
si può scegliere fra misura nulla/non disponibile e superamento16MiB. Entrambi
figli terminati/reaped, ring e21nomi assenti; intervallo esterno0.199147s.
Esistono result/emergenza/CSV, manca il summary finale del subject; exit1 e
qualifica falsa sono correttamente preservati. Nessun terzo ciclo o ricostruzione
dei pass da fonti diverse. Ultima copertura:1/12tentato,0pass; restanti11non tentati.

Totale13invocazioni native generate/688offerte configurate, sotto24/3072; due
lanci di suite consumati. Le prove pure29+34+38+40=141esecuzioni restano nel log;
non sono case invocations. Lint/format/static checks pertinenti, non suite storiche
complete o matrici operative. Nessuna ottimizzazione AB/BA.

Diagnostiche native:1048append evento,2oltre50µs, massimo80458ns;2135batch,
0oltre200µs, massimo89334ns. I due superamenti sono nel fixture contesa. Nessun
append evento/batch reale completato. Costi inclusivi/cicli/denominatori per caso
conservati, senza sottrazione overhead o campioni sostituiti. Task0052 conserva
permanentemente i suoi cinque superamenti e lo stato parziale/negativo.

## Risorse, storie e limiti

Ledger unico pre-growth **334entry/21.324.448B**, massimo32MiB, per entrambe
suite più pilot, snapshot/campioni/report/fallimenti/ricevute e copie curate
simultanee. Nessuna evidenza eliminata per recuperare quota. File logici e blocchi
allocati nel summary; mapping alias non doppio payload, metadati FS/kernel ignoti.
Il tempo generato esterno totale3.800107167s più10s riservati observer è sotto150s;
pilot6.016954667s più2s observer è sotto180s. La curation statica successiva è
separata dai programmi osservati, non un tail dichiarato misurato.

Budget pilot180s:45pre+2×30run+45post+30report/cleanup; setup10/drain5/ref-post10/
cleanup2, operation/no-progress2s e monitor gap250ms restano.100ms e50/200µs sono
diagnostici, non causa di retry. RSS64/1024/128MiB, somma1216 e guard residente512;
outer48+inner64+tracker16 entro128.21SemLock core/0outer/cap26;273nomi propri
controllati e assenti fra tutti i casi tentati. Backing kernel sconosciuto.

Envelope numerico proposto7.257.368B≤8MiB derivato da sorgenti/forme, non misura
di allocazione reale.8MiB heap Python e512MiB workspace nativo restano target non
validati. Il picco import del consumer reale non è stato campionato dopo il
fallimento:29.917.184B dell'ultimo checkpoint non certificano il lifetime peak.
Thread effettivi Torch/BLAS/Accelerate/decoder, schema/cache HDF e workspace reali
non stabiliti; richiesta ambiente1 non è evidenza effettiva.

Custody/prior history possono scaldare OS cache. Reopen HDF non è cold cache;
nessun purge/reboot/chiusura app/prefetch. Si trasportano descrittori software64B,
non byte detector. Timing include osservatori/controlli, non overhead puro di
trasporto/cache né throughput non strumentato. Le latenze non osservate restano
null, non0; maschere false sarebbero comunque servizio completato.

P1 finale incompleto; P2fallimento/visibilità risorse e workspace/thread aperti;
P3nessuna osservazione di servizio reale; P4concesso/consumato solo per questa
sessione fallita. Prossima decisione: correzioni software/resource osservabili e
nuova qualifica completa separatamente circoscritta; soltanto dopo, nuova
**autorizzazione stretta** di integrazione reale. Uno studio più grande non è
ancora giustificato. Nessuna conferma scientifica indipendente, utilità strict-tail,
efficienza fisica, causalità nonlineare, detector readiness o affiliazione ufficiale.

CPU/sintetico0049chiuso,0036unresolved_no_acquisition,0034gates,
YES/YES/YES,particle192/192consumato/deferral canonico,0024export accettato versus
0025performance fallita, tutti gli esiti storici e nessun MPS corrente invariati.

## Git soltanto manuale

Escludere diagnostici ignorati, data/model artifacts e cambiamenti estranei.
I nuovi file vanno letti prima dello staging; nessun comando seguente è eseguito.

```sh
git status --short --branch
git diff --check
git diff --stat
git diff -- README.md docs/project-memory.md docs/handoffs/README.md src/latenttrigger/streaming
git ls-files --others --exclude-standard
git diff --no-index -- /dev/null src/latenttrigger/streaming/hdf_consumer.py
git diff --no-index -- /dev/null src/latenttrigger/streaming/pilot54.py
git add -- README.md docs/project-memory.md docs/handoffs/README.md \
  src/latenttrigger/streaming/__init__.py src/latenttrigger/streaming/fixture.py \
  src/latenttrigger/streaming/quota.py src/latenttrigger/streaming/transport.py \
  src/latenttrigger/streaming/validation_v2.py src/latenttrigger/streaming/hdf_consumer.py \
  src/latenttrigger/streaming/pilot54.py scripts/development_hdf_consumer_pilot.py \
  tests/test_development_hdf_consumer_pilot.py \
  configs/streaming/development_hdf_consumer_pilot_v1.json \
  docs/development-hdf-consumer-pilot.md docs/prompts/0054-development-hdf-consumer-pilot.md \
  docs/handoffs/0054-development-hdf-consumer-pilot.md \
  results/tables/final/task0054-development-hdf-consumer-pilot-cases.csv \
  results/tables/final/task0054-development-hdf-consumer-pilot-summary.json
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "feat(streaming): add bounded HDF pilot with partial validation"
git push origin main
```
