# foglietti-cat

Repository del plugin per il framework CheshireCat per riassumere e dare informazioni a riguardo dei foglietti illustrativi dei medicinali.<br/>
La repo è divisa in due parti: 
- **CheshireCat** : Container docker e plugin CheshireCat
- **CheshireCatAPI** : Upload di pdf a CheshireCat tramite API

### **[Cambiamenti nel tempo](/history.md)**
### **[Problemi e cose varie](/description.md)**

---
 ## CheshireCatAPI

 L'entry point è il file [API_upload.py](/CheshireCatAPI/API_upload.py)<br/>
 ### **Funzionamento:**<br/>
 Prima di iniziare a fare l'upload dei file viene aperta una websocket con un nome utente specifico per il caricamento dei file in modo da poter ricevere i callback al completamento del caricamento dei PDF.<br/>
 Per la websocket si è usata la libreria del gatto:
 ```
cheshire_cat_api
```

Esempio di connessione tramite websocket ([API_upload.py](/CheshireCatAPI/API_upload.py)):
```python
import cheshire_cat_api as ccat

cat_client = ccat.CatClient(
    config=config,
    on_open=on_open,
    on_close=on_close,
    on_message=on_message,
    on_error=on_error,
)

cat_client.connect_ws()
```
Successivamente viene inviato un file tramite API del gatto usando la libreria requests.
[uploadfile.py](/CheshireCatAPI/uploadfile.py)
```python
import requests

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
Per ricevere la callback del caricamento completo del file si usa la funzione on_message ([websocket_functions.py](/CheshireCatAPI/websocket_functions.py)) per ricevere il testo inviato dal gatto (Purtroppo non è strutturato).
```python
def on_message(message: str) -> None:
    json_message = json.loads(message)

    if json_message["type"] == "notification":
        content_message: str = json_message["content"]

        log(content_message, "INFO")

        if content_message.startswith(config.rabbit_finished_message):
            config.message_called()
```
Appena il file viene caricato si continua per ogni file presenti nella cartella di input.

### **Configurazione:**<br/>
Per poter configurare l'upload è presente il file (config.json)[/CheshireCatAPI/config.json].
```json
{
    "websocket": {
        "base_url": "localhost",
        "port": 1865,
        "user_id": "upload_websocket",
        "auth_key": "",
        "secure_connection": 0
    },
    "rabbithole": {
        "url": "http://localhost:1865/rabbithole/",
        "finished_message": "Finished reading "
    },
    "folder": "files/",
    "log_file": "log.txt"
}
```
#### Websocket:
- *base_url*: url di base del gatto per la websocket
- *port*: la porta con cui verrà aperta la websocket
- *user_id*: il nome utente che verrà usato per aprire la websocket e inviare i file al gatto
- *auth_key* e *secure_connection*: altre configurazioni della websocket, non utilizzate nell'esempio
#### Rabbithole:
- *url*: url dell'API di upload file del gatto
- *finished_message*: questa è la stringa che il gatto inserisce all'inizio del messaggio per indicare che ha finito il caricamento di uno specifico file. Qua viene usata per capire se la lettura di un file è terminata
#### Altre configurazioni:
- *folder*: path alla cartella che contiene i PDF da caricare
- *log_file*: path al file di log

## CheshireCat - [docker compose](/CheshireCat/docker-compose.yml)

Per la libreria **tabula** usata per fare il parsing di tabelle nei PDF serve Java, quindi si è usato questo comando nel container del gatto:
```yaml
  command: bash -c "apt update && apt install -y default-jre && python3 -m cat.main"
```
---
Per poter usare Qdrant serve:
- Indicarlo nelle dipendenze
```yaml
  depends_on:
    - cheshire-cat-vector-memory
```
- Impostarlo nelle variabili d'ambiente
```yaml
  environment:
    - PYTHONUNBUFFERED=1
    - WATCHFILES_FORCE_POLLING=true
    - CORE_HOST=${CORE_HOST:-localhost}
    - CORE_PORT=${CORE_PORT:-1865}
    - QDRANT_HOST=${QDRANT_HOST:-cheshire_cat_vector_memory}
    - QDRANT_PORT=${QDRANT_PORT:-6333}
    - CORE_USE_SECURE_PROTOCOLS=${CORE_USE_SECURE_PROTOCOLS:-}
    - API_KEY=${API_KEY:-}
    - LOG_LEVEL=${LOG_LEVEL:-WARNING}
    - DEBUG=${DEBUG:-true}
    - SAVE_MEMORY_SNAPSHOTS=${SAVE_MEMORY_SNAPSHOTS:-false}
```
- Aggiungere il container
```yaml
  cheshire-cat-vector-memory:
    image: qdrant/qdrant:v1.9.1
    container_name: cheshire_cat_vector_memory
    expose:
      - 6333
    volumes:
      - ./cat/long_term_memory/vector:/qdrant/storage
    restart: unless-stopped
```

## CheshireCat - [plugin](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)

Durante la fase di test era necessario poter specificare il nome della medicina selezionata e poter ricevere la lista di tutti i file parsati.
Per fare questo sono stati creati due tool: 

[plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)
```python
@tool(return_direct=True)
def how_many_medicines_known(tool_input, cat):
    """Reply only to the question "How many medicines you know?" or to others which are stricly similar.
    Ignore generic questions about medicines.
    Input is always None
    Use this tool only if the user specifies to use a tool using #use tool#"""

@tool(return_direct=True)
def filename(tool_input: str, cat):
    """Reply to a file name, ONLY if specified using the word "file"
    Input is the file name
    Use this tool only if the user specifies to use a tool using #use tool#"""
```
---
Per poter parsare correttamente i PDF si è dovuta creare una [nuova classe](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/new_pdf_parser.py), la quale parsa i PDF in due passaggi:
- Nel primo passaggio tutto il testo contenuto nel PDF viene estratto tramite la libreria *PyPDF2*
- Nel secondo passaggio si usa la libreria *tabula* per estrarre solamente le tabelle dal file e poi vengono formattate in modo che il gatto le capisca.
Dopo questi passaggi nel metadata del *Document* di ritorno vengono inserite le tabelle.

Dopo il parsing, tramite l'hook *before_rabbithole_insert_memory* viene generato un embedding per ogni tabella e viene salvato nei metadata del *Document*

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

Visto che questi embedding verranno usati per selezionare la tabella richiesta dall'utene viene tolta tutta la formattazione delle tabelle tramite la funzione *replace*<br/>

Quando viene fatto il retrival dei point vengono selezionate le tabelle apparteneni ai file da cui provengono facendo l'embedding della query e selezionando solo la tabella con score più alto (Quella meno distante secondo la cosine similarity). Tutto questo viene fatto all'interno dell'hook *after_cat_recalls_memories* nel file [plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py).<br/>

---

Per filtrare solo i point con metadata corretto (Quelli che provengono da uno specifico foglietto illustrativo) si è usato l'hook *before_cat_recalls_declarative_memories*<br/>

[plugin.py](/CheshireCat/plugins/CC_plugin_foglietti_illustrativi/plugin.py)
```python
@hook
def before_cat_recalls_declarative_memories(declarative_recall_config, cat):
    # medicine is the filename or the tag
    declarative_recall_config["metadata"] = {"source": medicine}

    return declarative_recall_config
```

