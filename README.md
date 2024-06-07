# foglietti-cat
Use the CheshireCat AI to explain and read medicine informations

# Argomenti riunione 07/06/2024

(R) -> Richieste

- Siamo riusciti ad implementare la callback durante l'upload dei file

- Fornire la documentazione su un repository sullo stato attuale del lavoro, da tenere aggiornato (R)

- Il gatto non dà infomrazioni di farmaci di cui non ha la conoscenza in MODO DETERMINISTICO (R)

- L'estrazione del nome del farmaco deve includere un match tra l'input fornito e l'elenco dei farmaci presenti (anche riguardante i vari farmaci disponibili) (R)

- Far evitare al gatto di rispondere a domande la cui risposta non è specificata direttamente nei foglietti illustrativi (per esempio far rispondere alla domanda "Qual è la differenza tra l'aspirina e l'acetilcisteina?" ?).

- Non popolare la memoria dichiarativa; lavorare sul miglioramento della funzione di distanza e predisporre un livello di soglia per lo score al di sotto della quale il gatto non risponde. (R)

- Non far rispondere al gatto a domande riguardanti un farmaco se il context della domanda è impostato su un altro farmaco ( Per esempio se gli ho detto di parlarmi dell'aspirina, non mi risponde a domande sulla tachipirina) (R)

- Approfondire l'hack del # per escudere una specifica parte del prompt dalla domanda (es. # non usare il tool #).

- Per le informazioni tabulari bisogna:

  - Spiegare nel prefix la struttura con cui viene fornita la tabella
  - Struttura le informazioni per header di colonna e di riga e passare questa struttura al llm per parsare il risultato finale
  - Documentare in un pdf degli esempi di tabelle analizzate dal parser e descrivere gli eventuali problemi (R)

- Organizzazione del lavoro su git:
  - main -> conserva il codice che funziona in attesa di ulteriori merge
  - deve essere staccato un branch per ogni task, nuovo branch -> nuova task
