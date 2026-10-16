# Task0060 — Audit scientifico, correzioni e protocollo decisivo

## Metadata

- Data: 2026-10-16, Europe/Rome. Fase: audit scientifico/software e protocollo prospettico.
- Stato: `completed_project_scientific_audit_and_experiment_protocol`; audit, correzioni, validazione coerente finale e protocollo fattibile completati. Readiness operativa storica false.
- Branch `main`, upstream `origin/main`; base verificata `4a61c74b764afdd2f7aa4eb4c6c4598a48c53336`.
- Worktree inizialmente pulito, index vuoto, Task0059 già committata, memoria1.54.
- Ambiente esistente: Python3.12.12, NumPy2.5.3, Torch2.14.1, sklearn1.9.1, SciPy1.18.1, pytest9.1.1, Ruff0.16.10, h5py3.16.0. Nessun upgrade/installazione o risultato hosted CI/push verificato.

## Obiettivo e perimetro

Il mandato esplicito riprende lo sviluppo scientifico: la raccomandazione di chiusura
in0059 è superata, mentre il suo snapshot v1 resta storico e integro.0060 deve
produrre un vero audit del codice e dei test, correzioni mirate necessarie e un
solo esperimento fattibile. Non lancia0061/0062, non riapre eventi/modelli/score
originali, non ricalcola risultati scientifici reali, non esegue custody hashing
raw, acquisizione eventi, replay operativo o P4. Esposizioni YES/YES/YES, fallimenti,
pilot consumati e192step particle restano tali; readiness operativa false.

Prompt originale e handoff iniziale sono stati salvati prima del lavoro sostanziale.
La memoria corrente è stata aggiornata subito per distinguere il nuovo obiettivo
dalla chiusura storica; non sono stati riscritti handoff o protocolli congelati.

## Audit effettivo e confine della revisione

Inventario iniziale riprodotto:253Python source/75051righe,80Python test/34937righe,
1340funzioni statiche test,29script/6601righe,51config,190documenti e1workflow CI.
La raccolta iniziale conta3920casi parametrizzati: è una misura diversa. L'inventario
finale per file (`task0060-source-review.csv`) distingue lettura mirata, controllo
contrattuale/documentale, scansione raccolta/effetti collaterali, wrapper e semplice
inventario. I file `structural_only` **non sono stati esaminati individualmente**;
non è un audit riga per riga né una ricertificazione universale di tutti i moduli.

Ogni sottosistema ha una disposizione nel report inglese: provenienza/acquisizione,
split/deduplica/quarantena, rappresentazioni/scaler, PCA/AE/training, valutazione/
calibrazione/statistica, diagnostica/ricerca, CPU/parità, ONNX/ORT, MPS, simulatori,
streaming/startup/sessione/cleanup, supervisor risorse, script/config/CI/documentazione.
I hot path scientifici sono stati seguiti tra config, implementazione, test e record
curati. Sono stati letti solo codice, config, report e piccoli aggregati; nessun
payload originale, vecchio timing vettoriale o modello scientifico riaperto.

Il lettore v1 verifica/hash-a/scansiona file che contengono tutti i ruoli prima del
filtro di lettura. `allow_test=False` non certifica quindi assenza di accesso ai byte
del test. Questo **non dimostra contaminazione statistica del training**: l'EDA
seleziona i train prima delle statistiche e la calibrazione avviene dopo il freeze.
Il nuovo protocollo vieta quel lettore e richiede file separati per ruolo prima dei fit.

Oracoli nuovi: massa10/balance0 per due vettori opposti da5GeV; massa tramite
prodotti di coppia anziché la somma di quadrivettori della produzione;6permutazioni
con padding;4rotazioni e riflessione del fascio, con eta media che cambia segno;
PCA con covarianza diagonale/rango e residui noti; AUC7/8 e AP5/6 enumerate con ties;
limite binomiale zero-count; media di5eventi con coda che deve valere20. Le identità
matematiche non dimostrano simmetrie del rivelatore o utilità dei segnali.

## Difetti confermati e correzioni

Il registro CSV contiene16rilievi con ID/severità/tipo, file/funzione/riga, prova,
conseguenza, correzione, validazione, impatto storico e residuo.

- **F01, alto:** il costruttore AE ereditava dtype/device ambientali di Torch. Lo
  stesso seed sotto defaultFP64 produceva parametriFP64, incompatibili col contratto
  FP32 e con inizializzazione diversa. Factory esplicite CPU/FP32 preservano lo
  stream supportato storico e i default del chiamante. Riproduttore pre-fix:
  1failed/14passed. Nessun peso/score/feature/threshold storico modificato.
- **F02, alto:** con una memoryview esportata, la chiusura mmap falliva ma Store/
  cleanup perdeva ownership o descrittore. Due riproduttori OS reali fallivano.
  Ora mapping/fd restano registrati su errore e gli altri fd sono ritirati; dopo
  rilascio della view la chiusura è verificata anche in un figlio nuovo con timeout10s
  e oracolo OS EBADF. Un'ultima revisione ha riprodotto anche `quota.close`, che
  eliminava la registrazione nel `finally` nonostante il syscall fallito: corretto
  e aggiunto un terzo riproduttore, inizialmente1failed/19deselected. Un errore resta
  incertezza/ownership, non falso zero. Non è una ricertificazione IPC/crash/P4.
- **F03, alto, harness:** test di convergenza leggevano il modello originale; test
  streaming richiedevano root/slot/ledger0057/0058 già esistenti. Pin storici e mock
  I/O nel teardown impedivano il gruppo coerente e contaminavano quota/FDS. Ora
  usano documenti artificiali, nuovi mock repository, binding correnti **solo nelle
  copie di test**, cleanup in finally dopo ritiro delle iniezioni e ripristino dello
  stato. I pin/config congelati reali non vengono aggiornati. Un controesempio
  generato sostituisce la lettura della vecchia receipt; corretti regex obsoleta e
  controllo import esteso erroneamente agli adapter successivi già gated.
- **F04/F16, workflow:** bytecode e cache pytest/Ruff disabilitati; XDG/MPL/temp
  contenuti prima degli import nel runner. Il processo pytest blocca open Python
  di data/artifacts originali e scritture nel checkout. Non è una sandbox OS per
  qualsiasi I/O nativo. Il logging incrementale per fase conserva i fallimenti
  anche in caso di stop. Nessuna vecchia cache cancellata o contabilizzata a ritroso.

I rilievi residui sono limiti di disegno/misura o ipotesi: PCA6 controAE3 non isola
nonlinearità; eta signed non è invariante; Wilson condiziona su modello/soglia;
AP dipende dalla prevalenza artificiale; costo joint non è somma di campagne;
137occupancy mancano; latenze dei sopravvissuti e replay sintetici non danno rate
fisici/N indipendenti. Particle resta incompleto/deferito. ORT conserva il fallimento
del parent0025, MPS fisico non ricertificato. Non servono a questo esperimento CPU.

## Perché la conclusione scientifica v1 non basta

0033 documenta spostamenti centrali degli score ma code background competitive;
correlazioni con eta non sono meccanismo o importanza causale.0034/0036 restano
un disegno congelato e una route full-event unresolved; non sono proibizioni sul
nuovo studio.0049/0059 restano una sintesi valida dei risultati ammessi e dei limiti.

Dai conteggi già pubblicati nelle8righe AE,0060 calcola solo aritmetica descrittiva:
SIC nominale .740465/.615418/.339017/.020169 per two-prong e
.524261/.466991/.273640/.012245 per three-prong, tutti<1. Al taglio più stretto,
enrichment .7264117/.4410357 dai56/34su100000 contro116su150471.
Non è un massimo di curva, nuova significatività, conferma indipendente o prova
che ogni soglia possibile fallisca. AUC moderate .660/.586 non bastano a motivare
un selettore utile. Nessuna soglia/orientazione cambiata.

## Protocollo scelto e fattibilità

Una sola route: **ADC2021 v2**,12aggregati interpretabili degli oggetti forniti;
compactAE271parametri, referenceAE1999, stesso bottleneck3, PCA3 e Mahalanobis
con shrinkage fisso. Massimo6fit neurali (2architetture×3seed) più2analitici,
nessuna ricerca aperta/seed migliore/attention. Scaler train-only, selezione solo
background, checkpoint proprio ripristinato, calibrazione dopo freeze modelli;
finale e segnali protetti fino alla fine0061. La rappresentazione è nuova,
invariante per costruzione alle simmetrie dichiarate e limitata agli oggetti capped,
non validazione del modello LHCO né dati full-event.

Verificati metadati JSON/version history Zenodo dei tre record, licenzaCCBY4.0,
v2 ultima nelle risposte consultate, MD5 e byte esatti; nota bugfix non dettagliata.
Totale file680426757B, nessun evento scaricato. Sono positive consultazioni web e
11file locali di metadati, paper PDF/codice autori; non si dichiara zero download
in senso globale. Conteggi4M background/55969A/340544LQ vengono dal descrittore,
**non** da payload v2 accettati. L'array logico richiederebbe1.337GBFP32/2.673GBFP64;
non ci sono archivi da espandere. LHCO18983506 ha invece archiveXtoYYprime~4.9GB,
routefull-event ancora unresolved; una vista jet non sarebbe sostituto esatto.

0061 richiede almeno2.25M gruppi background e40k per segnale: train200k,
selection50k,calibration1M,finalBG1M e40kfinali per topologia. Deduplica/overlap
precedono l'assegnazione hash; nessuna statistica finale o outcome guida sviluppo.
Schema/nomi/classi/unità/cut/padding, checksum, conflitti e conteggi effettivi sono
check concreti iniziali; se falliscono si ferma prima dei fit senza route favorevole
alternativa. Holdout statistico non equivale a indipendenza di generazione o vero blind.
Il filtro leptonico impedisce generalizzazione a collisioni non filtrate.

PrimariaFPR.01, secondaria.001 già decise; efficienza compact almeno90% reference,
LB utility primaria≥.15 su entrambe le topologie e costo jointCPU B32 almeno25%
inferiore con regola8blocchi. Le FPR effettive e i loro intervalli devono essere
comparabili; i target non sono rate realizzati. Si propagano incertezza quantile,
intervalli background e44famiglie signal con bound paired sui gruppi; seed3 non
triplicaN. Cal1M/BG1M danno code attese10k/1k. Scenari con varianza paired.10 e
reference.20/compact.19 danno circa94%power condizionata della regola conservativa;
la calibrazione può ridurla. Non è garanzia o promessa di esito neurale positivo.
Baseline semplice dominante, negativo valido o inconclusivo sono esiti utili.

Budget prospettici nuovi:8GiB storage,4GiB RSS worker, un worker attivo,0servizi;
0061 massimo4ore con45min acquisizione/30min preparazione/20min per fit;0062 massimo
2ore,20min costoCPU. Nessuna dipendenza aggiornata, survey globale, Mac da liberare,
retry per scheduling favorevole o vecchio limite32MiB trasformato in legge universale.
Safety/source/science/tooling hanno esiti separati. Il protocollo è sostanzialmente
pronto per la preparazione controllata0061, non un token operativo/payload acceptance.

## Validazioni e tentativi conservati

Root nuova `/private/tmp/latenttrigger-task0060-w2Y1nVQT`; sottoroot distinte, mai
reset. Le vecchie root/allowance rimangono intatte. Il runner esegue processi puliti
con180s wall, inizialmente1GiB output osservato, poi2GiB prospettici dopo la misura
delle fixture. È un monitor periodico, non guard pre-growth all-writes; overshoot
osservati dei due stop iniziali sono conservati.

1. Raccolta iniziale3919/3920, un test native-named escluso per errore e poi reincluso
   perché effettivamente stub. Non è stato fatto un survey dell'host.
2. `portable-1`: stop1GiB/70.155s,2016marker pass/35E/8F. Mancano nodi/fasi esatti
   dopo interruzione; non si inventa un totale invocazioni. Include qualche vecchia
   matrice generated completa inizialmente non esclusa; attività positiva dichiarata,
   esclusa dai gruppi finali e non ripetuta per accettazione storica.
3. `portable-2`: stop1GiB/78.173s,1802nodi osservati;1789setup pass+13error,
   1763call-pass+39call-fail (inclusi13sottoverifiche),1800teardown pass+2fail.
   Questi numeri non costituiscono una suite pulita.
4. Gruppi mirati: `focused-1`239pass/16fail; `focused-2`48pass/30setup-error durante
   la costruzione del mock repo; `focused-3`79pass dopo le correzioni. I fallimenti
   introdotti nella riparazione del test sono dichiarati e conservati.
5. `portable-3`:3001pass+13subtest,938deselected,139.55s pytest/142.199s esterni,
   2132782824B output osservato, bundle `8f369943e0eb483e3fc577325ad41955ce91ed9c6db09e5d23e4761d0dc5627d`.
   È un pass coerente della versione prima dell'ultima correzione fd; non supplisce
   alla copertura della versione finale.
6. `fd-close-repro`:1fail/19deselected prima della correzione aggiuntiva.
7. **`portable-4`, bundle finale `9bc0812296844381510ffc3e211d3d18bc355d0af9a90c84f4ae43e0fd234fba`:**
   **3002pass+13subtest,938deselected,0fail/0error**,141.22s pytest e
   143.560983458s esterni; picco output osservato2133133980B sotto2GiB.
   Tutti417file source/test/script/config/CI corrispondono ancora al bundle.
   I98casi dei sei file preliminari passano insieme nel gruppo finale;65moduli.
   Questo è l'unico esito terminale usato per qualificare il sorgente finale.

Le10esclusioni del gruppo finale sono moduli con vecchie matrici service/model
complete e fixture di source-join/replay grandi: development_decision,
development_payload, partial_raw_chain, targeted_raw_chain, targeted_raw_service,
joint_service_replay, occupancy_service_replay, refined_service_replay,
prepared_service, development_raw.938aspettative non sono dichiarate passate.
Gli altri65moduli includono insieme i6file del check98 e tutti i test modificati.
I test positivi includono toy fit/optimizer/forward/score/calibrazione/HDF e processi
locali; non esiste un contatore completo legacy dei forward/step e non si dichiara0.
Solo le piccole integrazioni mmap/fd/figlio servono al cleanup cambiato; nessuna
matrice native/physical/ONNX/MPS storica, nuova attivazione P4 o scoring originale.

Ruff lint globale no-cache e format-check560file passano anche sul bundle finale.
JSON/CSV/link/diff e identità del bundle finale sono verificati senza riaprire payload.
Alla ripresa dopo il rate limit non risultavano processi di test interrotti: il
risultato terminale di `portable-4` era già completo. Sono stati ricontrollati gli
hash dei417file e aggiornati soltanto documenti/metadati; nessun fit o test numerico
è stato ripetuto senza necessità.
Nel sottoinsieme con logging incrementale sono3050nodi unici e8174call principali
completate, più39report di subtest annidati. Riproduttori e tentativo iniziale non
loggato sono separati: il totale esatto globale delle invocazioni resta sconosciuto,
non viene sostituito con marker di progresso. Dettagli per fase nel summary.

## File e riproducibilità

Output: report inglese, registro16rilievi, inventario per-file, summary con tentativi,
moduli/aspettative, fonti e numeri, protocollo inglese/configv2, prompt originale,
questo handoff, README/index/memoria1.55. Correzioni solo nel costruttore AE,
quota/Store cleanup e test/workflow correlati. Record originali non riscritti.

Ripetere il runner solo in una root nuova: `.venv/bin/python -B
scripts/run_scientific_audit.py --root /private/tmp/<nuova-root-univoca>` con
`PYTHONDONTWRITEBYTECODE=1`. Esso fissa cache/temp/thread/pytest prima del child,
salva source bundle e rapporti per fase. Una nuova esecuzione è lavoro sintetico
aggiuntivo, non un replay/permesso delle vecchie task. I risultati curati identificano
esattamente gli effettivi tentativi; non si copiano payload/fixture/cache in Git.

## Decisioni e follow-up

Nessun difetto confermato critico/alto rimane aperto per il perimetro scelto dopo
la qualificazione finale dell'ultima correzione. Restano limiti di scienza/trasferibilità e
condizioni di accettazione payload0061 esplicite, non booleani che li nascondono.
Non si certificano nuovi numeri fisici, deploy, source hash vecchi o conclusione
scientifica sperimentale già raggiunta.

**Task0061:** acquisizione limitata dei tre ADCv2, accettazione metadati/payload e
contenuto/overlap, preparazione per ruolo, implementazione/check generati finiti,
sei fit neurali/due analitici, selection/calibration background-only, freeze completo
con outcome finali protetti. **Task0062:** singola valutazione finale preregistrata,
incertezza paired/calibrazione, robustness/bias, confrontoCPU coerente e conclusione
positiva/negativa/inconclusiva supportata. Assorbire i fix ordinari in queste task;
nessuna microtask numerata o nuovo progetto infrastrutturale, nessun avvio qui.

## Git

Nessuno staging/commit/push effettuato. Nessuna modifica estranea iniziale o finale
rilevata. Base e branch sopra sono reali; non esiste un nuovo hash commit da citare.
Messaggio suggerito: `fix(research): audit science and preregister decisive experiment`.
Comandi manuali selettivi esatti nella risposta finale, lasciando fuori tutti gli
originali event/model/fixture/cache/diagnostici e qualsiasi lavoro non pertinente.
