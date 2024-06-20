# Problemi
---
## Classificazione tabelle pdf

<table>
    <thead>
        <tr>
            <th>Nome</th>
            <th>Immagine</th>
            <th>Risultati tabula-py</th>
            <th>Risultati Camelot</th>
            <th>Risultati img2table</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>FI LOPINAVIR E RITONAVIR MYLAN</td>
            <td><img src="https://github.com/luca2040/foglietti-cat/assets/152313871/f5b04126-7511-4797-b01a-fa3613101a02"></td>
            <td>Parsing sbagliato a causa della cella del titolo unita, il gatto non riesce a capire il contenuto.</td>
            <td>Colonne non riconosciute</td>
            <td>Nessun problema</td>
        </tr>
        <tr>
            <td>FI ACETILCISTEINA PSP</td>
            <td><img src="https://github.com/luca2040/foglietti-cat/assets/152313871/6a0b8252-6432-494c-8281-6a8cbf5101b4"></td>
            <td>Cella unita, parsing parzialmente sbagliato, il gatto capisce qualcosa ma non bene</td>
            <td>Tabella spezzata, il gatto capisce quasi nulla</td>
            <td>Nessun problema</td>
        </tr>
        <tr>
            <td>FI AUGMENTIN SCIROPPO 35 BB</td>
            <td><img src="https://github.com/luca2040/foglietti-cat/assets/152313871/92fbaa64-3b8c-4914-bd0e-3901ab610347"></td>
            <td>Non riconosce che cè una tabella</td>
            <td>Non riconosce che cè una tabella</td>
            <td>Bordi strani ma parsata correttamente, il gatto capisce tutto</td>
        </tr>
        <tr>
            <td>ETI METADIGEST KETO NFI 30CPS BLISTER</td>
            <td><img src="https://github.com/luca2040/foglietti-cat/assets/152313871/f983049c-02f0-491d-a009-d90050feafe9"></td>
            <td>Lasciamo stare</td>
            <td>Stessa cosa</td>
            <td>Parsato molto male ma il gatto capisce qualcosina.
            <br/>Le tabelle sul PDF sono parsate ma con tantissime righe che non esistono</td>
        </tr>
    </tbody>
</table>

---

## Il gatto risponde alla domanda su un farmaco usando le informazioni di un altro farmaco caricato nella memoria dichiarativa (Solved)

 ### Descrizione problema:

  Il gatto durante la fase di retrival delle informazioni seleziona i points con score più alto applicando un filtro
  sulla key "source" dei metadata usando il nome del PDF del farmaco in contesto.
  Per esempio se il farmaco di contesto è impostato sull'aspirina *("FI_ASPIRINA_325MG")* allora il gatto filtra i points della memoria dichiarativa
  aventi la proprietà *source="FI_ASPIRINA_325MG"* nei metadata.
  Tale filtraggio è implementato nell'hook *before_cat_recalls_declarative_memories*, ed avviene in modo sistematico usando come filtro il farmaco di contesto (che viene specificato prima che l'utente inizi la conversazione).
  Tuttavia se l'utente ponesse una domanda specificando un altro farmaco nel mezzo della conversazione (lasciando quindi inalterato il farmaco di contesto) il risultato che si otterrebbe è indefinito e potrebbe risultare in una tra le 2 seguenti casistiche:

  1. Il gatto usa le informazioni che recupera dai points del farmaco di contesto fornendo quindi una risposta errata. Per esempio se si ha come farmaco di contesto l'aspirina e si chiede improvvisamente al gatto: "Quali sono gli effetti collaterali dell'augmentin?", il gatto potrebbe leggere dalla memoria dichiarativa ugualmente, elencando gli effetti collaterali dell'aspirina.

  2. Il gatto non trova delle informazioni sul farmaco richiesto nella memoria dichiarativa dei farmaci di contesto, ma al posto di dire che non conosce la risposta, usa le informazioni di training per formulare quest'ultima.

 ### Soluzione del problema:

 La soluzione al problema consiste semplicemente nel modificare il prefix obbligando il gatto a rispondere solamente a domande riguardanti il farmaco di contesto *(La variabile med_name nel codice)*
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
