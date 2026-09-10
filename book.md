Clean Spec

Ingegneria delle Specifiche per l'Era dell'Intelligenza Artificiale

PARTE I: I FONDAMENTI TEORICI DELLA SPECIFICA NELL'ERA AI

Capitolo 1: Il Paradosso della Commoditizzazione del Codice

1.1 L'evoluzione dei livelli di astrazione del software

La storia dell'ingegneria del software è la storia del progressivo innalzamento dei livelli di astrazione computazionale. Ogni transizione epocale ha convertito un'attività ad alto dispendio cognitivo in un sottoprocesso compilabile:

Linguaggio Macchina ad Assembly: Eliminazione della traduzione manuale in codici operativi numerici.

Assembly a Linguaggi Procedurali compilati (Fortran, C): Automazione della gestione dei registri di CPU e del layout dello stack di chiamata.

Linguaggi Procedurali a Linguaggi ad Oggetti e Garbage Collected (Java, C#, Python): Automazione del ciclo di vita della memoria e standardizzazione delle gerarchie di tipi.

Programmazione Tradizionale a Spec-Driven AI Engineering: Il passaggio dal come un algoritmo deve essere tradotto in istruzioni sintattiche al cosa il sistema deve garantire a livello contrattuale, comportamentale e invariante.

In questo nuovo paradigma, il codice sorgente convenzionale (Python, TypeScript, Go, Rust) cessa di essere l'artefatto originale primario e diventa una rappresentazione intermedia a basso livello, prodotta da un motore di inferenza probabilistica che agisce a tutti gli effetti come un compilatore non deterministico.

1.2 L'illusione del "Vibecoding" e l'esplosione dell'entropia

Il termine vibecoding descrive l'approccio emergente in cui l'operatore umano interagisce con un Large Language Model (LLM) tramite prompt informali, iterazioni conversazionali non tracciate e una verifica meramente empirica ("sembra funzionare a video").

Questo approccio presenta un andamento ingannevole:

Nei primi stadi di un progetto (linee di codice $L < 1000$), la produttività percepita cresce in maniera vertiginosa. Il costo di generare un prototipo scende a una frazione marginale.

Non appena il sistema scala oltre la soglia del giocattolo ($L > 5000$ o interazioni tra più di due domini applicativi), il debito tecnico esplode. L'assenza di confini rigorosi produce entropia software non controllata.

Formalizziamo la dinamica dei costi tra approccio tradizionale e generazione non strutturata. Il costo computazionale e cognitivo della generazione di codice tramite LLM è quasi piatto:


$$C_{\text{generation}} = O(1)$$

Tuttavia, il costo di comprensione, verifica contrattuale, debugging e regression analysis in assenza di una specifica formale cresce con il quadrato delle interazioni tra i componenti non formalizzati:


$$C_{\text{verification}} = O(N^2)$$


dove $N$ rappresenta il numero di invarianti implicite presenti nel sistema.

Costo
  ^
  |                                   / Approccio Informale (Vibecoding)
  |                                  /  Costo verifica: O(N^2)
  |                                 /
  |                                /
  |                               /
  |                              /
  |-----------------------------/------------------------
  |                            /      Approccio Clean Spec (SDD)
  |                           /       Costo costante di verifica: O(1)
  |                          /
  +-------------------------------------------------------> Complessità Sistema (N)


Senza una specifica formale, ogni iterazione con l'LLM rischia di correggere un bug introducendo due regressioni invisibili, perché il modello non possiede una matrice di verità contro cui convalidare la coerenza globale.

1.3 La specifica software come unico artefatto a rendimento cognitivo positivo

Se la sintesi del codice è commodity, il valore ingegneristico si sposta a monte:

La chiarezza dei requisiti.

La modellazione formale dei domini e degli invarianti.

La definizione della matrice di fallimento.

La formalizzazione dei contratti di interfaccia.

Una specifica scritta secondo standard rigorosi (Clean Spec) ha rendimento cognitivo permanente: sopravvive al modello AI sottostante, può essere passata da un LLM all'altro, abilita la generazione autonoma di test contrattuali e funge da unica sorgente di verità immutabile nel repository.

Capitolo 2: Teoria dell'Informazione e Modelli di Linguaggio

2.1 L'LLM come motore di predizione statistica vincolato

Un Large Language Model opera calcolando la distribuzione di probabilità del token successivo condizionata dal contesto precedente:


$$P(T_{n} \mid T_{1}, T_{2}, \dots, T_{n-1})$$

Quando affidiamo all'LLM l'implementazione di un software, l'obiettivo dell'ingegnere non è "farsi capire da una persona", ma collassare lo spazio probabilistico degli output possibili verso il sottoinsieme ristretto di implementazioni corrette e deterministiche.

Se la specifica è vaga:


$$\text{"Gestisci le transazioni finanziarie con cura."}$$


lo spazio degli stati generabili ha una varianza $\sigma^2 \to \infty$. Il modello sceglierà percorsi statistici frequenti nel suo dataset di training, che spesso contengono codice insicuro, fallimenti nella gestione dei float o assenza di isolamento delle transazioni.

Se la specifica è formalizzata:


$$\text{Transazione } T = \langle S, D, A \rangle \quad \text{con } S \neq D, \, A \in \mathbb{N}^+, \, \Delta_{\text{balance}}(S) = -A, \, \Delta_{\text{balance}}(D) = +A$$


accompagnata da vincoli di concorrenza SERIALIZABLE e idempotenza su chiave UUIDv4, lo spazio probabilistico si contrae drasticamente, forzando il modello verso l'unica classe di implementazioni ammissibili.

2.2 Signal-to-Noise Ratio (SNR) e densità di vincolo

Uno dei fenomeni più deleteri nell'interazione con agenti AI è il Context Poisoning e la saturazione della finestra di contesto. L'efficacia di un modello non cresce linearmente con la lunghezza del prompt; al contrario, oltre una certa soglia di token irrilevanti o discorsivi subentra il fenomeno del Needle-in-a-Haystack Degradation.

Definiamo la Densità di Vincolo ($D_c$) di una specifica come:


$$D_c = \frac{\text{Vincoli Formali (Tipi, Invarianti, Pre/Post-condizioni)}}{\text{Numero Totale di Token}}$$

Una Clean Spec massimizza $D_c$. Elimina la cortesia verbale, i preamboli narrativi e le perifrasi colloquiali, sostituendoli con formulazioni logiche dirette e strutture dati autodocumentate.

2.3 Logica di Hoare applicata alle Specifiche AI

Per garantire che un agente di programmazione generi codice affidabile, la specifica deve essere formulata secondo le triple di Hoare:


$$\{P\} \; C \; \{Q\}$$


Dove:

$P$ è la Precondizione: lo stato valido del mondo prima che l'operazione venga eseguita.

$C$ è il Comando / Esecuzione: l'unità di codice o componente sintetizzato.

$Q$ è la Postcondizione: lo stato del mondo garantito al termine dell'esecuzione.

A queste aggiungiamo l'Invariante di Dominio ($I$): una condizione che deve risultare vera prima, durante e dopo qualsiasi mutazione di stato:


$$\forall s \in S, \quad I(s) = \text{true}$$

Se una specifica non dichiara esplicitamente $\{P\}$, $\{Q\}$ e $I$, l'agente AI sarà costretto a ipotizzarli per estrapolazione statistica, introducendo instabilità strutturale.

Capitolo 3: L'Inversione del Flusso: Spec-Driven Development (SDD)

3.1 La pipeline dello Spec-Driven Development

Lo Spec-Driven Development (SDD) non è un'evoluzione accessoria del Test-Driven Development (TDD); ne è il completamento formale nel paradigma agentico. Nel TDD umano l'ingegnere scriveva i test per chiarire a se stesso i requisiti prima di scrivere il codice applicativo. Nell'SDD, l'ingegnere scrive la specifica strutturata, la specifica genera o convalida i test, e l'agente sintetizza il codice applicativo per soddisfare entrambi.

       +-------------------------------------------------------+
       |             CLEAN SPEC (Autore: Umano)                |
       |     (Tipi, Invarianti, FSM, Contratti, RFC 2119)      |
       +-------------------------------------------------------+
                                  |
            +---------------------+---------------------+
            v                                           v
+-----------------------+                   +-----------------------+
|  Test di Proprietà &  |                   |  Sintesi Codice       |
|  Contratti API        |                   |  Applicativo          |
|  (Motore Determin.)   |                   |  (Agente AI)          |
+-----------------------+                   +-----------------------+
            |                                           |
            +---------------------+---------------------+
                                  v
                    +---------------------------+
                    |  Esecuzione & Validazione |
                    |  Determinica (CI / Mypy)  |
                    +---------------------------+
                                  |
                   [Fallimento]   |   [Successo]
                         +--------+--------+
                         v                 v
               Riavvita Spec / Agent    Commit &
               Auto-Correction Loop     Deploy


3.2 Il codice sorgente come artefatto derivato

In una pipeline SDD rigorosa vige una regola cardinale:

Regola Aurea di Clean Spec: Non modificare mai a mano il codice generato dall'agente. Se il codice è errato, lacunoso o sub-ottimale, il difetto risiede nella specifica. Correggi la specifica, riesegui l'agente.

Modificare il codice sorgente senza aggiornare la specifica introduce una frattura insanabile tra modello concettuale e implementazione. La specifica cessa di essere la Singola Fonte di Verità (Single Source of Truth - SSOT) e il progetto collassa nuovamente nel paradigma del legacy software ad alta entropia.

PARTE II: ANATOMIA E SINTASSI DI UNA CLEAN SPEC

Capitolo 4: Formati e Linguaggi: Oltre il Linguaggio Naturale Puro

4.1 Il fallimento dell'ambiguità verbale

Il linguaggio naturale convenzionale è ottimizzato per l'interazione sociale umana: tollera il sottinteso, sfrutta il contesto extratestuale e permette la sfumatura. Questi attributi sono fatali nell'ingegneria dei requisiti per sistemi probabilistici.

Consideriamo la frase:

"L'utente deve ricevere una notifica se il pagamento va a buon fine, a meno che non abbia disabilitato gli avvisi."

Questa frase lascia aperti i seguenti quesiti:

Qual è il canale di notifica (Email, SMS, Webhook, Push)?

L'operazione di invio notifica è sincrona o asincrona rispetto alla conferma del pagamento?

Se l'invio della notifica fallisce per indisponibilità della rete, la transazione di pagamento deve essere rollbackata?

Cosa si intende per "disabilitato gli avvisi" (tutti gli avvisi o specificamente quelli transazionali)?

4.2 Standardizzazione RFC 2119 e RFC 8174

Una Clean Spec adotta obbligatoriamente il vocabolario normativo definito dallo standard IETF RFC 2119 / RFC 8174:

MUST / SHALL: Indica un vincolo assoluto e vincolante del sistema.

MUST NOT / SHALL NOT: Indica una proibizione assoluta.

SHOULD / RECOMMENDED: Esprime una raccomandazione valida; possono esistere ragioni valide per deviare, ma le implicazioni devono essere valutate e documentate.

MAY / OPTIONAL: Indica una funzionalità puramente discrezionale.

4.3 Grammatica composita: Markdown + Schemi Rigidi + Mermaid

Una Clean Spec efficace utilizza una sintassi tripartita:

Markdown strutturato per la gerarchia logica e i vincoli normativi (RFC 2119).

JSON Schema / TypeSpec / Pydantic per la rigorosa definizione dei tipi di dati, vincoli numerici e pattern regex.

Mermaid.js per diagrammi di transizione di stato finiti e sequenze temporali.

Esempio: Specifica Formale del Processo di Notifica

### SPEC-PAY-042: Notifiche di Conferma Transazione

#### 1. Dichiarazione dei Vincoli Normativi
* Al completamento con esito `SETTLED` di una transazione, il sistema **MUST** accodare un evento di notifica.
* Il dispatching dell'evento **MUST NOT** bloccare o far fallire la transazione di pagamento già completata.
* Se l'utente ha impostato `preferences.notifications.transaction_receipts = false`, il dispatcher **MUST** ignorare l'evento registrando un audit log con stato `SKIPPED`.

#### 2. Modello Dati del Payload (JSON Schema Draft-07)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TransactionNotificationEvent",
  "type": "object",
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid"
    },
    "transaction_id": {
      "type": "string",
      "format": "uuid"
    },
    "amount_in_cents": {
      "type": "integer",
      "minimum": 1
    },
    "currency": {
      "type": "string",
      "pattern": "^[A-Z]{3}$"
    }
  },
  "required": ["event_id", "transaction_id", "amount_in_cents", "currency"],
  "additionalProperties": false
}


3. Automa a Stati Finiti della Consegna

stateDiagram-v2
    [*] --> Queued : Transazione SETTLED
    Queued --> EvaluatingPreferences : Consumatore estrae messaggio
    EvaluatingPreferences --> Skipped : Utente opt-out
    EvaluatingPreferences --> Dispatching : Utente opt-in
    Dispatching --> Delivered : 200 OK provider
    Dispatching --> RetryScheduled : Errore transiente (5xx)
    RetryScheduled --> Dispatching : Retry attempt <= 3
    RetryScheduled --> DeadLetterQueue : Retry attempt > 3
    Delivered --> [*]
    Skipped --> [*]
    DeadLetterQueue --> [*]



---

## Capitolo 5: I Tre Livelli della Specifica Pulita

Una specifica scalabile si articola su tre livelli discreti, rispecchiando i cerchi concentrici della Clean Architecture.



   +-----------------------------------------------+
   | Livello 0: Confini di Dominio & Architettura  |
   |  +-----------------------------------------+  |
   |  | Livello 1: Contratti I/O & Modello Dati |  |
   |  |  +-----------------------------------+  |  |
   |  |  | Livello 2: Regole di Stato & FSM  |  |  |
   |  |  +-----------------------------------+  |  |
   |  +-----------------------------------------+  |
   +-----------------------------------------------+



### 5.1 Livello 0: Architettura di Sistema e Confini di Dominio
Definisce la macrostruttura, le direzioni delle dipendenze e i confini operativi (*Bounded Contexts*).
* **Invariante Architetturale:** Le dipendenze puntano sempre dall'esterno verso l'interno. Il dominio centrale non deve importare database, driver web o framework.
* **Componenti ammessi:** Port Definition (interfacce astratte), Entità di Dominio, Casi d'Uso applicativi.

### 5.2 Livello 1: Contratti di Interfaccia e Modello Dati
Definisce con precisione algebrica cosa attraversa i confini dei componenti:
* **Input DTOs e Output DTOs:** Tipi primitivi vietati; utilizzo sistematico di *Value Objects* (es. `EmailAddress`, `Money`, `ISOCountryCode`).
* **Matrice di Fallimento (Failure Matrix):** Ogni singola operazione deve mappare l'intero spettro delle anomalie prevedibili.

#### Failure Modes Matrix Standard
| Condizione di Errore | Categoria | Codice Dominio | HTTP Status / RPC Code | Azione Richiesta |
| :--- | :--- | :--- | :--- | :--- |
| Conto sorgente inesistente | Business Error | `SRC_ACC_NOT_FOUND` | 404 Not Found | Terminare flusso |
| Saldo insufficiente | Business Error | `INSUFFICIENT_FUNDS` | 422 Unprocessable | Rifiutare transazione |
| Timeout database di persistenza | Infra Error | `PERSISTENCE_TIMEOUT` | 504 Gateway Timeout | Retry esponenziale |
| Payload non conforme a schema | Contract Error | `MALFORMED_PAYLOAD` | 400 Bad Request | Rifiutare con dettaglio |

### 5.3 Livello 2: Regole di Transizione di Stato ed Edge Cases
Questo livello cattura la logica dinamica. L'errore più comune nei prompt informali è affidare la dinamica temporale a descrizioni testuali. In Clean Spec ogni flusso complesso deve essere espresso tramite una **Tabella di Decisione Logica**.

#### Tabella di Decisione: Autorizzazione Prelievo
| Regola # | Saldo Disponibile $\ge$ Richiesto | Limite Giornaliero Rispettato | Rilevamento Frode = LOW | Esito Atteso | Effetto Collaterale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R1** | Sì | Sì | Sì | `APPROVATO` | Decremento saldo; emissione evento |
| **R2** | No | Qualsiasi | Qualsiasi | `RIFIUTATO` | Log `ERR_OVERDRAFT` |
| **R3** | Sì | No | Qualsiasi | `RIFIUTATO` | Log `ERR_LIMIT_EXCEEDED` |
| **R4** | Sì | Sì | No | `SOSPESO` | Inoltro a team compliance |

---

## Capitolo 6: I Principi S.O.L.I.D. Applicati alle Specifiche

I principi SOLID, formalizzati da Robert C. Martin per la programmazione orientata agli oggetti, trovano un'applicazione isomorfa e ancora più stringente nella stesura delle specifiche per agenti AI.

### 6.1 Single Responsibility Spec (SRS)
* **Principio:** Un file di specifica deve avere un solo e unico motivo per cambiare.
* **Violazione:** Includere nello stesso documento i requisiti di validazione anagrafica dell'utente e la logica di calcolo delle commissioni del gateway di pagamento. Se il fornitore di pagamento cambia fee, non dovremmo mai toccare la specifica utente.
* **Regola pratica:** La specifica di un caso d'uso non deve superare la memoria di lavoro ottimale del contesto di generazione (raccomandazione operativa: non oltre 300 righe di Markdown per singola specifica atomica).

### 6.2 Open/Closed Specs (OCS)
* **Principio:** Le specifiche devono essere aperte all'estensione, ma chiuse alla modifica.
* **Applicazione:** Definire le specifiche dei moduli core tramite contratti ed eventi astratti. Quando si introduce una nuova funzionalità (es. invio SMS oltre alle email), non si riscrive il core della transazione: si estende la specifica creando un nuovo subscriber che rispetta l'interfaccia contrattuale preesistente.

### 6.3 Liskov Substitution nelle Specifiche (LSS)
* **Principio:** Se un sottosistema o provider esterno implementa un'interfaccia definita da una specifica astratta, deve rispettarne tutte le invarianti senza indebolire le postcondizioni o rafforzare le precondizioni.
* **Esempio:** Una specifica astratta di `PaymentGatewayPort` garantisce l'idempotenza con tolleranza di ricezione di chiamate duplicate entro 60 secondi. Nessuna implementazione concreta (Stripe, Adyen, Mock) può richiedere parametri aggiuntivi obbligatori non specificati nell'interfaccia astratta.

### 6.4 Interface Segregation Spec (ISS)
* **Principio:** Un agente o modulo software non deve essere costretto a dipendere da specifiche che non lo riguardano.
* **Problema dell'Agent Injection:** Fornire all'LLM un gigantesco schema OpenAPI monolitico da 50 endpoint genera distrazione contestuale e allucinazioni su campi irrilevanti.
* **Soluzione:** Segmentare le interfacce in viste mirate (*Role-specific Views*). Passare all'agente esclusivamente il sotto-schema del controller su cui deve operare.

### 6.5 Dependency Inversion nelle Specifiche (DIS)
* **Principio:** Le specifiche dei moduli di alto livello non devono mai dipendere dalle specifiche dei dettagli di basso livello. Entrambi devono dipendere da astrazioni formali.
* **Violazione classica:** Scrivere nella specifica di calcolo del bilancio fiscale: *"Salva il risultato nella tabella PostgreSQL `tax_records` con una query UPSERT"*.
* **Formulazione corretta:** *"Il caso d'uso calcola il bilancio fiscale e lo delega all'interfaccia `TaxRecordPersistencePort.save(TaxRecord)`"*. La modalità di persistenza (Postgres, MongoDB, file system) è un dettaglio relegato a una specifica di adattatore separata.

---

# PARTE III: VERIFICA, VALIDAZIONE E WORKFLOW AGENTICI

---

## Capitolo 7: Spec-First e Test-First nell'Era Agentica

### 7.1 La sintesi dei test contrattuali dalla specifica
In un flusso tradizionale, i test sono scritti dall'essere umano per convalidare il codice. Nell'approccio Clean Spec, l'agente riceve la specifica e il suo primo compito non è scrivere l'implementazione, ma **sintetizzare la suite di test contrattuali e i test basati sulle proprietà**.

Poiché la specifica contiene tipi, limiti matematici e tabelle di decisione (Capitolo 5), la generazione dei casi di test è un'operazione computazionalmente deterministica:
* I rami della tabella di decisione diventano `assert` unitari.
* Gli estremi delle definizioni di schema generano controlli sui valori limite (*Boundary Value Testing*).
* Le invarianti logiche vengono tradotte in test basati sulle proprietà (*Property-Based Testing*).

### 7.2 Property-Based Testing come garanzia anti-allucinazione
Gli unit test statici (es. `test_calcola_sconto_10_percento`) hanno un valore limitato: l'agente AI potrebbe involontariamente hardcodare la soluzione per superare il test specifico.

Una Clean Spec impone la definizione formale di proprietà universali, traducibili in librerie come Hypothesis (Python) o fast-check (TypeScript):
$$\forall x \in \text{Carrello}, \quad \text{Subtotale}(x) - \text{Sconto}(x) \le \text{Subtotale}(x)$$
$$\forall x \in \text{Carrello}, \quad \text{PrezzoFinale}(x) \ge 0$$

```python
# Test generato deterministicamente dalla specifica
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=1, max_value=10000)))
def test_invariant_subtotal_always_greater_than_discount(items):
    cart = create_cart_with_prices(items)
    discount = apply_discount_rule(cart)
    assert cart.final_price() >= 0
    assert cart.final_price() <= cart.subtotal()


7.3 I Guardrail di Validazione Meccanica

Prima ancora che il codice arrivi a qualsiasi ambiente di esecuzione, deve attraversare tre cancelli di convalida automatica e puramente deterministica:

[Codice Generato]
       |
       v
+-----------------------+
| 1. Linter Sintattico  | ---> Fallimento: Rifiuto immediato & Auto-Fix
+-----------------------+
       | Successo
       v
+-----------------------+
| 2. Strict Type Check  | ---> Fallimento: Type Mismatch rispetto alla Spec
+-----------------------+
       | Successo
       v
+-----------------------+
| 3. Contract Tests     | ---> Fallimento: Invariante violata
+-----------------------+
       | Successo
       v
[Accettazione Artefatto]


Capitolo 8: Architettura di un Agente Guidato da Spec

8.1 Il loop di retroazione agentico (ReAct Loop vincolato)

Un agente per il software engineering non deve operare come una chat aperta, ma come un automa a stati finiti restrittivo:

$$\text{Spec} \longrightarrow \text{State 0 (Init)} \longrightarrow \text{State 1 (Plan)} \longrightarrow \text{State 2 (Execute)} \longrightarrow \text{State 3 (Validate)}$$

Se la validazione fallisce, l'errore generato dal compilatore o dal runner dei test viene reiniettato come feedback negativo contestuale:

$$\text{Delta} = \text{Atteso (da Spec)} - \text{Ottenuto (da Run)}$$

L'agente non legge nuovamente l'intero contesto, ma riceve esclusivamente il $\text{Delta}$ e corregge l'implementazione fino a quando l'uscita da Validate è priva di errori.

8.2 Struttura gerarchica dei file di contesto

Per evitare il context poisoning, i moderni ambienti di sviluppo agentici richiedono una stratificazione logica dei file di istruzione:

progetto/
├── .cursorrules / CLAUDE.md       # Regole operative universali (Livello Meta)
├── specs/
│   ├── ARCHITECTURE.md            # Livello 0: Confini, standard tecnologici
│   ├── modules/
│   │   ├── billing/
│   │   │   ├── domain_spec.md     # Livello 1 & 2: Invarianti e logica pura
│   │   │   ├── schema.json        # Contratti I/O formali
│   │   │   └── failures.md        # Failure Modes Matrix
│   │   └── identity/
│   └── tests/                     # Suite di verifica contrattuale
└── src/                           # Codice generato (Build Artifact)


Anatomia di un .cursorrules / CLAUDE.md conforme a Clean Spec

# ISTRUZIONI AGENTICHE VINCOLANTI

1. FONTE DI VERITÀ
   * La directory `specs/` contiene la specifica autoritativa.
   * Non inventare comportamenti non specificati. In caso di lacuna semantica, 
     FERMATI e richiedi un chiarimento per aggiornare la specifica prima di scrivere codice.

2. FLUSSO DI LAVORO
   * Passo 1: Leggi la specifica del modulo in `specs/modules/<nome>/`.
   * Passo 2: Genera i test di accettazione basati sulla Failure Matrix e sugli schemi JSON.
   * Passo 3: Scrivi l'implementazione minima necessaria a far passare tutti i test.
   * Passo 4: Esegui il type-checker statico in modalità strict (`tsc --noEmit` o `mypy --strict`).

3. VINCOLI DI CODIFICA
   * Nessun `any` o tipo dinamico non tipizzato.
   * Funzioni pure separate da effetti collaterali I/O (Clean Architecture).


Capitolo 9: Gestione del Ciclo di Vita: Versionamento e Git Hygiene

9.1 La Specifica come entità tracciata su Git

Nel paradigma Clean Spec, i commit storici del repository cambiano fisionomia. L'evoluzione funzionale viene catturata primariamente nella directory specs/:

commit a1b2c3d4
Author: Software Architect <architect@enterprise.org>
Date:   Thu Sep 10 14:00:00 2026

    spec(billing): formalize tiered subscription upgrade invariants
    
    - Add JSON schema for UpgradeSubscriptionCommand
    - Define state transition from TRIAL to PRO in Mermaid
    - Add failure modes: ERR_CARD_DECLINED, ERR_ALREADY_ACTIVE
    - Reference: RFC-2026-SUBS-09


Il commit successivo può essere eseguito direttamente da un agente autonomo (es. via GitHub Actions o workflow locale):

commit e5f6g7h8
Author: Coding Agent <agent-ci@enterprise.org>
Date:   Thu Sep 10 14:02:15 2026

    impl(billing): synthesize subscription upgrade use case from spec a1b2c3d4
    
    - Generated unit & property-based tests (100% contract coverage)
    - Implemented SubscriptionService.upgrade()
    - Static analysis: passed (mypy --strict: 0 errors)


9.2 Drift Detection: Rilevare la divergenza tra Codice e Specifica

Il disallineamento (Spec Drift) avviene quando uno sviluppatore modifica frettolosamente una riga di codice durante un incidente di produzione o quando un modello AI introduce un side-effect non previsto.

Per prevenire questo degrado, la pipeline di Continuous Integration deve includere un Linter di Conformità della Specifica:

Schema Check: Valida che tutte le rotte API espongano esattamente e solo i parametri definiti nello schema della specifica.

Exhaustive Error Coverage Check: Convalida che ogni codice di errore mappato nella Failure Matrix della specifica abbia un rispettivo test unitario che lo scateni.

Spec-to-Code Traceability Tagging: Ogni funzione pubblica deve includere nei suoi metadati o docstring il riferimento immutabile all'ID della specifica che implementa:

@implements_spec("SPEC-BILLING-042", section="1.2")
def calculate_prorated_refund(subscription: Subscription) -> Money:
    ...


PARTE IV: SPEC SMELLS E CATALOGO DEI REFACTORING

Capitolo 10: I Principali "Spec Smells"

Come il codice sorgente manifesta i Code Smells individuati da Martin Fowler e Kent Beck, così le specifiche scritte per modelli AI soffrono di patologie ricorrenti che ne compromettono l'efficacia compilativa.

10.1 The Omniprompt (Il Monolite Contestuale)

Sintomo: Un singolo file di prompt o specifica di 2000 righe che contiene regole architetturali generali, configurazioni del database, descrizioni della UI, validazioni dei form e requisiti di deployment.

Conseguenza: Saturazione dell'attenzione dell'agente. Il modello privilegia le istruzioni iniziali e finali (Lost in the Middle Effect), dimenticando vincoli di sicurezza critici posti al centro del documento.

Cura: Decomposizione gerarchica (Capitolo 11, Extract Bounded Context Spec).

10.2 The Handwave (La Vaghezza Tossica)

Sintomo: Uso di formule discorsive ad alto gradiente di ambiguità:

"Gestisci gli errori in modo robusto ed elegante."

"L'interfaccia deve essere veloce, intuitiva e reattiva."

"Fai in modo che il sistema scali bene sotto carico."

Conseguenza: L'agente inserisce blocchi try/catch vuoti, allucina messaggi generici o trascura del tutto la gestione della concorrenza.

Cura: Sostituzione con matrici di errore deterministiche e vincoli prestazionali formalizzati in millisecondi o complessità computazionale asintotica.

10.3 Syntactic Micromanagement (L'Over-Specification)

Sintomo: La specifica spiega all'agente come scrivere la sintassi riga per riga anziché definire cosa il sistema deve garantire:

"Definisci una variabile let i = 0, fai un ciclo for sull'array, e metti ogni elemento in un dizionario con chiave id."

Conseguenza: Impedisce al modello di utilizzare costrutti idiomatici, librerie vettorializzate, algoritmi ottimali o strutture dati adeguate. Se la specifica scende a livello di codice, ha perso la sua funzione di astrazione.

Cura: Definire precondizioni, postcondizioni e invarianti, lasciando all'agente la libertà esecutiva della sintassi.

10.4 Domain Leakage (Contaminazione da Dettagli Infrastrutturali)

Sintomo: La logica di business pura è mescolata con dettagli di trasporto o persistenza:

"Se il cliente è VIP, esegui una query UPDATE customers SET discount = 0.2 WHERE id = ? e restituisci un JSON con status code 200 via Express.js."

Conseguenza: Impossibilità di riutilizzare la regola di dominio in contesti diversi (es. CLI, batch worker, gRPC) e fragilità estrema nei cambi di framework.

Cura: Dependency Inversion applicata alle specifiche (DIS).

Capitolo 11: Catalogo dei Refactoring della Specifica

11.1 Refactoring: Replace Prose with State Table

Motivazione: Le descrizioni discorsive delle transizioni di stato nei flussi asincroni causano quasi invariabilmente rami morti o allucinazioni sui percorsi di eccezione.

Prima del Refactoring (Prosa Ambigua)

"Quando un ordine viene creato, è in attesa. Se il pagamento arriva, diventa pagato e viene spedito. Se il pagamento fallisce, viene annullato. L'utente può annullarlo solo se non è ancora stato spedito, ma se è già pagato bisogna fare il rimborso."

Dopo il Refactoring (Tabella di Transizione a Stati Finiti)

### FSM-ORD-01: Macchina a Stati dell'Ordine

| Stato Iniziale | Evento Scatenante | Condizione di Guardia | Stato Finale | Effetti Collaterali (Ports) |
| :--- | :--- | :--- | :--- | :--- |
| `PENDING` | `PAYMENT_RECEIVED` | Importo == Totale Ordine | `PAID` | `WarehousePort.reserveStock()` |
| `PENDING` | `PAYMENT_FAILED` | Nessuna | `FAILED` | `NotificationPort.sendAlert()` |
| `PENDING` | `USER_CANCELLED` | Nessuna | `CANCELLED` | Nessuno |
| `PAID` | `USER_CANCELLED` | Spedizione non avviata | `REFUNDING` | `PaymentPort.issueRefund()` |
| `PAID` | `SHIPMENT_DISPATCHED`| Tracking code presente | `SHIPPED` | `NotificationPort.sendTracking()`|
| `SHIPPED` | `USER_CANCELLED` | Non consentito | *Nessun cambio* | Ritorna errore `ILLEGAL_ACTION` |
| `REFUNDING` | `REFUND_SETTLED` | Conferma da Gateway | `REFUNDED` | `NotificationPort.sendReceipt()`|


11.2 Refactoring: Extract Bounded Context Spec

Motivazione: Una specifica monolitica contiene troppe responsabilità, eccedendo il focus contestuale dell'agente.

Meccanismo:

Identificare i confini di dominio (es. Catalog, Checkout, Identity).

Spostare i modelli dati interni e le regole specifiche nei file dedicati.

Sostituire i riferimenti diretti con Contratti di Interfaccia Pubblica o Domain Events.

PARTE V: CASI DI STUDIO COMPLETI ED ESERCITAZIONI

Capitolo 12: Caso Studio 1 — Motore Contabile a Doppia Entrata

Questo capitolo presenta una specifica completa, pronta per l'ingestione da parte di un agente di coding autonomo, per l'implementazione di un motore di contabilità bancaria conforme ai principi di Clean Architecture e Clean Spec.

# SPEC-CORE-001: Motore Contabile a Doppia Entrata (Double-Entry Ledger)

## 1. AMBITO E REQUISITI ARCHITETTURALI
* Questo modulo implementa il core di dominio per la registrazione contabile finanziaria.
* **Architettura:** Pure Domain Layer (Clean Architecture). Nessuna dipendenza da database, 
  framework web o librerie di terze parti al di fuori della standard library e del validatore di tipi.
* **Determinismo:** Tutte le operazioni monetarie **MUST** essere eseguite con aritmetica a 
  precisione fissa o interi a 64-bit (centesimi di unità). I tipi a virgola mobile (`float`, `double`)
  sono **STRICTLY FORBIDDEN**.

## 2. MODELLO DATI E CONTRATTI DI TIPO

### 2.1 Value Object: Money
* `amount_cents`: Integer (Valore assoluto).
* `currency`: Stringa (ISO 4217, 3 caratteri maiuscoli, es. "EUR", "USD").

### 2.2 Entità: LedgerEntry
* `account_id`: UUIDv4.
* `direction`: Enum [`DEBIT`, `CREDIT`].
* `amount`: Money.

### 2.3 Aggregate: Transaction
* `transaction_id`: UUIDv4.
* `timestamp`: ISO 8601 UTC.
* `entries`: Lista di `LedgerEntry` (minimo 2 elementi).
* `status`: Enum [`DRAFT`, `POSTED`, `REJECTED`].

## 3. INVARIANTI DI DOMINIO FONDAMENTALI (Hoare Logic)
Ogni transazione per poter passare allo stato `POSTED` deve soddisfare contemporaneamente:

1. **Balance Invariant (Conservazione del Valore):**
   $$\sum \text{Amount}(\text{DEBIT}) - \sum \text{Amount}(\text{CREDIT}) = 0$$
   La somma esatta dei debiti deve eguagliare la somma esatta dei crediti.
   
2. **Currency Uniformity Invariant:**
   $$\forall e_i, e_j \in \text{entries}, \quad \text{currency}(e_i) = \text{currency}(e_j)$$
   Tutte le voci di una singola transazione devono condividere la medesima valuta.

3. **Non-Zero Amount Invariant:**
   $$\forall e \in \text{entries}, \quad e.\text{amount\_cents} > 0$$
   Nessuna voce può avere valore nullo o negativo.

## 4. FAILURE MODES MATRIX

| Condizione Scatenante | Eccezione Dominio | Azione del Sistema |
| :--- | :--- | :--- |
| Somma Debiti $\neq$ Somma Crediti | `UnbalancedTransactionError` | Transazione marcata `REJECTED`; nessun bilancio alterato |
| Voci con valute miste | `CurrencyMismatchError` | Rifiuto immediato; log di audit |
| Meno di due voci | `InsufficientEntriesError` | Rifiuto della transazione |
| Account sorgente == Account destinazione su stessa transazione | `CircularEntryError` | Rifiuto della transazione |

## 5. REQUISITI PER LA SINTESI DEI TEST (Property-Based Testing)
L'agente implementatore **MUST** generare una suite di test che includa:
* Test di generazione casuale di $N$ transazioni sbilanciate (asserzione del sollevamento di `UnbalancedTransactionError`).
* Test di idempotenza sul posting della stessa transazione.
* Invariante di saldo globale: la somma netta di tutti i conti nel sistema dopo $K$ transazioni `POSTED` deve rimanere costante rispetto allo stato iniziale.


Capitolo 13: Caso Studio 2 — Refactoring di un Sistema Legacy via Spec

13.1 Metodologia di Archeologia Software Guidata da Agenti

Quando un team affronta una base di codice legacy priva di documentazione e ad alto disaccoppiamento, la riscrittura diretta ("blind rewrite") porta quasi sempre al fallimento. Clean Spec formalizza un processo in quattro fasi:

[Legacy Codebase Non Documentato]
              |
              v
   +----------------------+
   | FASE 1: Reverse Spec | ---> L'agente analizza i rami e genera la specifica grezza
   +----------------------+
              |
              v
   +----------------------+
   | FASE 2: Audit Umano  | ---> L'architetto corregge le ambiguità e impone le invarianti
   +----------------------+
              |
              v
   +----------------------+
   | FASE 3: Test Synth   | ---> Generazione della rete di test contrattuali (Safety Net)
   +----------------------+
              |
              v
   +----------------------+
   | FASE 4: Re-Synthesis | ---> L'agente genera il nuovo codice conforme a Clean Architecture
   +----------------------+


13.2 Regole per la Redazione della "Reverse Spec"

Identificare i Side-Effect Nascosti: Esaminare ogni mutazione di stato globale, query diretta al database o chiamata di rete all'interno dei loop legacy e documentarla come interfaccia Port astratta.

Isolare i Big Ball of Mud: Individuare variabili contestuali riutilizzate con significati multipli e suddividerle in Value Object immutabili e tipizzati.

Consolidare le Regole Implicite: Trasformare catene di if-else nidificate in tabelle di decisione esplicite (come formalizzato nel Capitolo 5).

13.3 Il Futuro: La Specifica come Software

Con l'avanzamento delle architetture ad agenti autonomi, il ruolo dell'ingegnere del software si è definitivamente ridefinito. Non siamo più operai della sintassi, incaricati di posizionare manualmente parentesi graffe, tipi o algoritmi di ordinamento elementari.

Siamo Architetti dei Vincoli.

La qualità di un software non si misura più dalla pulizia formale delle sue linee di codice, ma dalla limpidezza, rigore, eleganza e completezza matematica delle sue specifiche. Se una specifica è pulita, il codice sarà corretto, manutenibile e riproducibile all'infinito. Se la specifica è corrotta, nessuna intelligenza artificiale potrà salvare il sistema dal caos.