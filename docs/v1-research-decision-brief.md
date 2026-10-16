# RareGate v1 — Cosa abbiamo dimostrato e perché ci fermiamo qui

Abbiamo una baseline scientifica congelata, una fase CPU/sintetica conclusa nel suo
ambito e due piccole osservazioni reali d'integrazione, separate per PCA e AE.
**Concludiamo questa indagine preservando risultati e limiti.** Non abbiamo dimostrato
un trigger utile per anomalie rare, prontezza operativa o detector readiness.
Task0059 completa solo il consolidamento documentale; non rende accettati tutti gli
studi descritti e non costituisce certificazione software o release.

PCA a6componenti e AE v2 a155parametri usano le stesse8feature/scaler e calibrazione
originali. Su150471background condivisi e100000segnali per topologia, l'AE ha AUC
0,660064 a due prong e0,585877 a tre; PCA0,468489/0,462953. Sono risultati accettati
copiati, non metriche ricalcolate. Il ranking AE è moderato e peggiora a tre prong.
Alla soglia AE più stretta passano56/34segnali su100000, contro116background su150471.
AP e prevalenza della miscela non sono rate LHC; background condiviso non significa
replica indipendente. Non isoliamo l'effetto causale della nonlinearity né scegliamo
nuove soglie. Task0036 resta unresolved/no acquisition e i gate0034 invariati.

Le sei campagne CPU accettate misurano confini diversi: adapter precaricato,
packing,raw→feature,raw→score/decisioni e confronti m/B. Non si sommano o sottraggono
costi fra confini per inventare una misura congiunta. Le32occupazioni misurate lasciano
137punti mancanti; finestre calde e riusate non sono trial indipendenti. I replay FIFO
sono griglie sintetiche prescritte: conservano contesti sfavorevoli, dipendenza dai
mapping e473944righe di lavoro modellato mancanti con previous-anchor. Cambiano anche
controlli e storia della coda. Nessuna policy o velocità fisica ne segue.

| Osservazione reale separata | PCA /Task0056 | AE /Task0058 |
| --- | ---: | ---: |
| Offerte /completamenti /reject contention |64 /63 /1 |64 /62 /2 |
| Righe raw/feature incluse prove |207 /207 |206 /206 |
| Public calls /score rows /Booleane |174 /342 /1368 |168 /340 /1360 |
| Reference differite per gruppi realizzati |63 |60 |
| Custodia raw della sessione |2pass /5816520818B |2pass /5816520818B |
| Gate e parità del componente |passati |passati |
| Pilot complessivo accettato |false |false |

Task0056 fallisce dopo il PCA valido, prima dei worker AE, per ownership del journal.
Task0057 ripara e qualifica quel percorso su dati generati. Task0058 ottiene poi la
parità reale AE, ma rimane partial per il controllo globale dello storage. Non sono
un esperimento paired, un'unica campagna accettata o popolazioni fisiche nuove.
Task0054 resta separatamente failed/consumed, con due custodie riuscite ma nessun
servizio reale. Quattro mask non sono quattro eventi; i totali includono gate/reference.

L'ingresso trasporta descrittori software prima delle letture HDF, non byte evento
di un detector link. Output owned precede reference differite e accettazione finale.
NominalB8/500richieste/s non prova capacità sostenuta: PCA lavorò m1; AE58gruppi m1+
2gruppi m2. Custodia/gate/caricamenti/storia precedente possono scaldare la cache;
reopenHDF non significa OS cache fredda. Non confrontiamo causalmente candidati,
cache o trasporto e non mettiamo insieme latenze/percentili di sessioni diverse.

Task0058 conserva native_pilot_checks_passed=true,real_AE_integration_parity_observed=true,
ma pilot_accepted=false e P4 consumato. Tre cache del formatter furono scritte fuori
ledger:24124B sono lunghezze correnti allora registrate,32768B blocchi allocati;
dimensioni precedenti e delta ignoti. Il totale osservato12136251B e la riserva
366entry/21563584B stanno sotto32MiB, ma non provano controllo prima della crescita.
Non è cap esaurito o delta misurato di24124B. Nessuna riserva retroattiva, cancellazione,
waiver o nuova inferenza per riparare contabilità. La lezione futura è disabilitare
o controllare preventivamente le cache dei tool, in lavoro source-free separato.

La qualifica generata rimane evidenza positiva di software, aritmetica/modelli
artificiali/processi, distinta dagli originali. Fault attesi possono passare un check
software restando workload invalidi. Task0052 mantiene i cinque exceed e la copertura
finale incompleta;0053 cambia esplicitamente contratto, rendendo50/200µs diagnostici.
Non prova hard real time o costo senza strumenti. Kernel backing,heap/workspace
esatti e thread effettivi decoder restano ignoti. Il jointinner/tracker80MiB non
prova il vecchio16MiB;RSS non dimostra attribuzione esatta.169aspettative con copertura
passante non sono169test puliti insieme;26righe curate non sono26invocazioni native.

Ora la scelta utile è consolidare e fermarsi. Nuova utilità scientifica richiede
una domanda e un percorso indipendente appropriati; nuova evidenza fisica di carico/
cache/trasporto richiede confine,host,workload,criteri e autorizzazione bounded freschi.
Lo studio24×768/840s resta non concesso. Particle canonico resta differito,192/192
consumati;0024exportONNX accettato è distinto da0025performancefallita;nessunMPSattuale.
Esposizione YES/YES/YES e tutti gli esiti storici rimangono. Nessun nuovo task parte.

[Rapporto integrato](v1-research-conclusions.md),
[24 claim tracciabili](../results/tables/final/task0059-v1-claims.csv),
[39fonti/3376089B](../results/tables/final/task0059-v1-evidence-registry.csv) e
[summary](../results/tables/final/task0059-v1-consolidation-summary.json) permettono
controlli descrittivi da aggregati, non riproduzione di payload/distribuzioni o nuove
misure. Task0059 svolge **zero nuovo lavoro operativo**,senza cancellare attività
storica reale/generata. RareGate resta ricerca indipendente ispirata al computing
LHC, senza affiliazione ufficiale CERN/esperimenti o dichiarazioni d'utilità scientifica.
