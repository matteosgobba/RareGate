# Task0061 — Preparazione ADC, training e freeze

## Metadati e obiettivo

- Data: 2026-10-16 Europe/Rome; inizio osservato 12:15:45 UTC (14:15:45 locale).
- Base verificata: `d02e6a5f114e1979a5a5b5e8f11c84aba02eed41`.
- Branch `main`, tracking `origin/main`; worktree inizialmente pulito, indice vuoto.
- Nessuna verifica di freschezza remota, push o hosted CI; memoria iniziale1.55.
- Stato iniziale: in corso, controlli sintetici e sorgente/risorse da validare.
- Esito finale: `completed_adc_preparation_training_and_freeze`; pronto0062,
  valutazione finale falsa/0062 non avviata/utilità scientifica non valutata.

Questa task attua soltanto preparazione, training/selection, calibrazione e freeze
ADCv2 autorizzati dal prompt effettivo. Esiti finali, valutazione qualità e confronto
CPU restano Task0062, non avviata. Conservare Task0059, ancore0060, esposizioni,
allowance consumate e correzioni FP32/cleanup. Prontezza operativa generale falsa.

## Piano iniziale (storico, eseguito con gli emendamenti sotto)

Verificare ancore, implementare percorso12input/schema2 separato, testare con HDF
generati e oracoli indipendenti prima dell'acquisizione. Dichiarare layout, ledger,
denominatore quarantena e limiti prima dei payload. Congelare codice/test/config e
prompt; poi acquisire solo i3file pinnati, accettare sorgenti, separare ruoli,
eseguire al massimo6fit neurali+2analitici, calibrare e sigillare. Ogni fallimento o
interruzione rimane registrato; nessun reset o retry di fit. Budget4h inclusivo,
8GiB intero studio0061/0062,4GiB RSS proprio,1worker,0servizi.

## Git

Nessuno staging/commit/push. Base `d02e6a5`, branch `main`/upstream `origin/main`.
Messaggio suggerito: `feat(research): prepare ADC models and freeze decisive study`.
Non esiste un nuovo commit da citare né una verifica di push/CI remoto. I comandi
manuali selettivi sono nella risposta finale. Escludere tutti i payload/fixture/
cache/diagnostici ignorati e ogni lavoro estraneo.

## Esecuzione e correzioni prima dei fit

Ancore0060 tutte corrispondenti. Acquisizione reale unica accettata:680426757B,
3richieste evento/0redirect/0retry,219.055715084s esterni con exit/reap; checksum
MD5 e SHA256 su disco. Header effettivi FP64[N,19,4]:13451915background,
55969A,340544LQ. Il4M pubblicato era aspettativa, non condizione di uguaglianza.

Primo prepare fallito prima di righe decodificate: limite software5M aggiunto qui,
non difetto del payload. Diagnosi solo header rivela anche descrizioni publisher
MET_class_1/Four_Ele_class_2/Four_Mu_class_3/Ten_Jet_class_4 con ID corretti.
Emendamento esplicito pre-fit al parser e ammissione15M chunkwise, nessun cambio
a tagli/quarantena/feature/fingerprint/ruoli minimi/modelli/semi/score/statistica.
Fingerprint vettorizzati verificati byte-identici all'oracolo e versione singola.
Database vuoto e tentativo prepare1 conservati; prepare-v2 mantiene scadenza
cumulativa13:30:34.363160 UTC, inclusa riparazione/diagnosi/test.8GiB/4GiB invariati;
riserva group/index3.6GB, scratch usa temporaneamente riserva ruoli ancora assenti.

Validation1: ps proprio negato nel sandbox, child ritirato/no report/work iniziale
ignoto. Validation2/3:18/112call pass prima dello stop su symlink pytest/controesempi
generati; corretta distinzione fra alias test contenuti e alias payload proibiti.
Validation4:162pass;5:163pass. TelemetriaTALLY prima assente per lookup modulo
package invece di basename; sola correzione diagnostica dopo acquisizione,
binding1 e snapshot preservati, dipendenza acquisizione invariata/nessun replay;
validation6:163pass e binding2. Parser/admissione/performance esatta/budget poi
qualificati con validation7:164pass/7.14s, bundle
`807266df548528cc9594ee5eb1e4f6956694502cf171ef6f34fde0a0691bae70`/binding3.
I98core+20audit+46ADC passano insieme. Nessuna modifica ai sorgenti storici.

Attività ADC toy validation7:52costruzioni,138forward/2372righe,66Adam updates,
68score pubblici/2176righe padded,128score calibrazione conservati,6fit neurali+
2analitici nella matrice generata più2fit analitici-oracolo. Altri core-toy fuori da
questo contatore. Tentativi precedenti conservati, nessun globale-zero o totale
retroattivo inventato. Nessun fit/calibrazione ADC reale prima di questi emendamenti.

## Ruoli accettati, isolamento e risorse

Tutte13848428righe decodificate passano i tagli strutturali. Gruppi unici:
13449154background (2761duplicati),55969A,340544LQ.0quarantene/0conflitti cross-label.
Allocati200000train/50000selection/1000000calibrazione/1000000final background/
40000A/40000LQ:2330000gruppi distinti,0overlap. Residui11199154/15969/300544sigillati,
nessun pool di retry.4096development sono prefisso training,512per simmetrie;
512final-background sono regola futura, nessuna inferenza qui.

Prepare-v2 accettato674.801706917s esterni. Controllo indipendente post-preparazione:
rehash payload/DB chiuso,2330000membership riaperte solo per struttura, ordineSHA
e disgiunzione globale/prefisso dev verificati. Campagna preparazione cumulativa
1326.378265s<1800 inclusi primo fallimento, diagnosi/riparazione/test/identity;
nessun reset timer. Picco lifetime RSS901611520B, storage4.740GB a fine preparazione.
Osservazione periodica RSS/logical bytes e riserve scratch, non prova OS all-write;
cacheOS/native scratch unlink/directorymetadata non osservati integralmente.4GiB/
8GiB e1worker numerico/0servizi invariati; normali controller stdlib esterni.

Prima del primo fit aggiunti divieti privati SQLite/array non-training (anche
sqlite3.connect) e binding scorecalibrazione/DB nel manifest. Validation8:164pass,
AST preparazione/numerica invariati, nessun replay; bundle scientifico effettivo
`e12c417f9d9373c509b56065681d537b592be21d214decebb2966c3743071a95`/binding4.
Il guard Python integra loader/path espliciti, non è sandbox OS per nativeHDF.

## Fit e calibrazione reali

Sei tentativi neurali e2analitici tutti completi/consumati,0incompleti/0sostituzioni.
Ordine1729compact/reference,1730compact/reference,1731compact/reference,PCA3,Maha.
Tutti80epoche/cap,7840update ciascuno; checkpoint selezionati80/80,80/78,80/79.
Ogni modello ripristina il proprio minimo selection; perdita ripristinata identica,
reload/repeat B32 bitwise e ordine campioni comune per80epoche passano.
Il cap non dimostra convergenza. Totale47040update/480epoche/96Mpresentazioni train
sugli stessi200kgruppi;24.3Mselection inclusi restore sugli stessi50k. Nessuna scelta
di seed o checkpoint mediante segnali/calibrazione/esiti finali.

PCA3 SVD FP64 e Mahalanobis shrinkage.1/Cholesky fit una volta su200k; nessun rank/
shrinkage search. Pesi/stati/history/sampler/checkpoint hash in tabella8righe,
artefatti schema2 tutti ignorati sotto artifacts/models/decisive-v2-adc.

Calibrazione unica su1Mgruppi:8Mscore/250000call B32,0padding effettivo. Tutti16cut
strict> higher,9999/999accettati ai target.01/.001 e1tie; sono conteggi cal, non FPR
finale. Bracket1based[989658,990340]/[998890,999107], valori estremi e scorehash inCSV.
Dev reload/repeat98304score/3072call; simmetrie16384score/512call sui512train:
16report con errori raw/scaled/score0 e decision flips0. Totale score pubblici
8114688presentazioni/253584call su1004096eventi unici; non N indipendenti ripetuti.
Nessun score/efficienza/FPR/AUC/AP/SIC/NI/bias finale o matrice CPU reale.

## Correzione del sigillo e freeze finale

Primo complete-freeze.json128852B/SHA7a4c909c…3e83396 conservato con receipt/identity.
Il controllo dopo cleanup rivela active.json effimero nella mappa: flag ready
esplicitamente ritirato in freeze-manifest-v1-withdrawal.json. Difetto accounting/
ownership, non inferenza/parità. Nessun peso/soglia/score o dato modificato.

Nuovo sigillo immutabile `private/complete-freeze-v2.json`,130765B, SHA256
`e425d1bc50c644caf7c3fad1f2317472e33eca68686022d4eac52bf04d804ce6`.
La sola finalizzazione esclude il tracker e riusa per hash l'evidenza scientifica;
0fit/calibrazione/inferenza dev ripetuti. Regressione generata crea/rimuove davvero
il tracker e verifica ogni voce residua. Validation9 finale164pass/9.73s pytest,
10.316724208s esterni, bundle
`162e61abaad164b3c15a2609016ca97c679af0669a7c7847ec0fd72f3e5e9ec2`/binding5.
Tutti i file numerici/data/model/score/statistici invariati dal bundle scientifico.

Post-exit identity reader verifica184file/4791963942B e identitàcorrenti code/config/
test/prompt: tutto corrisponde,0missing,0worker attivi. Seal-v2 lifecycle2.249062500s,
lettore2.348140250s, storageosservato≈4.825GB. Fixture/token/precedenti tentativi mai
resettati;9invocazioni generate,164nodi unici osservati/1110call principali passate,
non un risultato unico1110test né un totale completo per il primo child non loggato.
TALLY finale:52costruzioni/138forward2372righe/66toyAdam/68call2176padded/128cal;
5figli negativiI/O,2observer,1runtime. Core-toy aggiuntivi fuori da questo contatore.

## Consegna e prossimo passo

Report inglese, configesecuzione,3CSV(10custody/8model/16cal),summary, prompt/handoff,
README/index/memoria1.56. Quattro ancore0060 immutate; nessun vecchio modello/pilota
riaccettato, Task0059snapshot/esposizioni/particle192/P4storici invariati.
Controlli finali passati: identità source/code/prompt/config, ancore0060,3CSV eJSON,
610link locali,21file pertinenti, indice vuoto, lint globale Ruff no-cache e
format-check573file, diff-check. Charge conservativo completo≈4825452225B (include
root ignorate, curati e copie working full-size, successivi minimi aggiornamenti
documentali espliciti), sotto8GiB. Clock globale include anche questi controlli e
reporting; dettagli/timestamp nel summary. Nessun hosted CI, push o prova di utilità.

**Task0062 soltanto dopo richiesta umana effettiva:** usare esclusivamente manifestv2
eSHA sopra, verificare184identità e runtime/thread, registrare intento esclusivo di
unblinding prima degli score finali. Poi valutazione unica/paired+cal uncertainty,
robustezza/biasfissi e CPU diretto coerente. NI90%, utilità.15 entrambe topologie,
FPRcomune e vantaggioCPU25% primaria.01 restano da valutare;.001secondaria.
Riportare anche esiti negativi/inconclusivi/baseline dominante. Nessun nuovo fit,
ricalibrazione, ricerca soglie, bestseed o uso residui per salvare un risultato.
Pronto0062,true blind/generation independence non dimostrati, utilitànonvalutata,
operationalreadinessfalse, finalevaluationfalse, Task0062startedfalse.
