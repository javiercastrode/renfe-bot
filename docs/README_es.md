# renfe-bot
![license](https://img.shields.io/github/license/emartinez-dev/renfe-bot.svg)

| Versión de Python compatible | Plataformas compatibles |
|-----------------------------|-------------------------|
| ![Python >= 3.12](https://img.shields.io/badge/python-%3E%3D%203.12-blue.svg) | ![Linux](https://img.shields.io/badge/platform-Linux-blue.svg) ![macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg) ![Windows](https://img.shields.io/badge/platform-Windows-brightgreen.svg) |


_You can also read this in [English](https://github.com/javiercastrode/renfe-bot/blob/master/README.md)_

## Descripción

Renfe-bot es un bot de Telegram diseñado para ayudar a los usuarios en la compra de billetes de tren de Renfe, el principal operador ferroviario de España. El bot monitoriza la disponibilidad de billetes, especialmente en situaciones en las que están agotados y solo vuelven a estar disponibles cuando alguien cancela su reserva. Notifica con prontitud a los usuarios cuando hay billetes disponibles para su compra. El bot cuenta con una interfaz de chat de Telegram para una mejor interacción con el usuario.

## Cómo ejecutarlo

### Opción A: Inicio rápido en Docker Linux

Crea un nuevo bot de Telegram en [@BotFather](https://t.me/BotFather) e inserta la clave de API en el siguiente comando.

```bash
mkdir renfe-bot && cd renfe-bot && curl -O [https://raw.githubusercontent.com/javiercastrode/renfe-bot/refs/heads/master/docker-compose.yml](https://raw.githubusercontent.com/javiercastrode/renfe-bot/refs/heads/master/docker-compose.yml) && echo "BOT_TOKEN=InsertYourTokenHere" > .env && sudo docker compose up -d
