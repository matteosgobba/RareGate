# Task0055 — Riparazione startup e osservazione tracker, senza retry operativo

## Metadati e decisione

Data: 2026-10-15, Europe/Rome. Stato: **`completed_software_only_streaming_startup_repair`**.
Readiness: **`requires_fresh_bounded_operational_authorization`**; operatività e P4 **false**.
Il nuovo sorgente finale supera tutti i 12 casi generati v2 e i 2 bootstrap CPU
source-free previsti. Questo risultato chiude la riparazione software; non accetta
un pilot reale, una pipeline fisica o lo studio 24 × 768.

Base effettiva: `main`, upstream `origin/main`, HEAD
`0dd42ee74521205b3918a43ef00aacb7be99198d`, indice e working tree inizialmente
puliti, riferimenti locali 0/0. Task0054 era committato, memoria 1.49, ora 1.50.
Nessuna verifica fresca di remoto, push o CI ospitata. Nessun AGENTS applicabile
trovato nei percorsi bootstrap. [Prompt originale](../prompts/0055-streaming-startup-resource-repair.md)
copiato integralmente dall'allegato e handoff iniziale salvati prima del lavoro
sostanziale. Nessuno staging, commit o push eseguito.

## Evidenza storica e difetti confermati

Task0054 resta **`partial_failed_development_hdf_consumer_pilot`**, pilot non
accettato e qualifica generata del suo sorgente finale incompleta. Sono positivi
storici i suoi due SHA256 raw, **5.816.520.818 B** complessivi. Successivamente:
zero caricamenti membership/golden/artefatti modello, aperture HDF, righe feature
e inferenza pubblica; PCA fallisce prima del ready, AE non tentato. Eccezione
esatta di startup e valore RSS rifiutato non furono conservati. Non sono stati
recuperati da nuovi esperimenti. Letti solo report/config/summary/handoff curati,
contratto v2 e sorgenti pertinenti; nessun vecchio journal ignorato o payload.

Il difetto raw-text versus stringa JSON canonica per l'identità Torch è confermato
dal sorgente, ma resta soltanto una causa storica plausibile. Questa task prova
che lo stesso pin canonico è supportato dalle librerie installate oggi. Non
ricostruisce il traceback perso. Sei fonti storiche conservano byte e SHA256,
incluse le tre ancore Task0054 da 17.406 / 47.001 / 180.164 B.

La politica autorizzata cambia esplicitamente la partizione privata
**inner 64 + tracker 16 MiB** nel vincolo **congiunto inner + tracker 80 MiB**.
Outer 48 MiB, producer 64 MiB, consumer 1024 MiB, aggregato 1216 MiB e carica
conservativa residente 512 MiB restano invariati. Il tracker finale raggiunge
**16.842.752 B**, 65.536 B oltre la vecchia partizione; la carica congiunta massima
è **48.332.800 B** su 83.886.080 B. Non è una prova del vecchio limite né del
valore rifiutato in Task0054.

## Implementazione e confini

`cpu_runtime.py` introduce un unico `RuntimeSession.initialize`, usato davvero
da `RealBackend` e dai worker source-free. Imposta prima degli import le sei
richieste di thread a 1, importa NumPy/Torch e helper CPU invariati, configura e
interroga i thread, verifica build canonica e arrotondamento, importa h5py/plugin
senza aprire HDF, ricontrolla i thread e termina a **payload_not_armed**. Nessun
selettore di dati/modello nella policy runtime. La fase payload del consumer è
separata e ricontrolla autorizzazione e identità del bundle: il grant consumato
Task0054 non corrisponde al nuovo sorgente e non viene simulato o riattivato.

`resources.py` valida l'ABI contro gli header SDK installati `sys/proc_info.h` e
`libproc.h`: record 96 B, resident all'offset 8, unità byte, ritorno intero/errno
conservati. Query soltanto del PID corrente o del tracker posseduto, identificato
dalla relazione interna multiprocessing PID/fd; nessuna scansione processi/device.
Stati distinti: not_started, startup_pending, observed, exited, unsupported,
query_error. Il valore positivo o errore viene trattenuto prima della guardia;
assenza non significa zero. Ready/t0 attendono un'osservazione valida entro 250 ms,
con polling massimo ogni 5 ms e monitoraggio continuo. Osservazione persa dopo
ready invalida l'esecuzione. Rimossa la selezione implicita della guardia in base
al nome Task0054/directory; la policy esplicita protegge anche i fixture generici.

Fasi e step precedono ogni azione fallibile. Errori primari, di report e di cleanup
sono campi indipendenti; traceback massimo 8 frame, stato payload, valori attesi/
osservati, RSS corrente e peak disponibile restano delimitati. Cleanup parziale,
limiter e risorse non dipendono dal successo del logging o dal mutex ring. La
correzione finale 0055.2 propaga nel wrapper reale il contesto runtime anche se il
checkpoint fallisce; un report finale è tentato indipendentemente.

Gli audit Python bloccano le radici dati/artefatti/risultati di produzione e tre
config fuori radice, coprendo i 17 file Task0054 senza resolverli o hasharli.
Sentinelle vietano np.load, h5py.File, ProcessedStore, costruttori/loaders/score
modelli nei worker runtime; producer e consumer generati mantengono il divieto
lungo il ciclo di vita. Nei quattro bootstrap: zero tentativi di open vietato,
zero open produzione riusciti, payload false e zero eventi. Import/help/error
non attivano sorgenti o fallback. Nessun HDF, neppure generato, aperto.

## Qualifica congelata, tentativi e risultati

| Gruppo | Versione / bundle | Esito e motivazione |
| --- | --- | --- |
| 1 | 0055.1 — `24eee96cc423fdcc85ec1b60e16cc520d21284693222cdc80aa874496dad33f0` | Tutti i 12 + 2 check passano. Revisione successiva identifica la perdita del contesto runtime nel wrapper di errore reale. |
| 2 finale | 0055.2 — `277539820154b19012d53b5a4ec1f05093244b7efa1877f3e09649cbba43e7d0` | Tutti i 12 + 2 ripetuti sul medesimo bundle finale di 30 pin. Riparazione di correttezza, non ricerca di un campione favorevole. |

Nessuna modifica sorgente durante le prove o dopo il secondo freeze; nessuna
copertura del primo bundle usata per completare il secondo. Consumati **28/28**
invocazioni native: 24 casi generati e 4 bootstrap runtime, **1120 offerte generate**
configurate su massimo 3072, runtime zero. Nessuna terza prova disponibile o
eseguita. I fallimenti iniettati passano solo le loro aspettative software:
interruzioni, record torn e quota/report failure restano workload anormali con
stati pendenti/incerti, non drenaggi validi.

Sorgente finale, casi normali: completati 127/123/122/64/0 su
128/128/128/96/32 offerte configurate. Schedulazione, contesa, rifiuti e quantili
condizionati restano osservazioni per caso, non inferenze di eventi indipendenti.
Su entrambi i gruppi, minimi ricostruibili: **879 righe read, 873 feature/score
aritmetici, 871 reference, 873 servizi completati e 3492 Boolean primari**.
Lavoro perso nei due casi torn resta sconosciuto; non è imputato a zero. Unit test
con numerica generata sono aggiuntivi, senza contare le loro righe come native.

Registrati **2116 append event / 2 superamenti**, massimo **98.667 µs**; **4314
append batch / 0 superamenti**, massimo **67.042 µs**. Un superamento nel caso
contention del gruppo1, uno nel torn finale. Soglie 50/200 µs diagnostiche v2,
nessuna sottrazione observer/control, ottimizzazione recorder o confronto AB/BA.
Le durate inclusive offer/batch e i loro denominatori restano nei risultati.

I quattro worker CPU reali osservano Torch 2.14.1, NumPy 2.5.3, h5py 3.16.0/HDF5
2.0.0, plugin importato; versione plugin non disponibile. Canonical Torch SHA256
atteso = osservato `6d6fa299a6d76bc6add8bfff4916da33cbc1636da24e90df594e6434f918b26c`;
raw-text diagnostico `7dc7bbe085616975d2b87b5c43ed0bd5e4a3a26e8e1013db641518c8d46daa1c`.
Intra/inter Torch 1, determinismo true, rounding 0, entrambi OpenMP 1, controllo
pubblico Accelerate single-thread con setter 0/getter 1, query iniziali/finali
valide. Thread decoder effettivi **unknown**: nessuna decodifica. Le etichette PCA/
AE sono metadati; nessun candidato esiste e le loro durate/RSS non confrontano
modelli. Peak lifetime worker finale 349.306.880 / 374.964.224 B; cleanup limiter
senza errori, exit0/reap normali per tutti.

## Test, tempo, risorse e storage

Finale **96 test focalizzati passati**: 57 nuovi + 36 integrazione stand-in già
pertinenti + 3 pure v2. Oracoli indipendenti per encoding/ABI/query, errori/valori
RSS zero-negativi-eccessivi-tardivi, ownership/PID, clock0 valido, readiness,
uguaglianza limite congiunto, ogni fase di import/inizializzazione, cleanup
parziale, report mancanti e perdita del valore Task0054. Esecuzioni pure totali
419: 418 pass, un primo failure audit sui tre config fuori radice, corretto prima
delle prove native. Un punto del vecchio log diventa NUL nel test che sostituisce
pwrite: log originale preservato e recheck con writer stabile passato. Nessun
rerun nativo nascosto. Lint/format e verifiche statiche JSON/CSV/pin/link/conti
completano la verifica; nessuna full suite storica o installazione.

Ledger immutabile **370 voci / 22.349.984 B** entro **33.554.432 B** per tutto
Task0055, entrambe le versioni, sample/journal, snapshot, report, emergenze,
receipt e copie curate simultanee. Unica radice nuova ignorata:
`data/task0055-validation/task0055`; mai cancellata evidenza per recuperare budget.
Il summary distingue byte logici posseduti e blocchi allocati; nessuna attribuzione
universale a metadata/kernel. Ring, record, mapping e cardinalità v2 restano;
21 SemLock core, 0 espliciti bootstrap/observer, massimo albero 26; **462 nomi
posseduti assenti** dopo i 22 casi streaming. Backing kernel, heap esatto 8 MiB e
workspace nativo 512 MiB rimangono non certificati. RSS non prova queste grandezze.

Intervalli soggetto esterni **9.345746166 + 8.830618916 = 18.176365082 s**, includendo
import, casi, report, finalizzazione, exit e reaping. Riserva receipt observer
4 s per gruppo, fuori dal soggetto: carica **26.176365082 s** su 200 s. Cap gruppo
100 s (soggetto 96, cleanup fino 98, receipt entro 100), ammissione del secondo
sul residuo. Curation statica successiva è fuori dai programmi e non finge una
coda temporale misurata. Cleanup generato massimo 32.220041 ms, gap interno
30.038250 ms, esterno 9.237917 ms; nessun forced/exit anomalo dei supervisori,
gruppi assenti e soggetti reap. L'upper charge conservativo da peak di tutti i
ruoli osservati, anche non simultanei e con pagine sovrapposte, è 503.644.160 B
sotto 512 MiB; non RAM fisica unica o misura di workspace.

## File, limiti e prossima decisione

[Report inglese](../development-streaming-startup-repair.md),
[config congelata](../../configs/streaming/development_streaming_startup_v1.json),
[28 righe curate](../../results/tables/final/task0055-streaming-startup-cases.csv),
[summary](../../results/tables/final/task0055-streaming-startup-summary.json).
Implementazione in cpu_runtime/resources/startup55, integrazioni minime nel core,
consumer, quota, heartbeat e transport; entrypoint e test dedicati. README,
indice e memoria aggiornati in loco a 1.50. Diagnostica privata ignorata esclusa
da Git; nessun array/ID/score reale nei curati.

P1 finale è qualificato. P2 guadagna osservabilità startup/thread/RSS sotto la
politica congiunta; cache/HDF/modelli reali, parity, workspace e decoder restano
non provati. P3 riguarda pipeline strumentata generata/bootstrap, non trasporto
byte rivelatore né prestazione fisica. **P4 non concesso qui**, Task0054 resta
consumato. La prossima decisione separata può essere un nuovo prompt pilot stretto
PCA→AE, due × 64 offerte B8/500 s⁻¹ invariati; non viene emesso o eseguito qui.
Nessun Task0056. Custody/HDF/array/modelli/inferenza pubblica operativi nuovi: **zero**.

Preservati Task0053 storico, Task0052 parziale/negativo, chiusura CPU/sintetica0049,
0036 unresolved_no_acquisition, gate0034, YES/YES/YES permanente, particle192/192
consumati/deferral canonico, export0024 accettato versus performance0025 fallita,
tutti gli altri esiti e nessun MPS corrente. Nessuna utilità scientifica strict-tail,
efficienza fisica, beneficio causale della non linearità, conferma indipendente,
detector readiness o affiliazione ufficiale CERN/esperimento deriva dal lavoro.

## Git manuale

Nessuna modifica preesistente da separare; base e file storici restano. Rivedere
anche i file nuovi; selezionare solo i percorsi Task0055 elencati nella consegna.
Comando Conventional Commit proposto: `fix(streaming): qualify source-free CPU startup and tracker guards`.
Push manuale per il branch effettivo: `git push origin main`, dopo review completa,
staging selettivo e review staged. Non includere `data/`, artefatti, ambienti o log;
non usare `git add .`. Nessun commit Task0055 o risultato CI/push è stato inventato.
