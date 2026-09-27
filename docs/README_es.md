# renfe-bot
![license](https://img.shields.io/github/license/javiercastrode/renfe-bot.svg)

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

```

### Opción B: Ejecución normal en tu ordenador

#### Requisitos

Este proyecto requiere al menos Python 3.12 y funciona en macOS, Linux y Windows.

#### Instalación

Sigue los siguientes pasos para instalar y configurar Renfe-bot:

Clona este repositorio en tu máquina local o descarga el código:

```bash
git clone [https://github.com/javiercastrode/renfe-bot.git](https://github.com/javiercastrode/renfe-bot.git)

```

Instala las dependencias necesarias con el siguiente comando:

```bash
pip install -r requirements.txt

```

Crea un nuevo bot de Telegram en [@BotFather](https://t.me/BotFather?utm_source=gemini) e inserta la clave de API al ejecutar el siguiente comando; la recordará:

```bash
PYTHONPATH=src/
python src/bot.py

```

o este otro si estás en el símbolo del sistema de Windows:

```bash
setx PYTHONPATH src/
python src/bot.py

```

### Opción C: Usar la interfaz de línea de comandos (CLI)

La CLI ofrece la forma más rápida de consultar trenes directamente desde tu terminal.

#### Inicio rápido

Una vez instaladas las dependencias del proyecto (consulta la **Opción B – Instalación** anterior), puedes ejecutar el programa de CLI con la siguiente sintaxis:

```bash
PYTHONPATH=./src python src/cli.py -o <ORIGEN> -d <DESTINO> --departure_date DD/MM/YYYY

```

Ejemplo:

```bash
PYTHONPATH=./src python src/cli.py -o Madrid -d Barcelona --departure_date 21/06/2025

```

El comando imprime una tabla como esta:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃        Trenes de Madrid a Barcelona – 21/06/2025             ┃
┡━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━┯━━━━━━━┩
│ Tipo de tren │ Salida       │ Llegada      │ Duración│ Precio│
├──────────────┼──────────────┼──────────────┼─────────┼───────┤
│ AVE          │ 06:30        │ 08:59        │ 2.5 h.  │ 46.90€│
│ AVE          │ 07:30        │ 10:05        │ 2.6 h.  │ 38.15€│ ← más barato que el promedio resaltado en verde
└──────────────┴──────────────┴──────────────┴─────────┴───────┘

```

#### Argumentos

* **`-o, --origin`** (obligatorio) – Nombre de la estación de origen.
* **`-d, --destination`** (obligatorio) – Nombre de la estación de destino.
* **`--departure_date`** (obligatorio) – Fecha del viaje en formato `DD/MM/YYYY`.

Las horas y los trayectos múltiples aún no se han implementado.

## Uso

### Bot

Para usar el bot, envíale un mensaje en Telegram. Debes proporcionar datos como las estaciones de origen y destino, y las fechas. El bot monitorizará la disponibilidad de los billetes y te notificará inmediatamente cuando haya uno disponible para tu viaje.

### CLI

Consulta la Opción C anterior.

## Contribuir

Este proyecto es de código abierto y las contribuciones son muy bienvenidas. Si deseas contribuir al proyecto, sigue estos pasos:

1. Haz un *fork* del repositorio.
2. Crea una nueva rama para tus cambios.
3. Realiza tus cambios.
4. Sube tus cambios a tu *fork*.
5. Envía una solicitud de extracción (*pull request*) con una descripción de los cambios.

Las contribuciones no se limitan a cambios de código; abrir incidencias (*issues*) o aportar sugerencias es igual de valioso.

## Licencia

Este proyecto está licenciado bajo los términos de la [Licencia MIT](https://opensource.org/license/mit/?utm_source=gemini).

La Licencia MIT es una licencia permisiva que permite la reutilización de software dentro de software propietario, siempre que todas las copias del software con licencia incluyan una copia de los términos de la Licencia MIT y el aviso de copyright.

Esto significa que eres libre de usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias del software, siempre que incluyas la atribución necesaria y proporciones una copia de la licencia MIT.

Puedes ver el texto completo de la licencia en el archivo LICENSE.
