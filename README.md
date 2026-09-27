# renfe-bot
![license](https://img.shields.io/github/license/emartinez-dev/renfe-bot.svg)

| Python Version Support | Supported Platforms |
|-------------------------|---------------------|
| ![Python >= 3.12](https://img.shields.io/badge/python-%3E%3D%203.12-blue.svg) | ![Linux](https://img.shields.io/badge/platform-Linux-blue.svg) ![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg) ![Windows](https://img.shields.io/badge/platform-Windows-brightgreen.svg) |


_También puedes leer esto en [Español](https://github.com/javiercastrode/renfe-bot/blob/master/docs/README_es.md)_

## Description

Renfe-bot is a Telegram bot designed to assist users in purchasing train tickets
from Renfe, the main railway operator in Spain. The bot monitors ticket
availability, especially in situations when tickets are sold out and only become
available when someone cancels their reservation. It promptly notifies users
when there are tickets available for purchase. The bot supports a Telegram
chatbot interface for enhanced user interaction.

## How to run

### Option A: Quick Start in Docker Linux

Create a new Telegram Bot in [@BotFather](https://t.me/BotFather) and insert the API key in the following command.

```bash
mkdir renfe-bot && cd renfe-bot && curl -O https://raw.githubusercontent.com/javiercastrode/renfe-bot/refs/heads/master/docker-compose.yml && echo "BOT_TOKEN=InsertYourTokenHere" > .env && sudo docker compose up -d
```

### Option B: Running normally in your computer

#### Requirements

This project requires at least Python 3.12, and it runs on macOS, Linux and
Windows.

#### Installation

Follow the below steps to install and set up the Renfe-bot:

Clone this repository to your local machine or download the code
```bash
git clone https://github.com/javiercastrode/renfe-bot.git
```

Install the required dependencies using the following command
```bash
pip install -r requirements.txt
```

Create a new Telegram Bot in [@BotFather](https://t.me/BotFather) and insert the API key when running the following command, it will remember it.

```bash
PYTHONPATH=src/
python src/bot.py
```

or this one if you are on Windows command prompt

```bash
setx PYTHONPATH src/
python src/bot.py
```

### Option C: Using the command‑line interface (CLI)

The CLI offers the fastest way to look up trains straight from your shell.

#### Quick start

Once the project’s dependencies are installed (see **Option A – Installation** above), you can run
the CLI program with the following syntax:

```bash
PYTHONPATH=./src python src/cli.py -o <ORIGIN> -d <DESTINATION> --departure_date DD/MM/YYYY
```

Example:

```bash
PYTHONPATH=./src python src/cli.py -o Madrid -d Barcelona --departure_date 21/06/2025
```

The command prints a table like this:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          Trains from Madrid to Barcelona – 21/06/2025        ┃
┡━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━┯━━━━━━━┩
│ Train type   │ Departure    │ Arrival      │ Duration │ Price │
├──────────────┼──────────────┼──────────────┼─────────┼───────┤
│ AVE          │ 06:30        │ 08:59        │ 2.5 h.   │ 46.90€│
│ AVE          │ 07:30        │ 10:05        │ 2.6 h.   │ 38.15€│ ← cheaper‑than‑avg highlighted in green
└──────────────┴──────────────┴──────────────┴─────────┴───────┘
```

#### Arguments

* **`-o, --origin`** (required) – Origin station name.
* **`-d, --destination`** (required) – Destination station name.
* **`--departure_date`** (required) – Date of travel in `DD/MM/YYYY` format.

Hours and multi-trip have not yet been implemented.

## Usage

### Bot

To use the bot, send a message to your bot on Telegram. You need to provide
inputs such as origin and destination stations, and dates. The bot will monitor
the ticket availability and notify you immediately when there's a ticket
available for your journey.

### CLI

See Option C above.

## Contributing

This project is open source and contributions are very much welcomed. If you
would like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes.
3. Make your changes.
4. Push your changes to your fork.
5. Submit a pull request with a description of the changes.

Contributions are not limited to code changes; opening issues or providing
suggestions are equally valuable.

## License

This project is licensed under the terms of the [MIT
License](https://opensource.org/license/mit/).

The MIT License is a permissive license that allows for reuse of software within
proprietary software provided that all copies of the licensed software include a
copy of the MIT License terms and the copyright notice.

This means that you are free to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the software, as long as you include the
necessary attribution and provide a copy of the MIT license.

You can see the full license text in the LICENSE file.
