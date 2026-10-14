# Task0047 — Targeted Partial-Occupancy Raw-to-Decision Measurement

## Stato e baseline verificata

2026-10-14 Europe/Rome, Task0047 soltanto. Unica campagna fisica
**parent_accepted_targeted_partial_raw_decision_measurement**, allowance propria
accettata/consumata, sessione `4b1ae2522d114b47a56a89abccd9918d`.
Git iniziale pulito main/origin/main, indice vuoto, HEAD effettivo
`afe11155cebfd7134b7d8963546e71c00d882608`, Task0046 committato; memoria1.41→1.42.
Nessuno staging/commit/push/hosted CI o install/update. La baseline615file tracciati
è salvata ignored; soltanto README/memory/index viventi vengono aggiornati.
Il prompt allegato effettivo è salvato integralmente prima di implementare;
l'handoff iniziale è preservato ignored prima di completare questo documento.

Il commit4658fc4 è stato ispezionato: rende contigue le componenti PCA durante il
fit prima della serializzazione. Il percorso di ricostruzione/score da artifact
caricato resta invariato. Task0047 non fitta PCA e carica l'originale congelato.
Si vincolano codice/build correnti; vecchie acceptance maps restano documenti
storici immutabili, senza pretendere che mappe superate diventino live acceptance.
Le basi4658fc4/92a628d/a8094adc e quelle precedenti restano storiche.

## Autorizzazione, implementazione e storia preservata

Il [prompt effettivo](../prompts/0047-targeted-partial-raw-decision-measurement.md)
autorizza una nuova campagna development-only dopo final-source software/native
acceptance, roundtrip del record emesso e freeze immutabile. Sono ammessi soltanto
originali membership/golden/raw selections, features congelate, modelli/threshold
CPU originali e decisioni nei budget fissati. Claim proprio0047 prima dei
prerequisiti fisici; ogni fallimento consuma, nessun retry/cambio grid/diagnostica.

Tredici helper additivi `targeted_raw_*` coprono planner/provider/wrapper/custody/
selection e fixture/std-parent/admission/worker/reporting/runtime; config chiusa
`development_targeted_raw_decision_v1.json`, validator dedicato e cinque file di
test. Vecchie CASES, packing, config, owner, grants, globals/budget e namespace
operativi non vengono ampliati. Il nuovo wrapper è parte del nuovo confine
misurato: i vecchi timing Task0045 non diventano intercambiabili con questi.

Task0046accepted/consumed con fallimenti e ipotesi next/previous preservati;
Task0045accepted/consumed con351coppie sfavorevoli e tre nativefixture failures;
la successiva assenza dell'assertion0045 non riscrive il suo failed cleanup da
sospensione. Task0043accepted/consumed, Task0044accepted replay e source-loader
failure, Task0041failed/consumed, Task0042software-only, Task0036unresolved,
Task0034gates scientifici, Task0025failure e particle192/192/canonical deferred
restano invariati. Exposure permanente **YES/YES/YES**, nessun reblinding.

## Selezione esplorativa e copertura residua

Bundle chiuso Task0046:10file/5382736B≤8MiB, tutti SHA/size prospetticamente fissi:
config/prompt/curatedsummary/scenarios/occupancies e plan/workflow/parent/receipt
simulation+reporting della sessione78a96792. Reader stdlib-only: paths relativi
safe/no componenti symlink, JSON duplicati/nonfiniti vietati, CSV con serialization/
newline originali e roundtrip LF/CRLF testato, contesti3024 e occupancies18629
riconciliati. Task/owner0046/scope/assignment-contract/config/prompt/consumed/parent,
receipt/output digests/zeroexit/reaping/deadline/release obbligatori. Embedded
source/event/model paths inerti, nessun traversal ricorsivo o engine0046 chiamato.

Ranking soltanto next_anchor/natural_anchor: aggregazione dispatch perB/m sull'intero
grid storico, esclusione15exact anchors, count decrescente poi m crescente. Nuovi:
B8m3/4/5/6; B32m3/4/5/6/7; B128m3…10. Si rimisurano tutti15references0045.
Grid corrente32casi: B1{1}, B8{1…8}, B32{1…8,31,32}, B128{1…10,32,127,128}.
Nessuna selezione adattata ai nuovi tempi. È selezione ingegneristica informata
ex post da replay sintetico, non conferma indipendente o distribuzione produzione.

Nuovi punti coprono99405/109080missing dispatches=91.1304%,556462/896210associated
completed events=62.0906%,677757505837/860108214675assigned ns=78.7991% nel main
storico. Busy coverage usa costi assegnati ipotetici. Rimangono137/169combinazioni
non misurate, incluse quelle con frequenza zero nel vecchio replay; zero frequenza
non equivale a servizio misurato. SelectionCSV169righe conserva rank/ref/new/residual,
counts/coperture e fingerprint immutabile del bundle metadata, senza eventIDs.

## Catena fisica, wrapper, ordine e parità

Tre worker freschi caricano ciascuno una volta original6999IDs int64<littleC>,
verificano dominio/unicità/sortedfirst1024/payloadSHA f80a9483 e una volta golden
originalFP32C[1024,8] con file/payloadSHA. Approved1024unique, rawunion384unique,
stessa di0043/0045. Split/dev manifests/transform scientific identity/preparation
Task0020successful sono vincolati; Task0020complessivo resta failed.

Per B, starts0/floor((1024−B)/2)/1024−B. Natural legge esattamente ID[p:p+m],
controlID[p:p+B], ognuno con propria selezione HDF, senza recenter con m, leggere
contigui raw arbitrari, slicing del fullbuffer o preload. Truth2100 verifica
background e resta fuori features. FP64 sort/wrap prima physicalFP32, aggregati
FP64 su tutti validparticles prima384truncation, frozenmass/log/scaler→FP32:
nessuna seconda standardizzazione, ProcessedStore o scaler construction.

Nuova identity `task0047_owned_C_FP32_actual_rows_public_score_strict4_copies_v1`:
validazione32grid/side/actualshape, bufferownedC FP32(actual,8), copia tutte righe
reali, unchanged publicmodel.score una volta, original4strict>threshold e copie
owned score/masks. Natural modelshape=m, control=B. Nessun argomento storico
service_B inventato per nuove forme, padding/dummy/splitting/kernel/tolerancechange.
Fixture: exact parity historical15case×2sides con service_Boriginali(quarter8/32),
independent public-score+explicitstrict4 oracle same-shape per17newcases. Ownership,
shape/single-call/strict-equality/full-extra-rows/denial beforeeffects testati.

PCA6componentFP64, AE155parameterFP32CPUv2/eval/inference, originaleightordered
channels, publicSSEFP64 e quattrostrict>threshold invariati. Sei originali model/
threshold instances/loadsets totali; nessun fit/optimizer/calibrazione/backendchange.
Same-shaped golden service, duechainrepeats, pre/post reference/feature/golden/
score/decisionbytes e input/parameters/thresholdhashes tutti esatti.2304sidegate
records1152pairedcontexts, mismatch[0,0,0] ovunque. Non si impone score identity
fra natural/full di diversa forma; niente extra diagnostic forward reale.

Worker1/3PCA→AE e32casesascendenti; worker2AE→PCA ecompleta lista inversa.
Percandidate/case3warmpairs poi20timed; resetwindow/sideorder perphase, windowi%3,
evennatural-first/oddcontrol-first. Warm1/1/1, timed7/7/6, order10/10. Gates pre/post
sempre ascendingcases/windows/sides. Timercheckedread→features→pack→publicscore/
strict4/copies; loads/windowprepare/hashes/reference/accounting/explicitqueries/
aftertimerchecks fuori. Feature calcolate trattenute perparità, senza ricomputo.
Integerns sincroni, timerimplementation/resolution registrati primadel timing,
independent continuous stamps e chronologies/warm durations conservati ignored.

## Risultati misurati correnti

[Report](../targeted-partial-raw-decision-measurement.md),
[selection](../../results/tables/final/task0047-targeted-partial-selection.csv),
[cells](../../results/tables/final/task0047-targeted-partial-raw-decision-cells.csv),
[pairs](../../results/tables/final/task0047-targeted-partial-raw-decision-pairs.csv),
[summary](../../results/tables/final/task0047-targeted-partial-raw-decision-summary.json).
384cells×20observazioni/192groups×20pairs,3840timedpairs/7680timedcalls. PairCSV
conserva entrambe20durate percell e tutte3840differenze/ratio; ownedaggregates
conservano listeordinate. Pool soltanto60osservazioni currentcandidate/B/m/side,
populationSD/linear p50p95p99 da actualvalues, nessun percentile mediato.

Medie di costo e medie dei60matched ratios per candidate/B/m; ratio.mean non è
ratioofmeans. Nessun costo pooled fra occupanze/candidate diverse.

| B/m | Classe | PCA natural/control ms | PCA ratio | AE natural/control ms | AE ratio |
| --- | --- | ---: | ---: | ---: | ---: |
| 8/3 | nuovo | 1.261/3.229 | .3888 | 1.277/3.194 | .3988 |
| 8/6 | nuovo | 2.600/3.319 | .7785 | 2.480/3.247 | .7658 |
| 32/3 | nuovo | 1.315/12.154 | .1077 | 1.297/11.988 | .1080 |
| 32/7 | nuovo | 2.884/12.218 | .2357 | 2.846/12.031 | .2364 |
| 128/3 | nuovo | 1.531/49.472 | .0309 | 1.560/48.096 | .0324 |
| 128/10 | nuovo | 4.455/49.077 | .0909 | 4.556/50.594 | .0907 |
| 128/32 | rimisurato | 12.792/48.889 | .2612 | 13.229/49.933 | .2649 |
| 128/128 | rimisurato/null | 48.611/48.722 | .9990 | 52.015/50.050 | 1.0170 |

333sfavorevoli natural−control>0,3507negative,0equal;332references/1new. Unico new
sfavorevole: worker3/PCA/B8m6/pair14/naturalfirst8.100041vs4.170292ms,
+3.929749ms/ratio1.942320. Null480pairs231positive249negative, senza equal-time
constraint. Extreme observed differences−104.921667…+113.213792ms e maximumside
226.994042ms conservati; sono extrema/counts, non distribuzione pooled o bound.
B1equalintended: meanpairedratio1.74095PCA/1.65901AE anche con side means quasi
uguali, effetti finiti di ordine/host. Nessuna attribuzione causale a componenti.
Tre figure reali e quelle fixture ispezionate leggibili, tuttiworker/order/units,
null/unfavorable, no interpolatedcurve. Nessun rerun/replotting fisico richiesto.

## Contatori effettivi, distinti dai piani e dalle righe uniche

Tutti requests/started/returned/completed coincidono; nessun inflight finale:

| Componente | Calls | Row presentations |
| --- | ---: | ---: |
| Timedcomplete chains | 7680 | 303240 |
| Warmcomplete chains | 1152 | 45486 |
| Pre/post chain repeats | 4608 | 181944 |
| Rawreads/features/chainservices ciascuno | 13440 | 530670 |
| Golden-only references | 2304 | 90972 |
| All publicservices | 15744 | 621642 |

Perworker4480reads/constructions176890rows,768refs30324rows,5248services207214rows;
percandidate7872services310821rows, AE7872forwards/reconstructions ePCA7872
reconstructions separati. Decisionvalues2486568Booleans. I ledger conservano
side/case/candidate/component intent e nestedactualfacts, non solo totals.

3membershiploads20997records inspected/3072selected presentations,3goldenloads
3072rows,6999originalmembershipsourceIDs/1024approvedunique/384rawunique.
6originalmodelinstances+6thresholdsets,3HDFopens/closes/6samehandlechecks,
2rawSHApasses5816520818B, hashprima/dopo5da8fda2 identico. Raw2908260409B,
original1100000×2101FP64/chunks62×2101/Blosc32001/schema/hardlink ecache1MiB/
521/.75 verificati sullo stesso readonlyhandle perworker attraversobothcandidates.
Nessun quartohandlemetadata, MD5pass/copy/numericscan, preload/dummyrows.

Preparazione selection:2closedloads20opens10765472B, primo byte/hash-only, secondo
semantic3024scenarios18629occupancies. Sessionpre10opens5382736B semantic e final
10opens5382736B byte-only, final0CSVrows parsed. Bytepreservation Git ecode/docs/
configinspections separati; nessuna riapertura selectionsource dal reporting.
Physical reporting/curation usa soltanto ownedaggregates/receipts/outputs, senza
array/model/originaltimingloads. OriginalTask0045timings non vengono aggiunti al
nuovo matrix. Geometry da13440readplan:312distinctchunks e451886172672B
repeated no-cache decodeupper, non I/O/decompression/cachemiss misurati.

Nuovi operationaloptimizer/scaler/calibration/scientificmetrics/eventfingerprint/
held-out/download/device/transport/queue-replay sono0. Raw/features/frozenCPU
inference/reconstruction/decision sono lavoro positivo autorizzato, non zero.
Nessun eventID/raw/particle/features/score/mask export; solo aggregate engineering.
Sequenze/grants/ledgers/hashesintegrity/snapshots/claims/logs restano ignored.

## Fresh acceptance e fallimenti software

Record finale `data/task0047-validation/c754adabdcb243968fcec137ce85d501/software-acceptance.json`,
332source/config/promptbindings,43packages,41nativebinary/metadata pins NumPy/HDF/
Blosc/TorchCPU ecanonicalJSONstringTorchbuildSHA6d6fa299.297focused,3368full+
3368portable artifact-free, lint/format/pipcheck pass. Full+portable regressioni
CPU-portate/strumentate in copiedroot privo operationaldata/artifacts. Bootstrap
146.179467s, emitted-record actualadmittednative roundtrip152.154486s, noncircular
sidecar: tutti384cells/gates/counters/reporting/exit/reap/release prima operational
freeze. Producer→serializedstrictouter→freeze/claim→controller→worker/exit e
independentbindings testati, niente unconditional-success admission mock.

Fallimenti preservati ignored: initialdirectpytest2collectionerrors/0tests; copied
fixturestatus18failed171passed; copiedscopeassertion1failed295passed; final-v1
resourcefixture1failed296passed. Final-v1 si ferma a focused, no full/native/
operationalfreeze. La fixture viene resa esplicitamente sintetica mentre ilvero
controller mantiene ilguard anticipato prima della custodia. Tutti riparati prima
claimfisico;0nativefixturefailures nuovi,0physicalfailures,1campagna consumata.
Curationowned-only elimina crosscasecostmeans dal draft nonpubblicato, preservato
ignored: restano categorycounts/extrema e costdistributions percase. Nessun codice,
sourcecost o measurement viene riparato dopo ilclaim. Vecchi fallimenti restano.

2actualnativefixture integrations:31488publicservices1243284rows,26880governed
raw/feature calls1061340rows,48setupcalls6144rows,12creator+12loadedmodels,
12thresholdloads,6HDFwrite/12HDFreadhandles generated. Sei dedicatedpublicmodel
fixture suites1536scores60648rows/12creator+12loadedmodels; sixcompleteToyworker
plans31488toypubliccalls1243284rows, subsetesclusialtridirectToytests. Twolegacy
instrumentedsubsets170models62forwards/reconstructions17420rows4optimizersteps
started/completed/0inflight e4syntheticcalibrations. Altri historicalfixtures fuori
daquesticontatori: nessun globalzero di modelli/optimizer/forward. Repeated fixture
work non aggiunge eventi acquisiti o nuove misure scientifiche.

## Clock, resources, lifecycle e limiti

Whole320.220989s/reserved316.507656s, prereq3.810659s/postraw1.302670s/final2.173606s.
Dispatch→normalexit/reap97.252629/97.289772/99.083146/report11.797523s, cap180/60;
cleanup≤.000371s dentrocaps, overshoot0. Wholecap780/reserved720/pre60/post45/
final15/cleanup2 immutati. Oneprerequisiteclaim/onephysicalexecution, nessun retry.

RSSpeaks372293632/378847232/336986112/report152616960B, maxnative203276288B;
controller114425856B/native69386240B, caps1GiB/512MiB/128MiB. Conservativeparent+
oneserialworker nativeupper272662528B, non globalRAMfloor/simultaneouspeak.
Ownednumericalbound56202376B<64MiB, reference/request/window/golden/ID344200B;
24×128×700×3FP64scratch+raw+2MiBmargin, no retainedrawbuffers. DerivedPythonenvelope
32MiB/worker for2944chronology/768gates/1280pairs/128cells/384referencehashes,
report48MiBparsed+16MiBsummary+256MiBplotenvelope, separate dalle arrays/sampleRSS.
Selectionpayload8MiB/parsed48MiB (prepobserved21056476B) separati e liberati prima
dispatch. Ownedstorage60127622B<128MiB, workerjournals13010678/13013749/13030209B
<16MiB, session47161270B<64MiB; logs<1MiB. Growthchecks primaappend econtinuous
storagechecks, conservative64KiBguardheadroom. Nessuncap aumentato.

Continuousclockinclude suspension, independentdeadline/exit supervision.65active
ownedidle-sleepassertionobservations, released/reaped/absent prima acceptance;
displaysleep permesso, no persistentsettings/purge/appclosure/globalRAMreserve.
Worker/reportWARN21279,parentWARN16958;critical/invalid0. WARNadvisory, costi
condizionati a questo contesto host. Query-startgapmax.124929/.087107/.094395/
report.119805/parent.088607s; terminalresourcegaps.305962/.348168/.300728/report
.075569s. Optionalcontext unknown/notobserved, no gap-freeclaim. Guardsovrapposti
non sottratti dai timing. Torch intra/inter1/deterministicCPU/BLAS/OpenMP/
Accelerate verificati; owned state restored, interop lifetimefreshprocessnormalexit.
BLOSC_NTHREADS1requested, effectivedecoderthreadingunknown. Tutti quattrobody
hashbound a output/identity eparentexitacceptance, bodycomplete da solo insufficiente.

## Interpretazione e prossima decisione

Naturalm physicalamortizationm, controlphysicalB, hypotheticalcontrolbill/m
esplicitamenteetichettato. Fullcontrols processanoB−mrighe reali ulteriori, quindi
contrasto include source selections/features/shapes/packing/host e non isoladecoder
omodello. Sparsewarmpairedwindows/gates/hash/cache non riproducono coldI/O o
partial-onlystreaming. Nessuna monotonicità/fit/interpolazione/upperbound/production
p99/scientificconfirmation/preferredpolicy. Old0045/0046contesto, nonpool/subtract
campaigns e nessun automaticqueue replay.137remainingoccupancies, streamingcache/
inputhistory, transport/detectorarrivals eindependentsignalsource restanounresolved.

Nuovo matrix internamente definito32case può supportare un successivo protocollo
versionato con scope/autorizzazione separati e trattamento esplicito degli altri137
punti. Questa è la prossima decisione delimitata; nessun Task0048automatico, nessuna
allowance consumata rinnovata. README/index/memory1.42 aggiornati, Git resta manuale.

## Git manuale — non eseguito

Branchmain/upstreamorigin/main verificati; indice vuoto. Rivedere anche gli altri
file nuovi prima dello stage. La lista è limitata ai33file Task0047curati/viventi,
con brace-expansion supportata dazsh/bash; nessun data/receipt/array/sequence/log.

```bash
git status --short
git diff --check
git diff --stat
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git diff --no-index -- /dev/null src/latenttrigger/benchmarks/targeted_raw_service.py

git add -- README.md docs/project-memory.md docs/handoffs/README.md \
  docs/prompts/0047-targeted-partial-raw-decision-measurement.md \
  docs/handoffs/0047-targeted-partial-raw-decision-measurement.md \
  docs/targeted-partial-raw-decision-measurement.md \
  configs/benchmarks/development_targeted_raw_decision_v1.json \
  scripts/validate_targeted_raw_decisions.py \
  src/latenttrigger/benchmarks/targeted_raw_{admission,custody,measure,native,planning,protocol,provider,reporting,runtime,selection,selection_fixture,service,worker}.py \
  tests/test_targeted_raw_{admission,chain,runtime,selection,service}.py \
  results/tables/final/task0047-targeted-partial-{selection.csv,raw-decision-cells.csv,raw-decision-pairs.csv,raw-decision-summary.json} \
  results/figures/final/task0047-targeted-partial-{joint-cost,paired-cost,selection-coverage}.png
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "feat(benchmarks): measure targeted partial service costs"
git push origin main
```
