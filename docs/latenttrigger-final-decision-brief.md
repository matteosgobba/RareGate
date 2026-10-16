# LatentTrigger — Decisione scientifica finale

16 ottobre 2026, Europe/Rome · Task0063 · Revisione delle sole evidenze accettate

**Il progetto ha prodotto un confronto scientifico valutabile fra qualità e costo. La compressione con compactAE non ha raggiunto l'obiettivo preregistrato; Mahalanobis emerge come baseline pratica raccomandata per questa rappresentazione e il carico misurato.** La validità condizionale dello studio, il successo dei singoli confronti e il superamento del criterio composto sono conclusioni distinte. La prontezza operativa resta **falsa**.

## Che cosa è stato ottenuto

ADC2021 è simulazione con preselezione leptonica e cap del publisher su MET/4 elettroni/4 muoni/10 jet. Il background effettivo contiene 13.451.915 righe / 13.449.154 gruppi esatti, contro quattro milioni nominali nel descrittore; le proporzioni SM effettive e l'indipendenza generativa non sono state stabilite. Deduplicazione esatta e separazione dei ruoli controllano duplicati e feedback, senza dimostrare vera cecità o generazione indipendente.

Il protocollo ha separato 200.000 gruppi training, 50.000 selection, un milione calibrazione, un milione background finale e 40.000 eventi per ciascun segnale A→4l e LQ→bτ. Dodici aggregati invarianti e scaler appresi solo sul training alimentano compactAE da 271 parametri, referenceAE da 1.999, PCA3 e Mahalanobis con shrinkage fissato a 0,1. I sei AE usano tre seed separati, con minimo selection proprio: tutti raggiungono il cap di 80 epoche. I risultati riguardano questi fit a budget finito, non reti convergenti/ottimali o tutti i metodi non lineari.

Task0062 ha eseguito un solo contesto finale: 1.000.000 background + 40.000 A + 40.000 LQ su otto stream, **8.640.000 score / 270.000 chiamate B32**. Gli stessi eventi condivisi fra seed restano 40.000 per segnale, non 120.000; nessun ensemble. I tassi effettivi risultano comparabili entro le tolleranze congelate a entrambi i punti.

## Perché la compressione compact fallisce

Al punto primario, target background 1%, le efficienze ai tagli empirici e i limiti simultanei al quantile della popolazione background sono:

| Selettore | A→4l, % [limiti] | LQ→bτ, % [limiti] |
|---|---:|---:|
| compactAE | 37,3342 [35,6553; 39,0218] | 6,8967 [6,1783; 7,6306] |
| referenceAE | 50,5283 [49,2335; 51,8072] | 10,6250 [9,7367; 11,4864] |
| PCA3 | 22,7175 [21,2887; 24,1704] | 11,9050 [10,8848; 12,9682] |
| Mahalanobis | 50,1325 [48,7729; 51,4571] | 15,8375 [14,649002; 16,972217] |

I limiti incorporano incertezza di calibrazione e molteplicità della famiglia congelata di 44 intervalli; non sono intervalli condizionati al solo taglio empirico. Gli intervalli compact−0,9reference sono [−0,097949; −0,064946] su A e [−0,035947; −0,017094] su LQ. Entrambi i limiti superiori negativi **escludono la ritenzione del 90%**. Compact soddisfa l'utilità su A, mentre il suo limite superiore LQ esclude il target del 15%; anche reference e PCA lo escludono su LQ.

Il costo congiunto compact/reference ha mediana appaiata **0,962989814**, con **0/8 blocchi ≤0,80**. Servivano mediana ≤0,75 e almeno 7/8 blocchi ≤0,80. Il blocco sfavorevole 1,205526537 resta incluso. Il fallimento del margine richiesto non dimostra lentezza uniforme né violazione di un cap di risorse.

## Che cosa dimostra Mahalanobis e che cosa significa il 15%

Il **15% è un target prospettico di utilità del progetto**, non una soglia universale di validità scientifica o un requisito dimostrato di un rivelatore. Il protocollo non lo deriva da un budget trigger LHC reale, da luminosità/nuisance o da una funzione di costo di deployment. Questa giustificazione applicativa rimane limitata. Il criterio viene conservato senza sostituirlo con un target favorevole e senza introdurre una nuova affermazione confermativa.

Mahalanobis misura **15,8375% LQ al taglio empirico**, già sopra il 15%. Il suo intervallo simultaneo [14,649002%; 16,972217%], per l'efficienza al quantile background della popolazione, attraversa il target: **non dimostra nessuno dei due lati**. Lo scarto di circa **0,351 punti percentuali** riguarda il limite inferiore richiesto dalla regola, non una misura di efficienza sotto target. Una mancata dimostrazione di quel requisito non rende invalida l'efficienza osservata o i confronti appaiati.

Mahalanobis migliora compact con limiti inferiori di **11,004 punti percentuali su A e 7,611 su LQ**, oltre il margine preregistrato di un punto. Su LQ supera anche reference con intervallo **[3,954; 6,456] punti**. Su A, reference−Mahalanobis **[−0,567; 1,386] punti** rimane irrisolto: non è una prova di equivalenza. PCA mantiene il suo compromesso, peggiore di compact su A e migliore su LQ.

Questi sono risultati utili e circoscritti. Non soddisfano la dominanza semplice completa del protocollo, perché il target assoluto LQ resta irrisolto e manca il margine CPU richiesto. Nessun selettore sostiene l'intera utilità su entrambe le topologie. Il punto secondario 0,001 resta sfavorevole su LQ: efficienze compact/reference/PCA/Mahalanobis 0,9667%/1,5958%/2,0750%/2,6625%, con tutti i limiti superiori sotto il target secondario del 5%. La ritenzione compact secondaria è esclusa su A e irrisolta su LQ.

## Il costo e i suoi limiti interpretativi

| Selettore | Score + maschere/output, B32 µs/chiamata | Oggetti in memoria → aggregati/scaling → score/maschere/output, B32 µs/chiamata |
|---|---:|---:|
| compactAE | 18,522 | 284,881 |
| referenceAE | 31,846 | 295,362 |
| PCA3 | 6,530 | 266,302 |
| Mahalanobis | 8,691 | 269,108 |

Sono due confini misurati direttamente, presentati come mediane di medie di blocco. Le medie dei seed sono calcolate prima dei rapporti appaiati. Mahalanobis/compact ha mediana **0,945206261**, circa **5,48% di costo congiunto in meno**, e solo **1/8 blocchi ≤0,80**; PCA/compact ha 0,925877925 e 1/8. Tutti mancano la regola 0,75/7-su-8.

Un costo comune consistente limita l'impatto di uno scorer economico: è un'interpretazione compatibile con i due confini e il percorso sorgente feature/scaling/scoring. Non è una scomposizione causale misurata separatamente. Non sottraiamo i tempi per stimare esattamente il costo delle feature, non sostituiamo il solo algoritmo al gate congiunto e non traduciamo queste misure in throughput fisico. La matrice storica contiene 384 celle, 49.152 chiamate misurate e 12.288 warmup sugli stessi 4.096 eventi di sviluppo.

## Limiti scientifici e rami ingegneristici differiti

Le 24 celle stream/formato sono qualificate e le 16 verifiche finali di simmetria passano senza cambi decisionali. Restano identità matematiche, non simmetrie dimostrate dell'accettanza del rivelatore. Nei profili primari reference/Mahalanobis accettano 92,3622%/94,5827% del background con almeno tre leptoni contro 0,0748%/0,1612% con un leptone: forte selettività descrittiva, senza prova causale o decorrelazione.

AP usa prevalenza costruita 1/26; SIC nominale non è significatività di scoperta o rate LHC. AUC e prestazioni ai tagli rispondono a domande diverse. Non vengono calcolati nuovi punti ottimali, intervalli o soglie. Lo studio rimane condizionale alla simulazione, alla rappresentazione troncata, ai seed e all'indipendenza approssimata dei gruppi.

ADC non conferma indipendentemente il vecchio modello LHCO: v1 conserva ranking moderato, test esposti e limiti delle campagne CPU/sintetiche. Task0034/0036 restano come registrate. Task0052 resta parziale/negativa; la parità PCA di Task0056 e AE di Task0058 resta positiva, ma i pilot complessivi non sono accettati. I 24.124 byte cache di Task0058 sono lunghezze registrate con crescita ignota, non esaurimento del cap. Particle resta a 192/192 passi consumati senza completamento canonico; ONNX export accettato resta distinto dal benchmark fallito, MPS corrente non verificato. Chiudere il progetto scientifico non richiede completare quei rami.

## Decisione, revisione e chiusura

**Raccomandazione:** adottare Mahalanobis come baseline/riferimento pratico per questi aggregati e questo carico misurato. Non scegliere compact come compressione riuscita e non certificare ottimalità universale o deployment. Conservare separatamente confronto valido, compressione negativa, vantaggi qualitativi Mahalanobis, target LQ irrisolto e margine CPU non raggiunto.

Task0063 ha verificato prima/dopo le 16 ancore, schemi e 804 righe dei cinque CSV, conteggi e medie per seed, famiglia e 88 estremi Bernstein, identità degli estremi binomiali/ranghi, tassi, rapporti CPU di tutti gli otto blocchi, simmetrie/profili, figure, link e integrità dei documenti. Le 16 disposizioni audit sono esplicite nel riepilogo. Non risultano contraddizioni materiali; una differenza storica nell'ultima cifra arrotondata è documentata senza modificare le fonti. Non sono stati riaperti dati grezzi/preparati, modelli o vettori, né ripetuti acquisizioni, fit, calibrazione, inferenza, timing, replay o suite storiche. I 3.002/204 test sono ricevute storiche, non nuovi test di questa revisione.

[Rapporto finale inglese](latenttrigger-final-report.md), [mappa claim/evidenze](../results/tables/final/task0063-final-claims.csv), [riepilogo della revisione](../results/tables/final/task0063-final-review-summary.json) e [handoff italiano](handoffs/0063-final-scientific-review-and-report.md) costituiscono la consegna. Il ciclo di ricerca corrente è chiuso; Task0064 non viene avviata. Qualsiasi lavoro scientifico o di deployment futuro richiede una domanda distinta e un mandato separato.
