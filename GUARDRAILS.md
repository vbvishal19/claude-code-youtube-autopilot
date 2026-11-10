# Guardrails for an AI agent with real access

These are the rules this pipeline runs under. Copy them into your own `CLAUDE.md`
(or equivalent) before you give an agent the keys.

1. **Keys live in files, never in chat.** OAuth clients, tokens and API keys sit in
   `secrets/` (git-ignored) or environment variables. The agent references paths, never
   values. If a key is ever pasted into a chat, rotate it.
2. **Verify identity before every write.** Any job that can act on more than one
   account checks *which* account its token belongs to and stops on a mismatch
   (see `upload_robot/upload.py`).
3. **Deletes are a human click.** The agent may move files into a `_to_delete/` folder.
   A person empties it.
4. **Ask before anything irreversible.** Publishing, spending money or credits,
   sending messages, pushing to a public repo: the agent prepares, a human says yes.
5. **Cheap checks before expensive steps.** Free stills and a contact sheet before
   paid animation; `--dry-run` before an upload.
6. **Fail loudly.** A scheduled job that handled zero items exits non-zero with a clear
   message (see `fail_loudly.py`). Silent success is the worst kind of failure.
7. **Run where the files are.** Scheduled jobs that need local files or sign-ins run on
   that machine, and check their inputs first.
