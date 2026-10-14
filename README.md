# SoundPins API

API REST (FastAPI, Pydantic v2) pour des extraits audio géolocalisés. Stockage : mock JSON (`data/mock_db.json`), thread-safe, écriture atomique.

## Lancer

```bash
uv sync
uv run fastapi dev
```

Docs interactives : http://localhost:8000/docs.

Variable : `SOUNDPINS_DB_PATH` (défaut `data/mock_db.json`).

## Qualité

```bash
uv run ruff check .
uv run pytest
```

Les tests utilisent un fichier JSON temporaire par test (fixture `storage`), `mock_db.json` n'est jamais modifié.

## Endpoints

CRUD sans authentification, sur `/api/v1/users/` et `/api/v1/pins/` (POST, GET liste, GET `/{id}`, PUT `/{id}`, DELETE `/{id}`).
Un pin référence un `user_id` existant ; supprimer un utilisateur supprime ses pins.

## Exemples de commits (Conventional Commits)

```
chore: initialise le projet (pyproject, ruff, requirements)
feat(storage): ajoute le stockage JSON thread-safe
feat(users): CRUD des utilisateurs
feat(pins): CRUD des pins
test: ajoute les tests users et pins
ci: ajoute le workflow GitHub Actions (ruff + pytest)
docs: rédige le README
```
