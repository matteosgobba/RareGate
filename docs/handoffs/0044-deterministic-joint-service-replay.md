# Task0044 — Replay deterministico della coda con servizi congiunti

## Metadati e risultato

Data:2026-10-13, Europe/Rome. Branch `main`, upstream `origin/main`, base verificata
`d4b92e55e3f8e32eefd5186c303c1d15205bc090`, Task0043 già committata. Checkout e
indice erano puliti; memoria verificata1.38, aggiornata1.39. Nessun commit risultante
è inventato: staging/commit/push restano manuali. Le basi storiche Task0043
`6d5fb446...`, Task0042 e Task0041 restano i rispettivi riferimenti di allora.

Stato finale: **parent_accepted_synthetic_joint_service_replay**, invocazione
`f6cee370c24f43a0b95558d4f2e03faa`. Completati tutti1764scenari,
8,820,000presentazioni,756contrasti ciclico−media e252contrasti ordine−ciclico.
Conservazione:7,954,126completati +865,874overflow =8,820,000generati;
ammessi=completati, pending finale0,1,998,537completamenti oltre100ms.
Sono somme di presentazioni ripetute, senza interpretazione come eventi indipendenti.

Consegnati [report](../deterministic-joint-service-replay.md),
[prompt effettivo](../prompts/0044-deterministic-joint-service-replay.md),
[config stretta](../../configs/simulation/joint_service_replay_v1.json),
[scenari](../../results/tables/final/task0044-joint-service-replay-scenarios.csv),
[contrasti](../../results/tables/final/task0044-joint-service-replay-contrasts.csv),
[sommario](../../results/tables/final/task0044-joint-service-replay-summary.json)
e tre figure ispezionate: esiti, latenza dei sopravvissuti, sensibilità/billing.
Gli helper `simulation/joint_*`,161nuovi test e un entrypoint di validazione sono
additivi. Motore/protocollo/costi costanti Task0037 e fonti storiche sono intatti.

## Ambito e custodia delle fonti

Il prompt effettivo è stato salvato prima dello sviluppo, insieme all'handoff
iniziale. Autorizza questo replay sintetico dopo nuova accettazione/freezing e
letture strette dei timing/provenienza Task0043; non autorizza nuovi dati, modelli,
misure fisiche, acquisizione, selezione di policy o Task0045.

La directory sorgente fissa è
`results/benchmarks/task0043-development-raw-decisions/e94e4aea9d6549f78c24c8ffe0881c4e/`.
Tutti i19file richiesti sono pin esatti (690,916byte): config/prompt originali,
summary/CSV curate, execution plan/workflow/parent acceptance e tre receipt,
aggregate, timer e JSONL. Sono verificati task/scope/parent accepted, relazioni,
parità esatta, exit normali/reaping/deadline originali e mappe hash degli output.
La CSV originale serializza i conteggi finestra come `7/7/6`; non viene ricostruita
una sequenza dalle medie arrotondate. Nessun path raw/modello/array embedded viene
seguito. Le13identità metadata software già presenti nella mappa originale sono
anch'esse congelate: due sovrapposizioni,30file unici/947,791byte. Gli11metadata
aggiuntivi sono controlli byte-only, senza parsing numerico di vecchi risultati.
I vecchi `.py` vengono controllati solo sulle voci originalmente dichiarate;
nessun vecchio controller viene rilanciato e la mappa non deve contenere nuovi file.

Ogni JSONL viene verificato sull'intero schedule ordinato184record (160timed,
24warmup): ordinale unico, candidate/B/phase/call e ciclo finestra. I24vettori
restano separati per candidato/B/ripetizione, ciascuno20durate intere positive ns.
Warmup esclusi prospetticamente; gate/reference mai aggiunti. `elapsed_ns` è il
servizio; timestamp continui/gap di strumentazione non diventano servizi/arrivi.
Ordine/durate e copie aggregate sono esatti. Le copie statistiche JSON/CSV sono
confrontate con quantili lineari/SD popolazione stdlib entro32ULP binary64,
regola meccanica di serializzazione, senza moltiplicatore empirico.

Replay accettato +verificatore indipendente parent:6letture JSONL/1104record,
960timed selezionati, sempre24vettori/480posizioni sorgente originali. Con la prima
invocazione fallita si arriva a7letture/1288record/980valori selezionati o derivati;
i20della prima invocazione non sono nuovi campioni. Copie aggregate native:
1120osservazioni,1288durate di chronology,448statistiche di cella;392statistiche CSV
convertite numericamente e192statistiche pooled caricate nei summary. Prima dello
replay,16ispezioni JSON metadata hanno incluso160copie osservazioni,
184chronology,64statistiche aggregate e256pooled; zero JSONL precedenti.
I contatori distinguono parsing, hash byte-only, riuso dei campioni e metadata
hardware/model/cache/scientifici che rimangono esclusivamente provenienza storica.

## Semantica e matrice deterministica

Un server FIFO non preemptive; drop-tail sulla somma attesa +eventi effettivi in
servizio, capacità1024. A parità di tempo: completamento, arrivi in ordine sorgente,
dispatch/flush. Timeout=arrivo originale del più vecchio in attesa +timeout;
final drain segue la stessa policy. Un batch cattura la propria durata: tutte le
latenze sono dispatch wait +quel costo; busy=sum delle durate assegnate, con
intervalli clipped all'orizzonte separati. Nessuna decomposizione inventata del
wait in queue e batching indipendentemente misurati.

Ogni scenario riparte j=0, consumato solo al dispatch (anche partial/flush/drain).
Ciclico q[j%20], reverse q[19-j%20], rotation10 q[(j+10)%20]; controllo
costante `(sum(q)+19)//20`. Nessun pooling/interpolazione/shuffle/fitting/outlier
replacement. Conteggi sugli indici originali e somme sono verificati anche
indipendentemente dal parent. Arrotondamento del controllo massimo1ns per batch,
senza sottrazione. Ciclo artificiale20batch/discontinuità al wrap: nessuna
osservazione misurata nuova o distribuzione stazionaria di produzione.

Generatore Task0037 immutato: PCG64/SeedSequence[3700,seed,mode_id,rate,stream_id],
stream arrivi/toy-score distinti; primo arrivo dopo primo gap, ceil periodico o
esponenziale almeno1ns.18trace immutabili/90,000eventi unici: periodic ePoisson,
rate500/2500/5000 input events/s, seed41/42/43,5000eventi ciascuna. Hash timestamp,
score e trace/horizon/rate realizzati sono in summary. Tutti i confronti hanno le
stesse trace bytes. I toy score Uniform[0,1) e cut stretti0.9/0.95/0.99/0.999
dopo completion servono alla conservazione, senza score/mask scientifici caricati
né claim di efficienza del classificatore.

Sette policy:B1/timeout0 eB8/32/128 ai timeout1ms/10ms. Due candidati e tre
ripetizioni separate, ciclico/costante:1512scenari. SoloPoisson2500/s, stessi tre
seed/tutte le policy/candidati/ripetizioni aggiunge252scenari reverse/rotation10;
il baseline ciclico esistente viene riusato. Deadline ingegneristica100ms,
late strettamente>deadline, senza requisito CERN o modifica dell'illustrazione1ms
Task0037. Rate/deadline conoscevano già i costi Task0043: congelare il disegno
assicura riproducibilità, senza indipendenza scientifica.

## Esiti, differenze e limiti

| Assegnazione | Presentazioni | Completati | Overflow | Late completati |
|---|---:|---:|---:|---:|
| Ciclico main |3,780,000|3,357,428|422,572|923,412|
| Costante main |3,780,000|3,357,777|422,223|918,148|
| Reverse |630,000|619,460|10,540|78,633|
| Rotation10 |630,000|619,461|10,539|78,344|

La sola media descrive bene molti conteggi, ma non riproduce tutti gli esiti fissi.
Ciclico−costante:637/756overflow identici,119diversi, range−10…+16;438/756late
identici,318diversi, range−21…+146. Somma differenze+349overflow/+5264late.
Differenze p99 sopravvissuti−1.289794…+6.984459ms. Il massimo positivo èAE B128/
1ms,Poisson5000/s,seed42,repetition2: entrambi3453completati/1547overflow su5000.
Il massimo aumento late+146 èAE B128/1ms,Poisson2500/s,seed43,repetition2,
5000completati per entrambi: il conteggio può cambiare anche senza overflow.

Ordine:249/252overflow identici; gli altri tre diminuiscono di1. Reverse−ciclico:
p99−2.332566…+8.022939ms, late−67…+222 (somma+412); rotation10−ciclico:
p99−2.263778…+3.208104ms, late−81…+175 (somma+123). Il caso reverse maggiore
èPCA B128/1ms,Poisson2500/s,seed41,repetition1:5000completati, +8.022939ms p99/
+222late. L'ordine ha quindi poco effetto sull'overflow di questo sottostudio,
ma può spostare latenza/deadline. Stesso multiset non implica stessa media del
prefisso assegnato se cambiano dispatch count/allineamento/ciclo/drain.
Nessuna significatività, CI o interpretazione causale su un modello di produzione.

I denominatori sono espliciti nelle CSV e nelle figure. Per B1 ciclico a500/s,
zero overflow/late, p99PCA0.612–1.732ms eAE0.648–2.014ms. A2500/s B1 perde
7.82–12.30% PCA/10.34–17.34% AE e ha p99 sopravvissuti577.926–597.081ms /
599.021–645.700ms. A5000/s B1 perde43.68–45.28% /44.94–47.86%;89.864–90.570% /
90.265–91.254% dei completati sono late. Tutte le altre policy e i casi sfavorevoli
rimangono nel report; non viene pubblicata una policy migliore.

**Billing partial:**425,677batch parziali,3,347,103eventi utili,
11,093,600slot B addebitati,7,746,497slot inutilizzati, utilità aggregate30.1715%,
4246.973707secondi virtuali di busy partial sommati fra scenari. Main ciclico
208,284partial/1,457,286utili/5,294,928slot. B128 ciclico a500/s utilizza solo
17.756–19.434% degli slot partial. Il minimo osservato2.34375% è un batch final
con3eventi/128slot (PCA,Poisson5000/s,seed41,repetition2,B128/1ms,ciclico).
Ogni m<B paga il selezionato servizio naturale completo B: ipotesi esplicita,
nessuna esecuzione di padding, misura natural-m o upper bound fisico generale.

1,705,396dispatch:962,026assegnazioni campione originale e743,370costanti.
Le noncostanti comprendono47,691cicli completi +8206remainder; i contatori restano
per scenario, senza concatenare worker. Orizzonte, pending/drain, full/partial,
slot, busy, toy conservazione e limite outstanding sono verificati. Al massimo
5000latenze per caso, liberate fra scenari. Nessuna matrice duplicata in JSON.

Sono stati ispezionati tutti e tre PNG finali; ogni osservazione/contrasto disegnato
è nei range. Latenza log, differenze symmetric-log con soglia esplicita, niente CI
né clipping. La curazione copia byte già accettati:0.546s su budget separato60s,
nessun replay per ridisegnare figure. JSON curata129,134byte; ledgers, receipts,
fixture, sequenze sorgente e source snapshot rimangono ignorati.

## Validazione fresca, admission e storia delle invocazioni

Accettazione finale:
`data/task0044-validation/30bc752c1cff474488bcd5bd3b0be537/software-acceptance.json`,
SHA256 `0f0d35fc7fff5342d764752117051de8be2164ac2c3acc8ae2505f2bb19330b6`.
Roundtrip noncircolare:
`1c49dcb2142f2265427856c0c6f804845a8c39462461d847d1cea22a847e6eef`.
269binding source/config/prompt/test,43package e36file metadata/native installati.
161nuovi test +27runtime Task0037 =188focused,2749full e2749portable artifact-free;
lint/format/dependencies/native bootstrap/roundtrip pass. Fixture generate di
provenienza/timing sostituiscono Task0043 durante tutte le suite. Non è CI hosted.

Copertura:wrong status/task/scope/hash/schema/schedule/order/phase/count/celle,
warmup contamination, float/zero durations, duplicate JSON keys, path unsafe /
symlink/foreign/oversized e path raw/model embedded mai dereferenziati; cursor /
reset/ciclo/reverse/rotation/ceil; partial/full billing, completion condivisa, tie /
oldest timeout/capacity includendo active/final drain/horizon/overflow virtuale /
conservazione.30oracle a tick indipendenti e30fixture costanti coincidono esattamente
con il motore Task0037, toy counts inclusi. Timeline manuali verificano costi
variabili con attese/overflow calcolabili a mano. Record real producer serializzato
→outer verifier→freeze immutabile→exclusive claim→worker. Record/freezing/reaping
falliti bloccano programmaticamente il dispatch; il replay real-source richiede
anche il roundtrip completato. Output e assegnazioni vengono ricontrollati dal
parent indipendente.

Tre versioni di software hanno acceptance proprie e conservate:
178/185/188focused,2739/2746/2749full+portable. La versione finale aggiunge, fra
l'altro, guard pressione del parent, verifica indipendente dei receipt native,
gate del roundtrip completato, serializzazione CSV originale e hash-only metadata
storici dichiarati. I report delle versioni precedenti non sono riemessi come
accettazione corrente.

11invocazioni native totali:9fixture (7accepted,2failed) e2real-source
(1failed prima di scenari,1accepted). Le prime due fixture falliscono rispettivamente
per `/bin/ps` bloccato dal sandbox e per entrypoint figlio errato: l'entrypoint
Task0037 respinge il namespace prima di grant/letture/simulazione. Nessuna campagna
storica viene eseguita; i fallimenti, exit/reaping e assertion release sono conservati.
La prima real-source, `3e17b7ffb0d341c693fb121d76f6e7ad`, termina1.615295s con
exit1/reaped per assunzione errata JSON sulla colonnaCSV originale `7/7/6`.
184record/20timed derivati, zero trace/scenari; tutte le269vecchie sorgenti/config
sono ricostruite e byte verificate in `preserved-source/`. Il caso è diventato
regressione generata; nuove suite/acceptance precedono il secondo replay.

I sette replay fixture accettati più quello reale generano144richieste trace /
720,000istanze di eventi, sempre18hash/90,000eventi distinti;14,112scenari /
70,560,000presentazioni. Fixture separatamente12,348scenari/61,740,000presentazioni.
Il risultato curato contiene una sola matrice finale. Le tre invocazioni fallite
aggiungono zero scenari; letture timing del fallimento reale sono incluse sopra.

Regressioni storiche sintetiche full/portable fanno realmente attività di modelli
ed optimizer. Nei6processi full/portable strumentati, subset research:510istanze,
186forward/52,260righe,186ricostruzioni,12toy optimizer step completati e12toy
calibrazioni. Altri modelli legacy/subprocess non sono nel counter: nessun claim
model/optimizer globalmente zero. Nei nuovi replay operativi/fixture Task0044,
nessun modello è importato, istanziato o eseguito.

## Clock, risorse, normal lifecycle e release

Clock Mach continuo, con sospensione inclusa nei deadline. Tempi finali: prerequisite
1.096291s, simulationworker12.785279s (dispatch→reap12.812134s), reporter1.857965s
(dispatch→reap1.928128s), finalization0.422446s, whole16.548633s, overshoot0.
Cleanup0.000158/0.000099s inclusi. Exit0/reaped/within deadline per entrambi i figli;
controller stdlib-only. Assert idle-system temporaneo verificato in8osservazioni,
poi helperTERM/reaped/assenza confermata; display sleep permesso, nessun setting
persistente cambiato.

RSS sim62,881,792B/report159,186,944B/controller65,503,232B; native riservato
50,331,648B/104,415,232B/controller62,914,560B. Vettori19,408B, trace6,285,148B,
output owned11,714,442B all'accettazione. Budget30s prereq/120s sim fino reaping /
60s reporting/15s final/240s whole/2s cleanup interni;1GiBworkerRSS/512MiBnative /
128MiBparentRSS/64MiBjournal/1MiBlog/128MiBoutput/8MiBfonti/1MiBservizi/16MiBtrace
rispettati. I cap non erano una prova preventiva di fattibilità.

13,748letture primaryWARN advisory,0CRITICAL/invalid/unknown. Gap query massimi
0.055160s sim/0.068850s reporter/0.073616s parent; gap terminali dei worker
0.027876/0.083833s. Monitoraggio campionato, senza prova degli intervalli non
osservati. Contesto RAM opzionale unavailable perché i worker vietano subprocess;
nessun global floor, pressure loop o imposizione di chiudere app. Boundary worker
vieta rete/subprocess/modelli/array raw; reporter legge solo aggregate owned.
Le misure dei guard e il tempo wall del simulatore non sono nuove misure di
servizio fisico né una campagna operativa CPU.


Correzione export-only: CSV curate normalizzate CRLF→LF per il controllo Git,
tutti i campi confrontati identici agli originali owned. Budget separato60s,
nessun nuovo replay/lettura timing; originali e receipt rimangono immutati.

## Contatori effettivi e stato preservato

```yaml
original_test_background model/evaluation accessed: YES
original_test_signal model/evaluation accessed: YES
three_prong_signal model/evaluation accessed: YES
Task0043_status_preserved: parent_accepted_development_raw_decision_measurement
accepted_timing_JSONL_loads_records_timed_selected:
  successful_replay_and_parent: [6, 1104, 960]
  failed_source_before_scenarios: [1, 184, 20]
  total: [7, 1288, 980]
service_vectors_unique_values: [24, 480]
other_provenance_aggregate_timing_reads:
  native_observation_copies: 1120
  native_chronology_duration_copies: 1288
  native_cell_statistic_copies: 448
  native_CSV_statistic_conversions: 392
  native_summary_pooled_statistic_copies: 192
  direct_metadata_JSON_inspections: 16
  direct_observation_chronology_cell_pooled_copies: [160, 184, 64, 256]
synthetic_trace_generation_requests_unique_events:
  final_matrix: [18, 90000]
  accepted_native_total_requests_generated_instances_distinct_events: [144, 720000, 90000]
replay_scenarios_started_completed_event_presentations:
  final_matrix: [1764, 1764, 8820000]
  accepted_native_total: [14112, 14112, 70560000]
main_and_order_contrasts: [756, 252]
service_assignments_cycles_partial_batches:
  dispatches_original_constant: [1705396, 962026, 743370]
  nonconstant_complete_cycles_remainder: [47691, 8206]
  partial_batches_useful_charged_unused: [425677, 3347103, 11093600, 7746497]
  partial_service_busy_ns: 4246973707069
conservation_final_pending: passed_0
new_event_feature_membership_golden_scientific_score_fingerprint_loads: 0
new_raw_HDF_access_or_byte_hash_passes: 0
new_replay_model_instantiations_forward_reconstruction_calls: 0
new_operational_optimizer_calibration_scientific_evaluations: 0
new_physical_service_timing_measurements: 0
downloads: 0
replay_invocations_status:
  native_total: 11
  fixture_accepted_failed: [7, 2]
  real_source_accepted_failed_before_scenarios: [1, 1]
```

I480sono posizioni di campioni misurati originali, non necessariamente480durate
intere tutte numericamente diverse.7JSONL letti non sono7nuovi worker misurati;
980valori selezionati/derivati non sono980nuove osservazioni.962,026assegnazioni
sono riusi dei campioni nel replay.90,000eventi distinti generati sinteticamente
sono presentati più volte in milioni di casi, senza nuovi dati fisici/scientifici.

Task0043 accettata/consumata; Task0041 failed/consumed, Task0042 software-only,
Task0036 `unresolved_no_acquisition`. Gates scientifici, esposizione permanente
YES/YES/YES, precedenti fallimenti e particle192/192 consumati/canonical deferred
restano immutati. Le fonti di costo sono sparse windows HDF warm già misurate:
questo replay non ricrea dipendenze cache/load/decoder né prova streaming reale,
trasporto/backpressure, distribuzione di produzione o conferma scientifica.
Startup/drain/workload finito, survivor selection e billing parziale limitano i
confronti. Prossima decisione separata: eventuali servizi naturali parziali misurati
oppure un altro confine streaming/trasporto mancante. Nessuna Task0045 avviata.

## Riproducibilità e Git manuale

Per nuova validazione software (fixture generate, senza bundle reale numerico):
`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m scripts.validate_joint_service_replay`.
La real-source invocation completata è registrata nei file owned sopra; non viene
suggerito di ripeterla senza contabilizzare esplicitamente una nuova invocazione.
Snapshot/freeze/claim/receipts/fixture restano ignorati; curate solo aggregate e PNG.

La review finale verifica file/pin/fonti/output, coverage/conservazione, fonti
software correnti, esclusioni Git e link. L'indice resta vuoto. Comandi manuali
per il branch/upstream realmente verificati, senza esecuzione automatica:

```bash
git status --short
git diff --check
git diff d4b92e55e3f8e32eefd5186c303c1d15205bc090 --stat
git diff d4b92e55e3f8e32eefd5186c303c1d15205bc090
git add -- \
  README.md \
  docs/handoffs/README.md \
  docs/project-memory.md \
  docs/deterministic-joint-service-replay.md \
  docs/prompts/0044-deterministic-joint-service-replay.md \
  docs/handoffs/0044-deterministic-joint-service-replay.md \
  configs/simulation/joint_service_replay_v1.json \
  scripts/validate_joint_service_replay.py \
  src/latenttrigger/simulation/joint_admission.py \
  src/latenttrigger/simulation/joint_engine.py \
  src/latenttrigger/simulation/joint_fixture.py \
  src/latenttrigger/simulation/joint_native.py \
  src/latenttrigger/simulation/joint_protocol.py \
  src/latenttrigger/simulation/joint_reporting.py \
  src/latenttrigger/simulation/joint_runtime.py \
  src/latenttrigger/simulation/joint_source.py \
  src/latenttrigger/simulation/joint_sweep.py \
  tests/test_joint_service_replay.py \
  results/tables/final/task0044-joint-service-replay-scenarios.csv \
  results/tables/final/task0044-joint-service-replay-contrasts.csv \
  results/tables/final/task0044-joint-service-replay-summary.json \
  results/figures/final/task0044-joint-service-replay-outcomes.png \
  results/figures/final/task0044-joint-service-replay-latency.png \
  results/figures/final/task0044-joint-service-replay-sensitivity.png
git diff --cached --check
git diff --cached --stat
git diff --cached
git status --short
git commit -m "feat(simulation): add deterministic joint-service queue replay"
git push origin main
```
