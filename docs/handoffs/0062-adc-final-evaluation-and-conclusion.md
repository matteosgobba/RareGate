# Task0062 — Valutazione finale ADC preregistrata

## Metadati e obiettivo iniziali

Data 2026-10-16 Europe/Rome. Primo orario osservato 17:08:07 UTC; l'ispezione
iniziale immediatamente precedente è inclusa prudenzialmente nell'avvio 17:07:00 UTC.
Scadenza totale 19:07:00 UTC, CPU massimo20min, riserva cleanup10s.
Base verificata `fa39e3a9949aa0cdb1b97a8d760ee84e9c0b70f7`, `main` con upstream
`origin/main`, worktree pulito e indice vuoto. Memoria1.56; nessuna prova nuova
di push, freschezza remota o hosted CI. Stato iniziale: in corso, nessun accesso
numerico finale o misura CPU. Un solo contesto finale autorizzato dal prompt0062.

## Confini e piano

Conservare tutti i file vincolati dal freeze0061 revision2. Verificare la mappa
chiusa dei184file e ancore; qualificare separatamente estensione/config/test/prompt
0062 su dati artificiali. Congelare le definizioni prima di costi/esiti. Preflight
runtime/risorse; parità B32 su4096righe di sviluppo; matrice CPU fissa senza retry;
intento esclusivo prima di aprire ruoli finali; un solo passaggio B32 degli8stream,
analisi44intervalli, robustezza/bias e conclusione. Nessun fit/acquisizione/
ricalibrazione o Task0063. Cap8GiB intero studio,4GiB worker,1worker,0servizi.

## Git

Nessuno staging/commit/push automatico. Revisione e comandi selettivi manuali nella
risposta finale. Escludere payload, score, pesi, fixture/cache/tracce ignorati e
lavoro estraneo. Risultati, validazione, limiti e identità saranno aggiunti qui.

## Esito finale e decisione scientifica

**`completed_preregistered_adc_evaluation`**: valutazione finale valida/completa
nel perimetro8stream e3formati tutti qualificati. Esito scientifico
`negative_compound_criterion`; prontezza operativa falsa. Ciclo0060–0062 concluso,
Task0063 non avviata. Nessuna nuova acquisizione, fit, optimizer, calibrazione,
selezione checkpoint/seed/soglia, ensemble o uso dei gruppi residui.

Target primario0,01,40.000gruppi per segnale:

| Arm | Efficienza A / limite simultaneo | Efficienza LQ / limite simultaneo |
|---|---:|---:|
| compact |0,373342 [0,356553;0,390218]|0,068967 [0,061783;0,076306]|
| reference |0,505283 [0,492335;0,518072]|0,106250 [0,097367;0,114864]|
| PCA3 |0,227175 [0,212887;0,241704]|0,119050 [0,108848;0,129682]|
| Mahalanobis |0,501325 [0,487729;0,514571]|0,158375 [0,146490;0,169722]|

Punti ai cut empirici congelati; limiti per quantili della popolazione con
incertezza di calibrazione, non intervalli condizionali ai soli cut empirici.
Compact−0,9reference: A[−0,097949;−0,064946], LQ[−0,035947;−0,017094]. Entrambi
upper<0: ritenzione90% esclusa. Utilità compact≥15% supportata A, esclusa LQ.
Reference/PCA LQ upper<15%; Mahalanobis LQ attraversa15%, quindi irrisolto.
Nessun arm sostiene il requisito di utilità congiunta su entrambe le topologie.

Tassi primari effettivi medi compact/ref/PCA/Maha:
0,009961667/0,009985667/0,009896/0,009953; tutti gli intervalli degli arm e delle
6differenze rispettano i limiti. Anche i6confronti secondari passano. Non esatta
uguaglianza né ricalibrazione finale. Tutte44righe d'inferenza/16stream FPR/32conteggi
signal stream più16medie d'arm sono pubblicate con scope espliciti. Nessun3N:
seed condividono40.000gruppi, background comune non duplicato per topologia.

Mahalanobis−compact lower primari+0,110035/+0,076110 su A/LQ, qualità migliore di
oltre1punto su entrambi. LQ supera anche reference[+0,039545;+0,064557]. Reference−Maha
su A[−0,005670;+0,013857] irrisolto. Non dichiarare dominanza completa: Maha non
passa utility LQ lower né gate CPU. PCA peggiora A/migliora LQ rispetto a compact.
Decisione: rifiutare il successo di compressione compact; mantenere Mahalanobis
come confronto semplice di qualità più convincente, senza certificare il requisito
composto. Il risultato A forte resta distinto dal mancato requisito congiunto.

## Baseline, ancore, isolamento e correzioni

Ancore7/7 esatte. Solo freeze0061revision2,130765B,
SHA256 `e425d1bc50c644caf7c3fad1f2317472e33eca68686022d4eac52bf04d804ce6`.
Primo freeze ritirato0061 conservato, mai fallback.184file/4791963942B e mappa
chiusa277file comportamento/3144047B verificati prima/dopo; runtime/build/thread
sostanzialmente identici (solo ordine record normalizzato). Nessun file vincolato
0061, initializer, config, guard o test modificato. Nuovi sorgenti fanno crescere
la vecchia discovery ricorsiva; non viene usata come falsa uguaglianza del bundle.

Estensione iniziale0062 `62c5203e36d26bf6e463780b92fdc6fd40c787fd700c6a55d3e09fc8964ca9e3`
conservata. Primo development fallisce sul contratto di provenienza: nuovo adapter
aspettava background, manifest identifica correttamente train-first-hash-ordered.
Stop prima del hashing/open numerico del ruolo, caricamenti modelli, score,
ricostruzioni, intento CPU o timer; nessun esito finale esposto. Preflight precedente
ha comunque letto4,792GB per integrità strutturale: nessun falso globale-zero.

Correzione soltanto nell'estensione, fixture aderente al manifest reale, regressione
positiva/negativa sulla provenienza e nuova qualificazione prima di ogni tempo/esito.
Intenti/fallimento/binding precedenti conservati. Nuovi preflight-v2/development-v2
con binding
`7cf503e5b9a88629f57db7214bb23e6b5e3be82b44d7cb4b7e7828122cf5a49d`;
scadenza globale invariata. Nessuna modifica a score, feature, modelli, soglie,
statistica o regole costo congelati. Non è un retry di inferenza/timing finale:
nessuna di quelle attività era cominciata nel tentativo respinto.

Context0062 distinto, output `data/decisive-v2-adc-task0062/`; non impersona Study0061.
Config+prompt effettivo+test/codice+freeze+intenti esclusivi vincolati. Help/import
inattivi, scope test separato/count≤256 finale, guard Python di lettura/scrittura
più controlli espliciti percorso/hash/ruolo; nessuna pretesa di sandbox OS.
Sorgenti originali/all-role/SQLite/calibrazione e pool residui negati al worker;
training non autorizzato. Hashing strutturale dei184file esplicitamente autorizzato.

## Validazione generata e attività positiva

Set coerente:98core scientifici+20audit+46ADC0061+38valutatore=202 prima del reale;
poi2presentazione su soli scalari con lo stesso set=204 nella consegna finale.
Ruff check/format no-cache sui nuovi file. Nessun vecchio sorgente condiviso cambia,
quindi esclusi vecchie matrici native costose, MPS/ONNX/particle/streaming e replay
3002portable. Esclusione per percorso, non falsi938deselected di questa suite.

| Invocazione generata | Call pass | Errori non-call | Fonte/nota |
|---|---:|---:|---|
| validation1 |194|1|NameError nel teardown telemetria, due import mancanti; conservato|
| validation2 |200|0|correzione e ampliamento controlli|
| validation3 |201|0|varianze/definizioni prima della prima ammissione|
| validation4 |202|0|contratto source label e fasi versionate|
| validation5 |202|0|bundle pre-outcome finale,21,64s/22,381s esterni|
| presentation-validation |204|0|nuovo rendering scalare, nessun cambio valutatore|
| final-presentation-validation |204|0|fonte finale consegnata,21,60s/22,424497s esterni|

204aspettative uniche,7invocazioni/1407call pass,0call fail,1errore teardown.
Non sono1407test distinti o7conferme scientifiche. La copertura finale è un unico
204pass coerente sulla fonte finale; il202 pre-unblinding resta il permesso numerico.

Attività positiva del gruppo finale, scope ADC0061 strumentato:52costruzioni,
138forward/2372righe,66toy Adam updates,68call pubbliche/2176padded,128calibrazioni
score conservati,1matrice generata6neurali/2analitici e2fit analitici-oracolo.
Estensione strumentata:1116call numeriche pubbliche/23680righe padded e469call
ricostruzione/4480righe;16load parità. Separati58880call/9850880row presentations
nel loop CPU con boundary artificiale, senza modello/inferenza fisica. Altri core
toy/factory/load non sono coperti integralmente da questi contatori; nessun totale
globale-zero o scope cumulativo retroattivo inventato. Figli I/O negativi,
osservatori normali/falliti/interrotti, help/guard e runtime generati sono bounded.

Oracoli indipendenti: piccoli conteggi/tie e CP zero-count chiusi, Bernoulli con
varianza1/3, direzione degli estremi/sostegno NI/segno inverso, stream indicatori
non ensemble, schedule intero, scenari di decisione positivo/negativo/inconclusivo.
Post-risultato un diverso conteggio via sort/searchsorted sui vettori già committati
conferma48count/tie e44identità dei punti da conteggi per seed: zero chiamate modelli.
È verifica degli stessi dati, non conferma indipendente di utilità.

## Attività originale e CPU

Parità sviluppo sui4096gruppi train: B32 reload/repeat e score0061 bitwise. Tutte
24stream/shape qualificate,0decision flip; maxerrorescore1,9750322675e−5 entro
allowance congelata; Mahalanobis ricostruzione N/A. Parità aggiunge163840righe/
35904call score e86016righe/29624call ricostruzione,16load modelli.

Un'unica matrice384celle/49152timed/12288warmup,61440call/11161600presentazioni
sugli stessi4096gruppi. Loop rep→stream ruotato→batch1/32/512→boundary alternato→call,
indici esatti protocollo. Gather fuori timer; score pubblico/2mask/output owned dentro,
feature/scaling dentro joint. Conservati tutti i tempi e blocchi, nessuna somma di
componenti, best-block/seed o retiming favorevole. Durata CPU13,739121s, ciclo
sviluppo intero15,840491s, tutti0skip.

Rapporti primari compact/ref:
0,956892/0,968508/0,935984/0,979975/0,957472/0,979998/0,945903/**1,205527**.
Mediana0,962989814,0/8≤0,80: gate fallito. PCA/compact mediana0,925877925/1of8;
Maha/compact0,945206261/1of8: entrambi falliti. Tutti i seed/blocchi nel CSV408righe
(384celle+24rapporti), tempi per batch/call dichiarati; vantaggio algoritmo solo
non sostituisce joint. Nessun rate fisico o p-value/universal speedup.

Dopo parità e intenti, un solo final-unblinding-intent esclusivo prima di qualsiasi
lettura numerica finale.24vettori FP64 completi/hashati/0padding:1Mbg+40kA+40kLQ×8,
8640000score/270000call. Progress/prefix/intent/commit impediscono riavvio o array
parziale presentato completo. Lifecycle finale15,538834s con reporting/exit/reap.
Nessun secondo passaggio di inferenza per figure, controllo o ricostruzione report.

Robustezza primi512finalBG:2trasformazioni×8stream,8192score/256call; riferimento
preso dagli score già conservati. Maxrawfeature3,33e−16, scaled/score0 e0flip su
entrambi i tagli.16report pass. Binning fisico esatto fornito: MET[0,30)/[30,60)/
[60,120)/[120,∞), leptoni1/2/≥3, jet0/1/2/≥3;264righe stream/arm nei2rate,0N<20.
Forte dipendenza molteplicità, non decorrelazione causale o label SM inesistenti.

Totale pubblico originale19973632presentazioni/367600call,24load;1084096gruppi
unici (1080000finali+4096train-dev). Non N indipendente moltiplicato da seed/timing.
Ricostruzioni e hash/letture di verifica sono separate; zero nuovi update/fit/cal.

## Risorse, custodia e presentazione

Whole-study8GiB e RSS worker4GiB,1worker attivo/0servizi; task≤2h, CPU≤20min,
cleanup10s. Riserva nuova260000000B dentro268435456B futura0061, nessun reset dei
totali o cancellazione vecchia evidenza/cache. Storage conservativo≈5,05GB;
picco reale lifetime912277504B, sampler894746624B nella fase finale. ThreadTorch/
BLAS effettivi1/zero loader, versioni/build esattamente0061; nessun MPS/ONNX,
servizio, survey globale, idle-gate, upgrade, chiusura app o reboot.

Origine clock conservativa17:07:00UTC prima di prima lettura17:08:07; include
implementazione,7gruppi generati,preflight fallito ammissione, nuove qualificazioni,
misura, finale, postflight, figure,curation/docs/verifiche finali/exit-reap. Receipt
conclusivo dà elapsed inclusivo reale; nessun reset per correzioni/fasi. Bytecode e
cache tool disabilitati; XDG/matplotlib/tmp contenuti da prima degli import.
Own PID campionato e lifetime RSS integrano riserve/allocazioni bounded; non prova
OS all-write/picco tra campioni/native scratch o disk fisico. Prima anteprima grafica
su soli piccoli aggregati senza RSS sampler separato; limite dichiarato, non
riaccettato retroattivamente. Rendering finale osservato0,981921s, sampled90652672B.
Warning NumPy opzionale su pyyaml conservato, nessuna installazione.

Score/tracce/margini/intenti/receipt privati ignorati. Manifest output content-bound
`data/decisive-v2-adc-task0062/private/output-identities.json`,171file,
SHA256 `f69eb330d039cb212b4192b04e827eb27f5bb90cfcb45ca1a67d356f5cc09781`,
primari chmod444. Curati solo scalari, conteggi/hash e3PNG. Prima grafica con etichette
troncate conservata privatamente; script di presentazione separato dopo unblinding
legge solo tabelle curati, corregge layout/legend senza toccare valutatore o stime.
204test finali e revisione visiva delle3figure; nessun report comporta nuovo score.

## File, riproducibilità e limiti

Nuovi modulo/script valutatore, script report congelato, script presentazione,
2file test,config0062,prompt/handoff,report inglese,brief italiano,5CSV/summary,
3figure e aggiornamentiREADME/index/memoria1.57. Il summary separa validity,
completion,scientific verdict,rate/utility/retention/CPU,source e tooling/resources.
Sono mantenuti16cut e44intervalli completi anche sfavorevoli. AP prevalenza1/26;
SIC nominale approssimazione background-dominated, nessuna significatività scoperta,
rate LHC o intervallo SIC simultaneo inventato. ZeroB gestito con limite esatto finito.

Indipendenza condizionale dei gruppi non dimostrata dal solo hashing esatto. ADC
prefiltrato, cap4e/4mu/10jet, nuova vista12feature; actualBG13.451.915non4M e mistura
SM nominale non verificata. Modelli a80epoche non optimality. Nessun dato dimostra
prontezza rivelatore/affiliazione ufficiale/CERN o speedup MPS/ONNX. Task0059snapshot,
LHCOYES3,particle192,vecchiP4falliti/consumati e correzioni0060/0061 invariati.

Per riprodurre le figure usare soltanto lo script scalare sui CSV/summary curati,
con cache contenute; per gli audit riusare vettori/tempi esistenti, non i comandi
real final/development consumati. Non avviare un nuovo task/fit o riusare residui.

## Git finale

Branch effettivo main/upstream origin/main, basefa39e3a. Indice lasciato vuoto;
nessuno stage/commit/push automatico, nessuna affermazione su remoto fresco/CI.
Consegna manuale selettiva con esclusione data/artifacts/fixture/cache/diagnostici
ignorati e lavoro estraneo. Messaggio suggerito:
`feat(research): conclude preregistered ADC quality-cost study`.

## Verifiche e clock conclusivi

Consegna verificata 2026-10-16T17:48:42.544058+00:00: elapsed inclusivo 2502.544058s dall'origine
contabile17:07UTC, sotto7200s con riserva10s; nessun lavoro numerico residuo.
Charge logico conservativo 5051343928B (≈5.051344GB), più i minimi byte
conclusivi summary/handoff/receipt esplicitamente contabilizzati nella ricevuta.
23file pertinenti (20nuovi/3living modificati), indice senza stage.638link locali
validi;5CSV con24/48/44/408/280righe,JSON finiti,hash figure/tabelle/source coerenti.
Ruff check e format-check6file nuovi passano; diff-check pulito. HEAD e ref locale
origin/main entrambi fa39e3a9949aa0cdb1b97a8d760ee84e9c0b70f7, nessun fetch/CI/push.
Tutti i worker posseduti ritirati; dati/modelli/fixture/cache/diagnostici ignorati
esclusi dalla consegna Git. Stato finale invariato: completed_preregistered_adc_evaluation,
validità/completamento veri, criterio composto negativo, prontezza operativa falsa.
