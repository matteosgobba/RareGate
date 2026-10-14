# Task0048 — Refined-Support Paired Service Replay

## Metadata e stato iniziale

2026-10-14 Europe/Rome. Task0048 soltanto, completato.
Stato finale: **parent_accepted_synthetic_refined_support_service_replay**, unica
allowance0048 accettata/consumata; sessione b1815dee77c5462d889d5fc4e15db3c7.
Baseline verificata: main, upstream origin/main, HEAD
939014bc2c8f6c86db01258c4f72cb1c29f89960; working tree e indice inizialmente puliti.
645file inizialmente tracciati; allineamento locale main/origin/main0/0.
Memoria1.42→1.43. Prompt effettivo salvato integralmente prima delle modifiche.
Ambiente locale: macOS 26.6.2 arm64, Python 3.12.12 nella `.venv` esistente;
nessuna installazione o aggiornamento delle dipendenze.

## Ambito e autorizzazione

Replay sintetico model-free separato, esclusivamente sul bundle chiuso Task0047
accettato. Due supporti correnti, due mapping, due billing; nessuna nuova misura
fisica né caricamento raw/model/feature/score scientifico. Una sola allowance
real-source condizionale è stata reclamata dopo fresh acceptance, roundtrip
del record emesso e freeze immutabile. Nessun secondo source sweep. Nessun commit/push/staging.

## Storia preservata

Task0047 accepted/consumed, tutti i 333 confronti sfavorevoli (1 su un punto
nuovo, 231 a piena occupanza),
fallimenti software e cleanup storici immutati. Task0046/0045/0043 accepted/consumed,
Task0044 accepted replay, Task0041 failed/consumed, Task0042 software-only,
Task0036 unresolved, Task0034 scientific gates, Task0025 failure e particle192/192.
Exposure permanente YES/YES/YES. Nessuna assenza successiva ripara cleanup falliti.

## Validazione e risultati

Validazione software finale superata; unica sessione sui tempi chiusi Task0047
accettata e consumata. I risultati, le risorse e i fallimenti precedenti sono
riportati nelle sezioni seguenti. Il commit e il push restano manuali.

## Implementazione e contratto

Nove moduli additivi `refined_service_*`, config chiusa e validator propri0048.
Nessun engine, classe, globale, authority, config o budget storico è stato ampliato.
I clock/guard e le pure utility compatibili restano invariati; il nuovo guard
controller applica continuamente128MiB. Il reader usa solo stdlib e helper puri;
il worker impedisce import/letture raw/model/scientifici, rete e subprocess.
Il parent mantiene custodia byte-only a blocchi64KiB; parsing completo soltanto
nel simulation worker. Reporting legge soltanto file predecessori owned e
hash-bound, senza copie ridondanti o rigenerazione di tracce/scenari.

Due supporti dallo stesso campaign corrente: coarse_reference15punti rimisurati,
refined_3232punti (primario), con identici vettori agli anchor comuni. PerB1{1};
coarseB8{1,2,7,8}/B32{1,2,8,31,32}/B128{1,2,32,127,128}; refinedB8{1…8}/
B32{1…8,31,32}/B128{1…10,32,127,128}. Nessun timing0045 entra nel lookup.
Next=min k≥m, previous=max k≤m; natural usa natural_k, control contemporaneo
full-B dello stesso caso/pair. Non si sostituisce un unico(B,B) o un costo medio.
Cursor separati zero-origin per anchor/scenario, indice modulo20, un solo advance
per dispatch; nessun advance su arrivi/completion/decision/audit/idle. Le fasi
cross-anchor e i cicli sono costruiti, non cronologia fisica osservata.

FIFO nonpreemptive, capacity1024waiting+inservice/drop-tail, tie completion→
arrivi ordinati→dispatch, full immediato, timeout dall'arrivo originale più
vecchio, drain completo, int64-ns checked. Ogni dispatch completa m eventi; k/B
sono lookup e lavoro sorgente modellato, non righe fisiche eseguite o eventi
aggiunti. Naturalk<m conserva deficit firmato. Slotutilization nominaleB è
batching descriptor, non prova di padding. Quattro strict toy cuts dopo
completion; late strettamente>100ms illustrativi. Startup idle resta incluso
nell'orizzonte da tempo zero/utilizzazione, con horizon/pending/drain espliciti.

Generator0037/0044 invariato, due modi×trerate500/2500/5000×treseed41/42/43,
5000eventi:18tracce una volta per sweep,90kposizioni sintetiche, hash e stream
score separato. Sette policy(1,0), B8/32/128×timeout1/10ms. Grid6048scenari/
30.24Mpresentazioni;756contesti con otto varianti e6048contrasti. D=natural−control;
4billing,2previousD−nextD,2refinedD−coarseD, con entrambi i level changes e tutti
otto ID/denominatori. Null propagato, mai quantile mancante=0. Quantili separati,
nessuna media fra ripetizioni; p99 riguarda superstiti ed esclude overflow.

Occupancy compatte(scenario_id,m), vectorID/classecodice0reference1new, conteggi,
busy utile, righe actual/model e differenze firmate. Anchor inclusi unused,
fingerprint interi/ordine originale,20count,wrap/remainder, campioni inutilizzati
e dot-product esatto. Gli indici inutilizzati si ricostruiscono dai count zero.
Join streaming ordinato conserva soltanto histogram corrente/otto risultati,
riconcilia full/partial/exact/mapped/new/reference/righe/busy e tutti i contrasti.
B1support/mapping per lato, refinedB8next/previous exact e fixture indipendente
all-full passano; natural/control full-work restano distinti. Provenienza e
anchor eligibili/unused vengono confrontati separatamente dagli assignment eseguiti.

## Preparazione sorgente e contabilità

Il bundle0047 chiuso è24file/17238096B, cap24MiB esplicitamente autorizzato,
non8MiB/16MiB. Tutti i pin sono nel config;11anchorSHA forniti e13pin aggiuntivi
sono vincolati prima del freeze e riconciliati con receipt/workflow. Nessun path
embedded raw/model/array/selection viene seguito. Si distinguono summary owned
aggregate_report_body_complete e curated parent_accepted_targeted_partial_raw_
decision_measurement; shared body identico salvo status, added parent/accounting
campi preservati. Nessuna reintroduzione dei vecchi cost means cross-case rimossi.

Copertura originale384cells/3840pairs/7680timedNspositivi,1152warmNs esclusi,
8832side records;192vettori×20pair ordinati. Schedule/repetition/window/side/model
shape/wrapper/class e tutte le copie/statistiche riconciliati; differenze esatte,
ratio meccanici,32ULP binary64 soltanto per serializzazione statistiche. Source
acceptance richiede task/owner0047, campagna actual nonsynthetic/consumed, parità
esatta, zeroexit/reaping/deadline/overshoot0/assertionrelease e assenza. Selection169
righe/15reference17new137residual, tutti i campi/digest/rank verificati senza aprire
input storici. Restano tutti i 333 confronti sfavorevoli (1 nuovo, 231 a piena
occupanza) e tutte le osservazioni lente. La denominazione storica full/null
indica lavoro a piena occupanza, non una differenza di durata necessariamente nulla.

Preparazione: un'ispezione24open/17238096B di pin/schema (17JSON e3CSV; JSONL3file,
8832righe framed, solo6record first/last decodificati). Un parse24open/17238096B
si arresta prima dei JSONL per il campo legacy planned_counts; l'originale0047 usa
counts. Il secondo parse24open/17238096B completa3JSONL/8832record,7680timed e
1152warm, senza queue. Lettura contestuale aggiuntiva prompt0047:1open25014B;
report/documenti/code/config sono ispezioni contestuali separate. I load di bundle
non rappresentano un totale globale di tutte le open di codice/librerie/test.

I primi quattro copiedroot software includevano byte-only tutti i curated tables:
fra questi,4filecurated0047=1386509B per copia e config/prompt0047=50005B, quindi
6file/1436514B per copiedroot. La ricostruzione di queste copie è esplicitamente
retrospettiva, non un journal prospettico. Includevano anche vecchie timing CSV
0045 come byte; nessun vettore0045 è stato parsed/assegnato dal nuovo engine.
La procedura finale elimina pair/cell CSV e timing JSONL dai copiedroot. Undici
aggregate/identity metadata necessari ai test storici sono allowlisted; summary
0045 serve soltanto al loro byte-identity contract. Due code-context source0047
(config/prompt) e undici reference sono journaled prima/dopo copia. I fixture
storici possono leggere/hashare questi metadata: attività distinta dai parse
chiusi0047 e da qualunque source timing assignment.

Le copie di durata non diventano nuove misure: per parse completo, oltre7680
record timed originali ci sono30720durationcopies (7680ciascuna in aggregate
chronology/cellobservations/pairs e curatedpairs), più1152warmcopies nella
chronology. Warm1152originali sempre esclusi. Il lookup conserva7680valori in192
vettori; ripetizioni e assegnazioni non aumentano il numero di misure originali.

## Fallimenti e versioni software preservati

Due smoke generated falliscono: alias/tmp/symlink-root, poi fixturetimed_pairs1800
invece3840. Lint trova loop/import/placement/order, riparati prima dell'acceptance.
Il parse preparatorio planned_counts fallito è preservato con tutte le24open e
zero JSONL parsing/scenari. Il primo native generated fallisce0.807211s per
sandbox /bin/ps, prima di simulare; assertion propria released/reaped/absent.
Il secondo native preliminare completa6048scenari in70.740883s, con normalexits/
reaping/cleanup/overshoot0/3figure ispezionate. Successivo review identifica una
contabilità Python incompleta dei Trace: contava header, non i payload dataclass.
I metadata per-trace e RSS originali restano; il helper finale conta anche tuple/
payload e il regression test verifica il confronto con il generator. Quel native
preliminare non viene usato per l'acceptance finale corrente.

Softwarev1:223focusedpass, full interrotto dal validator per audit review; nessun
terminalfull/counter legacy conclusivo, attività positiva non quantificata per
quella invocation. v2:226focusedpass, full graceful interrupt con1933passed e
counter legacy85modelinstances/31forward-reconstruction/8710rows/2optimizersteps
completed/0inflight/2syntheticcalibrations. v3:244focusedpass, full timeout240s,
nessun terminalfull/counter conclusivo. Si passa a tre partizioni disgiunte,
ciascun processo sempre≤240s; non si aumenta alcun cap del replay/sessione.
V4 viene ritirato dal source-map checkpoint dopo review copy scope; i due shard
legacy completano1730+1638test, ma non viene emessa acceptance per quella versione. V5:249focused
pass, copied fixture troppo stretto:1572passed/1failed/157setup errors per metadata
storici mancanti; nessun native/operational claim. L'allowlist finale11metadata
risolve le dipendenze preservando i contratti storici. Tutte queste evidenze e i
record di versione restano ignored; nessuna acceptance è fabbricata o riutilizzata.

## Validazione finale, distinta dai test fisici Task0047

Record `data/task0048-validation/e66943af8eeb4315970f4ea16e7d0253/software-acceptance.json`,
SHA25630245db9d1a8e685e30519e44b8aaf20ae6fa8a1380f2739cda4358fc549b010.
324bindings source/config/prompt,43packages,36native/metadata pins.250focused
(223nuovi+27runtime comuni),3591full e3591portable locali artifact-free;
1730+1638+223test per ciascun full/portable, exit0/error0/failure0/skip0 e XML
hash-bound, copertura file completa e disgiunta. Ogni subprocess≤240s, logicalfull
248.651s: non è il cap whole del source session. Lint/format/pipcheck pass,
nessun install/update/hostedCI. Ultimi subset regressioni:18,32,22,3pass; altri
focused140/196/215 e versioni precedenti sono distinti, non sommati come nuova
copertura. Le3368prove fisiche-chain0047 non vengono presentate come acceptance
per questo engine.

Native finale bootstrap1e0e3748:71.420867s, storage68953508B/controller61620224B;
emitted-record roundtripcd3c94d0:75.160743s/storage69052808B/controller76824576B.
Entrambi6048scenari/30.24Mpresentazioni/6048contrasti/39744anchor, normalexit/reap,
release/absence/overshoot0. Tracce6290173B e lookup1563500B reali, entro16/2MiB.
Record emesso immutabile e sidecar noncircolare: l'effettivo plan admitted usa il
recordSHA, non un unconditional-success admission mock. La successiva allowance
operativa viene reclamata prima della prima custody originale. I metadata context
finali hanno13record di copia journaled:2config/prompt0047 e11legacyaggregate/
identity; nessuna timing pair/cell CSV o JSONL nel copiedroot.

## Risultati correnti accettati

[Report](../refined-support-service-replay.md),
[scenarios](../../results/tables/final/task0048-refined-service-replay-scenarios.csv),
[contrasts](../../results/tables/final/task0048-refined-service-replay-contrasts.csv),
[occupancies](../../results/tables/final/task0048-refined-service-replay-occupancies.csv),
[anchor audit](../../results/tables/final/task0048-refined-service-replay-anchor-audit.csv),
[summary](../../results/tables/final/task0048-refined-service-replay-summary.json).

Unica sessione source b1815dee77c5462d889d5fc4e15db3c7 accettata/consumata in
78.911485s.6048started=completed/0inflight,30,240,000presentazioni da90kposizioni
sintetiche/18tracce generate una volta.27,544,586completed+2,695,414overflow,
6,067,628late survivors, pending0.7,896,652dispatch sample assignments,
39,291occupancy rows e39,744anchor (27,216refined/12,528coarse);6048contrasti,
conservazione e controlli numerici verificati dal parent streaming. Ogni variante
ha756contesti e3,780,000presentazioni generate; sono somme di grid ripetuto,
non popolazioni indipendenti.

D=natural−control; valore positivo di loss/late significa più eventi nel lato
natural. Tutti gli sfavorevoli e i null restano, senza policy winner:

| Supporto / mapping | Overflow natural / control | D overflow | Late natural / control | D late |
| --- | ---: | ---: | ---: | ---: |
| coarse / next | 381281 / 380877 | +404 | 852814 / 875117 | −22303 |
| coarse / previous | 190168 / 380640 | −190472 | 409071 / 859155 | −450084 |
| refined / next | 380777 / 380832 | −55 | 852258 / 873972 | −21714 |
| refined / previous | 220090 / 380749 | −160659 | 472767 / 872474 | −399707 |

Refined next:overflow D−102…+375,174negative/77positive/505zero; late D
−1059…+754,225negative/171positive/360zero. Refined previous conserva32positive
loss e110positive late; survivor-p99 D−108.508…+231.352ms(next) e
−453.741…+16.022ms(previous). Mapping interaction refined somma−160604overflow/
−377993late, p99contrast−542.253…+5.525ms. Nessun percentile mediato o inferenza
paired-event/confidence; popolazioni superstiti possono differire, overflow escluso
da p99. Overflow+late/generated tiene entrambe le componenti e denominatori chiari.

| Refined−coarse | Δ natural overflow | Δ control overflow | ΔD overflow | Δ natural late | Δ control late | ΔD late |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| next | −504 | −45 | −459 | −556 | −1145 | +589 |
| previous | +29922 | +109 | +29813 | +63696 | +13319 | +50377 |

Controlli non costanti: cambiano selezione del caso, fase e queue history.
Δbusy assegnato natural/control−429.612499/+0.295364s(next),+206.020397/
+3.387494s(previous) sul grid; non runtime misurato. Support p99interaction
−32.628…+13.624ms(next),−386.314…+419.229ms(previous). Non si sottraggono i risultati
Task0046, non si isola causalmente il beneficio di misurare nuovi punti.

| Supporto / mapping / lato | Mapped batch % | Mapped useful event % | Mapped busy % | Modeled rows−completed |
| --- | ---: | ---: | ---: | ---: |
| coarse / next / natural | 10.1298 | 26.1459 | 44.1473 | +1232479 |
| coarse / next / control | 13.4686 | 32.3013 | 56.6702 | +3775478 |
| coarse / previous / natural | 23.2733 | 52.2386 | 32.2416 | −1098737 |
| coarse / previous / control | 13.6244 | 32.5306 | 56.7839 | +3833345 |
| refined / next / natural | 0.7443 | 9.1235 | 10.6613 | +104609 |
| refined / next / control | 3.0517 | 19.1196 | 31.5834 | +3780793 |
| refined / previous / natural | 3.7612 | 27.3306 | 15.2802 | −473944 |
| refined / previous / control | 3.0598 | 19.2371 | 31.6024 | +3771366 |

Denominatori rispettivamente batches, completed useful events, total assigned
busy; exact=complemento. Counts/denominatori e surplus/deficit separati sono nel
summary. Newanchor usati per97395batch/515977eventi/224354451006ns(next natural),
146212/1060580/390199074495(previous natural); control83325/449298/703182181612 e
96895/776004/1377773659049. Resto sourceuse reference, coarse soltanto reference;
non sono distribuzioni controfattuali. Originali restano7680 misure, non il
numero di assegnazioni né somma delle eligiblevectors dei due supporti.

Nuove occupanze residue emergono nella history refined rispetto al corrispondente
coarse contesto/mapping/lato; residual significa `(B,m)` non nei32punti misurati.
È una differenza locale per contesto, non novità globale o nuova misura:

| Mapping/lato | Contesti con nuovi residual /756 | Batch interessati | Eventi utili | Assigned busy ns |
| --- | ---: | ---: | ---: | ---: |
| next/natural | 143 | 493 | 28808 | 15990157528 |
| next/control | 114 | 223 | 9395 | 8705324108 |
| previous/natural | 137 | 21201 | 382135 | 94227792556 |
| previous/control | 170 | 1186 | 53072 | 57750556347 |

Union categorie104/54/112/92B-m rispettivamente e liste complete nel summary.
La curation usa join dei soli ownedCSV ordinati, currentcontext/coarseoccupancy
sets;0originalsource reopen,0queue/trace regen. Primo pass metadata/copie0.700s,
con outcome CSV/PNG bit-identici al body accettato e receipt originale preservato.
Public summary compatto conserva192fingerprint/shape/wrapper/class, non sequenze,
trace/latency arrays o receipt/grant/claim dettagliati; questi restano ignored,
con snapshot prima della compaction e catena SHA di curation. Tutti333adverse,
1 nuovo outlier e i 231 confronti sfavorevoli a piena occupanza rimangono nei
sorgenti e nelle sequenze originali escluse da Git.

Tre figure effettive ispezionate, senza rerender/correzioni post-sessione:
[refined billing](../../results/figures/final/task0048-refined-service-replay-outcomes.png),
[support e due livelli](../../results/figures/final/task0048-refined-service-replay-support.png),
[residui/modelrow](../../results/figures/final/task0048-refined-service-replay-residual.png).
Tutti seed/repetition e unfavorable/null, unità/denominatori, faceting4/12/8axes,
symlog0.01pp e signed colorlineare±1%, marker9 distinti. Nessun replaysorgente per
plotting, nessuna curva interpolata o p-value/CI.

## Risorse, lifecycle e contatori effettivi

Prereq1.630978s/simulation69.933625s/report3.631421s/final0.541362s/whole78.911485s;
cap30/120/60/15/240, cleanup0.000202/0.000116s≤2dentrocap. Entrambi exit0, normal
reaped e parentaccepted; overshoot 0. Diciannove osservazioni confermano attiva
l'assertion temporanea contro lo sleep del sistema, poi
released/reaped/confirmed absent. Display sleep permesso; nessun settingpersistente,
purge/cache/globalRAMfloor/appclosure. Nuovi scope/claim non riparano cleanup storici.

RSSsimulation120995840/report174948352/controller66961408B; native60358656/
113868800/parent50331648B. Upper conservativo parent+maxserialworker164200448B,
non simultaneous/globalRAM. Cap1GiB/512MiB/128MiB invariati. Parsed containers
41125773B (+margini nel codice)≤128MiB, paired lookup+metadata+currentmargin
1563500B≤2MiB, trace6290173B≤16MiB, descriptor containers1165031B; diversi dai
campionamenti RSS/native. Currentlatency/wait/batchentries≤5000,FIFO≤1024,
occupancy≤128,anchorcounts≤260,8resultscontrastcontext. Paired payload SHA/order
liveness e source parsing temporaries rilasciati prima dei servizi sintetici.

Ownedstorage56527103B≤128MiB; CSV25979114B controcombined56MiB, guard64MiB,
otherreserve8MiB; perfile12/32/32/16MiB, rowlimits291168/39744congrowth prima della
write. Occupancy rappresentazione intera≤108B perrow da bounds di colonne
(≤5000eventi,≤128rows,≤int64busy),291168×108=31446144B+header≤32MiB;
anchor≤287B/row,39744×287=11406528B+header≤16MiB. I controlli effettivi di rowlength,
file e totale restano conservativi e non autorizzano storage illimitato. PublicCSV
5275638/10101680/2307188/8294608B e3PNG208382/488066/360776B; summary compatto
circa1.1MB. Originali owned/evidenzedettagliate ignored, non in staging.

WARNworker/report55556,parent2743; CRITICAL/invalid0, latched_errorNone.
Query-startgap0.085897simulation/0.325999report/0.699812parent; terminalgaps
0.047682/0.103931s. Optionalcontextunknown/notobserved, non gap-free; guardtime
sovrapposto non sottratto. Il runtime della simulazione non è latenza fisica trigger.

Sessionmetadata:24prebyte-only+24workerparsed+24finalbyte-only=72open51714288B;
solo worker3JSONL/8832record.7680unique originaltimed,1152excludedwarm,
30720duplicate timedcopies/1152warmcopies. Parent0aggregate/chronologyparse e
reporting0originalsource reopen.18trace generation/90kunique posizioni/30.24M
presentazioni finali, started=completed6048/inflightNone e7896652sampleassignment.
192sourcevectors,90eligiblecoarse subset:non si sommano come misure nuove.

Quattro generatednative invocations:1fallito pre-scenari e3matrici complete
accepted (1preliminare con vecchia contabilitàTrace,2finali),18144scenari/
90.72Mpresentazioni/54trace generations. Actualsource aggiunge6048/30.24M/18.
Stessi90kPCG64positions rigenerati, non270k nuovi eventi acquisiti. Tutti i native
replay0048 eseguono0modelli. Cinque record legacy subset persistiti (uno0 per setup
failure):340modelinstances/124forward-reconstruction34840rows/8toyoptimizersteps
started=completed/0inflight/8syntheticcalibrations. Due fullinterrotti non hanno
counter terminali; altri modelli/HDF/metriche toy storici sono fuori dal subset:
attività positiva distinta, nessun global-zero claim.

Nuovo operational raw/feature/membership/golden/scientific-score/eventfingerprint
load, HDF/rawcustody, model/load/inference/reconstruction, optimizer/scaler/
calibration/scientificmetrics/download/device/transport/newphysicaltiming=0.
La lettura di timingmetadata e la queue/toy arithmetic sono lavoro positivo,
non timing fisico nuovo. Exposure permanente YES/YES/YES, tutta la storia indicata
all'inizio resta; nessun allowance reset o retroactive repair.

## Interpretazione e prossima decisione delimitata

È trasporto di costi finiti warm-window nel matrix dichiarato, con cicli artificiali.
Refined lascia137occupanze non misurate. Anche B8exact non riproduce input/cache/
ordine fisico streaming. k≠m è ipotesi e previousk<m può sotto-contare righe; né
mapping né spread sono bound empirici o intervalli che contengono necessariamente
la realtà. Pairing del lookup non abbina fisicamente job/survivor fra queue che
si separano. Assignedmeans sono sequenze sintetiche, non distribuzioni fisiche
pooled. Nessuna indipendenza delle tre ripetizioni, componente causale, scientific
confirmation, productionp99 o deploymentpolicy segue. Transport/detectorarrivals,
cachehistory e independent signal source restano unresolved.

Prossima decisione: scegliere con scope/autorizzazione nuovi quale evidenza residua
occupancy oppure streaming/cache/transport è necessaria per ridurre questa
dipendenza, senza eleggere una policy. Nessun Task0049 automatico o altro grid.
README/index/memory1.43 aggiornati; namespace/datareceipts/claim/log ignored,
nessuna source sweep o misura ripetuta dopo acceptance.

## Verifica finale degli artefatti e della documentazione

La verifica conclusiva conferma ancora validi il record di software acceptance
e il roundtrip sul record emesso, senza modifiche al codice congelato. I quattro
CSV curati sono identici ai file accettati, con 6.048 scenari, 6.048 contrasti,
39.291 occupanze e 39.744 righe anchor. I sette hash di CSV e figure coincidono;
il summary conserva i 192 fingerprint di vettore/ordine e i 18 hash delle tracce.
Sono stati controllati 444 link locali: nessun collegamento mancante.

Il summary pubblico finale ha SHA256
`60f4adb3ac52582f14dd7fb8befa6673ce1914b8f9025b8022509854a2fffe52`;
quello owned accettato resta invariato a
`4aab9ade875e6dd7f85f7a2cd23199389640a56e9dee1abc66b1af92a6174dfa`.
La compaction finale mantiene pubblici stati, conteggi e hash; timestamp delle
osservazioni opzionali e journal dettagliati di copia restano ignorati, insieme
agli snapshot precedenti e alla catena SHA di curation. La descrizione retrospettiva
di v4 distingue ora l'allowlist intermedia di tre riferimenti dai successivi undici.
Questa verifica non apre il bundle sorgente originale e non rigenera code o tracce.
Il record dettagliato è `data/task0048-validation/final-metadata-git-check.json`.

## Git manuale — ultimo passaggio

Verifica finale: branch `main`, upstream `origin/main`, entrambi al commit base
`939014bc2c8f6c86db01258c4f72cb1c29f89960` (0 avanti / 0 indietro); indice vuoto.
Sono previste tre modifiche a documenti living e ventitré nuovi file Task0048:
26 percorsi selettivi. Nessun file storico operativo viene modificato.
I namespace `data/task0048-validation/` e
`results/simulations/task0048-refined-service-replay/`, incluse allowance, receipt,
log, freeze e sequenze dettagliate, restano ignorati. Non usare `git add .` o
`git add -f`. Questi comandi sono per l'utente e non sono stati eseguiti da Codex.
Il commit suggerito non esiste ancora; nessun push o hosted CI è dichiarato.

Dalla root del repository:

```sh
git status --short
git diff --check
git diff --stat
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git ls-files --others --exclude-standard
git add -- \
  README.md \
  docs/project-memory.md \
  docs/handoffs/README.md \
  docs/prompts/0048-refined-support-service-replay.md \
  docs/handoffs/0048-refined-support-service-replay.md \
  docs/refined-support-service-replay.md \
  configs/simulation/refined_service_replay_v1.json \
  scripts/validate_refined_service_replay.py \
  src/latenttrigger/simulation/refined_service_admission.py \
  src/latenttrigger/simulation/refined_service_engine.py \
  src/latenttrigger/simulation/refined_service_fixture.py \
  src/latenttrigger/simulation/refined_service_native.py \
  src/latenttrigger/simulation/refined_service_protocol.py \
  src/latenttrigger/simulation/refined_service_reporting.py \
  src/latenttrigger/simulation/refined_service_runtime.py \
  src/latenttrigger/simulation/refined_service_source.py \
  src/latenttrigger/simulation/refined_service_sweep.py \
  tests/test_refined_service_replay.py \
  results/tables/final/task0048-refined-service-replay-scenarios.csv \
  results/tables/final/task0048-refined-service-replay-contrasts.csv \
  results/tables/final/task0048-refined-service-replay-occupancies.csv \
  results/tables/final/task0048-refined-service-replay-anchor-audit.csv \
  results/tables/final/task0048-refined-service-replay-summary.json \
  results/figures/final/task0048-refined-service-replay-outcomes.png \
  results/figures/final/task0048-refined-service-replay-support.png \
  results/figures/final/task0048-refined-service-replay-residual.png
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "feat(simulation): add refined-support paired service replay"
git push origin main
```
