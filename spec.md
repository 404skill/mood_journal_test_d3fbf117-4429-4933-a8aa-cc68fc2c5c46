# Journal Entry System

**Project Details:**

Mood Journal API is a backend-focused learning project that helps users log daily journal entries and receive personalized insights based on their emotional tone. It’s designed to teach real-world development concepts through a simple but emotionally resonant use case.

The system supports journal entry creation, automatic mood extraction (via stubbed logic or AI integration), mood-based content suggestions (like songs and foods), and analytical insights such as mood trends and distributions.

This project covers key backend engineering topics including:

RESTful API design

CRUD operations with persistent storage (SQL/NoSQL)

Data modeling and input validation

Sentiment analysis (mocked or AI-driven)

Static data mapping and enrichment

Aggregation and analytics

Logging and testability

Ideal for junior developers or learners in a company setting, it’s structured to progressively introduce concepts with clear, testable milestones using familiar modern stacks (e.g., Spring Boot, Express.js, or FastAPI).

### Task 1: Initialize Project

**Goal**: Download the project via CLI, and verify the server and test template build successfully.

**What we test**:

- A single call to `GET /health` that should return `200 OK` with a JSON body indicating service health.
1. `GET /health` should respond with something like:
    
    ```json
    {
      "status": "OK"
    }
    ```
    

**<Tip>**

1. Run **Test a project** in the CLI and verify that the first task’s test passes.

### Task 2: Define Journal Entry Model and **POST** Route

**Goal**: Define the data structure for a journal entry and implement `POST /entries` to save entries to the database.

**What to include in the model**:

- `id` - UUID
- `text` - string (non-nullable, not empty)
- `createdAt` - timestamp

**<Tip>**

- `id` can and should be auto generated as a UUID, by the database.
- `createdAt` should get a default value of current timestamp.

**add the `POST /entries` route – Create Entry save to database**

**Goal**: Add new journal entries to database via post request.

**Prerequisite:** familiarize yourself with HTTP status codes - ****[https://en.wikipedia.org/wiki/List_of_HTTP_status_codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)

- **Status codes**:
    - **201 Created** on success, and return entry ID.
    - **400 Bad Request** if validation fails.
- **Request example**:
    
    ```
    {
      "text": "My first journal entry"
    }
    ```
    
- **Response example**:
    
    ```
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
    ```
    
- **Error format**:
    
    ```json
    { "error": "Text must not be empty" }
    ```
    

**<Tip>**

- Validate request, make sure parsing of request body matches your model’s structure. in case validation failed, return `400 bad request`
- Return the created entry id as confirmation.
- A common way to structure an API project is to split it into three layers: controllers, services, and repositories. Controllers accept the HTTP requests and map them to actions, services hold the business logic and orchestration, and repositories isolate all the database calls—keeping each concern focused, testable, and easy to swap out or extend later.

---

### Task 3: Define the Remaining CRUD Operations

### `GET /entries` – Return All Entries

**Goal**: Return a JSON array of all entries,

- **Response example**:
    
    ```json
    [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "text": "First entry",
        "createdAt": "2025-06-22T16:45:00Z"
      },
      { … }
    ]
    ```
    

**<Tip>**

- Return `200 OK` with `[]` if no entries exist.

### `GET /entries/:id` – Return Specific Entry

**Goal**: Return a single entry by its ID.

**Status codes:**

- **200 OK** with entry JSON if found.
- **400 Bad Request** if `:id` is not a valid UUID.
- **404 Not Found** if the entry doesn’t exist.

### `PUT /entries/:id` – Update Entry

**Goal**: Update the `text` of an existing entry, and update the Journal Entry model to include the `updatedAt` - (timestamp) field

**Status codes:**

- **200 OK** with the updated entry id on success.
- **400 Bad Request** for validation failures or malformed UUIDs.
- **404 Not Found** if no entry matches `:id`.
- **Request example**:
    
    ```
    {
      "text": "Updated journal entry"
    }
    ```
    
- **Response example**:
    
    ```json
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
    ```
    

**<Tip>**

- Update the `updatedAt` field when successfully updating a Journal Entry.

### `DELETE /entries/:id` – Delete Entry

**Goal**: Remove an entry by its ID.

**Status codes:**

- **204 No Content** on successful deletion.
- **400 Bad Request** if `:id` is not a valid UUID.
- **404 Not Found** if the entry doesn’t exist.

### Task 4: Mood Extraction Service

**Goal**: Convert journal text into a single mood label, and save it as part of the journal entry in the database.

**What we test for:**

the new response for the `GET /entries` routes, should now include the mood field, this means, changing the Journal Entry as model as well.

now, the `POST /entries` request flow, should also include a step to ‘extract’ mood from the entry’s text, and save it to the database when creating the entry.

notice, that the current Journal Entry model doesn’t have the `mood` field, and so entries already existing in the database, don’t have it as well. consider a way to naturally adding the mood field to them.

<hint> when requested, if an entry doesn’t have a mood field, extract its mood, and save it to the database, as well as return it as part of the response. </hint>

**Instructions:**

We are going to use an external API based on an ML model, in order to extract ‘emotions’ from a given text.

### 1. Get your free HF token

1. Go to [https://huggingface.co/join](https://huggingface.co/join) and create an account (e-mail only).
2. Verify email address.
3. In your profile → Settings → Access Tokens, click “New token” (no card required), and give read and write permissions.

### Curl example:

```bash
# replace HF_TOKEN with the token you generated
curl -X POST https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base \
     -H "Authorization: Bearer HF_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"inputs":"I am so tired and frustrated today"}'
```

**Sample response**:

```json
[
  { "label": "sadness", "score": 0.72 },
  { "label": "anger",   "score": 0.15 },
  { "label": "joy",     "score": 0.04 },
  { "label": "neutral", "score": 0.05 },
  { "label": "fear",    "score": 0.03 },
  { "label": "disgust", "score": 0.01 }
]
```

You get a list of emotion labels sorted by confidence, use the label with the highest confidence to determine the ‘mood’ of the Journal Entry.

**<Tip>**

- This ‘conversion’ logic should be an encapsulated service treated as a ‘black box’
- Access tokens are secure, time-limited credentials issued by an authentication service that your application includes in API requests to prove its identity and permissions. They ensure that only authorized clients can access protected resources and enforce fine-grained access control.

### Task 5: Filter by Moods on the `GET /entries` endpoint.

**Goal**: Allow clients to supply one or more moods as a comma-separated list to filter the entries returned by `GET /entries`.

**What we test**:

- A request like `GET /entries?moods=happy,sad` returns only entries whose `mood` is `"happy"` or `"sad"`.
- If no entries match, returns `200 OK` with an empty array.

**Request example**:

```
GET /entries?moods=happy,sad
```

**Response example**:

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "text": "I love sunny days",
    "createdAt": "2025-06-22T10:00:00Z",
    "mood": "happy"
  },
  {
    "id": "4b6d7e12-1234-5678-abcd-9f0e1d2c3b4a",
    "text": "I miss my friends",
    "createdAt": "2025-06-21T14:30:00Z",
    "mood": "sad"
  }
]
```

**<Tip>**

- Read the `moods` query parameter, split on commas, and filter your database query accordingly.
- Treat missing or empty `moods` parameter as “no filter” (i.e. return all entries).

### Task 6: create the `GET /mood/summary` endpoint – Mood Distribution

**Goal**: Provide a summary of how many entries exist for each mood label.

**What we test**:

- A call to `GET /mood/summary` returns a JSON object mapping each mood to its count.

**Request example**:

```
GET /mood/summary
```

**Response example**:

```json
{
  "happy": 12,
  "sad": 5,
  "angry": 1,
  "tired": 3,
  "neutral": 4
}
```

**<Tip>**

- Return `200 OK` even if there are no entries, in which case the response can be `{}`.

### Task 7: Addition of time Range Filter for the `GET /entries` and `GET /mood/summary` endpoints.

**Goal**: Support `startDate` and `endDate` query parameters (ISO 8601) to limit results to entries whose `createdAt` falls within the given range.

**What we test**:

- `GET /entries?startDate=2025-06-20&endDate=2025-06-22` returns only entries from June 20 through June 22 inclusive.
- `GET /mood/summary?startDate=2025-06-20&endDate=2025-06-22` correctly counts only those entries.

**Request examples**:

```
GET /entries?startDate=2025-06-20&endDate=2025-06-22
GET /mood/summary?startDate=2025-06-20&endDate=2025-06-22
```

**Response examples**:

- **Filtered entries** (`GET /entries?startDate=2025-06-20&endDate=2025-06-22`):
    
    ```json
    [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "text": "Summer vibes",
        "createdAt": "2025-06-20T09:15:00Z",
        "mood": "happy"
      }
    ]
    ```
    
- **Filtered summary** (`GET /mood/summary?startDate=2025-06-20&endDate=2025-06-22`):
    
    ```json
    {
      "happy": 1
    }
    ```
    

**<Tip>**

- If only one parameter is provided, treat the missing bound as unbounded (e.g. no `endDate` → up through “now”).
- Validate date formats and return `400 Bad Request` if they’re invalid (e.g. `{ "error": "Invalid date format" }`).