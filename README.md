# Retrozia Vote Monitor

Script Python qui surveille automatiquement le timer de vote sur [retrozia.fun](https://retrozia.fun) et envoie une notification push sur ton telephone quand tu peux voter.

## Fonctionnement

1. Le script se connecte a ton compte Retrozia et recupere le temps restant avant le prochain vote
2. Il attend la fin du timer
3. Des que le vote est disponible, il t'envoie une notification push via [ntfy](https://ntfy.sh)
4. Il reverifie 5 minutes apres chaque notification (le temps que tu votes)
5. Une fois le vote fait, il detecte le nouveau timer et recommence

Le script tourne en boucle, tu n'as rien a faire a part voter quand tu recois la notif.

## Installation

### 1. Installer les dependances Python

```bash
pip install aiohttp python-dotenv
```

### 2. Configurer les notifications (ntfy)

[ntfy](https://ntfy.sh) est un service de notifications push gratuit, sans compte requis.

- Installe l'app **ntfy** sur ton telephone ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) / [iOS](https://apps.apple.com/app/ntfy/id1625396347))
- Ouvre l'app et abonne-toi a un topic avec un **nom long et difficile a deviner** (c'est le nom du topic qui fait office de mot de passe, n'importe qui peut envoyer/lire les messages d'un topic public)
- Exemple : `retrozia-vote-a7x9k2m` plutot que `vote`

### 3. Configurer le .env

Copie le fichier d'exemple et remplis-le :

```bash
cp .env.example .env
```

```env
RETROZIA_USERNAME=ton_pseudo
RETROZIA_PASSWORD=ton_mot_de_passe
NTFY_TOPIC=ton-topic-ntfy
```

### 4. Lancer le script

```bash
python vote_monitor.py
```
