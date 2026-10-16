# ADC2021: decisione scientifica finale

Task0062, 16 ottobre2026. **Valutazione completata e valida; criterio composto di
compressione negativo.** Il ciclo sostanziale0060–0062 arriva a una conclusione
sperimentale. Non viene avviata Task0063. La prontezza operativa generale resta falsa.

Il compactAE non conserva il90% dell'efficienza del riferimento su nessuno dei due
segnali e non riduce del25% il costo CPU congiunto. I tassi di background sono invece
comparabili secondo tutte le regole congelate. Quindi non possiamo attribuire il
fallimento a una differenza di tasso accettato o sostituire l'endpoint principale.

## Che cosa è stato misurato

Una sola valutazione sui ruoli protetti: **1.000.000 gruppi background,40.000 A→4l e
40.000 LQ→bτ**, otto stream già congelati. Sono8.640.000 score/270.000 chiamate B32;
non8,64milioni di eventi indipendenti. Le tre inizializzazioni condividono gli stessi
40.000 eventi e ogni modello usa il proprio taglio di calibrazione. La media è fra
indicatori di accettazione per evento: nessun ensemble, voto o media degli score.

Nessun nuovo download, fit, passo di ottimizzatore, checkpoint, calibrazione o ricerca
di soglia. I sei AE erano tutti arrivati al limite80epoche: confronto fra quei
modelli a budget finito, non reti ottimali o sicuramente convergenti. Tutte le
allowance di training restano consumate.

La tabella mostra stime ai tagli empirici congelati e, fra parentesi, limiti
simultanei per l'efficienza al quantile della popolazione background, propagando
l'incertezza di calibrazione. Non sono intervalli condizionati al solo taglio empirico.

| Selettore | A→4l, target background1% | LQ→bτ, target background1% | CPU congiunta B32, µs/chiamata |
|---|---:|---:|---:|
| compactAE |37,334% [35,655;39,022]|6,897% [6,178;7,631]|284,881|
| referenceAE |50,528% [49,234;51,807]|10,625% [9,737;11,486]|295,362|
| PCA3 |22,718% [21,289;24,170]|11,905% [10,885;12,968]|266,302|
| Mahalanobis regolarizzato |50,133% [48,773;51,457]|15,838% [14,649;16,972]|269,108|

I costi tabellati sono mediane di otto medie di blocco; le tre medie dei seed sono
combinate prima del confronto. Il gate usa i rapporti appaiati di ogni blocco,
non il rapporto fra questi valori tabellati.

## Vettore dei criteri primari

- **Ritenzione90%: esclusa su entrambi i segnali.** Gli intervalli per
  compact−0,9reference sono[−0,09795;−0,06495] su A e[−0,03595;−0,01709] su LQ.
  Entrambi i limiti superiori sono negativi. I rapporti descrittivi delle efficienze
  puntuali sono73,89% e64,91%, senza attribuire loro un intervallo ottenuto dividendo
  limiti marginali.
- **Utilità compact, limite inferiore≥15%: passa A, fallisce LQ.** Reference e PCA
  hanno anch'essi limiti superiori LQ sotto15%. Mahalanobis ha un intervallo LQ che
  attraversa15%: requisito non dimostrato, non utilità esclusa. Nessun candidato
  sostiene l'intera affermazione di utilità su entrambe le topologie.
- **Tasso comune: passa.** FPR medie effettive compact/reference/PCA/Mahalanobis:
  0,009961667/0,009985667/0,009896/0,009953. Tutti gli intervalli delle medie e delle
  differenze rispettano le tolleranze preregistrate, anche al punto secondario.
  Comparabili entro tolleranza non significa esattamente uguali.
- **Costo congiunto: fallisce.** Mediana degli otto rapporti compact/reference
  **0,962990**, con **0/8≤0,80**; servivano mediana≤0,75 e almeno7/8≤0,80.
  Il blocco sfavorevole1,205527 rimane incluso. L'algoritmo isolato è più economico
  (18,522 contro31,846µs B32), ma non sostituisce il costo diretto con feature/scaling.

Il punto secondario0,001 non salva il criterio principale: nessun selettore supera
la soglia di utilità del5% come limite inferiore su entrambi i segnali.

## Che cosa cambia la baseline semplice

Mahalanobis migliora compact su entrambi i segnali: i limiti inferiori delle
differenze appaiate sono **+11,004 e+7,611 punti percentuali**, ben sopra il margine
preregistrato di un punto. Su LQ supera anche reference: differenza supportata
+3,954…+6,456punti. Su A reference−Mahalanobis resta irrisolto[−0,567;+1,386]punti.
PCA è un compromesso: peggiore di compact su A, migliore su LQ.

Non chiamiamo questo una vittoria completa secondo il protocollo. Per Mahalanobis
mancano sia la dimostrazione del limite LQ≥15%, sia il vantaggio CPU congiunto
richiesto: rapporto mediano su compact0,945206 e solo1/8blocchi≤0,80. Anche PCA manca
il gate CPU e l'utilità congiunta.

**Decisione tecnica:** non scegliere compactAE come risultato riuscito di
compressione qualità/costo. Mahalanobis è il confronto semplice più convincente
per questa rappresentazione, particolarmente su LQ, e rende ingiustificata una
preferenza per compact basata sulla sola rete neurale. Non certificare nessun
candidato come selettore utile su entrambe le topologie secondo l'intero criterio.
Il risultato su A resta forte: circa metà del segnale con reference/Mahalanobis
contro circa1% del background. È una conclusione utile e limitata, non una proposta
di cercare nuove architetture finché il test diventa favorevole.

## Robustezza, selettività e limiti

Parità B32 di reload/ripetizione esatta; tutte le24combinazioni stream/formato
B1/B32/B512 qualificate, nessuna esclusione o tolleranza cambiata. Le16verifiche di
rotazione0,7rad/riflessione sui512eventi finali fissati passano: feature scalate e
score identici, zero cambi di decisione;8.192score trasformati/256chiamate aggiuntive,
separati dal passaggio originale. Le identità degli aggregati non dimostrano una
simmetria fisica perfetta del rivelatore.

La selezione dipende molto dalla molteplicità. Reference/Mahalanobis accettano
92,36%/94,58% del background con almeno tre leptoni, contro0,0748%/0,1612% di quello
con un leptone. Sono profili descrittivi con denominatori espliciti; nessuna prova
di decorrelazione causale né efficienza per sottoprocesso SM senza etichette.

Il file background effettivo contiene13.451.915righe/13.449.154gruppi, non i4milioni
nominali del descrittore. Le proporzioni SM nominali non sono state verificate.
ADC è simulazione prefiltrata sui leptoni, con oggetti troncati dal publisher e
12aggregati nuovi. Non conferma il precedente modello LHCO. Holdout statistico,
indipendenza del generatore, nuovi processi e vera cecità sono affermazioni diverse:
la deduplicazione esatta non prova indipendenza generativa. AUC/AP rimangono
secondarie; AP usa prevalenza artificiale1/26. SIC nominale non è significatività
di scoperta, rate LHC o stima con luminosità/nuisance.

Il freeze0061v2 e tutti i184file sono verificati prima/dopo; il primo freeze ritirato
rimane ritirato. Il primo adattatore0062 ha fallito sul nome di provenienza dello
sviluppo prima di aprire righe/inferire/misurare: correzione versionata e qualificata
con202test prima di ogni tempo/esito, tentativo conservato. Un precedente errore di
teardown generato rimane registrato. Il gruppo finale comprende204test coerenti,
con controlli scientifici/core/ADC/audit e presentazione; escluse le matrici native
storiche costose e i rami MPS/ONNX/streaming non modificati. I test includono lavoro
numerico/modelli/optimizer su giocattoli e non dimostrano utilità fisica.

Una sola matrice CPU completa:384celle,49.152chiamate misurate,12.288warmup, tutti
i seed e blocchi; nessun retry favorevole. RSS lifetime massimo del worker reale
912.277.504B, intero studio circa5,05GB sotto8GiB, un worker e zero servizi. Budget
2ore e20min CPU rispettati; la matrice richiede13,739s e il ciclo finale15,539s.
Sono osservazioni di RSS/storage propri e limiti di allocazione, non una prova OS
di ogni scrittura o picco. La prima anteprima grafica su soli aggregati non aveva
un sampler RSS separato; la presentazione finale è osservata e il limite è esplicito.
Bytecode/cache disabilitati o contenuti; nessun reset di cache o pilot storici.

[Report inglese completo](decisive-adc-results.md),
[sintesi strutturata](../results/tables/final/task0062-adc-evaluation-summary.json),
[44intervalli](../results/tables/final/task0062-adc-paired-inference.csv),
[costi completi](../results/tables/final/task0062-adc-cpu-costs.csv) e
[handoff italiano](handoffs/0062-adc-final-evaluation-and-conclusion.md).
Task0059, esposizioni e pilot falliti/consumati, correzioni0060/0061 e prontezza
operativa falsa restano preservati. Nessun nuovo esperimento viene avviato.
