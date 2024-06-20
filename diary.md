# foglietti-cat

Use the CheshireCat AI to explain and read medicine informations

## Argomenti riunione 07/06/2024

(R) -> Richieste

1. Siamo riusciti ad implementare la callback durante l'upload dei file

2. Fornire la documentazione su un repository sullo stato attuale del lavoro, da tenere aggiornato (R)

3. Il gatto non dà informazioni di farmaci di cui non ha la conoscenza in MODO DETERMINISTICO (R)

4. L'estrazione del nome del farmaco deve includere un match tra l'input fornito e l'elenco dei farmaci presenti (anche riguardante i vari farmaci disponibili) (R)

5. Far evitare al gatto di rispondere a domande la cui risposta non è specificata direttamente nei foglietti illustrativi (per esempio il gatto non deve rispondere alla domanda "Qual è la differenza tra l'aspirina e l'acetilcisteina?" ?).

6. Lavorare sul miglioramento della funzione di distanza e predisporre un livello di soglia per lo score al di sotto della quale il gatto non risponde. (R)

7. Non far rispondere al gatto a domande riguardanti un farmaco se il context della domanda è impostato su un altro farmaco ( Per esempio se gli ho detto di parlarmi dell'aspirina, non mi deve rispondere a domande sulla tachipirina) (R)

8. Approfondire l'hack del # per forzare istruzioni dal prompt (es. # non usare il tool #).

9. Per le informazioni tabulari bisogna:

  - Spiegare nel prefix la struttura con cui viene fornita la tabella
  - Strutturare le informazioni per header di colonna e di riga e passare questa struttura al LLM per parsare il risultato finale
  - Documentare in un pdf degli esempi di tabelle analizzate dal parser e descrivere gli eventuali problemi (R)

10. Organizzazione del lavoro su git:
  - main -> conserva il codice che funziona in attesa di ulteriori merge
  - nuovo branch -> deve essere staccato un branch per ogni task 

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
Per capire quando viene ricevuta una risposta viene aperta una websocket con lo stesso nome utente di quello usato per fare l'upload, e si aspetta la risposta del gatto.

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
Dato il numero elevato dei point per documento è stata creata una classe che mantiene in memoria i punti di certe query che si ripetono ed evita di ricalcolare il vettore ogni volta.

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

Il parser ora salva nei metadata un dizionario composto da tabella e relativo embed per ognuna di esse, in modo da poter salvare l'embed nei metadata del point.

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

E' stato esteso il prefix richiedendo al gatto di rispondere esplicitamente in modo approfondito e descrittivo suddividendo i contenuti con un elenco puntato 

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

E' stato aggiunto un nuovo requisito da implementare prima che il gatto fornisca la risposta: il comportamento da ottenere consiste, data una lista di parole chiave, di forzare il gatto ad usare precisamente quei termini per fornire una risposta al posto di impiegare altri sinonimi.<br/>
Una seconda opzione potrebbe essere, al posto di forzare il gatto ad usare quelle parole specifiche in fase di generazione della risposta, quella di effettuare un controllo a posteriori su di essa per individuare gli eventuali sinonimi impiegati e fare un mappaggio con le parole chiave.<br/>
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

### Tool che vengono richiamati quando non servono

E' stato limitato lo scenario in cui vengono richiamati degli tool quando si sta in realtà facendo una domanda la cui risposta deve essere basata sulla memoria dichiarativa. (non risolto al 100%, ma ridotto al punto da non essere fastidioso in fase di conversazione) <br/>
Per farlo è bastato aumentare il valore di soglia (thresold) della memoria procedurale, andando quindi ad evitare che venga agganciato un tool quando lo score del prompt dell'utente sta al di sotto di tale soglia.
Il thresold è stato impostato a 0.8, e tale scelta è frutto di semplici osservazioni empiriche con cui è stato riportato che l'aggancio del tool avviene correttamente quando lo score è superiore a tale valore.

```python
  procedural_memory_thresold = 0.8

  // Other code ....

  @hook  
  def before_cat_recalls_procedural_memories(procedural_recall_config, cat):
  
      procedural_recall_config["threshold"] = procedural_memory_thresold
  
      return procedural_recall_config
```

---

## 13/06/2024

### Test qualitativo dell'output con altri embedder

Sono state effettuate delle prove usando gli altri embedder e valutando in che modo tale cambiamento influisse in modo qualitativo sulla risposta fornita dal gatto.
Si riporta che usando altri embedder che non siano quello di Qdrant (locale) l'attribuzione dello score varia in modo notevole, passando da uno score medio dei points recuperati di 0.8 ad uno di 0.5. 
Tale abbassamento di score introduce problemi proprio a livello di retrival in quanto non viene più effettuato il filtraggio di informazioni appartenenti a foglietti illustrativi diversi: ciò comporta in pratica che se si chiede al gatto una domanda sull'aspirina, per la risposta potrebbe far uso di points di altri farmaci.
Inoltre il cambiamento di score porta anche problemi con l'aggancio dei tool di selezione del farmaco di contesto, e quindi con il retrival della memoria procedurale.
Per non vanificare il lavoro svolto fino ad ora la soluzione più immediata e agevole è proprio quella di non cambiare embedder; tuttavia ciò non significa che la transizione verso un altro embedder, comporti un ritorno al punto di partenza, ma che per riadattare il retrival correttamente bisognerebbe fare un lavoro su parametri come il threshold, o magari operare degli adattamenti alla funzione di distanza.

---

## Argomenti riunione 13/06/2024

(R) -> Richieste

1. Il gatto in una parte delle risposte usa ancora una parte di informazioni che non sono presenti nella memoria dichiarativa, ma che bensì derivano dal training del LLM. L'obiettivo da raggiungere è azzerare, o perlomeno ridurre a livello tollerabile, le informazioni che non sono presenti dai foglietti illustrativi ma che derivano dalla conoscenza del LLM. (R)

2. Verificare il prompt injection ovvero i modi con cui l'utente riesce a far alterare il comportamento del gatto forzandolo a dare risposte che non dovrebbe dare. Da approfondire se e quando l'uso dei cancelletti come hack (# istruzioni #) possa rappresentare un rischio per la generazione di prompt malevoli; sarebbe interessante dal punto di vista del prompt segnalare anche il bug di quando si passa al gatto una stringa json e questo intende i suoi campi come delle variabili.

3. Qualora le domande dell'utente richiedano una risposta approfondita, il gatto deve rispondere in modo articolato, viceversa quando la domanda richiede un'informazione precisa la risposta deve essere concisa. Da tenere conto che la problematica principale riguardante questo punto riguarda la scelta del criterio con cui si può far intendere al gatto la necessità di una risposta articolata da una precisa. Nel suo svolgimento è quindi consigliabile di fornire al gatto una definizione del concetto di "articolato e preciso" a priori e poi testare come le sue risposte seguano il criterio prestabilito fino a raggiungere un risultato accettabile.
Si rammenta che in ogni caso risposte troppo prolisse e sbrodolose non rientrano nel caso d'uso previsto per un farmacista, il quale si ipotizza che la maggior parte delle volte richieda una risposta la cui lettura sia veloce e le cui informazioni siano comunque precise. (R)

4. Approfondire la causa del mancato filtraggio dei metadati quando si cambia embedder.

5. Approfondire anche la task riguardante l'elenco dei sinonimi delle parole chiave. L'intento principale sarebbe quello di avere una risposta in cui eventuali sinonimi delle parole chiave predefinite, non siano presenti a fine di maggiore chiarezza; per esempio se come parola chiave ho il termine "medicinale", esso dovrà essere usato globalmente della risposta anche in sostituzione di altri sinonimi come "medicina", "farmaco", "cura" ecc. Per facilitare lo svolgimento della task si consiglia di usare come parole chiave termini poco comuni ma che siano parole palesi, ciò facilita la fase di analisi perchè consente di individuare subito se sono state operate le sostituzioni con le parole chiave. La seconda opzione che si può tenere conto è quella di effettuare un controllo a posteriori da parte del LLM dandogli la risposta del gatto e facendogli individuare gli eventuali sinonimi. (R)

## 17/06/2024

### Creazione script per testare la libreria [img2table](https://github.com/xavctn/img2table) per il parsing delle tabelle nei pdf
E' stata testata la libreria sopraddetta su un insieme di 121 pdf al fine di analizzare i risultati ottenuti per compararli con quelli delle altre librerie di estrazione tabelle precedentemente provate.
Un riepilogo comparativo dell'accurattezza mostrata da ciascuna libreria è stata inserito nel documento "Problemi e cose varie" alla sezione ["Classificazione tabelle pdf"](https://github.com/luca2040/foglietti-cat/blob/main/conclusions.md#classificazione-tabelle-pdf). <br/>
L'adozione di questa libreria ha portato a risultati di un'accuratezza imparagonabile rispetto a quelle adottate in precedenza, riuscendo ad individuare tutte le tabelle presenti in un pdf e soprattutto permettendo di ottenere il risultato in un formato strutturato come HTML (tale caratteristica ha presentato un punto di svolta, in quanto librerie come "tabula" non consentivano di ottenere direttamente un formato standard per la rappresentazione di dati tabulari). 
Il formato di uscita che è stato scelto di mantenere è l'HTML per via della sua semplicità, tuttavia l'altra opzione che offre la libreria è quella di ottenere la tabella parsata come un pandas DataFrame, da cui si potrebbero ricavare ulteriori formati come il csv ( opzione che però non è stata presa in considerazione, come spiegato nella [sezione successiva](https://github.com/luca2040/foglietti-cat/blob/main/diary.md#scelta-formato-strutturato-per-dati-tabulari-da-passare-al-gatto) ).
Si riporta lo script impiegato per effettuare i test, a fini di replicazione:
```python
from img2table.ocr import TesseractOCR, PaddleOCR, EasyOCR, DocTR
from img2table.document import PDF


import os
import time
import numpy
import traceback
import pytesseract

from typing import List

# Global variables

files_path = "C:\\Users\\danie\\OneDrive\\Desktop\\img2table-test\\files"
html_output_path  = ""
txt_output_path = ""

count = 0

ocr_dict = {
       "Tesseract": TesseractOCR(n_threads=1, lang="ita"),
       "Paddle": PaddleOCR(lang="it"),
       "EasyOCR":  EasyOCR(lang= ["it"]),
       "DocTR": DocTR(detect_language=True)

}


# ==================================================
# Functions 

def extract_text(pdf, filename):
        global txt_output_path
        # Getting pages of pdf and extracting text from them
        pages : List[numpy.ndarray] = pdf.images
        
        text_data = ""
        for page in pages:
                text = pytesseract.image_to_string(page)
                text_data += text + "\n"

        # Saving the extracted text in a file
        if not os.path.exists(txt_output_path):
               os.makedirs(txt_output_path)

        new_file = os.path.join(txt_output_path, filename.upper().replace(".PDF", ".TXT"))
        with open(new_file, "w+", encoding="utf-8") as f:
               f.write(text_data)


def process_files(in_path, out_path, ocr_class): 
      
      for file in os.listdir(in_path):
        filepath = os.path.join(in_path, file)
        
        # If there is a directory, I go into it recursively until I found pdf files
        if os.path.isdir(filepath):
                new_out_path = os.path.join(out_path, file)
                process_files(filepath, new_out_path, ocr_class)
                continue

        # If the file isn't a pdf, I go to the next:
        if not file.upper().endswith(".PDF"): continue

        # Checking if the output path exists. If not, it creates it.
        if not os.path.exists(out_path):
               os.makedirs(out_path)

        # Checking if the output html file still exists, in order to avoid
        # inutil computations during developing phase.
        html_path = os.path.join(out_path, f"""{file.upper().replace(".PDF", ".html")}""")
        if os.path.exists(html_path): continue 

        # Getting PDF and extracting text
        pdf = PDF(filepath, 
        detect_rotation=True,
        pdf_text_extraction=True)

        # extract_text(pdf, file) REACTIVATE THIS LINE

        # Table extraction
        print(f"Exctracting {file}...\n")

        try:
                global current_ocr
                extracted_tables = list(pdf.extract_tables(
                                        ocr=ocr_class,
                                        implicit_rows=True,
                                        borderless_tables=True,
                                        min_confidence=50).values())

                # Converting ExtractedTables into html strings
                html_table_list = []
                for table in extracted_tables:
                        if table: 
                                for t in table:
                                        html_table_list.append(t.html)
        
                # Writing the tables found in the html file
                with open(html_path, "a+", encoding="utf-8") as f:
                        for html_table in html_table_list:
                                f.write(html_table.replace("<table>", """<table border="1">"""))

                 

                # Printing progression
                global count
                global total
                count+=1
                print(f"""Done conversion for {file}, ({count}/{total}) {round(count/total*100)}% \n\n""")
        except Exception as e:
               traceback.print_exc()
               print(f"Non è stato possibile parsare {file} a causa dell'errore \n {str(e)}")


# ==================================================
# Entry point:

if __name__ == "__main__":
        for name, ocr in ocr_dict.items():

                # Setting the current output path and counting the elements
                html_output_path = os.path.join(files_path, "..", name, "html")
                txt_output_path = os.path.join(files_path, "..", name, "txt")

                pdf_num = len([file for _, _, files in os.walk(files_path, topdown=True) for file in files]) 
                html_num = len([file for _, _, files in os.walk(html_output_path, topdown=True) for file in files]) 
                total = (pdf_num - html_num)

                # Starting extraction
                start_time = time.time()
                process_files(files_path, html_output_path, ocr)
                print(f"""{name} took {"{:.2f}".format(time.time()-start_time)}s.""")

```

N.B: per chi volesse eseguire lo script sul proprio computer locale, fare attenzione alle seguenti righe:
```python
files_path = "C:\\Users\\danie\\OneDrive\\Desktop\\img2table-test\\files"
html_output_path  = ""
txt_output_path = ""

count = 0

ocr_dict = {
       "Tesseract": TesseractOCR(n_threads=1, lang="ita"),
       "Paddle": PaddleOCR(lang="it"),
       "EasyOCR":  EasyOCR(lang= ["it"]),
       "DocTR": DocTR(detect_language=True)

}

```

- Sostituire nella variabile ```files_path``` il path in cui sono salvati i pdf nel proprio computer locale; non importa se nel percorso indicato ci sono file con estensione diversa da ".pdf" o cartelle, lo script li ignorerà e passerà ad estrarre le tabelle solo nei pdf, salvando le tabelle estratte in ogni documento in un relativo file html.

-  Essendo img2table una libreria basata su OCR, è possibile passarne uno custom inserendone la relativa istanza nel dizionario ```ocr_dict```, la key del dizionario può essere una stringa qualsiasi che viene usata per creare una cartella di output in cui saranno salvati i risultati ottenuti applicando quell'OCR: lo script infatti effettua l'estrazione delle tabelle usando ogni OCR al fine di avere dei risultati comparabili. <br/>
Per far uso delle classi degli OCR è necessario effettuare la corretta installazione per ognuno di essi come riportato nella [documentazione della libreria](https://github.com/xavctn/img2table?tab=readme-ov-file#installation-). La comparazione dei vari OCR è riportata nei [prossimi paragrafi](https://github.com/luca2040/foglietti-cat/edit/main/diary.md#comparazione-ocr).

Infine una volta accertate le funzionalità della libreria abbiamo implementato quest'ultima all'interno del parser del gatto, non solo per l'estrazione delle tabelle, ma anche per quella del testo.

### Scelta formato strutturato per dati tabulari da passare al gatto

Una volta verificati i risultati della libreria, bisognava scegliere quale formato strutturato passare al gatto affinchè i dati contenuti potessero essergli comprensibili al fine di ottenere delle risposte corrette.
L'idea iniziale era quella di sostituire l'html delle tabelle nella posizione corretta all'interno del testo estratto, tuttavia è stato accertato che tale operazione non serviva in quanto è bastato passare le tabelle alla fine del testo per poter ricevere delle risposte esaustive da parte del gatto. Di conseguenza è stato anche accertato che l'html è un formato comprensibile, ed eventuali errori di incomprensione da parte del gatto non sono stati individuati. 

## Comparazione OCR:

Durante la fase di comparazione degli OCR, ci si è accorti del seguente dettaglio riguardo la libreria: l'estrazione delle tabelle avviene la maggior parte delle volte senza usare l'OCR passato come argomento. Infatti l'OCR viene impiegato solamente per estrarre dati da eventuali immagini presenti nei pdf; pertanto se la tabella non è presente all'interno di un'immagine, la libreria non utilizzerà le funzionalità dell'OCR. Essendo tale casistiche presente per tutti i pdf, la scelta del miglior OCR rimane dunque irrilevante.

