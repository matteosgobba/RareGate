# Task0046 — Occupancy-Aware Paired Service Replay

## Metadata e stato

2026-10-14 Europe/Rome, Task0046 soltanto. Stato effettivo
**parent_accepted_synthetic_occupancy_service_replay**, unica source allowance
accettata/consumata, sessione `78a96792b4b04f809e0e0c7717a7b02d`.
Git iniziale pulito main/origin/main, indice vuoto; base effettiva
`4658fc4d59f3fce892f6897c7f36b85f00f21566`. La planning baseline92a628d è il
commit Task0045;4658fc4 aggiunge la riparazione CI/PCA roundtrip già committata.
Entrambi sono preservati; a8094adc resta la base storica di Task0045.
Memoria verificata1.40, ora1.41. Python3.12/macOS Apple Silicon/.venv esistente;
nessuna installazione/aggiornamento, commit/push o hosted CI.

## Obiettivo e autorizzazione

Il [prompt effettivo](../prompts/0046-occupancy-aware-service-replay.md), salvato
prima dell'implementazione, autorizza un replay model-free e una sola sessione
condizionale di timing metadata dopo nuova validazione/roundtrip/freeze.
Arrivi, eventi, toy scores e queue sono sintetici. Nessuna nuova misura fisica,
accesso numerico raw/ID/golden/features/score/fingerprint, HDF, modello, inference,
reconstruction, optimizer/calibrazione/scienza/download/device/transport o Task0047.
I nuovi moduli hanno owner/task0046; nessun grant/budget/globals storico è ampliato.

Task0045accepted/consumed,351coppie sfavorevoli e tre fallimenti fixture preservati;
la verifica tardiva di assenza non riscrive il suo failed cleanup da sospensione.
Task0043accepted/consumed, Task0044accepted replay con source-loader failure,
Task0041failed/consumed, Task0042software-only, Task0036unresolved,
Task0034gates scientifici, Task0025failure, particle192/192/canonical deferred e
permanentYES/YES/YES rimangono invariati. Il replay corrente non azzera il lavoro
raw/features/frozen inference/reconstruction/decision positivo di Task0045.

## Implementazione e decisioni tecniche

Nove helper additivi `src/latenttrigger/simulation/occupancy_*.py`, config chiusa
`configs/simulation/occupancy_service_replay_v1.json`, test dedicato e validator
`scripts/validate_occupancy_service_replay.py`. Protocol/provider di assegnazione,
source reader, fixture writer, engine, sweep, reporting, runtime, admission e
controller separati; riuso soltanto di helper puri/guard compatibili invariati.
Gli engine Task0037/0044 e i file storici sono byte preservati.

Il bundle operativo contiene esattamente23file/6489729B: cinque curati/config/
prompt, attempt0045, plan/workflow/parent/reportingreceipt/reportingsummary,
receipt/aggregate/timings/timer per tre ripetizioni. Tutti23SHA/size sono chiusi
prospetticamente; path relativi safe/no symlink, JSON duplicati/nonfiniti vietati,
CSV/JSONL schema/coperture/ordine/copie esatti. I path raw/model/source_map restano
stringhe inerti, senza dereferenziazione. Loader stdlib-only, nessun adapter fisico.

Identità originale0045/owner/scope/packing/paired-contract/config/prompt, modelli/
input come hash string, campaign reale consumata, parità completa e linkparent
sono verificati. Receipt digest/output digest, exit0/reaping/noovershoot/deadline/
release necessari: body_complete non basta. Owned summary
aggregate_report_body_complete e curated summary parentaccepted hanno hash diversi;
si confrontano esplicitamente timing/count/parity/pooled/paired condivisi e link
workflow/parent, non interi documenti o geometry come input di costo.

180celle/1800pairs/3600durate temporizzate originali riconciliate con aggregate
observations/pairs e4140chronological timed+warm side records.540warm durate escluse.
90vettori separati `(candidate,repetition,B,k)` ×20coppie ordered; originalpair IDs,
ordine natural-first/control-first, finestre7/7/6 e shape/service_B preservati.
Tutti valori lenti/sfavorevoli rimangono, niente pool/trim/clamp/fit/interpolazione.
Statistiche: finite/type/exact integers e32ULP solo serializzazione binary64;
reference stdlib riproduce linear rank e two-branch lerp del writer, testato
separatamente contro NumPy, senza modificare costi o tolleranze scientifiche.

Anchors B1{1}, B8{1,2,7,8}, B32{1,2,8,31,32}, B128{1,2,32,127,128}.
Next sceglie min k≥m; previous max k≤m. Natural usa natural_k; control usa il suo
full-B contemporaneo dallo stesso vector/k. Ogni variante completa m eventi
sintetici, senza produrre k/B eventi aggiuntivi. Per32/8 naturalservice_B8;
128/32 naturalservice_B32; altri casi service_B=B, control sempreB. Questi argomenti
non cambiano B nominale/policy/window. k≠m è ipotesi di lavoro non misurato;
previous può sottocontare righe. Nessun upper/lower bound empirico o monotonia.

Ogni scenario riparte con cursori zero indipendenti peranchor; una sola scelta
pair[cursor[k]%20] perdispatch, poi avanzamento del solo k. Arrivi/completion/
decision/idle/audit non avanzano. Fase zero comune e cicli20 sono artificiali;
source pairing a lookup non implica stessi jobs/survivors/occupancies/cursors fra
queue divergenti. B1 mapping negative control esatto; m=B natural/control conserva
noise finito, non viene imposto delta0.

FIFO nonpreemptive/capacity1024 waiting+active/drop-tail; ties completion→source
arrivals→dispatch, timeout da oldest original arrival, full immediato da idle,
final drain completo. Integer-ns positive durations/additions controllate.
Latency=dispatchwait+service assegnato; busy=sum exact duration assignments.
Toy decision strict .9/.95/.99/.999 soltanto dopo completion; late strict>100ms.
GeneratorPCG64/SeedSequence originale [3700,seed,mode_id,rate,stream_id], stream
score separato; ceil gap originale.18traces5000eventi periodic/Poisson ×rate500/
2500/5000 ×seed41/42/43, generate una volta e riusate fra tutte le varianti.
2candidate×7policy×3source repetitions×4varianti=3024scenari;90kunique synthetic
positions e15.12Mpresentations. Source repetitions e seeds sono fattori distinti.

CSV occupancy streamed peractualm con k/exact-vs-mapped/counts/useful/busy/righe
modellate e signed k−m/row differences. Control modeledworkB, naturalk, capacity
m. Colonne nominalBslots ereditate sono descrittori batching, non padding o lavoro
naturalk.12528anchorrows comprendono zero categories/20counts/wrap/remainder/
unused/fingerprints; duration dotproducts ricostruiscono busy. Bounds145584occupancy
rows/12528anchors, actual18629/12528. Nessun event/dispatch/latency export.

## Risultati effettivi

[Report](../occupancy-aware-service-replay.md), [summary](../../results/tables/final/task0046-occupancy-service-replay-summary.json),
[scenari](../../results/tables/final/task0046-occupancy-service-replay-scenarios.csv),
[contrasti](../../results/tables/final/task0046-occupancy-service-replay-contrasts.csv),
[occupanze](../../results/tables/final/task0046-occupancy-service-replay-occupancies.csv),
[anchor audit](../../results/tables/final/task0046-occupancy-service-replay-anchor-audit.csv).
3024started/completed,15120000requested/completed presentations,3981226dispatch
sampleassignments; generated=13761044completed+1358956overflow,admitted=completed,
finalpending0;3166580late survivors.2268contrasti:756next natural−control,
756previous natural−control,756interaction previousdiff−nextdiff, con previous−next
levels/allfour denominatori. Tutti90vettori e tutti20pairindices usati in almeno
un contesto; inutilizzati nei singoli scenari sono espliciti.

Ogni riga somma756contesti/3780000repeated eventpresentations, non indipendenti.

| Mapping / billing | Completed | Overflow | Late | Mapped batches | Mapped useful events | Mapped busy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| next natural | 3392514 | 387486 | 923236 | 10.0777% | 26.4173% | 44.1412% |
| next control | 3394551 | 385449 | 884926 | 13.4359% | 32.9507% | 56.9710% |
| previous natural | 3579492 | 200508 | 474904 | 22.8193% | 51.5299% | 31.3287% |
| previous control | 3394487 | 385513 | 883514 | 13.3117% | 32.7304% | 56.5879% |

Main next natural−control: **+2037overflow/+38310late**, outcome fraction aggregata
+1.067381pp; costo busy complessivo più basso non implica miglior outcome. Nei756
contrasti overflow−181…+146,90negative/138positive/528zero; overflow-or-late/generated
−33.92…+59.70pp,253negative/174positive/329zero. Survivor p99−119.254…+123.557ms,
432negative/324positive. Sono preservati tutti peggioramenti.

Previous natural−control:−185005overflow/−408610late, outcomeaggregato−15.704101pp;
individual outcome−98.30…+58.94pp, p99−500.976…+123.557ms. Questa ipotesi natural
modella2497839righe contro3579492eventi utili: **−1081653righe**. Nextnatural
modella4623512contro3392514utili: **+1230998righe**. Non sono righe fisicamente
eseguite; la sottocontabilizzazione previous è parte dell'ipotesi, non prova di
un beneficio naturale reale. Control modeledwork7143365/7120053, differenze utili
+3748814/+3725566; signedanchor−actual +483971/−784177 separato.

Interaction outcome−97.20…+15.92pp,43positive/267negative/446zero; p99
−473.696…+12.591ms,40positive/501negative/215zero. Lo spread di due mapping scelti
non deve coprire la realtà. Le subgroup mapped/exact hanno storie diverse e non
sono counterfactual; survivor p99 cambia anche per popolazioni overflow diverse.
Nessun percentile mediato, causal effect, CI/pvalue o policy selezionata.

Tre figure accettate e visivamente ispezionate leggibili, units/denominatori/
symlog .01pp/.01ms e tutti seed/reps/null/unfavorable: outcomes, survivor latency,
reliance. Reliance panels: nextnatural/previousnatural/nextcontrol espliciti;
quattro varianti complete nei CSV/table. Nessun rerun perplotting/layout.

## Validazione finale e fallimenti preservati

Record finale `data/task0046-validation/f95ee267926f4f8697c52dd7d07ca092/software-acceptance.json`:
167focused,3071full,3071portable artifact-free; lint/format/pip-check pass.
294source/config/prompt bindings,43installed packages,36native/metadata filepins;
final source snapshot ignored. Bootstrapgenerated32.183913s e admitted emitted-record
roundtrip34.100509s con sidecar noncircolare passano prima del freeze reale.
Producer/outer/schema/freeze/claim/controller/worker/exit sono testati insieme,
con verifiche indipendenti; nessun unconditional-success admission mock.

Sei native fixture invocations: zero-scenario duplicate exclusive source-audit
failure, primo full accepted32.850989s, validationv1bootstrap accepted33.569526s,
v1roundtrip failed9.422317s perparent scan/temp replacement race, poi i due finali
accepted. Nessuno è una source session reale. v1roundtrip conserva723started/
722completed cases,3615000started/3610000completed presentations,1202853assignments
nei casi completati; current scenario inflight/assignments/completions unknown.
Exit−15/supervised termination/reaped, nessun receipt worker finale, assertion
released/reaped/absent; non viene chiamato exit normale o matrix complete.
Failed worker sampled peak78610432B/native46137344B, parent63668224B/33554432B;
primo failed peaks55590912/55951360B e37748736B native, journals/receipts preservati.

Correzioni finali: audit già durevole non risalvato exclusive; storage usa lstat
singolo e ammette soltanto scomparsa di owned JSON atomictemp, con regressiontest;
contrasti parent verificati streamed per mantenere envelope, occupancy verification
mantiene soltanto current group/order. Native acceptance non è mockata.
Preparatory signedp99 serializer rejection252ULP preservata; formula binaria del
writer riprodotta senza toccare costi/tolleranza. Iterazioni unit/lint documentate
nel factual failure index ignored, distinto dall'originale stdout dei check.

Due software versions eseguono full/portable in copie senza data/artifacts/models/
checkpoints operativi; quattro research subsets strumentati:340toy model instances,
124forwards/reconstructions34840rows,8optimizersteps started/completed,0inflight,
8synthetic calibrations. Altri legacyfixtures fuori da quei contatori: nessun
claim globale-zero. I nuovi reader/engine/sweep/native occupancy hanno0modelli/
optimizer. Quattro acceptedfixture matrices60.48Mpresentations, più partialv1
come sopra;18traces generate per cinque fixture sweeps che hanno iniziato tracce,
90generationrequests/450k repeatedpositions, stessi90kuniquetracepositions.
Piccoli toy/generator test sono separati, non nuovi eventi acquisiti.

## Accessi metadata e attività operativa

Preparazione:3closed23bundle loads,69opens/19469187B,9JSONL byteopens/12420lines.
Initial schema inspection parses6JSONLrecords e tutte le aggregate copies; due
full schema validations parse8280records. Una fallisce statistic serialization;
non inizia allowance. Successiva validazione accetta90vettori; finale softwareusa
soltanto fixture generate, nessun timingoperativo come testfixture.

Sessione: precheck full23, worker full23, final bytecustody23 =69opens/19469187B.
Primi due:6semantic JSONLloads/8280records (7200timed/1080warm presentations).
Ultimo:3JSONL hash-only opens,0parsedrecords/0nuovivettori. Ogni semantic load
confronta14400timed durationcopies (aggchronology,cellobservations,aggpairs,curated
pairs) +540warmchronologicalcopies. Originali3600timings,1800pairs,90vectors
restano unici,3981226lookupreuse non aggiunge misure. Code/docs/packages bytechecks,
metadatafixture e curationowned-only sono contabilizzazioni distinte dal bundle.

Session tracegeneration18requests/90000positions; stessi18traces/hashes riusati
3024volte nella matrice,15120000presentations. Reporting non riapre timing sources,
non rigenera tracce/scenari/modelli. Curation copia soltanto output accettati e
legge ownedaggregates/receipts. EventIDs/raw/particle/features/scores/masks non
sono esportati; niente dettagli event/dispatch/latency. Logs/receipts/claims/plans/
source maps/sequence arrays restano ignored, curati solo aggregate engineering.

Nuovi operational raw/event/membership/golden/features/scientific-score/event-
fingerprintpayload loads, model/inference/reconstruction/optimizer/scaler/
calibration/scientific metrics/HDF/rawhash/download/device/transport/physical
measurement sono0. Non significa0lavoro storico o fixture e non cancella YES3.

## Risorse, clock, lifecycle e limiti

Caps: prereq30s/sim120s/report60s/final15s/whole240s/cleanup2s dentroworker caps;
RSS1GiB/native512MiB/controller128MiB/source8MiB/lookup1MiB/traces16MiB,
latencies≤5000/currentcase/output128MiB/journals64MiB/log1MiB. Whole35.930375s,
prereq1.626991s, simdispatch→reap30.324291s/report2.874879s/final.465359s,
overshoot0; due exit0/reaped/within deadlines. Cleanup.000090/.000110s.

RSS peak222838784B/native150667264B, controller108216320B; parentnative79495168B,
parent+un serialworker sampled-upper230162432B, nonunique/simultaneous/global RAM.
Owned storage36406677B; lookup+currentmargin722834B, tracecontainers6285148B,
aggregatecontainers54318194B. BoundcurrentPythonworkspace4MiB deriva da tre liste
≤5000, FIFO≤1024,128bins/100anchor-index counts e sorted/temporary margine; parsed
source64MiB conservativo separato da8MiBpayload. Source parsing è liberato prima
degli aggregate; quantili/latencies rilasciati percase. Bounds separati dalle
sampleRSS/native reservations; nessun global RAM floor o cache purge/appclosure.

Continuous clock comprende sospensione e supervisionaexit indipendentemente
dalle query.12assertion active observations, release/reap/absence prima parent
acceptance; display sleep permesso/no persistentsettings. Sim/report primary
NORMAL27642/44, parent1233;WARN/CRITICAL/invalid0 qui. WARN resta advisory,
critical/invalidveto. Max query-start gaps.112593/.116076/parent.202091s;
terminalgaps.048777/.082212s. Workeroptionalcontext unavailable perchésubprocesses
vietati, parentoptional nonosservato: non gap-free monitoring. Freshprocess/owned
thread cleanup e state/resource closure verificati prima accettazione.

I costi sono finite warm-window paired observations trasportate mediante ipotesi
sparse e cicli artificiali. Non misurediogni m, coldI/O/partial-onlycachehistory,
decoder/model causality, physical latency/bound/distribution/productionp99, arrivals
reali/transport/signal confirmation. Runtime35.93s è simulazione. Task0044 usa
Task0043 e contratto diverso, non si sottraggono campagne né si riscrive0044.

## Prossima decisione e riproducibilità

Allowance consumed: non rilanciare source controller/validator come rinnovo.
Freeze/config/prompt/code/build/evidence restano hashbound; altri run richiedono
scope/autorizzazione separati. La prossima decisione può delimitare le mancanti
occupanze fisiche o streaming/transport; questi mapping non definiscono una policy
né confermano sorgente scientifica. Nessun Task0047 automatico.
README/index/memory1.41 aggiornati;592baseline tracked identities conservate salvo
soli tre livingfiles. Git manuale sotto, nessun staging/commit/push effettuato.

## Git manuale — non eseguito

Da main con upstreamorigin/main verificati. Review dei nuovi file prima dello stage,
poi soltanto questi artefatti curati; evitare namespace ignorati/evidence/arrays.

```bash
git status --short
git diff --check
git diff --stat
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git diff --no-index -- /dev/null src/latenttrigger/simulation/occupancy_engine.py

git add -- README.md docs/project-memory.md docs/handoffs/README.md \
  docs/prompts/0046-occupancy-aware-service-replay.md \
  docs/handoffs/0046-occupancy-aware-service-replay.md \
  docs/occupancy-aware-service-replay.md \
  configs/simulation/occupancy_service_replay_v1.json \
  scripts/validate_occupancy_service_replay.py \
  tests/test_occupancy_service_replay.py \
  src/latenttrigger/simulation/occupancy_admission.py \
  src/latenttrigger/simulation/occupancy_engine.py \
  src/latenttrigger/simulation/occupancy_fixture.py \
  src/latenttrigger/simulation/occupancy_native.py \
  src/latenttrigger/simulation/occupancy_protocol.py \
  src/latenttrigger/simulation/occupancy_reporting.py \
  src/latenttrigger/simulation/occupancy_runtime.py \
  src/latenttrigger/simulation/occupancy_source.py \
  src/latenttrigger/simulation/occupancy_sweep.py \
  results/tables/final/task0046-occupancy-service-replay-scenarios.csv \
  results/tables/final/task0046-occupancy-service-replay-contrasts.csv \
  results/tables/final/task0046-occupancy-service-replay-occupancies.csv \
  results/tables/final/task0046-occupancy-service-replay-anchor-audit.csv \
  results/tables/final/task0046-occupancy-service-replay-summary.json \
  results/figures/final/task0046-occupancy-service-replay-outcomes.png \
  results/figures/final/task0046-occupancy-service-replay-latency.png \
  results/figures/final/task0046-occupancy-service-replay-sensitivity.png
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "feat(simulation): add occupancy-aware paired service replay"
git push origin main
```
