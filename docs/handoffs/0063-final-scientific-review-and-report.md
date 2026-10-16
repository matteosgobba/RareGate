# Task0063 — Revisione scientifica finale e rapporto di progetto

## Metadati e stato iniziale

- Data: 2026-10-16, Europe/Rome; avvio osservato 20:02:57 CEST.
- Task: 0063, solo revisione di evidenza curata e documentazione finale.
- Stato iniziale: in corso; validazioni e conclusioni ancora da completare.
- Branch effettivo: `main`, upstream locale `origin/main`.
- Commit base verificato: `4b03b404a47cb75360748a95f15a480523b7c89b`.
- Working tree inizialmente pulito, indice vuoto. Nessun fetch o controllo CI remoto.
- Ambiente: macOS, zsh, interprete Python standard già presente; nessun runtime ML.

## Obiettivo e confini

Produrre rapporto inglese, brief italiano, mappa claim/evidenza e riepilogo strutturato.
Preservare il verdetto preregistrato negativo sulla compressione e valutare equamente
Mahalanobis. Il nuovo mandato dell'utente autorizza questa revisione dopo Task0062;
non autorizza un nuovo esperimento né avvia Task0064.

Sono esclusi dati grezzi/preparati, vettori, modelli, HDF, scoring, training, calibrazione,
timing, replay, acquisizioni e controlli dei 184 payload. I percorsi incorporati nelle
fonti sono riferimenti inerti. Non eseguire entrypoint Task0061/0062 o suite storiche.

## Limiti prospettici

45 minuti dal primo controllo osservato (scadenza 20:47:57 CEST), 16 MiB cumulativi
per nuovi artefatti/temporanei/copie e 256 MiB RSS del processo di revisione.
Bytecode disabilitato prima dell'aritmetica; temporanei contenuti in
`/private/tmp/task0063-review`. Misure osservate e limiti di enforcement saranno
riportati senza pretendere una prova globale di tutte le scritture del sistema.

## Validazione pendente

Identità iniziale/finale delle 16 ancore; registro limitato delle ulteriori fonti;
schemi/conti/valori finiti e aritmetica aggregata; intervalli e gate; rapporti CPU
appaiati; simmetrie/profili; ispezione visiva di tre figure; 16 disposizioni audit;
link, integrità JSON/CSV, accordo rapporto/brief, aggiornamenti correnti e diff.

## Risultato scientifico della revisione

La revisione conferma la coerenza degli aggregati: studio ADC condizionalmente
valido e completo, criterio composto compact **negativo**. Il rapporto finale
presenta la contribuzione come confronto auditabile qualità/costo, senza rivendicare
un algoritmo nuovo, stato dell'arte, affiliazione CERN o prontezza rivelatore.

- Ritenzione compact90% esclusa su entrambi i segnali: NI primary upper−.064946/
  −.017094; non è una semplice mancata significatività.
- Compact/reference/PCA escludono il target assoluto primario15% su LQ; tutti
  sostengono quello su A. Mahalanobis LQ è **irrisolto**, non escluso.
- Mahalanobis LQ al taglio empirico15,8375%; bound simultaneo al quantile background
  della popolazione[14,649002%;16,972217%]. Il gap inferiore0,350997827punti riguarda
  la regola, non un'efficienza misurata sotto target.15% è un target prospettico
  del progetto, senza derivazione da un budget trigger reale/luminosità/nuisance/
  funzione di costo deployment. Nessuna soglia o famiglia inferenziale cambiata.
- Mahalanobis migliora compact con lower11,004/7,611punti su A/LQ; migliora reference
  su LQ[3,954;6,456]punti. Reference−Maha su A[−0,567;1,386]punti è irrisolto, non
  equivalenza. PCA conserva il compromesso A peggiore/LQ migliore di compact.
- Rapporti CPU joint B32 mediani compact/reference.962989814 (0/8≤.80),
  PCA/compact.925877925 (1/8),Maha/compact.945206261 (1/8). Tutti mancano median≤.75
  e7/8≤.80. Conservato il blocco compact sfavorevole1.205526537.
- Circa5,48% di costo congiunto inferiore osservato per Maha è utile ma distinto dal
  margine25% richiesto. Costi algoritmo/joint compact18,522/284,881µs,reference
  31,846/295,362,Maha8,691/269,108 per chiamata32eventi. Peso del processing comune:
  interpretazione compatibile con i confini e il source path, non scomposizione
  causale misurata né costo feature ottenuto per sottrazione.
- Secondaria.001 mantenuta: tutti i LQ upper<5%; NI compact esclusa A/irrisolta LQ;
  utilità PCA A irrisolta. Nessun SIC ottimizzato o nuovo intervallo.

**Decisione tecnica:** Mahalanobis come baseline/riferimento pratico per questi12
aggregati e il workload misurato; non compact come compressione riuscita. Nessuna
piena dominanza preregistrata, ottimalità universale o readiness operativa. Chiudere
il ciclo attuale senza Task0064 o ricerca automatica di un gate favorevole.

## Fonti limitate e preservazione

Registro esplicito di31fonti curate, circa1,33MB unici e ogni file≤1MiB:16ancore,
README/development/memory/index, handoff0060/0061, due report v1, summary audit0060,
solo testo di evaluator/statistics/presentation e le tre PNG finali. Gli ulteriori
percorsi vengono identificati prima della lettura e hashati nel registro iniziale.
Il livello di lettura è mirato alle parti pertinenti, non certificazione di ogni
riga storica. L'inventario iniziale dei nomi ha mostrato anche percorsi payload;
nessun payload è stato aperto. Nessun manifest privato o suo file membro seguito.

Le16ancore sono confrontate con byte/SHA256 del prompt prima/dopo. Le altre fonti
immutabili vengono ricontrollate; README/memory/index hanno identità iniziale e
finale distinte perché sono gli aggiornamenti di navigazione autorizzati.
Nessun contenuto di data/artifacts, score/tracce, modello, protocollo, codice/test
congelato o report sperimentale storico modificato. Nessun rehash dei184input.
Task0062 già registrò quello; la ricevuta resta evidenza storica.

La frase0062 «nessun successore avviato» resta storicamente vera. Questo prompt è
un nuovo mandato umano separato, limitato alla revisione0063. Gli aggiornamenti
correnti distinguono quel fatto dal nuovo stato, senza riscrivere la storia.

## Controlli effettivi e risultati

È stato usato Python standard con `-B`, `PYTHONDONTWRITEBYTECODE=1` e temporanei
contenuti prima dell'aritmetica. Nessun import del progetto, NumPy,Torch,SciPy,
h5py,pytest o plotting. Gli script temporanei sono ricevute di revisione fuori
checkout, non una nuova pipeline/framework di test o telemetria.

1. Cinque CSV: schemi, scope, selettori univoci, valori finiti e conteggi
   **24/48/44/408/280 =804righe**. Background16stream+8arm,signal32stream+16arm;
   cost384celle+24rapporti; robustness16identità+176stream+88arm profili.
2. Tutti i conteggi per seed, denominatori e medie finite a eventi condivisi;
   nessun3N. Verifica di punto efficiente/differenza/NI da conteggi, SIC nominale
   già definito e FPR corrispondente, senza curva o estimando nuovo.
3. Copertura esatta della famiglia44:24difference+4NI+16efficiency. Tutti88estremi
   Bernstein ricostruiti dagli endpoint means/variances ddof1 e supporti del CSV;
   errore massimo assoluto0 con la formula congelata. Segno inverso[−upper,−lower]
   verificato per le conclusioni sulle baseline. Non ricostruiti pairing/varianze
   dagli eventi: le statistiche sufficienti restano quelle registrate.
4. Estremi CP:32identità di probabilità binomiale controllate con ricorrenza PMF
   scalare standard, residuo massimo7,82e−13; Wilson residuale≤2,17e−19.
   Verificate le disuguaglianze dei ranghi calibrati[989658,990340]/[998890,999107]
   con la medesima allocazione, senza metodo/intervallo/soglia alternativo.
5. Tutti8arm interval checks e12pair rate checks nei limiti prospettici; qualità,
   NI e utilità classificate supported/excluded/unresolved, oltre ai Booleani.
6. CPU: prodotto cartesiano384celle,32warmup/128timed per cella; tutti24rapporti
   ricostruiti dai mean_ns, media seed prima del rapporto e mediana su8blocchi.
   Costi B32 per i due confini ricostruiti inµs/chiamata. Nessuna selezione di blocchi.
7. Contabilità1contesto,1M/40k/40k,8stream,8.64M/270kB32/0padding; sviluppo/parità,
   CPU11.161.600presentazioni/61.440call e simmetrie8.192/256 separate dagli eventi
   indipendenti. Le ripetizioni non diventano nuovi campioni.
8. Tutte16identità finali e24celle parità qualificate; profili con denominatori,
   somma1M per partizione, sommaaccepted al totale e medie seed coerenti, nessunN<20.
9. Tre figure aperte visivamente senza rigenerazione: etichette leggibili, frazioni
   di efficienza,µs/call e tutti8blocchi corretti. Tabella numerica nel nuovo report
   consente la lettura fine dei bound; nessun problema grafico materiale.
10. Mappa25claim con path/selettori/hash e16disposizioniF01–F16 esplicite. Controlli
    JSON/CSV, link locali, accordo report/brief, stato corrente e diff nella chiusura.

Nessun nuovo pytest/Ruff o suite storica. I3002test+13subtest di0060 e204di0062 sono
risultati storici dei rispettivi bundle, non risultati0063. Nessuna nuova prova di
freschezza remota o hosted CI. Aritmetica aggregata non significa replica indipendente.

## Discrepanze e tentativi della revisione

**Nessuna contraddizione materiale nei risultati.** Discrepanza solo espositiva:
la tabella inglese0062 mostra PCA A22.717% e Maha LQ15.837%, mentre quella italiana
22.718%/15.838%. Gli aggregati esatti sono22.7175%/15.8375%; differenza nell'ultima
cifra mostrata0,001punto. I nuovi documenti usano quattro decimali; originali immutati.

La prima esecuzione di controllo si è fermata su un selettore del revisore chiamato
`reflection`; l'etichetta reale è `beam_reflection`. Corretto soltanto il selettore
nello script temporaneo e ripetuta l'aritmetica sugli stessi aggregati. Non era un
difetto sperimentale, non ha causato accesso ai payload o cambio delle fonti.

## Sedici disposizioni audit

Nel JSON ogniID ha categoria finale, motivazione, evidenza con hash/selettore e
limite residuo. In sintesi: F01/F02/F03/F04/F16 corretti con validazione registrata;
F05/F06/F07/F09/F15 affrontati dal nuovo disegno e dalle evidenze ADC;
F08/F13/F14 restano limitazioni; F10/F11/F12 rami differiti/esclusi.
Le categorie non cancellano i residui: pairing indipendente, capacità/ottimizzazione,
interferenze host e limiti di simulazione continuano a delimitare i claim.

## Limiti scientifici e storia preservata

Cap80epoche,tre seed; generazione indipendente/proporzioni SM/vera cecità ignote;
preselezione e cap oggetti; forte profilo di molteplicità; AP1/26 e SIC descrittivo;
nessuna prova di simmetria fisica/decorrelazione/causa della nonlinearità. Questi
limiti sono espliciti e non sono ragioni per prolungare automaticamente lo studio.

V1LHCO resta ranking moderato e testYES/YES/YES; ADC non lo conferma. Task0034/0036,
Task0052partial/negative, Task0056PCA e0058AE positivi per componente ma pilot
non accettati,24124Bcache lengths/crescita ignota,particle192/192,ONNXexport accettato
versus benchmark fallito e MPS corrente non verificato rimangono invariati.
Nessuna allowance o prontezza operativa ripristinata.

## File, riproducibilità e dipendenze

Consegna intenzionale9path: prompt/handoff0063,report inglese,brief italiano,
claimsCSV,reviewJSON,README,memory1.58,index. Tre figure0062 referenziate senza copie.
Il report contiene circa2144parole di prosa (2684 incluse intestazioni/tabelle alla
prima verifica), entro il mandato2000–3500 più tabelle. Nessuna nuova dipendenza.

La mappa di riproducibilità distingue ruoli/fit da0061,qualità e bound dai3CSV,
costi dal408righe,profili/parità daCSV/summary e storia dai report curati. Gli hash
espliciti permettono il confronto di questi documenti. Non fornisce una verifica
indipendente del pairing evento per evento o dei184payload. Una replica piena o
nuovi dati/modelli/timing richiedono domanda e mandato separati; i vecchi comandi
consumati non sono normali passi di verifica. Nessun Task0064 proposto o avviato.

## Risorse e limiti di osservazione

La richiesta `RLIMIT_RSS` è stata respinta da macOS sia abbassando soft+hard sia
solo soft (`ValueError: current limit exceeds maximum limit`). Non viene dichiarato
un enforcement OS disponibile. La revisione mantiene input totali<2MiB,file≤1MiB,
aritmetica scalare,nessun runtime ML/plotting e controlli del lifetime RSS ai confini.
Il processo aritmetico ha osservato23.298.048B, ben sotto256MiB; i massimi finali e
byte/clock sono aggiunti nel riepilogo conclusivo. È un limite osservativo esplicito,
non certificazione globale del sistema. Riserva conservativa8MiB per scritture
cumulative di file piccoli e temporanei entro16MiB; nessuna delivery copy o cache
esterna. Non viene costruito un monitor globale per affermare tutte le scritture OS.

## Git e chiusura

Branchmain/upstreamorigin/main,base4b03b404. Nessunostage/commit/push/thread automatico.
Solo nove path intenzionali; data/artifacts/modelli/cache/temporanei fuori consegna.
Messaggio suggerito: `docs(research): finalize scientific review and project report`.
La risposta finale termina con status/diff,staging selettivo,review staged,commit
ConventionalCommit e push manuali. Non esiste un nuovo commit di consegna da citare.


Un secondo controllo metadati ha inizialmente assunto int/Boolean nei model_records
0061; sono stringhe provenienti dal CSV. Applicata conversione esplicita di epochs
e confronto letterale True/False nel solo checker; tutti i sei cap80/nonconvergenza
sono confermati. Nessuna fonte scientifica o conclusione corretta per questo motivo.


## Verifica conclusiva e stato della consegna

**completed_final_scientific_review_and_report**, osservato il 2026-10-16T18:18:47.108347+00:00:
950.108s dall'avvio18:02:57UTC, entro2700s senza reset. Il piccolo controllo
metadati finale successivo resta nello stesso clock. Picco lifetime dei processi
standard-library osservati26.427.392B (circa25,2MiB)<256MiB, enforcementRSS OS non
disponibile come dichiarato. Charge logico osservato consegna (incluse per intero
le tre living sources) circa0,61MB, temporanei circa0,09MB; riserva conservativa
cumulativa8MiB entro16MiB. Nessun modello/runtimeML/cache esterna o delivery copy.
Nessuna prova globale di tutte le scritture OS viene affermata.

Controlli finali passati:16ancore prima/dopo e tutte le ulteriori fonti immutabili,
8output identities0062 (5CSV+3PNG),25claim/16disposizioni,649link locali validi,
JSON senza chiavi duplicate/nonfinite,CSV/scope esatti,report/brief concordi,
2144parole prosa/2684totali report. Diff e whitespace puliti;solo9path intenzionali,
indice vuoto. HEAD e riferimento localeorigin/main entrambi4b03b404a47cb75360748a95f15a480523b7c89b.
Questo non è controllo remoto fresco o CI. Nessun comando operativo consumato,
staging,commit,push o thread avviato. Nessun difetto materiale residuo nascosto;
limiti scientifici e limite RSS sono dichiarati. Operational readinessfalse,
nessuna Task0064 o altra attività automatica. È concluso il ciclo di ricerca corrente.


La verifica Git diretta dei sei file nuovi ha poi segnalato i terminatori CRLF
del writer CSV standard come trailing whitespace. Normalizzato a LF soltanto il
nuovo claimsCSV, senza cambiare campi/righe, e verificata l'assenza di CR nei nove
file di consegna. Aggiornato l'hash del nuovo CSV nel riepilogo; fonti storiche
immutate. Check Git diretto e controlli di consegna ripetuti dopo la correzione.
