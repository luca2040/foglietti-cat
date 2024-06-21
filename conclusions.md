# Conclusioni
In questa sezione riportiamo quali sono gli obiettivi raggiunti fino ad ora ripercorrendo brevemente la loro soluzione.

## Miglioramento retrieval
Inizialmente il retrieval del gatto non era soddisfacente perchè rischiava di ricavare le informazioni da qualsiasi foglietto, quindi rischiando di confonderle.<br/>
La soluzione a questo problema è stata raggiunta impostando un tag per ciascun foglietto illustrativo e usarlo per ricavare solo quelli il tag del farmaco selezionato.

## Miglioramento parsing
Il parser integrato del gatto dava alcuni problemi, soprattutto sulla parte di parsing delle tabelle, ciò è stato risolto usando l'OCR *Tesseract* e la libreria *img2table*, rispettivamente usati per il parsing di testo e tabelle all'interno dei PDF.
Successivamente le tabelle parsate vengono formattate in HTML in modo che il gatto riesca a leggerne il contenuto.

## Upload PDF tramite API
Questo problema è nato dal fatto che il Gatto non implementa nessuna callback strutturata nella risposta di upload file completato, quindi per ovviare questo problema si è usata una websocket aperta specificatamente per l'upload di file e si resta in ascolto fino a quando non viene ricevuta la frase "Finished reading ...", la frase non è strutturata quindi in futuro può causare dei problemi.

## Rischi di prompt injection
Durante lo sviluppo del progetto si è pensato che un utente possa malevolmente cambiare la "personalità" del gatto facendo sì che non risponda come desiderato ma magari con informazioni errate. Per risolvere questo rischio sono state implementate nel prefix delle frasi atte ad evitare questo rischio.

## Uso di parole chiave
Ci è stato inviato un documento contenente una lista di parole chiave che sarebbero dovute comparire nella risposta fornita dal gatto con dei link.
Insieme a queste parole erano definiti inoltre i relativi sinonimi; la richiesta era quella di far evitare al gatto di rispondere usando questi sinonimi ma preferendo la parole chiave a fine di maggiore chiarezza.
E' stato quindi forzato il gatto ad usare nella risposta le parole contenute nella lista, che gli sono state passate in un file con estensione ".txt", al posto di altri sinonimi. Ciò consentirà in futuro di applicare i link d'interesse
sulle parole.

---

# Problemi aperti

### Classificazione tabelle pdf

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
            <td>Nessuna informazione estratta</td>
            <td>Nessuna informazione estratta</td>
            <td>Parsato molto male ma il gatto capisce qualcosina.
            <br/>Le tabelle sul PDF sono parsate ma con tantissime righe che non esistono</td>
        </tr>
    </tbody>
</table>
