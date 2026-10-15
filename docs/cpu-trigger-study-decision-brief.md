# Chiusura dello studio CPU e trigger sintetico — decision brief

La fase dichiarata di misure CPU native e studio sintetico delle code può essere
chiusa. Abbiamo una baseline scientifica congelata, misure computazionali accettate
su confini espliciti e risultati di sistema riproducibili. Non abbiamo ancora
dimostrato un trigger utile per anomalie rare, prestazioni fisiche in streaming o
prontezza per un rivelatore. LatentTrigger resta ricerca indipendente ispirata al
computing LHC, senza implicare affiliazioni ufficiali con esperimenti o CERN.

La baseline confronta PCA e un piccolo autoencoder su due segnali. L’AE ha AUC
osservata circa 0,660 sul two-prong e 0,586 sul three-prong; il vantaggio di ranking
è moderato e si indebolisce cambiando topologia. Non possiamo attribuirlo alla
sola non linearità. Al taglio AE più stretto passano soltanto 56 e 34 segnali su
100.000, contro 116 background su 150.471. Il background è condiviso, quindi non
fornisce due repliche indipendenti. Prevalenza e AP della miscela valutata non
sono tassi fisici LHC. Il [report](cpu-trigger-study-synthesis.md) conserva tutte
le quattro righe di qualità e i sedici punti calibrati originali, senza nuove
metriche, soglie, significatività o intervalli.

Le misure CPU accettate rispondono a domande distinte: adapter su input già
preparati, packing e ritenzione, lettura HDF e costruzione delle feature, catena
diretta raw→score→quattro decisioni. I costi diretti sono primari: sommare componenti
o sottrarre campagne diverse non misura overhead. Il padding del Task0038 esegue
vere righe dummy; i controlli full-B dei Task0045/0047 elaborano eventi reali
aggiuntivi; la fatturazione full-B nel simulatore è un’ipotesi. Anche finestre,
wrapper, cache e denominatori differiscono.

Il Task0047 corrente misura 32 punti nominal-B/m: 17 nuovi e 15 riferimenti
rimisurati, lasciando 137 occupanze su 169 senza misura. Per B128/m10, le medie
natural/control sono 4,455/49,077 ms per PCA e 4,556/50,594 ms per AE, ciascuna
su sessanta osservazioni del proprio caso. Restano tutti i 333 confronti
sfavorevoli. Questi campioni warm e dipendenti non definiscono una distribuzione
universale né certificano input e cache di uno stream fisico.

Il Task0048 completa 6.048 scenari e altrettanti contrasti: 30.240.000 presentazioni,
27.544.586 completamenti, 2.695.414 overflow, pending finale zero e 6.067.628 eventi
tardivi. Sono somme di griglie ripetute da 90.000 posizioni sintetiche, non eventi
indipendenti o un tasso fisico. Il refined next dà natural−control pari a −55
overflow e −21.714 tardivi, ma conserva rispettivamente 77 e 171 contesti
sfavorevoli. Previous dà −160.659 e −399.707, con deficit di 473.944 righe modellate.

Resta mapping sul 9,1235% degli eventi utili e 10,6613% del busy next natural;
previous arriva al 27,3306% e 15,2802%. Le interazioni refined−coarse sono
−459/+589 overflow/tardivi con next e +29.813/+50.377 con previous. Cambiano anche
i controlli: natural/control variano di −504/−45 overflow e −556/−1.145 tardivi
con next; +29.922/+109 e +63.696/+13.319 con previous. Non isoliamo quindi il
beneficio causale delle nuove misure. B8 ha lookup completo ed equivalenza dei
mapping per lato, ma non validazione streaming. P99 riguarda superstiti diversi;
né mapping è un bound fisico e nessuna policy viene scelta.

La prossima decisione consigliata è un **protocollo soltanto progettuale** per
streaming/cache/transport di sviluppo: workload e ruoli ammessi, host e storia
della sorgente, confine temporale, risorse, criteri di successo e arresto, evidenza
indipendente necessaria. Affronta ciò che una nuova griglia sparsa non risolve.
Come obiettivo progettuale iniziale: soli background di sviluppo e modelli
congelati, occupanze entro B1/8/32/128, domande di carico 500/2.500/5.000 eventi/s,
confine ingresso software prima del decode→output delle quattro decisioni.
Vanno distinti cache iniziale, ordine e riuso degli input, transport reale o
in memoria. Successo significa contabilità completa e fattibilità dimostrata;
identità, parità, risorse o deadline non valide impongono arresto. Gli eventuali
budget devono essere derivati e autorizzati successivamente.
Non autorizza implementazione, budget operativo, acquisizioni o Task0050. Runtime,
precisione, altro hardware e particle sono opzioni separate, non prerequisiti.

Il ritorno allo sviluppo scientifico richiede una valutazione indipendente adeguata:
Task0036 resta `unresolved_no_acquisition`, tutti i campioni restano esposti
YES/YES/YES e i gate Task0034 invariati. Particle conserva 192/192 consumati e
canonical execution differita. L’export ONNX Task0024 accettato non sana il
benchmark Task0025 fallito; il vecchio snapshot MPS non descrive disponibilità
attuale. Questa chiusura usa metadata curati e aritmetica descrittiva, senza nuovi
esperimenti. La decodifica incidentale iniziale di vettori incorporati nel summary
Task0046 è dichiarata e corretta nel reader finale; non ha alimentato calcoli.
Sono preservati anche fallimenti e attività positive dei fixture storici.
