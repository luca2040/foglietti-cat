# Conclusioni
In questa sezione riportiamo quali sono gli obiettivi raggiunti fino ad ora ripercorrendo brevemente alla loro soluzione.

## Miglioramento retrieval
Inizialmente il retrieval del gatto non era soddisfacente perchè  

## Miglioramento parsing

## Upload PDF tramite API

## Rischi di prompt injection



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
