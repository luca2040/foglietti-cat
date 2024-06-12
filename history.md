# foglietti-cat

Use the CheshireCat AI to explain and read medicine informations

## Argomenti riunione 07/06/2024

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

## 10/06/2024

### Branch better-upload

Migliorato l'upload dei file tramite API del gatto.

[uploadfile.py](/CheshireCatAPI/uploadfile.py)

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
---
Per capire quanto viene ricevuta una risposta viene aperta una websocket con lo stesso nome utente di quello usato per fare l'upload, e si aspetta la risposta del gatto.

[websocket_functions.py](/CheshireCatAPI/websocket_functions.py)

```python
def on_message(message: str) -> None:
    json_message = json.loads(message)

    if json_message["type"] == "notification":
        content_message: str = json_message["content"]

        log(content_message, "INFO")

        if content_message.startswith(config.rabbit_finished_message):
            config.message_called()
```

### branch table-embedding

Per poter selezionare solamente le tabelle a cui si sta facendo riferimento è necessario calcolare il vettore di ognuna.
Dato il numero elevato dei point per documento è stata creata una classe che mantiene in memoria i punti di certe query che si ripetono ed evita di ri calcolare il vettore ogni volta.

[optimized_embedder.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/optimized_embedder.py)

```python
class optimized_embedder:
    def init(self, cat: CheshireCat) -> None:
        self.cat = cat
        self.stored_points = {}
        self.last_filename = None

    def embed_table(self, query: str, filename: str) -> List[float]:
        query_hash = hashlib.sha256(query.encode("UTF-8")).hexdigest()

        if filename != self.last_filename:
            self.last_filename = filename
            self.stored_points = {}

        if query_hash not in self.stored_points.keys():
            query_embed = self.cat.embedder.embed_documents([query])[0]
            self.stored_points.update({query_hash: query_embed})

        return self.stored_points[query_hash]
```

---

è stata aggiunta la funzione di cosine similarity

[functions.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/functions.py)

```python
def cosine_similarity(query: List, point: List) -> float:
    return dot(query, point) / (norm(query) * norm(point))
```

---

Il parser ora salva nei metadata un dizionario composto da tabella e embed di essa per ogni tabella, in modo da poter salvare l'embed di ogni tabella nel metadata del point.

[new_pdf_parser.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/new_pdf_parser.py)

```python
return all_text, [{"table": table, "embed": None} for table in tables_text]
```

---

Nell'hook @before_rabbithole_insert_memory si fa l'embed della tabella usando la classe optimized_embedder spiegata prima.

[plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)

```python
@hook
def before_rabbithole_insert_memory(doc, cat):

    if "tables" in doc.metadata.keys():
        for table in doc.metadata["tables"]:
            if not table["embed"]:
                table_text = (
                    table["table"]
                    .replace("(", " ")
                    .replace(")", " ")
                    .replace("[", " ")
                    .replace("]", " ")
                )

                table["embed"] = cat_embed.embed_table(
                    table_text, doc.metadata["source"]
                )

    return doc
```

---

Nell'hook @after_cat_recalls_memories si è aggiunta la parte per calcolare la similarità tra l'embed della tabella e la query per selezionare solo la migliore.

[plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)

```python
        if "tables" in metadata.keys():
            max_score = 0
            best_table = ""

            for table in metadata["tables"]:
                score = cosine_similarity(user_query, table["embed"])
                if score > max_score:
                    max_score = score
                    best_table = table["table"]

            dec_mem[0][0].page_content += "\n" + best_table
```

## 11/06/2024

### prefix per obbligare il gatto a rispondere solo ad un medicinale

[plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)

```python
@hook
def agent_prompt_prefix(prefix, cat):

    prefix = f"""
    Sei un farmacista, e rispondi in modo professionale.
    Non rispondi con informazioni che non ti sono state fornite esplicitamente.
    Non rispondi a domande inappropriate.
    Ad ogni domanda rispondi nel modo più completo e preciso possibile.

    TU CONOSCI SOLAMENTE QUESTA MEDICINA: "{med_name}" , NON RISPONDI A NESSUNA DOMANDA SU ALTRI FARMACI
    SE TI VIENE CHIESTO SE CONOSCI ALTRE MEDICINE DEVI DIRE DI NO, E SE TI VIENE CHIESTO DI APPROFONDIRE DEVI DIRE DI NO
    """

    return prefix
```

---

### risposte del gatto troppo corte 

[plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)

E' stato esteso il prefix richidendo al gatto di rispondere esplicitamente in modo approfondito e descrittivo suddividendo i contenuti con un elenco puntato 

```python
  @hook
def agent_prompt_prefix(prefix, cat):

    prefix = f"""
    Sei un farmacista, e rispondi in modo professionale.
    Non rispondi con informazioni che non ti sono state fornite esplicitamente.
    Non rispondi a domande inappropriate.
    Ad ogni domanda rispondi nel modo più completo e preciso possibile.
    Rispondi in modo descrittivo e completo scrivendo la risposta usando elenchi puntati per suddividere in modo chiaro i contenuti.
    NON DEVI ESSERE TROPPO BREVE, ma riportare più informazioni possibili riguardo la domanda.

    TU CONOSCI SOLAMENTE QUESTA MEDICINA: "{med_name}" , NON RISPONDI A NESSUNA DOMANDA SU ALTRI FARMACI
    SE TI VIENE CHIESTO SE CONOSCI ALTRE MEDICINE DEVI DIRE DI NO, E SE TI VIENE CHIESTO DI APPROFONDIRE DEVI DIRE DI NO
    """

    return prefix
```

## 12/06/2024

### Riallineamento 

E' stato aggiunto un nuovo requisito da implementare prima che il gatto fornisca la risposta; il comportamento da ottenere consiste, data una lista di parole chiave, di forzare il gatto ad usare precisamente quei termini per fornire una risposta al posto di impiegare altri sinonimi.<br/>
Una seconda opzione potrebbe essere, al posto di forzare il gatto ad usare quelle parolo specifiche in fase di generazione della risposta, quella di effettuare un controllo a posteriori su di essa per individuare gli eventuali sinonimi impiegati e fare un mappaggio con le parole chiave.<br/>
Inoltre è stato richiesto di effettuare maggiori prove al fine di testare la correttezza e il livello di precisione dell'output del gatto, magari anche variando il prefix per forzare una maggiore dipendenza al Context Of Documents.

---

### Branch wordlist

In questo branch è stata aggiunta la possibilità di specificare una wordlist di sinonimi da usare per forzare l'uso di alcune specifiche parole.

```python
@hook
def agent_prompt_prefix(prefix, cat):
    with open("/app/cat/wordlist/wordlist.json", "r") as file:
        wordlist = file.read()

    prefix = f"""
    ........................

    Nelle tue risposte usa maggiormente queste parole come sinonimi ad altre.
    {wordlist}

    ........................
    """

    return prefix
```

La wordlist viene caricata direttamente dal file json e data nel prefix all'LLM, quindi se si vuole anche specificare delle parole da cambiare, usare certi simboli o mettere link si può specificare nel file json.

---

### Hook che vengono richiamati quando non servono

E' stato limitato  lo scenario in cui vengono richiamati degli hook quando si sta in realtà facendo una domanda la cui risposta deve essere basata sulla memoria dichiarativa. (non risolto al 100%, ma ridotto al punto da non essere fastidioso in fase di conversazione) <br/>
Per farlo è bastato aumentare il valore di soglia (thresold) della memoria procedurale, andando quindi ad evitare che venga agganciato un hook quando lo score del prompt dell'utente sta al di sotto di tale soglia.
Il thresold è stato impostato a 0.8, e tale scelta è frutto di semplici osservazioni empiriche con cui è stato riportato che l'aggancio del hook avviene correttamente quando lo score è superiore a tale valore.

```python
  procedural_memory_thresold = 0.8

  // Other code ....

  @hook  
  def before_cat_recalls_procedural_memories(procedural_recall_config, cat):
  
      procedural_recall_config["threshold"] = procedural_memory_thresold
  
      return procedural_recall_config
```
