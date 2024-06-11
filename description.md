# Problemi
# Classificazione tabelle pdf

Esempio di pdf parsato correttamente

<p align="center">
  <img width="65%" height="65%" src="https://github.com/luca2040/foglietti-cat/assets/152313871/f5b04126-7511-4797-b01a-fa3613101a02">
</p>

---

Esempio di pdf parsato in modo sbagliato

<p align="center">
  <img width="65%" height="65%" src="https://github.com/luca2040/foglietti-cat/assets/152313871/6a0b8252-6432-494c-8281-6a8cbf5101b4">
</p>

- Non importa quante tabelle ci siano, l'importante è che la tabella sia strutturata.
- Se in una riga ci sono delle celle unite meglio se non cè nient'altro.
- Se la stessa tabella è divisa in più pagine ma senza riportare gli indici su entrambe le pagine non viene parsata correttamente.
- Le celle della tabella devono essere separate da linee.

## Come ricreare questo problema:

Quando si parsa un file pdf possono verificarsi questi problemi se una riga che contiene delle celle unite ha anche delle celle non unite oppure unite in verticale.
Se la tabella è divisa in più pagine diverse il gatto non è in grado di capire gli indici e quindi non è in grado di rispondere correttamente.
