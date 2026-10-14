# Task0045 — Paired natural-partial raw-to-decision measurement

## Metadata e stato finale

2026-10-13, Europe/Rome; macOS Apple Silicon, Python3.12/.venv, CPU originale.
Task0045 soltanto. **parent_accepted_natural_partial_raw_decision_measurement**:
una sola sessione operativa, allowance consumata, nessun retry. Checkout iniziale
pulito, indice vuoto, main/origin/main allineati ad
`a8094adc697895a2f8ef05b6a24f0e1aeb86603c` (Task0044 committata), memoria1.39.
Il prompt effettivo è salvato prima dell'implementazione; questo handoff aggiorna
l'initial handoff dello stesso task. Nessun nuovo commit/push/staging o hosted CI.
Il vecchio `d4b92e55...` e tutte le altre basi task-time restano storiche.

Il risultato chiude il confine operativo natural-partial prescritto. Non esegue
padding, trasporto, simulatore, ricerca di policy, nuova scienza o Task0046.
Task0043 accepted/consumed, Task0044 replay sintetico accepted con il precedente
source-loader failure conservato, Task0041 failed/consumed, Task0042 software-only,
Task0036 unresolved_no_acquisition e particle192/deferment restano invariati.
Esposizione storica held-out **YES/YES/YES** permanente; gate scientifici,
fallimenti/allowance precedenti e artefatti storici non sono riqualificati.

## Obiettivo, contratto e decisioni tecniche

Confronto prospettico in coppie: `natural_m` legge i primi m ID approvati della
finestra contenente B, costruisce le feature congelate, alloca/copia esattamente m
righe nel servizio CPU natural originale e conserva score pubblico/quattro
Decision/result copies. `full_B_control` fa una lettura HDF propria dei B eventi
reali della stessa finestra, percorre la stessa catena e conserva tutti i B
risultati. B−m sono lavoro fisico reale del controllo, non dummy.

Casi immutabili: B1:m1; B8:m1/2/7/8; B32:m1/2/8/31/32;
B128:m1/2/32/127/128. Le finestre di entrambi i lati partono da
0, floor((1024−B)/2), 1024−B: nessun ricentramento usando m e nessun partial
ottenuto tagliando un buffer raw full già letto. service_B è B per i casi
Task0038 già supportati; soltanto32/8 usa service_B8 e128/32 usa service_B32.
Sono le vecchie chiamate natural8/8 e32/32, con allocazione effettiva8/32righe.
Il validator e packing storici rimangono byte invariati. Il controllo usa sempre
service_B=B, m_actual=B; a m=B il lavoro previsto è identico, non le durate.

Worker1/3: PCA→AE, casi ascendenti. Worker2: AE→PCA, lista completa inversa.
Per candidato/caso: tre warm-up pairs, poi venti timed pairs; cicli resettati per
fase, finestra i mod3, natural-first agli i pari, control-first ai dispari.
Temporizzati:20coppie/40chiamate, finestre7/7/6 e ordine10/10. Prima e dopo ogni
blocco candidato, gate ascendenti per tutti i casi/finestre/lati: un reference
natural golden-only e due catene complete per lato. Feature/golden byte identici;
score/mask/repeat identici al reference della stessa forma; post=pre e input/
Parameters/modelli/threshold immutabili. Nessun oracle natural-vs-full,
certificate universale, ampliamento tolleranza o passaggio diagnostico FP64 reale.

Timer integer-ns sincrono da subito prima della checked selected read fino a
packing/score/quattro decisioni/copied results. Lookup finestre, load, hash/parità,
accounting durevole e query esplicite guard/thread sono esterni. Le feature già
calcolate sono confrontate dopo il timer, senza ricostruzione/seconda
standardizzazione. Nessun preload raw, servizio feature-only o esecuzione differita.

Tutte le identità/ruoli/scienza/lineage Task0039/0040/0043 sono mantenute: source
int64[6999]/56120B, prefix1024 `f80a9483...`, HDF2908260409B `5da8fda2...`,
golden FP32[1024,8]/32896B file`7164bfd7...`/payload`2ba0776a...`.
Resolver originale domain/unique/sorted-prefix, split/dev manifests/transform e
preparazione Task0020 riuscita; la campagna complessiva Task0020 resta fallita.
La union effettiva coincide con le tre B128 windows Task0043:384raw unique, dentro
1024approved, non popolazione ampliata o allineamento solo filename/lunghezza.

Originali entry complete `prepared_batch_service_v1.json`: hash file/config/
result/scientific, otto feature ordinate, training e calibration relationship.
PCA sei componenti FP64; AE v2 CPU FP32/155parametri/eval/inference; SSE pubblico
FP64; quattro confronti stretti score>threshold. Ogni modello/threshold set una
volta per worker, sei istanze di ciascun tipo di load complessivo. Nessun pickle,
nuovo backend, scaler/threshold ricalcolato o fitting. Le feature riusano
canonicalize→physical_aggregates→standardized_aggregates/Parameters frozen:
sort/wrap sourceFP64 prima della conversione physicalFP32, aggregatiFP64 su tutti
i validi prima di qualsiasi384truncation, regole massa/log/scaler e finaleFP32.
Label2100 verifica background e rimane fuori dalle feature; nessuna particle view.

## Modifiche e file

Config additiva `configs/benchmarks/development_partial_raw_decision_v1.json`;
nove helper `src/latenttrigger/benchmarks/partial_raw_*.py` (planner, protocol,
provider, measure, admission, runtime, native controller, worker, reporting),
validator `scripts/validate_partial_raw_decisions.py`, tre file test dedicati.
Owner/task/namespace0045 propri, senza cambiare globals, guard o budget storici.
Il planner puro conserva schedule/casi/shape/side/window/ordine/budget/dedup;
provider chiuso verifica permesso/prefix/shape/oggetti modello/threshold prima del
backend e nega copie alterate del permesso. Slice contigua solo se tutto
l'intervallo coincide con gli ID richiesti. Ledger nested durevole registra
intent, richieste/returned/completed e inflight anche su eccezione.

Producer→record serializzato→strict outer admission→freeze/claim→controller→worker
è testato insieme, con controlli indipendenti. Record/software non equivale a
execution authority; il prompt effettivo è l'autorizzazione di una nuova unica
sessione, dopo final validation/roundtrip/freeze/prerequisiti. Primo prerequisite
reale consuma anche su errore; vecchie allowance non vengono riaperte.

Curati: [report](../natural-partial-raw-decision-measurement.md),
[prompt](../prompts/0045-natural-partial-raw-decision-measurement.md), questo handoff,
180celle CSV,1800coppie CSV, summary JSON e tre figure joint/paired/chronology.
Ogni cella conserva20timings tramite le due colonne delle20coppie corrispondenti;
90gruppi conservano20difference/ratio,60pooled side distributions usano60valori
originali, mai percentile mediati. Tutti worker/calls/outlier sfavorevoli restano.
Raw/particle/feature/score/mask/ID non sono esportati. Data/validation, sequences,
permessi/plans/receipts/ledgers/freezes/integrity maps restano ignored.
README, indice e living memory aggiornati a1.40;568baseline tracked bytes
preservati eccetto i tre living documenti intenzionalmente aggiornati.

## Validazione finale, dipendenze e fallimenti software conservati

Record finale:
`data/task0045-validation/c5d9634ddf0a4d7ca2050a79eb315739/software-acceptance.json`.
172focused,2921full,2921portable artifact-free; lint/format/pip-check pass.
298source/metadata bindings,43distribuzioni installate,41file nativi NumPy/HDF/
Blosc/TorchCPU, canonical JSON-string Torch build e prompt/config/scope/shape/
packing/schedule/budget. Nessun install/update o backend replacement.
Bootstrap102.746576s e actual emitted-record admitted native roundtrip94.216284s
parent accepted:180celle/coppie/gate/counter/cleanup/reporting completi ciascuno,
exit0/reaping/caps/release. Sidecar non circolare e record immutabile; soltanto
questa acceptance permette il freeze operativo. Nessuna sorgente numerica reale,
modello originale, rawSHA/HDF operativo durante la validazione.

Cinque native fixture invocations conservate:58.391436s complete-body ma
publication rejected per journal filename;31.341330s partial rejected per gara
tra enumeration e atomic rename;944.558936s rejected per deadline continuo
(ordinary endpoints40.239327s, compatibile con sospensione), poi i due accepted
finali. Il terzo registra reap/release non tempestivamente confermati: supplemental
readonly cleanup osserva successivamente tutti i PID proprietari e assertion
assenti, senza riscrivere il failed receipt. La correzione additiva del storage
riserva4MiB per un temporaneo JSON riconosciuto scomparso, nega la perdita di altri
file e non allarga cap. Anche un focused165passed/5failed e tutti i source
snapshot/log restano. Questi fallimenti software non sono campagne operative.

Fixture totals durevoli conosciuti:26725reads/features/1090961rows,
31393servizi/1279124rows/5116496Boolean,28fixture models/threshold load instances;
un reference127righe inflight del test sospeso non è conteggiato completed.
14setup provati dal raggiungimento dei loader:112raw/featurecalls14336rows,
28creator models oltre28loads,14write+14setup-read HDF handles, setup forwards0.
Ogni focused/full/portable finale dedicato include2498toy public score services
100974rows, distinti da NN forwards. Sei instrumented historical research subsets
full/portable dei tre software runs:510model instances/186forwards+reconstructions/
52260rows/12toy optimizer updates/12synthetic calibrations; altri legacy fixture
models rimangono fuori da tale subset. Nessun global-zero model/forward/update
claim, né hosted CI. Tutte queste attività sono separate dai conteggi reali.

## Risultati fisici e interpretazione

Sessione `1872bdaa920f49598ec8eafcf4ea3c08` in
`results/benchmarks/task0045-natural-partial-raw-decisions/`, parent accepted,
allowance consumata. Whole164.220661s/reserved160.995997s/prereq3.298504s/
postcustody1.345023s/finalization2.149012s/overshoot0. Clock del controller nativo
dopo software admission/freezing; nessun numerical load prima dei prerequisiti.

| Quarter B/m | PCA natural/full mean ms | AE natural/full mean ms | PCA/AE mean paired ratio |
| --- | ---: | ---: | ---: |
| 8/2 | .9538 / 3.2642 | .9766 / 3.3027 | .2922 / .2965 |
| 32/8 | 3.1698 / 12.1486 | 3.3309 / 12.5523 | .2602 / .2643 |
| 128/32 | 12.7916 / 48.6105 | 13.2394 / 50.1811 | .2627 / .2634 |

Medie da60osservazioni per stesso candidato/B/m/lato. Il rapporto è calcolato
prima per coppia, poi mediato; non è rapporto di medie. Delta natural−full a128/32
−35.8189/−36.9416ms. PCA128/32: natural/m .399738ms, control/B .379770ms fisiche,
hypothetical control/m1.519078ms utili; il controllo esegue128eventi reali.

351natural-slower pairs conservate:100/1320partial,251/480null m=B. I casi partial
sfavorevoli appartengono alle occupancies quasi piene, non sono nascosti. Delta
partial−58.505583…+3.430125ms/ratio.010364…1.116384; null
−100.614667…+5.497958ms/ratio.263420…3.749211. B1null ha medie lato vicine ma
ratio medi1.8142/1.6709: ordine/host finiti e asimmetria dei rapporti contano,
nessuna durata identica attesa. Slowest retained call151.721125ms. Tre figure
visivamente ispezionate leggibili; marker worker1cerchio/2quadrato/3triangolo nella
joint, ordine nella paired, tutti3600timings nella chronology; nessun trimming.

I quarter points sono sparse exploratory anchors informati da Task0044, non una
cost curve per ogni m o conferma scientifica indipendente. Prehash/pre-gates/
alternazione/ripetizioni e cache persistente1MiB521/.75 sono contesto caldo, non
cold I/O o partial-only streaming history. La differenza comprende selezione raw,
features, packing e model shape diversi; non isola decoder/disk/model causality,
upper bound universale o p99produzione. No interpolazione/fitting/selected policy.
Task0043 e bills Task0044 rimangono contesto storico: non si sottraggono campagne,
non si riscrive/riesegue replay0044, nessuna misura arrivals/queue/transport.

## Conteggi operativi effettivi e parità

| Componente | Calls | Row presentations |
| --- | ---: | ---: |
| Timed chains | 3600 | 145920 |
| Warm chains | 540 | 21888 |
| Pre/post repeated chains | 2160 | 87552 |
| Selected reads / feature constructions, ciascuno | 6300 | 255360 |
| Golden-only reference services | 1080 | 43776 |
| Public score / quattro decisioni | 7380 | 299136 |

180celle/90paired groups/1800timed pairs/270warm pairs;540paired gate contexts,
1080side records. Tutte6300richieste/returned read e costruzioni completate,
7380servizi completed e1196544Boolean; nessun inflight finale. Parità esatta
feature/golden e score/mask/repeat/reference/post0/0/0mismatch same-shaped.
Modelli/input/Parameters/threshold immutabili, nessuna cross-shape attribution.

Membership3load/20997inspected/3072selected da6999source records,1024approved
unique. Golden3load/3072rows/1024unique. Raw384unique distinti da255360repeated
presentations. Per worker2100reads/features85120rows,360references14592rows,
2460servizi99712rows. Per lato e worker raw natural1050/26810, control1050/58310;
servizi natural1230/31406, control1230/68306. Side/case breakdown nel summary,
non righe sorgente.

Sei original frozen models e threshold instances, tre per candidato.
Per candidato3690public computations149568rows:3690PCA reconstructions e3690AE
forwards/reconstructions separatamente. I nuovi raw/feature/model inference/
reconstruction/decision work sono reali positivi autorizzati, non zero.
HDF3readonly opens/closes,6schema/filter/hard-link/cache checks sulle stesse tre
handle; nessuna quarta opening. RawSHA2passes5816520818byte presentations, hash
originale identico. No MD5/copy/numeric scan. Geometry6300requests:312chunks,
217339541760B/202.413222GiB repeated no-cache decoded upper geometry, non I/O,
decompression/cache misses misurate; decoder threads effettivi sconosciuti.
Operational optimizer/scaler/calibration/scientific metrics/fingerprints/
held-out/signal/selection requests/download/ProcessedStore/device/transport/
replay/padding/dummy/preload rimangono0; ciò non azzera il lavoro fixture storico.

## Risorse, clock e lifecycle

Cap immutabili: prereq60s,3numerical workers180s dispatch→normal exit/reap,
report60s,postraw45s,final15s,reserved720s,whole780s;cleanup2s dentrocap.
RSS worker1GiB/native512MiB/controller128MiB/arrays64MiB;combinedjournals16MiB
per process e64MiB session/log1MiB/owned outputs128MiB. Numerical dispatch
57.226544/47.730071/45.177413s, report5.561614s. Quattro exit0/reaped;
cleanup .000799/.000158/.000304s numerici. Nessun guard latch.

RSS max404832256B, native reserved207470592B, controllerRSS51265536B;
conservative parent+un serial worker native245219328B. Owned output26832267B.
Bound arrays55858176B (128rows/24particle temporaries + raw +2MiB margin),
reference/request/golden/ID retained186880B nel margine, raw buffers retained0.
Bound distinto da sample RSS/native all-malloc-zone reservations e da physical
unique RAM/attribution. Assertion-helper RSS è separato contesto.

Numerical primary NORMAL6602/WARN3315/CRITICAL0/unknown0;report65NORMAL;
parent6370NORMAL/4632WARN. WARN advisory, primary critical/invalid veto.
Max query-start gap worker3.500353s/parent2.843063s; terminal gaps
.549615/.235053/.273158/.087250s. Nessuna continuous-resource-sampling claim:
continuous clock sorveglia deadline/exit indipendentemente dalle query e include
sospensione. Optional unavailable/unobserved context esplicitamente unknown,
nessun global RAM floor/cache purge/app closure. Environment prima degli import,
Torch intra/inter1/deterministic CPU/BLAS-OMP-Accelerate originali;
BLOSC_NTHREADS richiesto1, decoder effettivo unknown.

35osservazioni active dell'owned temporary idle-system assertion; release/helper
reaping/assenza confermate prima della parent acceptance. Display sleep permesso,
nessuna impostazione persistente. Handle/stati posseduti/limiter/thread/determinismo
ripristinati; interop one-time liberato dall'uscita/reaping del fresh process.
Body complete non è parent acceptance: qui uscita, caps, custodia finale, source/
build/output identity e release sono tutti passati.

## Riproducibilità, alternative e prossima decisione

Config/prompt/helper/tests/build finali congelati, admission record/freeze/claim,
execution plan/marker/grant/ledgers/receipts/sequences ignorati e conservati.
Non rilanciare il validator/controller come se riaprisse la sessione: allowance
consumed. La curation legge soltanto gli owned aggregates/receipts e copia outputs
già accettati; non autorizza altri model/data runs. Esclusi reuse vecchi grant,
preloaded full buffer, padding, cross-shape oracle, extra diagnostics, tolleranza
repair, fastest-run selection, cause attribution e policy choice.

Prossima decisione separata: se usare queste misure sparse in un futuro replay
versionato, definire prospetticamente ogni occupancy m non misurata e la nuova
cache/input-history assumption, poi autorizzare il task pertinente. Nessun
Task0046 automatico, nuovo source/signal confirmation, acquisition, scientific
protocol change o particle training. Conservare lo stato storico sopra.

## Git manuale — non eseguito da Codex

Branch/upstream effettivi main/origin/main, HEAD invariato `a8094adc...`, indice
vuoto.26path del task:23nuovi e3living modificati; nessun unrelated work rilevato.
I comandi vanno revisionati/eseguiti dall'utente. Non aggiungere data/, risultati
benchmarks ignorati, snapshot, array, sequenze, permessi o ricevute.

```bash
git status --short
git branch -vv
git diff --check
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git diff --no-index -- /dev/null docs/natural-partial-raw-decision-measurement.md
git add -- \
  README.md docs/project-memory.md docs/handoffs/README.md \
  docs/prompts/0045-natural-partial-raw-decision-measurement.md \
  docs/handoffs/0045-natural-partial-raw-decision-measurement.md \
  docs/natural-partial-raw-decision-measurement.md \
  configs/benchmarks/development_partial_raw_decision_v1.json \
  scripts/validate_partial_raw_decisions.py \
  src/latenttrigger/benchmarks/partial_raw_admission.py \
  src/latenttrigger/benchmarks/partial_raw_measure.py \
  src/latenttrigger/benchmarks/partial_raw_native.py \
  src/latenttrigger/benchmarks/partial_raw_planning.py \
  src/latenttrigger/benchmarks/partial_raw_protocol.py \
  src/latenttrigger/benchmarks/partial_raw_provider.py \
  src/latenttrigger/benchmarks/partial_raw_reporting.py \
  src/latenttrigger/benchmarks/partial_raw_runtime.py \
  src/latenttrigger/benchmarks/partial_raw_worker.py \
  tests/test_partial_raw_admission.py tests/test_partial_raw_chain.py tests/test_partial_raw_runtime.py \
  results/tables/final/task0045-natural-partial-raw-decision-cells.csv \
  results/tables/final/task0045-natural-partial-raw-decision-pairs.csv \
  results/tables/final/task0045-natural-partial-raw-decision-summary.json \
  results/figures/final/task0045-natural-partial-raw-decision-joint-cost.png \
  results/figures/final/task0045-natural-partial-raw-decision-paired-cost.png \
  results/figures/final/task0045-natural-partial-raw-decision-chronology.png
git diff --cached --check
git diff --cached --stat
git diff --cached
git status --short
git commit -m "feat(benchmarks): measure paired natural partial raw-to-decision services"
git push origin main
```
