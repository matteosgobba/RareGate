Autorizzo una sola Fase B della Task0028 secondo il piano congelato con SHA256 canonico:

`77f92d951b034575299ed81d6cf61d19d49430b41b954d03b5d3ec62b1179fa9`

Il consenso copre:

1. Acquisizione del payload fissato `events_anomalydetection_Z_XY_qqq.h5`, record Zenodo 6466204, versione v5, con dimensione e MD5 preregistrati.
2. Custodia del nuovo file e controllo di unicità/overlap mediante i fingerprint originali di tutti i ruoli R&D, esclusivamente per integrità.
3. Preparazione delle otto feature con formule, ordine e scaler congelati.
4. Una valutazione del nuovo segnale per ciascuno dei candidati nativi congelati PCA-v1 e compact-autoencoder-v2.
5. Riuso numerico dei due array di score di background accettati della Task0026.

L’autorizzazione è condizionata al superamento di tutti i gate. Comprendo che il background è già esposto e riutilizzato: questo studio riguarda la generalizzazione del segnale, senza fornire una nuova misura indipendente della generalizzazione del fondo.

Non autorizzo fitting, aggiornamenti dell’ottimizzatore, ricalibrazione o selezione di candidati/soglie in risposta ai risultati. Un accesso interrotto deve comunque essere dichiarato.

Procedi nella stessa Task0028:

- Verifica le identità correnti del piano, dell’accettazione, delle sorgenti, dei modelli, delle trasformazioni, delle calibrazioni e dei riferimenti.
- Registra questo messaggio umano nel registro di autorizzazione previsto.
- Mantieni il codice e il protocollo congelati.
- Esegui una sola volta:
```css
.venv/bin/python -m latenttrigger.evaluation.three_prong --run-final --allow-test --plan-sha256 77f92d951b034575299ed81d6cf61d19d49430b41b954d03b5d3ec62b1179fa9
```

Preserva l’ordine acquisizione → preparazione → PCA → AE → consolidamento, i limiti di tempo/memoria, i batch 4096 con coda completa e tutte le soglie originali.

Un fallimento impedisce le fasi successive. Nessun retry, resume, ampliamento dello schema o modifica dei limiti dopo la prenotazione.

Completa report, summary, handoff, README, indice e memoria secondo l’esito effettivo. Conserva registri e risultati parziali; riporta esposizione e lavoro in-flight anche in caso di interruzione.

Nel resoconto italiano spiega:

- Integrità, layout effettivo, conteggi, unicità e overlap.
- ROC-AUC e AP sul nuovo segnale, con prevalenza dichiarata.
- Efficienza alle quattro soglie congelate, conteggi e intervalli.
- Accettazione relativa TPR/FPR e comportamento nella coda più restrittiva.
- Confronto descrittivo con il segnale a due prong, esplicitando il background condiviso e l’assenza di una nuova analisi di significatività.
- Tempi separati di acquisizione, preparazione, valutazione e reporting.
- Risorse, uscita dei processi e limiti della conclusione scientifica.

Mantieni Task0025 fallita/consumata e particle 192/192 consumato e differito.

Concludi con i comandi Git manuali selettivi. Non eseguire staging, commit o push.
