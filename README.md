# PyConFR 2026 migrations talk demonstration project

This is a demonstration project for my (French) talk given at [PyConFR 2026](https://www.pycon.fr):
[**Migrer les données d'une application Web... sans que tout explose**](https://www.pycon.fr/2026/fr/talks/long-talk.html#talk-KGCRHA)

## Slides

Retrouvez les slides de la présentation [ici](./pyconfr26_migrer_les_donnees_dune_application_web.pdf) !

## Reproduire la présentation

Ce repo contient illustre un projet SQLAlchemy / Alembic minimal.

Pour fonctionner, il nécessite d'avoir un serveur [PostgreSQL](https://www.postgresql.org/download) local en fonctionnement.
Si l'URL / port / user... du serveur ne sont pas ceux par défaut, exportez les bonnes valeurs:

```
export PGUSER=foo
export PGPASSWORD=bar
export PGPORT=5435
...
```

J'utilise [uv](https://docs.astral.sh/uv) pour gérer les dépendances et exécuter le code
(et je vous recommande de faire pareil !)

Ce code a été écrit et testé sur macOS, il fonctionne normalement sous Linux et probablement
(modulo quelques modifications à la marge dans les commandes à exécuter) sous Windows.

### Préparation

```bash
# Installer le projet Python
uv sync
# Créer la DB de démonstration (nommée `pycon`) dans l'état initial
uv run setup_db.py
# Dire à psql de l'utiliser par défaut
export PGDATABASE=pycon
# Créer le user test
psql -c "INSERT INTO public.user (name) VALUES ('Katharina BERARDA');"
# Petit alias pour y voir plus clair
alias query_tables='psql -c "SELECT * FROM alembic_version"; psql -c "SELECT * FROM alembic_version_after"; psql -c "SELECT * FROM public.user;"'
alias query_tables_2='psql -c "SELECT * FROM alembic_version"; psql -c "SELECT * FROM alembic_version_after"; psql -c "SELECT * FROM public.user"; psql -c "SELECT * FROM public.user_comment;"'
```

### Migrer le schéma sans downtime

La migration créant `user.notes` est dans [`41290166298f_add_notes.py`](./app/alembic/versions/41290166298f_add_notes.py). Pour voir son fonctionnement (en deux temps) :

```bash
query_tables
uv run alembic upgrade +1
query_tables
MIGRATION_STEP=after uv run alembic upgrade +1
query_tables
```

Le système custom (incluant la partie `deployment_tag`) est fonctionnel dans [`alembic/env.py`](./app/alembic/env.py).

### Migrer la donnée sans perte

La migration remplaçant `user.notes` par la table `user_comment` est dans [`faa622910d09_notes_to_user_comment.py`](./app/alembic/versions/faa622910d09_notes_to_user_comment.py). Pour voir le fonctionnement du pattern expand-contract :

```bash
psql -c "UPDATE public.user SET notes = '🫒';"

# 1 & 2. Créer le nouveau schéma & les triggers de recopie
uv run alembic upgrade +1
query_tables_2  # user_comment est créée, l'olive n'est que dans user

# 3. Copier la donnée initiale
psql -c "INSERT INTO user_comment (user_id, content) SELECT id, notes FROM public.user;"
query_tables_2  # L'olive est dans les deux tables !
psql -c "UPDATE public.user SET notes = '🌲';"
query_tables_2  # Le sapin est dans les deux tables !

# 4. Déploiement de la version N+1
psql -c "UPDATE public.user SET notes = '🍎';"  # Le trigger marche toujours...
query_tables_2
psql -c "UPDATE public.user_comment SET content = '🌼';"  # ...dans les deux sens !
query_tables_2

# 5. Suppression de l’ancien schéma & des triggers de recopie
MIGRATION_STEP=after uv run alembic upgrade +1
query_tables_2  # La colonne user.notes n'existe plus
```

### Assurer l'intégrité des migrations

À ce stade, notre dernière migration a supprimé la colonne `user.notes`, mais elle est toujours dans [`models/user.py`](./app/models/user.py) !

Vérifions-le :

```bash
uv run check_migrations.py
```
