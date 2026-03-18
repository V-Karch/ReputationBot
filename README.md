# ReputationBot

Pokemon Scarlet and Violet reputation bot for a trading Discord server

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Project Structure](#project-structure)
* [Requirements](#requirements)
* [Setup Instructions](#setup-instructions)
* [Usage](#usage)
* [Database](#database)
* [Notes](#notes)
* [Security Considerations](#security-considerations)
* [Extension](#extension)
* [License](#license)

---

## Overview

ReputationBot is a modular Discord bot built with `discord.py` that provides:

* User reputation tracking (positive/negative feedback)
* Moderation tools for managing reputation entries
* Predefined informational autoreplies
* Interactive pagination and UI components (buttons, modals)

The bot uses SQLite for persistent storage and Discord slash commands (`app_commands`) for core functionality.

---

## Features

### Reputation System

* `/reputation` — Give positive or negative reputation with a reason
* `/check_reputation` — View a user’s total reputation and history
* `/manage_reputation` — Moderator-only interface for editing entries
* Cooldown enforced per user to prevent spam

### Moderation Tools

* Delete specific reputation entries by ID
* Manually add entries via modal input
* Paginated history viewer with interactive buttons

### Utility Commands (Prefix-based)

* `!customot` — Displays Custom OT tutorial
* `!stamp` — Explains Pokémon GO stamp vs origin marker
* `!crosspost` — Warns against crossposting
* `!tradechannels` — Lists correct trade channels

### Admin Commands

* `/setup` — Initializes the database (owner only)
* `!sync` — Syncs slash commands (owner only)

---

## Project Structure

```
.
├── cogs
│   ├── autoreply.py
│   └── points.py
├── db.py
├── LICENSE
├── main.py
├── model
│   ├── history_paginator.py
│   └── reputation_manager.py
├── points.db
├── README.md
└── token.txt
```

---

## Requirements

* Python 3.11.5+
* `discord.py`

Install dependencies:

```
pip install discord.py
```

---

## Setup Instructions

### 1. Clone the Repository

```
git clone <repo-url>
cd ReputationBot
```

---

### 2. Configure the Bot Token

Create a file named:

```
token.txt
```

Insert your Discord bot token inside:

```
YOUR_BOT_TOKEN_HERE
```

---

### 3. Set Owner ID

Replace all instances of:

```
OWNER_ID = 123456789012345678
```

with your actual Discord user ID.
(This will be changed to a config file later)


---

### 4. Run the Bot

```
python main.py
```

---

### 5. Initialize Database

Run this slash command once:

```
/setup
```

---

### 6. Sync Slash Commands

```
!sync
```

---

## Usage

### Give Reputation

```
/reputation user:<member> experience:<positive|negative> reason:<text>
```

---

### Check Reputation

```
/check_reputation user:<member>
```

---

### Manage Reputation (Owner Only)

```
/manage_reputation user:<member>
```

---

## Database

SQLite file:

```
points.db
```

Schema:

```
reputation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_user_id INTEGER,
    author_user_id INTEGER,
    point_value INTEGER,
    reason TEXT
)
```

---

## Notes

* Slash commands require syncing (`!sync`) after changes
* Cooldown for `/reputation` is 5 minutes per user per guild
* Views (buttons/modals) timeout after inactivity
* SQLite connection is reused per DB instance

---

## Security Considerations

* No permission system beyond owner checks
* Raw SQL execution exists (`exec_sql`)
* Input validation is minimal

---

## Extension

To add new functionality:

1. Create a new file in `/cogs`
2. Define a Cog class
3. Add commands or listeners
4. Include:

```
async def setup(client):
    await client.add_cog(YourCog(client))
```

All `.py` files in `/cogs` are automatically loaded.

---

## License

[MIT](LICENSE)
