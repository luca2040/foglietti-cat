# Problemi
---
## Classificazione tabelle pdf

### Esempio di pdf parsato correttamente

<p align="center">
  <img width="65%" height="65%" src="https://github.com/luca2040/foglietti-cat/assets/152313871/f5b04126-7511-4797-b01a-fa3613101a02">
</p>

---

### Esempio di pdf parsato in modo sbagliato

<p align="center">
  <img width="65%" height="65%" src="https://github.com/luca2040/foglietti-cat/assets/152313871/6a0b8252-6432-494c-8281-6a8cbf5101b4">
</p>

- Non importa quante tabelle ci siano, l'importante è che la tabella sia strutturata.
- Se in una riga ci sono delle celle unite meglio se non cè nient'altro.
- Se la stessa tabella è divisa in più pagine ma senza riportare gli indici su entrambe le pagine non viene parsata correttamente.
- Le celle della tabella devono essere separate da linee.

### Come ricreare questo problema:

Quando si parsa un file pdf possono verificarsi questi problemi se una riga che contiene delle celle unite ha anche delle celle non unite oppure unite in verticale.
Se la tabella è divisa in più pagine diverse il gatto non è in grado di capire gli indici e quindi non è in grado di rispondere correttamente.

---

## Il gatto risponde alla domanda su un farmaco usando le informazioni del farmaco caricato nella dichiarativa (Solved)

 ### Descrizione problema:

  Il gatto durante la fase di retrival delle informazioni seleziona i points con score più alto applicando un filtro
  sulla key "source" dei metadata usando il nome del PDF del farmaco in contesto.
  Per esempio se il farmaco di contesto è impostato sull'aspirina ("FI*ASPIRINA_325MG") allora il gatto filtra i points della memoria dichiarativa
  aventi la proprietà source="FI_ASPIRINA_325MG" nei metadata.
  Tale filtraggio è implementato nel hook \_before_cat_recalls_declarative_memories*, ed avviene in modo sistemastico usando come filtro il farmaco di contesto (che viene specificato prima che l'utente inizi la conversazione).
  Tuttavia qualora l'utente ponesse una domanda specificando un altro farmaco nel mezzo della conversazione (lasciando quindi inalterato il farmaco di contesto) il risultato che si otterrebbe è indefinito e potrebbe risultare in una tra le 2 seguenti casistiche:

  1. Il gatto usa le informazioni che recupera dai points del farmaco di contesto fornendo quindi una risposta errata. Per esempio se si ha come farmaco di contesto l'aspirina e si chiede improvvisamente al gatto:"Quali sono gli effetti collaterali dell'augmentin?", il gatto potrebbe elencando gli effetti collaterali dell'aspirina.

  2. Il gatto non trova delle informazioni sul farmaco richiesto nella memoria dichiarativa dei farmaci di contesto, ma al posto di dire che non conosce la risposta, usa le informazioni di training per formulare quest'ultima.

 ### Soluzione del problema:

 La soluzione al problema consiste semplicemente nel modificare nel prefix facendo tenere conto al gatto di rispondere solamente a domande riguardanti il farmaco di contesto (La variabile med_name nel codice)
 bloccando preventivamente il verificarsi della situazione previo descritta.

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
