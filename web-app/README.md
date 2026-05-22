# Lean Hogs — Web App

Interactive spread and butterfly analysis tool for CME Lean Hog futures. Reads settlement data from an Excel file and generates Plotly charts with zoom, pan, and hover tooltips.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) with Compose v2+

## Quick start

```bash
DATA_DIR=/path/to/your/data ./start.sh
```

Open **http://localhost:8080** in your browser.

`start.sh` builds both images, starts the stack in the foreground, and tears down the containers automatically when you press `Ctrl+C`.

---

## Data directory

The API container mounts one directory as `/data`. Place your `hog_settlements.xlsx` (or any similarly formatted file) inside that directory.

| Env var | Default | Description |
|---------|---------|-------------|
| `DATA_DIR` | `./data` (created automatically) | Host path mounted to `/data` inside the API container |
| `PORT` | `8080` | Host port the app is served on |

The **Data File** input in the UI expects the path as seen from inside the container — so a file at `<DATA_DIR>/hog_settlements.xlsx` on the host is accessed as `/data/hog_settlements.xlsx` in the UI (the default).

### Examples

**macOS / Linux**
```bash
# Folder next to the compose file
DATA_DIR=./data ./start.sh

# Absolute path
DATA_DIR=/home/jules/trading/settlements ./start.sh

# Custom port
PORT=3000 DATA_DIR=./data ./start.sh
```

**Windows — Command Prompt**
```cmd
set DATA_DIR=C:\Users\jules\trading\settlements
set PORT=3000
docker compose up --build
```

**Windows — PowerShell**
```powershell
$env:DATA_DIR = "C:\Users\jules\trading\settlements"
$env:PORT = 3000
docker compose up --build
```

On Windows use `docker compose up --build` directly instead of `start.sh` (bash is not available by default). Run `docker compose down` afterwards to remove the containers.

**Any platform — `.env` file**

Create a `.env` file in the `web-app` directory and Docker Compose will pick it up automatically:

```env
DATA_DIR=/home/jules/trading/settlements
PORT=3000
```

On Windows use forward slashes or double backslashes in the `.env` file:
```env
DATA_DIR=C:/Users/jules/trading/settlements
PORT=3000
```

---

## Excel file format

| Column | Content |
|--------|---------|
| A | Dates (`yyyy-mm-dd` or `mm/dd/yyyy`) |
| B+ | Settlement prices, one column per contract, named `LN{MONTH}{YEAR}` (e.g. `LNK2024`) |

Sparse data (empty cells) is fine — the app forward-fills gaps of up to 3 days.

---

## Features

### Spreads (near − far)
Select a near contract and one or more far contracts. Five chart views:

| Tab | Description |
|-----|-------------|
| **Historical** | All years overlaid on a shared seasonal axis; 25–75th percentile band + mean |
| **Continuous** | Actual calendar dates; 7-day rolling average |
| **Monthly Boxplot** | Distribution by calendar month + current-year time series |
| **Weekly Boxplot** | Distribution by ISO week + current-year time series |
| **Individual** | One chart per historical year, overlaid with the current year |

### Butterfly (x − 2y + z)
Select predefined combos (JKM, KMN, …) or build a custom three-leg combo. Two view modes:

- **Standard** — individual year lines + mean + percentile band
- **Condensed** — current year + mean only; band highlighted in yellow

Percentile band upper/lower limits are adjustable via sliders. Hover tooltips show the band values in both modes.

### Popout
Every chart has a **↗** button next to its title that opens it full-size in a new window with all Plotly controls enabled.

---

## Development (without Docker)

**Backend**
```bash
cd backend
npm install
npx tsx watch src/index.ts   # runs on :3001
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                  # runs on :5173, proxies /api → :3001
```

Set the **Data File** path in the UI to the absolute path of your Excel file on disk.

---

## Troubleshooting

**`Failed to Setup IP tables` / `No chain/target/match by that name` (Linux with firewalld)**

firewalld flushes iptables chains when it starts, which invalidates Docker's NAT rules. Restart Docker to re-register them:

```bash
sudo systemctl restart docker
./start.sh
```

If this happens after every reboot, ensure Docker starts after firewalld:

```bash
sudo systemctl enable docker
```

Alternatively, switch firewalld to the iptables backend. Edit `/etc/firewalld/firewalld.conf` and set:

```
FirewallBackend=iptables
```

Then restart both services:

```bash
sudo systemctl restart firewalld
sudo systemctl restart docker
```

---

## Architecture

```
web-app/
  backend/    Express + TypeScript — loads Excel, computes spreads & butterflies
  frontend/   React + Vite + Plotly.js + Tailwind CSS
  start.sh    Docker launcher
```
