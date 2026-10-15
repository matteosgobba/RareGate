# Task0051 — Fondazione software streaming con sole fixture generate

## Metadata, obiettivo e stato

2026-10-15, Europe/Rome. Stato **`completed_software_only_development_streaming_foundation`**;
readiness **`requires_native_characterization_and_operational_authorization`**.
Implementati core e verifiche dichiarate, senza acceptance della campagna fisica.

Base effettiva `3521c8f6c61e63f32ae63eb6892043b4c267d856`, branch `main`, upstream
`origin/main`, riferimenti locali0/0,686file tracciati, indice/albero inizialmente
puliti. Task0050 è committato; Task0049 resta commit42ab4458. Le basi storiche dei
due task e tutti i loro artefatti rimangono intatti. Nessun fetch/verifica remota,
push o hosted CI implicato. Memoria1.45→1.46 in place. Nessuna modifica preesistente.

Prompt allegato copiato integralmente prima del codice; handoff iniziale scritto
prima del lavoro sostanziale. Letti sviluppo, memoria, README/indice, Task0050
protocollo/spec/summary/handoff, pyproject, ignore e init del package. Nessun
AGENTS.md applicabile. I tre pin forniti20769/43882/23611B corrispondono esattamente;
manifest/hash delle evidenze nel summary. Nessuna espansione dei path embedded,
helperTask0049, riconciliazione57fonti o payload quantitativo storico.

## Cosa funziona e perché il confine è limitato

[Report inglese](../development-streaming-software-foundation.md),
[config fixture-only](../../configs/streaming/development_streaming_foundation_v1.json)
e [summary software](../../results/tables/final/task0051-development-streaming-foundation-summary.json)
descrivono i nuovi moduli isolati `src/latenttrigger/streaming/`: protocol,
transport, records, generated, supervision, fixture e init. Un solo test mirato e
uno script di validazione esclusivamente generata. Nessun modulo legacy modificato.

Descrittori little-endian64B, token fixture16B obbligatorio e reserved-zero;
slot metadata64B,64slot,4096control: **12288B condivisi**. Produttore/supervisore/
consumer sono ruoli spawn distinti. Tutti gli accessi slot/control usano un mutex
comune: pubblicazione tail linearizza ammissione. Un try non bloccante distingue
contention/capacity. Dequeue rende riutilizzabile lo slot ma trattiene credito;
ring+staged+active≤64. Il commit terminale pubblica output posseduto e libera
credito una volta. FIFO, m1…8, oldest-admission1ms, partial finale a chiusura.
Nessun lock durante lavoro/logging/sleep normale; il lock trattenuto è soltanto
il fault avversario esplicito. Non ci sono Queue/Pipe/socket per messaggi evento,
ack o risultato; bootstrap/sentinel spawn restano infrastruttura del runtime.

Il produttore usa tempi lazy `t0+floor(k*10^9/rate)`, lag>2ms missed, massimo4
nonstale tentativi per wake, nessuna submit≥H o feedback da completamenti. U è
la sequenza simbolica0..127/448..575/896..1023, identità presentazione distinta
posizione. Le formule768/500-2500-5000 sono testate senza lanciare24casi.
Gather stabile a layer dei duplicati, selezioni crescenti esatte e scatter FIFO
preservano ogni occorrenza. Backend unico di memoria generata, tabella artificiale,
feature/score aritmetici e quattro soglie esplicitamente artificiali. Riferimento
indipendente con indexing/comparazioni scalari bypassa i wrapper nuovi; strict>
rifiuta tie, maschere tutte false completano comunque il servizio.

Nessun provider HDF, path operativo, modello pubblico/congelato o fallback reale.
Import/help non creano risorse/processi; modalità non supportate falliscono prima
di accessi payload/import numerici. L'interfaccia futura non implementa handles,
cache/gate fisici o parità score/features congelati.

## Memoria condivisa: fallimento preservato e scelta esplicita

Il primo tentativo nativo POSIX `SharedMemory` è fallito in setup con EPERM,
prima di avviare produttore/consumer o generare array. Il risultato non è stato
rimpiazzato né chiamato pass. La versione seguente usa un **file temporaneo
posseduto mappato shared**: medesimi12288B/layout/mutex, creazione/unlink del
supervisore, attach/close dei figli. Non è una coda di file-messaggi e non esiste
fallback automatico. I12288B di backing storage stanno entro il cap; non sono un
secondo buffer RAM. Nessun privilegio richiesto o modifica al Task0050 necessaria.

Un mutex e4Event spawn corrispondono a21SemLocks. Python3.12/resource_tracker
resta responsabile della loro gestione; il mapping file è esplicitamente chiuso/
unlinked, non registrato come POSIX SharedMemory. Nessun warning tracker-leak nei
console conservati. Non è provato il backing kernel/nativo≤65536B: P2 rimane aperto.

## Record, contabilità e lifecycle

Event/batch record512B versionati/CRC, timestamp nullable con bit di validità e
reason, overflow esplicito. Producer unico writer eventi, consumer batch/output,
32record fase512B per ruolo. Supervisor legge dopo stop/reap: nessun doppio writer
sullo stesso record. Record assente non vale timestamp0; scrittura torn/corrotta
invalida contabilità senza inventare side effect. Liste/mapping di riconciliazione
hanno cardinalità≤768. Batch registra anche intent/return degli stadi e subread;
proiezione a cutoff arbitrario/H/stop separa stati e denominatori.

O=U+M+S; S=J+Rcapacity+Rcontention+A; A=Qring+Qstaged+X+C+F+K.
U e in-flight restano dopo abort, niente pending-zero fittizio. Output disponibile
resta C se il check seguente fallisce; quattro Booleani non sono quattro eventi.
Con avvio fallito senza t0, H è assente e le offerte sono non iniziate.

Clock servizio perf_counter_ns e supervisione continua Mach, alternativa portabile
CLOCK_BOOTTIME; fake clock/monitor per boundary e fault.2s no-progress/operazione,
5s drain e gap250ms distinti dalla deadline100ms illustrativa, che è osservazione
workload. Native fixture≤5s incluse cleanup≤2s, riserva cleanup interna al timer.
Cleanup non acquisisce il mutex morto o attende ack finale: stop/join/terminate/
kill/reap, close/unlink posseduti, ripetizione unlink sicura. Forzatura non rende
normale il caso. Errori di journal/close non impediscono il tentativo di release.

## Verifiche effettive, fallimenti e versioni

**82 test focused pass**, lint/format pass. I pass intermedi68/73/77/80 restano
separati; nessun full suite storico/fixture model o regressione larga eseguito.
Nessuna utility shared legacy cambiata. Test indipendenti coprono byte/offset,
reserved/token/overflow, timeout/horizon/catch-up, crediti staged/active, tutte le
forme, callback illegali, proprietà/no-alias/tie/nonfinite, record/CRC/cutoff,
incertezza/annullamento, monitor/deadline e failed start/leak/cleanup. Audit import/
help/malformed mode e root region impediscono payload operativi; AST vieta vecchi
import e API message-queue. Prime segnalazioni lint/formato corrette, senza test
nativi o campagne storiche implicite.

| Versione | Tentativi / offerte configurate | Esito effettivo |
| --- | ---: | --- |
| v1 |1 /128 |POSIX setup EPERM,0figli/input; sette scenari non tentati |
| v2 |8 /296 |Otto check software pass, inclusi5fault previsti: read prima/dopo return, dopo output, mutex morto e secondo start fallito |
| v3 |3 /144 |Check wrap, dopo output e mutex morto pass dopo affinamento commit output/timestamp intent |
| Totale |**12 /568** |11check software attesi pass,7casi intenzionalmente anormali e4normalmente drenati; limite12esaurito |

I source snapshot effettivi delle versioni native sono conservati ignored e
hash-bound. Dopo v3 sono stati aggiunti guard errori journal/close/snapshot in cleanup
e precheck overflow terminale, verificati deterministicamente nei82test; nessun tredicesimo tentativo,
nessuna pretesa di full matrix nativa fresca sul sorgente finale. Il core reale
spawn/mapping/servizio è quello esercitato, con tale delta dichiarato.

Intervalli di validazione registrati:4.656941582s totali contro90s; massimo run
1.510224833s contro5s. I comandi esterni inclusivi di altro lavoro occupano circa
5.12s, clock/scope distinti senza sottrazione. Diagnostica/source snapshot ignored
1.358.584B al reporting, ben sotto16MiB. Nessuna ulteriore invocazione nativa.

Contabilità aggregata ai diversi stop:411due =11unresolved+2missed+398submitted;
398=329admitted+32capacity+37contention;329=318completed+9ring+2active.
29offerte future nei processi avviati, altre128del setup mai avviato. Le due prove
wrap mantengono1/3rifiuti contention e127/125completati, senza trimming/retry.

Lavoro nativo generato:264read intent,319righe returned (1read incerto);
262feature/score stub call,318righe;260riferimenti indipendenti,316righe;
1272Booleani output +1264comparazioni reference. Dieci backend consumer hanno
costruito tabelle generate. L'attività numerica dei test unit è positiva aggiuntiva,
non sommata arbitrariamente a questi conteggi nativi. Nessun forward/modello
pubblico o inferenza operativa; nessun global-zero numerico/timing.

RSS lifetime osservato massimo: supervisor25.591.808B, producer25.264.128B,
consumer33.800.192B; somma massima dei picchi per run84.623.360B. Pagine condivise/
picchi si sovrappongono;0nelle fasi non osservate non significa0memoria. Gap massimo
monitor21.533208ms, cleanup32.068291ms. Non misurati native reserve/global RAM/device
né processi utente non pertinenti. Append evento fino714000ns, batch173625ns;
tre osservazioni evento superano il proposto50µs. Restano visibili e non certificano
50/200µs operativi, distribuzioni di overhead o throughput dello studio fisico.

## Risorse e matrice P1–P4

Core:12288B mapping;786432B event+batch a768record ciascuno;49152B fase;
9216B output. Peak backing storage857088B a768,194048B a128. Inventario numerico
fixture conservativo34080B, byte di alias non duplicati. Cardinalità Python/JSON
bounded, JSON≤65536B, ma byte Python/native/kernel non sono un bound dimostrato.
RSS outer guard producer64/consumer1024/supervisor128MiB, aggregato1216MiB; nessuna
prova di fattibilità decoder/modello reale. Scope fixture12×128/1536,5s/90s/16MiB
rispettato; non è un sistema di grant/allowance o una prenotazione.

| Gate | Stato e limite |
| --- | --- |
| P1 |Core implementato, prove deterministiche e percorsi multiprocess osservati; guard cleanup finali deterministici soltanto. Fondazione software completa |
| P2 |Layout/cardinalità/copie e osservazioni proprie parzialmente risolti; backing21SemLocks, heap Python/native/librerie, HDF/cache/model workspace e thread effettivi aperti |
| P3 |Clock/monitor/safety/cleanup implementati e limitate osservazioni generate; scheduling/clock/supervisione/overhead full service ancora da caratterizzare |
| P4 |**Non concesso**:0raw/HDF/custody/modello/operazioni; studio24×768 e840s rimane prospettico |

Prossima decisione: scope separato per caratterizzazione nativa e implementazione/
autorizzazione operativa, dopo revisione dei gap. Nessun Task0052 o campagna fisica
segue automaticamente. Chiusura CPU/sintetica Task0049 preservata; Task0036
`unresolved_no_acquisition`, gateTask0034, YES/YES/YES, particle192/192 consumati/
canonical differita e tutti gli esiti storici invariati. Task0024 export accettato
non sana Task0025 performance fallito; nessun claim MPS attuale. Correttezza generata
non dimostra utilità strict-tail, efficienza fisica, causa nonlineare o detector
readiness; ricerca indipendente, nessuna affiliazione ufficiale CERN/esperimenti.

## Riproducibilità, file e verifica finale

Comandi mirati nel report; --help è senza effetti. I12tentativi nativi del task
sono esauriti, nessun comando di riproduzione lanciato automaticamente. Summary
contiene hash source/config/prompt, versioni native, esiti e limiti. Log/binari/
source snapshot sono ignored sotto data/task0051-validation, senza payload per
evento curati. Nuovi17file complessivi inclusi i3shared aggiornati:7moduli,1test,
1script,1config,1report,1summary,prompt/handoff,README/memoria/indice.

JSON/layout/arithmetic/flag/unità, link nuovi/modificati, hash evidenze immutati,
scope Git/index verificati staticamente. Nessuna installazione, raw/HDF (neppure
metadata/hash), array membership/golden/scientifici, modello pubblico/congelato,
reconstruction/fit/optimizer/calibration/science/acquisizione/replay/controller
storico/device survey/prenotazione operativa. Positive misure/fixture storiche
rimangono storiche. Ambiente esistente Python3.12.12/ruff0.16.10, nessun update.

## Git manuale — ultimo passo

Nessuno staging/commit/push eseguito. Task0049 eTask0050 sono già committati e
non hanno modifiche pendenti; questo lavoro dipende da3521c8f6, senza riscrivere
basi storiche. Escludere log/binari/snapshot fixture e qualsiasi modifica estranea.
Revisionare i file nuovi collegati e il diff, quindi staging selettivo e review
completa staged prima di commit/push su main→origin/main:

```sh
git status --short --branch
git diff --check
git diff -- README.md docs/project-memory.md docs/handoffs/README.md
git ls-files --others --exclude-standard
git add -- src/latenttrigger/streaming tests/test_development_streaming_foundation.py scripts/validate_development_streaming_foundation.py configs/streaming/development_streaming_foundation_v1.json docs/development-streaming-software-foundation.md results/tables/final/task0051-development-streaming-foundation-summary.json docs/prompts/0051-development-streaming-software-foundation.md docs/handoffs/0051-development-streaming-software-foundation.md README.md docs/project-memory.md docs/handoffs/README.md
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "feat(streaming): add data-free streaming foundation"
git push origin main
```
