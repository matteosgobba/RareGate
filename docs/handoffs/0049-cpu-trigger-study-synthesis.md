# Task0049 — Integrated CPU and Synthetic Trigger Study Closure

## Metadata, obiettivo e stato

2026-10-14, Europe/Rome. Task0049 soltanto. Stato:
**completed_curated_cpu_trigger_synthesis**. È una sintesi offline di risultati
curati, senza nuova acceptance nativa. La fase dichiarata di misure CPU e studio
sintetico delle code è chiusa entro il proprio scope; validazione streaming,
conferma scientifica indipendente e deployment restano irrisolti.

Baseline effettiva: branch `main`, upstream `origin/main`, HEAD
`d26d64425da9b738c6d92fd3d852122ca36d92b0`, 0 avanti / 0 indietro, working tree e
indice inizialmente puliti, 668 file tracciati. Task0048 era già committato;
`939014bc…` resta la sua base storica. Memoria 1.43 → 1.44. Prompt effettivo copiato
integralmente prima del lavoro; handoff iniziale conservato fra i draft ignorati.
Ambiente Python 3.12.12 della `.venv` esistente, helper solo stdlib; nessuna
installazione, aggiornamento o verifica attuale di device/runtime disponibile.

## Decisione e risultato integrato

La baseline PCA/AE congelata ha una comparazione scientifica accettata sui due
segnali dichiarati. L’AE mostra ranking moderato, più debole sul three-prong:
AUC 0.6600638025267328 / 0.5858771149922577, AP 0.5474272683246686 /
0.479971651666809. PCA resta sotto 0.5 nell’orientamento SSE originale, senza
inversione favorevole dopo il risultato: AUC 0.4684886579473786 /
0.4629531325637498. Non è un confronto capace di isolare la non linearità.

Al taglio AE più stretto restano 56/100000 segnali two-prong e 34/100000
three-prong contro 116/150471 background condiviso. Tutte le quattro righe di
qualità e i sedici punti calibrati originali, con soglie in precisione originale,
sono conservati. Il background riusato non è una replica indipendente; prevalenza
ed AP della miscela non descrivono un tasso fisico LHC. Non sono state calcolate
nuove metriche, curve, soglie, significatività o intervalli. B4096 scientifico e
parità computazionale su piccoli window di sviluppo hanno identità condivise,
ma scope diversi: i gate non certificano tutte le decisioni test in streaming.

Le sei campagne CPU accettate hanno confini distinti. Task0022 misura adapter/
ricostruzione/score su input preparati; Task0038 aggiunge packing e ritenzione;
Task0040 misura lettura selezionata, feature e loro joint diretto; Task0043 misura
raw→feature→score pubblico→quattro decisioni. Task0045 e Task0047 misurano coppie
natural m / controllo full-B con eventi reali aggiuntivi. Il padding Task0038
esegue davvero righe dummy, mentre il full-B del replay è billing ipotetico.
Non si sommano componenti o sottraggono campagne per dichiarare overhead/speedup.

La tabella dei confini conserva candidato, actual/nominal shape, wrapper/packing,
window/population, timer, inclusioni/esclusioni, cache/thread, campioni/ordine/
ripetizioni, unità, parità e limiti. Task0038 usa window basati su m; Task0045/0047
su B. Tutte le ripetizioni e le osservazioni lente restano. Nei 306 pool fissi
l’helper recupera un totale intero di ns univoco da count e mean serializzato,
poi verifica il mean pesato del solo caso. Sette mean Task0022 hanno una differenza
di serializzazione di una ULP binary64; sono registrati senza cambiare tempi o
allargare tolleranze sperimentali. Nessuna media di percentili o distribuzione
fisica pooled fra casi eterogenei.

Task0047 corrente è autoritativo per i suoi 32 punti: 15 riferimenti rimisurati e
17 nuovi, su 169 occupanze legali, quindi 137 non misurate. A B128/m10 le mean
natural/control sono 4.4550686/49.07731471666667 ms PCA e
4.55622155/50.59356456666667 ms AE, ciascuna sul proprio pool di 60 osservazioni.
Restano tutti i 333 confronti sfavorevoli, incluso quello nuovo e i 231 a piena
occupanza. Il wrapper actual-row corrente non amplia guard storici; i costi non
sono automaticamente intercambiabili con Task0045 o Task0043.

## Sistemi sintetici e residui correnti

Task0037 usa 10000/100000/1000000 eventi/s, deadline illustrativa 1 ms e 378 scenari.
Task0044/0046/0048 usano 500/2500/5000 eventi/s, deadline 100 ms, sette policy e
le stesse 18 identità trace; i quattro cut toy sono indipendenti dalle label
fisiche. I vecchi e nuovi grid non vengono combinati. Le presentazioni ripetute
non sono eventi indipendenti e non si sommano i 90000 per studio come campione
globale. L’helper confronta hash già curati, senza generare tracce.

Task0044 riconcilia 1764 scenari/1008 contrasti; cyclic−constant +349 overflow e
+5264 tardivi nel suo matrix. Reverse e rotation10 appartengono solo al subset
Poisson2500. Task0046 riconcilia 3024 scenari/2268 contrasti della campagna0045:
next +2037/+38310, previous −185005/−408610. Questi risultati storici non vengono
sottratti dal Task0048 corrente per attribuire un beneficio alle nuove misure.

Task0048 conserva 6048 scenari/6048 contrasti: 30240000 presentazioni =
27544586 completamenti +2695414 overflow; pending finale 0 e6067628 tardivi fra
completati. Ogni variante genera 3780000 presentazioni, con 756 contesti comuni.
Sono stati verificati tutti gli otto totali, tutte le famiglie, le identità degli
scenari costituenti e i loro denominatori, la conservazione e ogni descriptor
contrast presente. B1 ha108contesti di controllo, refinedB8 ne ha216 con uguaglianza
next/previous per lato e mapped batch/event/busy zero.

D=natural−control; positivo significa peggioramento natural:

| Supporto / mapping | D overflow | D tardivi |
| --- | ---: | ---: |
| coarse / next | +404 | −22303 |
| coarse / previous | −190472 | −450084 |
| refined / next | −55 | −21714 |
| refined / previous | −160659 | −399707 |

Refined next conserva77contesti con overflow positivo e171con tardivi positivi;
range rispettivi −102…+375 e−1059…+754. Previous conserva32/110contesti sfavorevoli;
range overflow −1925…+81 e tardivi −4674…+58. Le somme possono nascondere danno.
Le variazioni di p99 dei superstiti sono descrittive, non event-paired e non
production p99: popolazioni diverse ed esclusione degli overflow impediscono
l’interpretazione causale. Non vengono sommati o mediati percentili.

| Refined−coarse | Δ natural overflow | Δ control overflow | ΔD overflow | Δ natural tardivi | Δ control tardivi | ΔD tardivi |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| next | −504 | −45 | −459 | −556 | −1145 | +589 |
| previous | +29922 | +109 | +29813 | +63696 | +13319 | +50377 |

Gli anchor comuni usano gli stessi vettori correnti, ma supporti diversi cambiano
caso di controllo, fase del campione e storia della coda. Natural refined next
mantiene mapping sul9.1235% degli eventi utili e10.6613% del busy; previous
sul27.3306%/15.2802%. Il surplus next è104609righe; il deficit previous473944,
conservati separatamente. Il costo di k<m applicato a m resta ipotesi di lavoro
non misurato, non bound inferiore; next non è bound superiore. I cursori indipendenti
zero/mod20 e i cicli sono fasi costruite, non cronologia fisica.

Nuove occupanze residue rispetto al coarse matched emergono in143contesti next
natural e137previous natural, con493/21201batch e28808/382135eventi. Nei controlli:
114/170contesti,223/1186batch e9395/53072eventi. Sono conteggi curati copiati:
nessun ledger occupancy/anchor è stato riaperto e non sono nuove misure o scoperte
globali. Lookup B8 completo non riproduce input/cache di streaming.

## Fonti, scope e deviazioni dichiarate

Registry esatto di57fonti,26010109byte sotto32MiB per pass completo. Le sei SHA
obbligatorie sono state verificate e tutti gli altri pin fissati prima della
sintesi sostanziale. Nessuna espansione tramite glob o path embedded; source/model/
array/timing/operational path nelle fonti restano stringhe inerti. Le sole letture
quantitative sono quelle dei file curati allowlisted; SHA e status parent storici
non costituiscono una nuova reacceptance. Tutti i byte storici restano invariati.

Deviazione iniziale: il summary curato Task0046 incorpora anche `vectors` con
`paired_integer_payload`/pair IDs. Due parse JSON generici (inventory iniziale e
ispezione mirata) hanno decodificato incidentalmente90vettori/3600durate originali
per pass,7200presentazioni di valori. Non sono stati usati per statistiche,
assegnazioni o replay. Il reader finale esclude lessicalmente l’intero subtree
prima del decoding semantico; i byte dell’intero file restano hash-bound. Questo
finding è esplicito in config, report e summary: non si dichiara falsamente zero
per quelle decodifiche. Nessun timing-pair CSV, timing JSONL o evidenza operativa
storica ignorata è stata aperta.

Un primo tentativo del helper si arresta su `case_order`, campo stringa non ancora
incluso nello schema numerico: nessun output nuovo viene accettato da quel tentativo.
Lo schema è corretto prima del pass completo. Il suo journal conserva byte e stato
parziale; l’hash dell’ultima lettura, interrotta prima del drain del generator, non
fu emesso e resta una limitazione del primo logger, non una verifica inventata.
Il reader finale registra il digest ad ogni chunk e conserva journal preesistenti.
Lint rileva una lambda assegnata, corretta con funzione esplicita. Nessun esperimento
è stato tentato o allowance consumata. Un journal di pass completo è stato
sovrascritto da un successivo pass identico: la contabilità precedente è ricostruita
come tale da57pin immutati e output terminale, mai presentata come prospettica.

| Pass / journal | Aperture | Byte letti | Hash presenti | Nota |
| --- | ---: | ---: | ---: | --- |
| prospective-source-registry.json | 57 | 26010109 | 57 | Byte-only |
| schema-inspection-reads.json | 57 | 26010109 | 57 | Metadata / aggregati |
| targeted-source-reads.jsonl | 29 | 12499447 | 29 | Metadata / aggregati |
| curation-attempt-1.json | 43 | 3625559 | 42 | Fallito su schema,ultimo digest non emesso |
| curation-attempt-2.json | 57 | 26010109 | 57 | Metadata / aggregati |
| prior-complete-curation-pass-reconstructed.json | 57 | 26010109 | 57 | Ricostruito, non prospettico |
| final-curation-reads.json | 57 | 26010109 | 57 | Metadata / aggregati |
| delivery-curation-reads.json | 57 | 26010109 | 57 | Metadata / aggregati |
| delivery-reproduction-reads.json | 57 | 26010109 | 57 | Metadata / aggregati |
| final-source-preservation.json | 57 | 26010109 | 57 | Byte-only |

Totale cumulativo: **528 aperture / 224205878 byte**. Sono riletture degli stessi 57 file, non nuove misure. Ogni pass completo usa 26.010.109 byte; il cap32MiB riguarda l’input chiuso di ciascun pass, non un conteggio di misure indipendenti. Bootstrap/code/config Task0049 e piccoli fixture temporanei sono contesto separato, non inclusi nel totale delle57fonti. Il registro aggregato e i journal dettagliati rimangono ignorati.


Sono positivi letture metadata, hash, parsing di aggregati e aritmetica descrittiva.
Nuovo raw/event/membership/golden/feature/scientific-score/fingerprint numerico,
array scientifici, HDF/raw custody, modelli/inference/reconstruction, optimizer/
fitting/scaler/calibration, nuove metriche/curve/intervalli/significatività,
download/acquisizioni, verifica attuale hardware/runtime, timing fisico, trace
creation, queue replay, vecchi controller/workflow, grant/reservation/claim e sleep
assertion sono zero. L’eccezione delle timing arrays incorporate è quella dichiarata
sopra. Le attività positive storiche di modelli/optimizer/fixture non sono ripetute
e non vengono nascoste da un global-zero claim.

## File e verifiche realmente eseguite

[Report inglese](../cpu-trigger-study-synthesis.md):2959parole di prosa, lead246,
più sette tabelle verificabili. [Brief italiano](../cpu-trigger-study-decision-brief.md):
693parole. Nessuna nuova figura; i link rimandano a PNG storici immutati.
[Config](../../configs/reporting/cpu_trigger_synthesis_v1.json), helper stdlib e
29piccoli test indipendenti accompagnano cinque CSV e un summary:
57righe evidence registry,23boundary rows,4replay rows,20conclusion rows,
23claim rows. Le classi sono physical_measurement,synthetic_result,
scientific_context,software_only,unresolved; ogni claim ha fonte/chiave, scope/
denominatore, assunzioni ed estensione non supportata.

Le fixture verificano input sicuri/cap/hash, duplicate/nonfinite JSON/CSV, proiezione
senza decoding del payload, null/precisione, count interi non Boolean, recovery
indipendente di somme, tutte le otto identità di contrasto e level changes,
conservazione e denominatori di un piccolo scenario indipendente, assenza di
import operativi. Primo giro27test, giri finali29; contano come copertura29,
non somma di nuove prove sperimentali. Lint/format sui due file nuovi passano.
Il helper completo ricostruisce aggregati e confronto report/tabelle; `--check`
verifica la riproducibilità senza riscrivere output. Log/draft rimangono ignorati.
Nessuna full suite storica, matrice nativa, pip/install/update o hosted CI invocata.

Ricetta dalla root: l’eventuale audit deve avere un nome nuovo, oppure si omette
`--audit`; il helper non sovrascrive journal di verifica precedenti.

```sh
.venv/bin/python scripts/summarize_cpu_trigger_study.py --check \
  --audit data/task0049-validation/reproduction-check.json
.venv/bin/python -m unittest tests.test_cpu_trigger_synthesis -v
.venv/bin/ruff check scripts/summarize_cpu_trigger_study.py tests/test_cpu_trigger_synthesis.py
.venv/bin/ruff format --check scripts/summarize_cpu_trigger_study.py tests/test_cpu_trigger_synthesis.py
```

Machine output mantiene token decimali originali come stringhe e interi come interi.
Display ns/1000000→ms; mean mostrate a6decimali, cell mean a3, percentuali mapped
 a4. Non si fanno fit/interpolazioni né pooling fra campagne/casi eterogenei.
I file storici continuano a documentare outlier, null e fallimenti originali.

## Storia, limiti e prossima decisione separata

Task0048/0047/0046/0045/0043 accepted/consumed,0044/0037 studi sintetici accettati,
0041failed/consumed,0042software-only e0036unresolved restano invariati.
Task0024 export/equivalence accettato non sana Task0025: ORT3 non termina normalmente,
quindi benchmark performance fallito/consumato. Task0023 è snapshot storico
fallito/unavailable, non disponibilità MPS attuale. Task0039 è fondazione metadata,
0041non fornisce costi reali accettati e0042ripara software; esclusi dalle misure
fisiche accettate. Nessuna assenza successiva sana cleanup storici.

La baseline scientifica è completa nel suo scope, non conferma indipendente:
Task0036 `unresolved_no_acquisition` conserva blocker di completezza/unità/
indipendenza/conteggi/storage sotto protocollo invariato. Exposure permanente
YES/YES/YES, gate Task0034 e particle192/192/canonical deferral restano. Nessuna
affiliazione ufficiale CERN/esperimenti viene implicata.

Decisione: chiudere questa fase e mantenere i modelli congelati. Default prossimo
passo, solo se separatamente scelto: **design-only development streaming/cache/
transport protocol**. Target proposto: background di sviluppo, input/modelli
congelati, actual occupancies entro B1/8/32/128 e domande di carico500/2500/5000;
confine ingresso software prima del decode→output quattro decisioni. Disegnare
storia cache/ordine/riuso, transport e host/thread scope, derivare risorse/buffer/
output/deadline e criteri di successo/arresto: identità/parità/conservazione e
supervisione valide, stop su errore o infeasibilità. Non è piano eseguibile,
budget operativo o nuova sorgente. Indipendenza scientifica resta prerequisito
per sviluppo di modelli informato dai risultati. Runtime/precisione/altro hardware/
particle sono opzioni separate, non obblighi per chiudere; riempire tutti137punti
non è automaticamente il prossimo task. Nessun Task0050 avviato.

README, indice e sezioni correnti della memoria1.44 aggiornati in posto: obiettivi,
stato simulatore, hardware/stato scientifico, roadmap, futura domanda e vecchio
snapshot MPS. Storia datata e report/config/codice/curated source rimangono invariati.

## Controllo conclusivo di consegna

Tutte le 57 fonti corrispondono ancora ai pin prospettici dopo la curation;
il prompt effettivo è byte-identico all’allegato. Il pass `--check` ricrea
esattamente i sei output. Verificati 458 link locali, nessun collegamento mancante,
hash dei cinque CSV e dei propri artefatti di riproduzione, lunghezze dei documenti
e accordo delle sette tabelle. Il summary finale ha SHA256
`97b17c15ebdc25157a2751154d0408a2c2eaee8c6980555257f95650888617e3`.
HEAD/upstream restano alla base, indice vuoto; tre file living modificati e tredici
file nuovi, nessuna modifica storica non prevista. Il record dettagliato è
`data/task0049-validation/final-delivery-checks.json`, ignorato insieme ai draft.

## Git manuale — ultimo passaggio

Nessuno staging, commit o push eseguito. La lista selettiva comprende soltanto
16file Task0049/shared living; draft e journal in `data/task0049-validation/`
restano ignorati. La base è `d26d64425da9b738c6d92fd3d852122ca36d92b0`; il nuovo
commit suggerito non esiste ancora. Comandi manuali dalla root:

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
  docs/prompts/0049-cpu-trigger-study-synthesis.md \
  docs/handoffs/0049-cpu-trigger-study-synthesis.md \
  docs/cpu-trigger-study-synthesis.md \
  docs/cpu-trigger-study-decision-brief.md \
  configs/reporting/cpu_trigger_synthesis_v1.json \
  scripts/summarize_cpu_trigger_study.py \
  tests/test_cpu_trigger_synthesis.py \
  results/tables/final/task0049-cpu-trigger-evidence-registry.csv \
  results/tables/final/task0049-cpu-service-boundaries.csv \
  results/tables/final/task0049-replay-comparability.csv \
  results/tables/final/task0049-refined-replay-conclusions.csv \
  results/tables/final/task0049-cpu-trigger-claims.csv \
  results/tables/final/task0049-cpu-trigger-synthesis-summary.json
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "docs(research): close CPU and synthetic trigger study"
git push origin main
```
