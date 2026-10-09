# Task0026 — Actual human Phase B authorization

Autorizzo la Fase B della Task0026 secondo il piano congelato con SHA256 canonico:

`2c97dc2ac903de4a911968bc2f97725cd3d80e18498b1003604c9e4562e3d86f`

Il consenso copre un unico passaggio sui 150.471 eventi `test_background` e sui 100.000 eventi `test_signal` per ciascuno dei due candidati nativi congelati:

1. PCA-v1.
2. Compact-autoencoder-v2.

Sono consapevole che il primo accesso espone il test held-out anche se l’esecuzione viene interrotta. Non autorizzo riaddestramento, ricalibrazione o selezione dei candidati in risposta ai risultati di questa valutazione.

Procedi nella stessa Task0026:

- Verifica che piano, sorgenti, dipendenze, modelli, calibrazioni e store corrispondano alle identità approvate.
- Riutilizza la readiness e l’accettazione della Fase A; non ripetere il controllo di custodia consumato.
- Registra questo messaggio umano nel registro di autorizzazione previsto, vincolandolo al piano e all’accettazione correnti.
- Esegui una sola volta il percorso protetto:
```css
.venv/bin/python -m latenttrigger.evaluation.guarded --run-final --allow-test --plan-sha256 2c97dc2ac903de4a911968bc2f97725cd3d80e18498b1003604c9e4562e3d86f
```

Mantieni ordine PCA poi AE, batch 4096 con code complete, soglie, precisioni, metriche e limiti congelati. Un fallimento impedisce il candidato successivo; nessun retry o resume automatico.

Conserva tutti i registri di accesso e gli eventuali risultati parziali. Riporta l’esposizione effettiva anche in caso di interruzione.

Se la campagna viene accettata, completa tabelle e figure scientifiche, report, summary, handoff, README e memoria. Spiega in italiano:

- ROC-AUC e AP, con prevalenza dichiarata.
- FPR del background ed efficienza del segnale alle quattro soglie congelate, con conteggi e intervalli.
- Punti empirici a FPR/TPR fissati, distinti dalle soglie calibrate.
- Differenze tra PCA e AE e loro relazione con capacità e costi CPU accettati.
- Risorse, tempi, uscita dei processi e limiti dell’interpretazione.
- Quale conclusione scientifica è sostenuta dai dati e quale prossimo passo è giustificato.

Mantieni Task0025 fallita/consumata e i suoi rapporti prestazionali provvisori. Particle resta 192/192 consumato.

Concludi con i comandi Git manuali selettivi. Non eseguire staging, commit o push.
