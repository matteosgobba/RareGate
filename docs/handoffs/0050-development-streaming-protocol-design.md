# Task0050 — Protocollo di streaming di sviluppo, solo design

## Metadata, obiettivo e baseline effettiva

2026-10-15, Europe/Rome. Stato finale:
**`completed_design_only_development_streaming_protocol`**; readiness separata:
**`requires_prerequisites`**. Design completato e verificato staticamente, nessuna
acceptance nativa, implementazione, prova di fattibilità o autorizzazione operativa.

Branch `main`, upstream `origin/main`, HEAD/base effettiva
`42ab4458002997e1ed45ff8ecdd6aae95dd2729f`, commit locale Task0049. I riferimenti
locali HEAD/origin/main coincidono (0/0); nessun fetch o verifica remota fresca,
push o hosted CI è dedotto. Albero iniziale pulito, indice vuoto, 681 file
tracciati e nessun non tracciato. Il quadro di pianificazione era quindi cambiato:
Task0049 è committato, non più un insieme di modifiche pendenti. La sua base
storica `d26d64425da9b738c6d92fd3d852122ca36d92b0` resta intatta, come tutte le
basi dei task precedenti. Completamento, commit e push sono stati distinti.

Letti protocollo di sviluppo, README, indice e memoria; nessun AGENTS.md applicabile
rinvenuto nel percorso del repository. Prompt effettivo salvato integralmente e
handoff iniziale creato prima dell'analisi sostanziale. Versioni iniziali dei tre
documenti condivisi conservate per confronto temporaneo e recuperabili dalla
base Git; dimensioni/hash sono nel summary. Nessuna modifica preesistente Task0049
da attribuire a Task0050. Memoria aggiornata in place **1.44→1.45**; documenti
storici immutati, nessuna correzione retroattiva necessaria.

## Decisione, motivazione e confine

[Protocollo inglese](../development-streaming-protocol.md),
[specifica dichiarativa](../../configs/protocols/development_streaming_v1.json) e
[summary di design](../../results/tables/final/task0050-development-streaming-design-summary.json)
raccomandano solo B8: tutte le sue occupanze 1…8 hanno supporto storico, utile
per studiare un confine nuovo senza un'altra griglia sparsa. Quel supporto non
certifica streaming. PCA sei componenti e AE v2 congelati restano due candidati
fissi, senza selezione basata su fisica o nuovi risultati.

L'esperimento futuro avrebbe tre processi: supervisore, produttore, consumer.
Un ring locale di memoria condivisa trasporta descrittori little-endian da64B;
solo il consumer apre HDF, seleziona righe, decodifica, costruisce le feature
full-particle congelate, esegue score pubblico a forma m reale e quattro decisioni
strette, con copie possedute. È ingresso software di richieste prima di HDF,
non ingresso di byte fisici di eventi o link di rivelatore. Array già decodificati
sposterebbero preprocessing/cache/proprietà nel produttore; payload codificati
richiedono un codec/framing indipendente oggi non contrattualizzato. Nessuno di
questi confronti è aggiunto e nessuna differenza sarà chiamata overhead puro di
trasporto o suo beneficio causale.

La nuova evidenza mancante sarebbe il comportamento congiunto di produttore reale,
ring finito, HDF, feature e decisioni sotto carico esplicito. Può restituire perdita,
ritardi, nessun beneficio o inconclusività; non è un tentativo di riparare i tail
scientifici. La fase CPU/sintetica chiusa dal Task0049 resta chiusa nel suo scope.

## Workload esatto proposto

24 run: 2 candidati ×3 carichi periodici **500/2500/5000 eventi/s** ×2 storie
`reopened/primed` ×2 ripetizioni. Ogni run offre **768 presentazioni**, totale
**18.432**; orizzonti1.536/.3072/.1536s. Ordine completo e case ID univoci nella
specifica: prima ripetizione carichi crescenti/PCA→AE/reopened→primed, seconda
inverte tutti e tre gli ordinamenti annidati. Nessun B aggiuntivo o Poisson.

U concatena simbolicamente `0..127`, `448..575`, `896..1023` del medesimo prefisso
ordinato di1024ID dalla sorgente6999. Le formule dei report danno startB128
0/floor((1024−128)/2)/1024−128=0/448/896; finestre minori contenute. Ogni run
usa U[k mod384], k0…767, due passaggi pianificati, identità distinta per ciascuna
presentazione. **384righe raw** e **1024righe approvate/golden** sono scope diversi;
nessun ID reale è stato letto o elencato. Perdite non vengono sostituite. Righe
ripetute non aumentano gli eventi sorgente indipendenti. Nuovo ordine e gather/
scatter necessitano proprie verifiche e autorizzazione futura.

Arrivi open-loop con tempi interi calcolati pigramente, senza traccia generata:
`t0+floor(k*10^9/rate)`. Ritardo produttore>2ms causa missed; massimo4tentativi
di recupero per risveglio, resto due missed; niente rallentamento adattivo o
submit dopo H. Try-lock non bloccante: contention e capacità sono rifiuti distinti.
Capacità totale **64richieste ammesse**, incluse ring/staging/attive; batch reale
m≤8, timeout più vecchio da ammissione **1ms**, FIFO. A H si chiudono nuove
submit e si drenano i già ammessi, partial finale immediato, massimo **5s**.

**100ms** è deadline illustrativa di sviluppo: overload, overflow e late sono
risultati validi, non stop automatici. Separati producer lag, code, servizio joint,
output−offerta intenzionale, pending e drop. Quantili condizionati ai completati
con n, nessuna latenza imputata ai persi o media di quantili fra run.

## Cache, parità e contabilità falsificabile

Due SHA raw globali futuri, prima/dopo tutti i run, possono scaldare pagine OS.
Per run: membership/golden/un candidato caricati una volta, pre gate su handle A,
chiusura/reset buffer applicativi, riapertura B con cache1MiB/521/.75. Reopened
non legge raw per warm-up dopo riapertura; primed esegue48B8 chain/384righe su B,
poi entrambe le storie misurano U due volte con B persistente. Pre gate toccano
posizioni0…7; golden/riferimenti, custody, run precedenti e host condiviso fanno
parte della storia. **Nessuna storia dimostra cold OS/page cache**; nessun purge,
reboot/reset globale/chiusura app. Il contrasto include lavoro e tempo di priming,
oltre a gruppi eventualmente diversi: non isola un meccanismo di cache.

Pre e post: per m1…8, un riferimento indipendente golden della stessa forma e
due chain raw; feature/score/mask/repeat/identità esatti, finite/owned/strict
`score > threshold`, tie rifiutati. Ogni batch misurato completato verifica feature
con golden e dopo drain riceve un riferimento indipendente con **lo stesso gruppo
e forma realizzati**, ripetizioni comprese, confrontando direttamente i byte degli output conservati
(6144B score e3072B mask per run, transitori in memoria). Nessuna certificazione per gruppi
non osservati, piccoli gate storici o B4096 scientifico. Le tolleranze storiche
non sono allargate; i controlli fuori timer influenzano la coda e vengono dichiarati.

Record evento/batch fissi da512B, timestamp monotoni ns e owner espliciti. A H
si proiettano transizioni linearizzate: O=U+M+S; S=J+Rcapacity+Rcontention+A;
A=Qring+Qstaged+X+C+F+K. Dopo drain normale pending/U/J/F/K=0 e
768=M+Rcapacity+Rcontention+C. Quattro Booleani non sono quattro eventi;
decisione falsa completa comunque servizio. HDF/feature/call/row intent, inflight,
return, fail e stati incerti restano distinti. Un errore di parità dopo output
invalida il run senza riclassificare C come un secondo evento fallito.

## Envelope prospettico, non misurato o concesso

Massimi dell'intero studio, inclusi gate, warm-up e riferimenti:

- Offerte18.432; gate768chain/3456righe; priming576chain/4608righe.
- HDF requests e feature/chain calls≤19.776; raw/feature rows≤26.496.
- Golden fissi384call/1728score rows; riferimenti realizzati≤18.432call/righe.
- Candidate calls≤38.592; score rows≤46.656; Booleani≤186.624.
- 24membership load/167.976record,24golden load/24.576righe,24model/threshold load;
  48handle aperti/chiusi,96check schema; due SHA raw/5.816.520.818B futuri.
- Drain non aggiunge offerte. Nessun lavoro numerico di setup nascosto.

Ring/control12.288B più65.536B bookkeeping nativo; raw134.464B più scratch134.464B;
proposta24temporanei particellari3.225.600B e modello/reference2MiB. Inventario
proposto7.667.952B sotto8MiB array/record, più8MiB Python/serialization. RSS consumer/
producer/supervisor1024/64/128MiB, aggregato1216MiB; nativo512MiB aggregato
(384/64/64). RSS/nativo/pagine condivise si sovrappongono, non sommare come RAM
fisica indipendente. Log4MiB/run×24+8MiBglobali=104MiB, cap128MiB.

Run≤30s incluse setup10, arrivi≤1.536, drain5, reference/post10, cleanup2:
componenti≤28.536s. Totale≤**840s**=24×30+45custody iniziale+45finale+30report/
cleanup finale, nessuna prenotazione. Timeout operativo/no-progress2s, monitor
target100ms/gap massimo250ms, overhead proposto append50µs evento/200µs batch.

La stima113.15759616s applica solo per pianificazione46656righe×storica meanB1AE
.606340ms×fattore4; non è un bound di servizio, budget o prova dei limiti. Host
storico M5/Mac17,2/16GB/arm64 macOS26.6.2; nessun probe attuale. Workspace librerie,
thread decoder, cache OS e contesa restano incerti.

## Prerequisiti, stop e prossimo passaggio separato

P1: revisione/implementazione separata di ordine/gather/ring/contabilità e fixture
data-free per concorrenza/errori/lifecycle. P2: provare inventario/copie/temporanei,
workspace modello/HDF/librerie/sincronizzazione entro cap e thread effettivi CPU
futuri;24temporanei/2MiB non sono allocazioni già dimostrate. P3: caratterizzare
clock tra processi/risoluzione/scheduler/try-lock/overhead/monitoring/cleanup.
P4: nuova decisione operativa che leghi identità congelate, scope384/1024/gruppi,
risorse e verifiche; grant/acceptance consumati non trasferibili. Nessuna macchina
di autorizzazione nuova è implementata.

Stop studio al primo problema di identità/parità/nonfinite, popolazione imprevista,
cap memoria/storage/tempo, accounting perso, clock/sospensione, monitor primario
fallito/gap>250ms/CRITICAL, processo/close/reap/unlink/cleanup falliti. WARN advisory,
unknown opzionale dichiarato. Preservare lentezza, esiti sfavorevoli e run incompleti;
nessun retry automatico o rimpiazzo. Esperimento valido, risultato prestazionale e
utilità scientifica sono tre giudizi separati.

Task0036 resta `unresolved_no_acquisition`; gateTask0034 invariati; esposizione
permanente YES/YES/YES; particle192/192 consumati/canonical differita. Tutti gli
esiti storici accettati/falliti/software-only restano; export ONNX Task0024 accettato
non sana Task0025 performance fallito. Nessun claim MPS attuale. L'ingegneria non
dimostra utilità strict-tail, efficienza fisica, causa nonlineare o detector readiness.
LatentTrigger è ricerca indipendente, senza affiliazione ufficiale CERN/esperimenti.

## File, verifica e limiti effettivi

Creati prompt, questo handoff, protocollo, spec e summary; aggiornati solo README,
indice e sezioni pertinenti della memoria. Nessun modulo runtime/test/fixture/figura.
Letti18file curati autorizzati **968.762B**, più tre sorgenti **solo testo**,7.789B:
`development_raw_adapter.py`, `development_raw_membership.py`, `targeted_raw_service.py`.
Totale univoco **976.551B <4.194.304B**, separato dal bootstrap. Gli altri due
sorgenti opzionali non sono stati letti. Registry57file solo provenienza; nessuna
riconciliazione57, helperTask0049 o summaryTask0046/vettori letto. Path embedded
inerti, link verificati solo per esistenza senza aprire payload.

Controlli statici passati: JSON strict/duplicati/finite e flag no-execution;
24case ID univoci/ordine/matrice;29limiti di conteggio riconciliati, aritmetica
memoria/storage/tempo e prerequisiti; tabelle/spec coerenti;1938parole inglesi
escluse tabelle/diagramma;456link locali esistenti, nessuno mancante; hash18+3
evidenze invariati; diff/index/branch e whitelist otto file. Dettagli nel summary. Nessun test storico/full/native/CI è stato
eseguito. Nessuna operazione raw/HDF/hashraw/array/modello/inferenza/trace/replay/
acquisizione/probe/prenotazione/streaming è avvenuta in Task0050. Attività positive
storiche, incluse misure/fixture/modelli, restano positive storiche: nessun global-zero.

Il prossimo passo è **decidere separatamente lo scope di implementazione dopo
review P1–P4**; non misurare automaticamente, non avviare Task0051. Il design è
reviewable ma non operationally ready. Nuova accettazione o completamento fisico
non sono dichiarati.

## Git manuale — ultimo passo

Nessuno staging, commit o push eseguito. Task0049 è già nella base42ab4458:
nessuna sua modifica pendente da includere, né staging hunk necessario per
separarla. Questo design dipende da quel commit; su una copia con Task0049 non
committato andrebbe prima revisionato/committato separatamente, senza attribuirlo
a Task0050. I tre shared document sono confrontati con i contenuti di questa base.
Revisionare gli otto file, poi solo se il diff è quello voluto:

```sh
git status --short --branch
git diff --check
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git diff --no-index -- /dev/null docs/prompts/0050-development-streaming-protocol-design.md
git diff --no-index -- /dev/null docs/handoffs/0050-development-streaming-protocol-design.md
git diff --no-index -- /dev/null docs/development-streaming-protocol.md
git diff --no-index -- /dev/null configs/protocols/development_streaming_v1.json
git diff --no-index -- /dev/null results/tables/final/task0050-development-streaming-design-summary.json
git add -- README.md docs/project-memory.md docs/handoffs/README.md docs/prompts/0050-development-streaming-protocol-design.md docs/handoffs/0050-development-streaming-protocol-design.md docs/development-streaming-protocol.md configs/protocols/development_streaming_v1.json results/tables/final/task0050-development-streaming-design-summary.json
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "docs(protocol): design bounded development streaming study"
git push origin main
```

I confronti `--no-index` restituiscono normalmente exit1 quando mostrano differenze.
Comandi proposti per l'utente, non eseguiti da Codex.
