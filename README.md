# hotel-reservation-sockets

[![CI](https://github.com/mhbemani/hotel-reservation-sockets/actions/workflows/ci.yml/badge.svg)](https://github.com/mhbemani/hotel-reservation-sockets/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A hotel reservation system over plain TCP sockets, written in Python for a computer-networks course. One multi-threaded server and a menu-driven command-line client talk through newline-delimited JSON.

## What it does

- Sign up / log in; view and edit your profile
- View rooms, book a room (dates, number of beds, balance check), cancel a reservation, early check-out
- Admin users can list all users and add, remove, re-price or change the capacity of rooms
- Server state is stored in JSON files (`server/data/`), and every command and file change is logged under `server/logs/`

## Protocol

One JSON object per line, request `{"action": "...", "params": {...}}`, response `{"code": "...", "message": "...", "data": ...}`.
Response codes and messages are in `server/data/Errors.json` (for example `104` success, `403` access denied, `401` invalid value).

Actions: `login`, `signup`, `view_user_information`, `view_rooms`, `booking`, `cancel`, `edit_info`, `get_reservations`, `get_active_reservations`, `leaving`, `view_all_users` (admin), `admin_rooms` (admin), `logout`.

## Run it

```
cd server && python3 server.py     # asks for today's date (DD-MM-YYYY), then listens on 127.0.0.1:8000
cd client && python3 client.py     # in another terminal
```

Host and port for the server are in `server/data/config.json`; the client uses `127.0.0.1:8000` (`client/utils.py`).
`server/data/` holds demo users and rooms (the demo accounts have plain-text passwords).

## Limitations

- Passwords are stored in plain text and requests identify the user only by the `id` sent by the client (there is no session or token), so this is a teaching project, not something to expose to a network.
- JSON files are rewritten on every change without locking, so concurrent clients can overwrite each other's updates.
