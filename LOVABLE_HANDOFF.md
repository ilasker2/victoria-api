# Paste this into Lovable

Victoria’s product UI is built in Lovable. Coaching logic stays in a **separate** Cursor backend. Do not put the Python API, `knowledge/`, or `workspace/` in this Lovable project.

## How GitHub sync works (Lovable-owned)

1. In Lovable: **Project settings → Git → Connect GitHub**. This **creates a new private repository** from this project (Lovable cannot attach an existing GitHub repo).
2. Clone that new repo next to the backend on your machine (Cursor).
3. Sync is two-way on `main`: Lovable ↔ GitHub ↔ local clone.
4. If you already have frontend files (e.g. an older `victoria-web` scaffold), either:
   - **ZIP upload** into Lovable and rebuild, then Connect GitHub; or
   - Connect GitHub first, then copy files into the new clone and `git push` so Lovable picks them up.
5. This project may use **TanStack Start**. Reuse the API contract below; adapt file paths to the Lovable stack. Keep calls in a small client module — do not move coaching logic into edge functions.

## Backend address (local)

| Environment | Base URL |
|---|---|
| Local (Cursor backend) | `http://127.0.0.1:8787` |
| Lovable cloud preview | Cannot reach your localhost. Use mocks in preview, or a tunnel URL later. |

Start the backend from the Cursor repo (`victoria`):

```bash
python3 -m server
```

CORS is open (`Access-Control-Allow-Origin: *`). No auth. Sessions are in-memory. Server binds to `127.0.0.1` only.

Suggested env for the frontend (name may vary by Lovable/Vite/TanStack setup):

```
VITE_API_URL=http://127.0.0.1:8787
```

If you run the frontend locally with a Vite (or similar) proxy, you can leave the base URL empty and proxy `/api` → `http://127.0.0.1:8787`.

## How requests should look

### 1. Health / meta

`GET {BASE}/api/meta`

Example response:

```json
{
  "ok": true,
  "provider": "claude",
  "model": "claude-sonnet-5-5",
  "company_id": "tidewell-systems",
  "profiles": [{ "id": "the-lead-seed-fund", "name": "The lead seed fund" }],
  "persistence": "memory"
}
```

### 2. Start a session

`POST {BASE}/api/sessions`  
Headers: `Content-Type: application/json`  
Body:

```json
{}
```

Example response (opening task menu):

```json
{
  "session_id": "abc123",
  "message": "I'm Victoria. What do you want to work on?\n\n1. Figure out what funding stage you are at\n...",
  "mode": "chooser",
  "task": null,
  "provider": "claude",
  "model": "claude-sonnet-5-5",
  "topic": "orientation"
}
```

### 3. Send a message

`POST {BASE}/api/sessions/{session_id}/messages`  
Headers: `Content-Type: application/json`  
Body:

```json
{ "text": "1" }
```

(`text` is whatever the founder typed — menu number or free text.)

Example response fields to render:

- `message` (string) — show as the assistant bubble
- `session_id`, `mode`, `task`, `topic`, `provider`, `model`
- `calculations` (optional array) — only when not withheld
- `calculations_withheld` (boolean) — hide calc UI in investor practice until feedback

### 4. Optional: reload session

`GET {BASE}/api/sessions/{session_id}` → state + `history`

## Minimal client (TypeScript)

```ts
const BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

async function readJson<T>(res: Response): Promise<T> {
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

export async function getMeta() {
  return readJson(await fetch(`${BASE}/api/meta`));
}

export async function createSession() {
  return readJson(
    await fetch(`${BASE}/api/sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }),
  );
}

export async function sendMessage(sessionId: string, text: string) {
  return readJson(
    await fetch(`${BASE}/api/sessions/${sessionId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    }),
  );
}
```

## UI behavior to implement

1. On load: call `getMeta()` and show provider/model status (or “API unreachable — start python3 -m server”).
2. **Start session** → `createSession()` → show `message` as first assistant bubble; keep `session_id`.
3. Composer → `sendMessage(sessionId, text)` → append user + assistant bubbles.
4. Menu picks are just text (`"1"`, `"2"`, free text). No special endpoints.
5. If `mode === "investor"`, offer an “Ask for feedback” control that sends text like `Please give me feedback`.

## What stays in Cursor (not Lovable)

- Python API (`server/`)
- Finance calculations, Claude calls, public-resource fetching
- Case data (`workspace/`), rules (`.cursor/rules/`), knowledge files

Backend edits take effect after restarting `python3 -m server`. No Lovable redeploy needed for coaching logic.
