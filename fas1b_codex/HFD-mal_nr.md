# HFD: varianter i skrivning av målnummer (mål nr)

Det här är en copy-paste-vänlig översikt över vanliga sätt som HFD anger **målnummer** i referat/avgöranden, inklusive intervall ("range") och kombinationer med *och/samt*.

---

## 1) Grundformat (ett målnummer)

- `NNNN-NN`  
  Ex: `1536-23`

---

## 2) Flera målnummer (lista)

### 2.1 Komma-separerade
- `6963-15, 6969-15`

### 2.2 Med konjunktion
- `6980-24 och 6981-24`
- `A samt B` (förekommer också)

> I löptext kan prefix förekomma: `Mål: ...` / `mål nr ...` / `Mål nr. ...`

---

## 3) Intervall (range)

### 3.1 Typografiskt streck (en-dash)
- `6107–6109-23`

### 3.2 Dubbelt bindestreck ("tekniskt" intervalltecken)
- `6159--6160-14`

### 3.3 Enkelt bindestreck som intervall (kan förekomma)
- `4569-4571-22`  
  *(kan i vissa kanaler/texter avses som intervall; kräver ofta kontext)*

---

## 4) Kombinationsformer (blandningar)

- `6578-14, 6159--6160-14`
- `7550–7558-21 samt 664–669-22`
- `xxxx-xx--xxxx-xx och xxxx-xx`
- `xxxx-xx--xxxx-xx och xxxx-xx--xxxx-xx`

---

## 5) Normalisering (robust maskinell hantering)

1. **Normalisera intervalltecken**  
   Behandla `–` och `--` som samma sak internt (välj en standard, t.ex. `--`).

2. **Splitta listor först**  
   Dela på `,` samt orden ` och ` och ` samt `.

3. **Städa tokens**  
   Trimma whitespace och ta bort ev. prefix som `Mål:`, `mål nr`, `Mål nr.`.

4. **Klassificera token**
   - **Single:** `^\d+-\d{2}$`
   - **Range:** `^\d+(?:--|–|-)\d+-\d{2}$`

---

## 6) Expansion av intervall (valfritt)

Om du vill expandera ranges till en lista:

- `6107–6109-23` ⇒ `6107-23`, `6108-23`, `6109-23`

Princip:
- Tolka `start` och `slut` som löpnummer.
- År-suffixet `-YY` gäller för alla i intervallet.

---

## 7) Regex (exempel)

- **Single:**  
  `(?<!\d)(\d{1,5}-\d{2})(?!\d)`

- **Range:**  
  `(?<!\d)(\d{1,5})(?:--|–|-)(\d{1,5})-(\d{2})(?!\d)`

---

## 8) Filnamnsstrategier när flera mål finns

Utgår från din mall: `HFD_{YEAR}_ref-{NNN}__mal-{MALNR}.pdf`

### Alternativ A: behåll originalform (normaliserad)
- `HFD_2025_ref-049__mal-6980-24_och_6981-24.pdf`

### Alternativ B: kompakt lista (underscore-sep)
- `HFD_2025_ref-049__mal-6980-24_6981-24.pdf`

### Alternativ C: range bibehållen (normaliserad till `--`)
- `HFD_2025_ref-013__mal-6107--6109-23.pdf`

> Tips: spara alltid både **originalsträng** och **normaliserad/parsad** form i metadata (CSV/JSON), så att du kan reproducera och felsöka senare.
