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

# 10/06/2024

# Branch better-upload
Migliorato l'upload dei file tramite API del gatto.

File: /CheshireCatAPI/uploadfile.py
```python
def upload_file(
    filepath: str,
    filename: str,
    url: str,
    stream=None,
    user="user",
    type="text/plain",
) -> any:

    files = {"file": (filename, stream or open(filepath, "rb"), type)}
    data = {"chunk_size": "", "chunk_overlap": ""}

    headers = {"accept": "application/json", "user_id": user}

    response = requests.post(url, headers=headers, files=files, data=data)

    return response
```

Per capire quanto viene ricevuta una risposta viene aperta una websocket con lo stesso nome utente di quello usato per fare l'upload, e si aspetta la risposta del gatto.

File: /CheshireCatAPI/websocket_functions.py
```python
def on_message(message: str) -> None:
    json_message = json.loads(message)

    if json_message["type"] == "notification":
        content_message: str = json_message["content"]

        log(content_message, "INFO")

        if content_message.startswith(config.rabbit_finished_message):
            config.message_called()
```
