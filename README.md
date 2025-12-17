# Mini Project Sesi 20 - Edge Computing & IoT in Cloud

**IoT Monitoring System dengan HiveMQ, Python, InfluxDB, dan Grafana**

Sistem monitoring IoT yang mensimulasikan data sensor (energy monitoring, room monitoring, motor monitoring) dan mengirimkannya melalui protokol MQTT menggunakan HiveMQ broker, kemudian menyimpan data ke InfluxDB dan memvisualisasikannya menggunakan Grafana.

## 📋 Daftar Isi

- [Arsitektur Sistem](#arsitektur-sistem)
- [Fitur](#fitur)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Prerequisites](#prerequisites)
- [Instalasi dan Setup](#instalasi-dan-setup)
- [Menjalankan Project](#menjalankan-project)
- [Mengakses Dashboard](#mengakses-dashboard)
- [Struktur Project](#struktur-project)
- [Konfigurasi](#konfigurasi)
- [Troubleshooting](#troubleshooting)

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │ Energy          │         │ script simulasi │            │
│  │ monitoring      │────────▶│ kirim data      │            │
│  │ Room monitoring │         │ (python, js, go)│            │
│  │ Motor monitoring│         │ publisher       │            │
│  └─────────────────┘         └────────┬────────┘            │
│                                       │                      │
│                                       ▼                      │
│                              ┌────────────────┐              │
│                              │    HiveMQ      │              │
│                              │  MQTT Broker   │              │
│                              └────────┬───────┘              │
│                                       │                      │
│                                       ▼                      │
│                              ┌────────────────┐              │
│                              │ script simulasi│              │
│                              │ terima data    │              │
│                              │ (python, js, go)│             │
│                              │  subscriber    │              │
│                              └────────┬───────┘              │
│                                       │                      │
│                                       ▼                      │
└───────────────────────────────────────┼───────────────────────┘
                                        │
                                        ▼
                   ┌────────────────────────────────┐
                   │ ┌──────────┐  ┌──────────┐    │
                   │ │ telegraf │  │ influxdb │    │
                   │ └──────────┘  └──────────┘    │
                   │ ┌──────────┐                  │
                   │ │ grafana  │                  │
                   │ └──────────┘                  │
                   └────────────────────────────────┘
```

## ✨ Fitur

- **Publisher (Simulator Sensor)**
  - ⚡ Energy Monitoring: Konsumsi daya (W), tegangan (V), arus (A)
  - 🌡️ Room Monitoring: Suhu (°C), kelembaban (%), indeks kualitas udara
  - ⚙️ Motor Monitoring: Status (ON/OFF), RPM, suhu, level getaran
  - 🔄 Auto-reconnect dengan exponential backoff
  - 📝 Logging terstruktur dengan level konfigurasi

- **Subscriber (Data Processor)**
  - 📩 Subscribe ke semua topik MQTT
  - 💾 Menyimpan data ke InfluxDB dengan batching
  - 🔄 Retry logic untuk koneksi gagal
  - 📊 Parsing dan transformasi data JSON

- **Monitoring Stack**
  - 🐝 **HiveMQ CE**: MQTT broker dengan web UI (port 8080)
  - 📈 **InfluxDB 2.x**: Time-series database untuk menyimpan metrics
  - 📊 **Grafana**: Dashboard visualisasi real-time dengan auto-provisioning

## 🛠️ Teknologi yang Digunakan

- **MQTT Broker**: HiveMQ Community Edition
- **Programming Language**: Python 3.9+
- **MQTT Client**: paho-mqtt
- **Database**: InfluxDB 2.x
- **Visualization**: Grafana
- **Containerization**: Docker & Docker Compose
- **Libraries**: 
  - `paho-mqtt` (MQTT client)
  - `influxdb-client` (InfluxDB Python client)
  - `python-dotenv` (Environment management)

## 📦 Prerequisites

Pastikan sudah terinstall:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python** (version 3.9+)
- **pip** (Python package manager)
- **Git** (untuk clone repository)

Verifikasi instalasi:
```bash
docker --version
docker-compose --version
python --version
pip --version
```

## 🚀 Instalasi dan Setup

### Quick Start (Menggunakan Makefile)

```bash
# 1. Clone repository
git clone <repository-url>
cd codespaces-blank

# 2. Setup environment dan install dependencies
make setup

# 3. Start Docker services
make start

# 4. Run publisher dan subscriber (di background)
make run-bg

# 5. Open Grafana dashboard
make dashboard
```

### Manual Setup (Tanpa Makefile)

#### 1. Clone Repository

```bash
git clone <repository-url>
cd codespaces-blank
```

#### 2. Setup Environment Variables

```bash
cp .env.example .env
```

Edit file `.env` jika diperlukan (default settings sudah configured untuk development).

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Start Docker Services

```bash
docker-compose up -d
```

Tunggu beberapa saat sampai semua container berjalan. Verifikasi dengan:

```bash
docker-compose ps
```

Output yang diharapkan:
```
NAME                IMAGE                      STATUS
grafana             grafana/grafana:latest     Up
hivemq              hivemq/hivemq-ce:latest    Up
influxdb            influxdb:2.7-alpine        Up
```

#### 5. Verifikasi Services

- **HiveMQ Control Center**: http://localhost:8080
- **InfluxDB UI**: http://localhost:8086
- **Grafana**: http://localhost:3000

## 🎛️ Makefile Commands

Project ini dilengkapi dengan Makefile untuk mempermudah operasional. Lihat semua commands:

```bash
make help
```

### Commands yang Tersedia:

**Setup:**
- `make setup` - Setup environment dan install dependencies
- `make install` - Install Python dependencies saja

**Docker Management:**
- `make start` - Start semua Docker services
- `make stop` - Stop semua Docker services
- `make restart` - Restart semua Docker services
- `make status` - Show status services
- `make logs` - Show logs dari semua services

**Run Applications:**
- `make run-bg` - Run publisher & subscriber di background
- `make stop-apps` - Stop background apps
- `make publisher` - Run publisher (foreground)
- `make subscriber` - Run subscriber (foreground)

**Monitoring:**
- `make dashboard` - Open Grafana dashboard
- `make hivemq` - Open HiveMQ Control Center
- `make influxdb` - Open InfluxDB UI
- `make logs-pub` - Show publisher logs
- `make logs-sub` - Show subscriber logs

**Cleanup:**
- `make clean` - Stop dan remove containers (keep data)
- `make clean-all` - Clean everything termasuk volumes (⚠️ hapus data)

## 🎯 Menjalankan Project

### Cara 1: Menggunakan Makefile (Recommended)

```bash
# Start semua services
make start

# Run publisher dan subscriber di background
make run-bg

# Monitor logs
make logs-pub    # Publisher logs
make logs-sub    # Subscriber logs

# Open dashboards
make dashboard   # Grafana
make hivemq      # HiveMQ Control Center

# Stop applications
make stop-apps
make stop        # Stop Docker services
```

### Cara 2: Manual

#### Menjalankan Publisher (Simulator Sensor)

Di terminal pertama:

```bash
cd publisher
python publisher.py
```

Output yang diharapkan:
```
2025-12-16 10:00:00,123 - Publisher - INFO - Connecting to MQTT broker at hivemq:1883...
2025-12-16 10:00:00,456 - Publisher - INFO - ✓ Connected to MQTT broker at hivemq:1883
2025-12-16 10:00:00,789 - Publisher - INFO - 🚀 Publisher started. Publishing every 5 seconds.
2025-12-16 10:00:00,790 - Publisher - INFO - Press Ctrl+C to stop...

2025-12-16 10:00:01,001 - Publisher - INFO - 📊 Energy: 532.45W
2025-12-16 10:00:01,002 - Publisher - INFO - 🌡️  Room: 24.5°C, 55.2%
2025-12-16 10:00:01,003 - Publisher - INFO - ⚙️  Motor: ON (1850 RPM)
```

### Menjalankan Subscriber (Data Processor)

Di terminal kedua:

```bash
cd subscriber
python subscriber.py
```

Output yang diharapkan:
```
2025-12-16 10:00:05,123 - Subscriber - INFO - Connecting to InfluxDB at http://influxdb:8086...
2025-12-16 10:00:05,456 - Subscriber - INFO - ✓ Connected to InfluxDB (org: iot-org, bucket: iot-data)
2025-12-16 10:00:05,789 - Subscriber - INFO - Connecting to MQTT broker at hivemq:1883...
2025-12-16 10:00:06,012 - Subscriber - INFO - ✓ Connected to MQTT broker at hivemq:1883
2025-12-16 10:00:06,013 - Subscriber - INFO - ✓ Subscribed to topics:
2025-12-16 10:00:06,014 - Subscriber - INFO -   - iot/energy
2025-12-16 10:00:06,015 - Subscriber - INFO -   - iot/room
2025-12-16 10:00:06,016 - Subscriber - INFO -   - iot/motor
2025-12-16 10:00:06,017 - Subscriber - INFO - 🚀 Subscriber started. Listening for messages...

2025-12-16 10:00:07,001 - Subscriber - INFO - 📩 Received from iot/energy
2025-12-16 10:00:07,002 - Subscriber - INFO - ✓ Stored energy data: 532.45W
```

### Alternatif: Run di Background

Untuk menjalankan kedua script di background:

```bash
# Terminal 1
cd publisher && nohup python publisher.py > publisher.log 2>&1 &

# Terminal 2
cd subscriber && nohup python subscriber.py > subscriber.log 2>&1 &

# Monitor logs
tail -f publisher/publisher.log
tail -f subscriber/subscriber.log
```

## 📊 Mengakses Dashboard

### Grafana Dashboard

1. Buka browser dan akses: **http://localhost:3000**
2. Login dengan credentials default:
   - **Username**: `admin`
   - **Password**: `admin`
3. Skip perubahan password (atau ganti sesuai kebutuhan)
4. Dashboard **"IoT Monitoring Dashboard"** sudah otomatis ter-provision
5. Buka menu **Dashboards** → **IoT Monitoring Dashboard**

#### Dashboard Features:

**Energy Monitoring Section:**
- 📈 Time-series chart konsumsi daya
- 🎯 Gauge current power consumption
- ⚡ Stat panel untuk voltage dan current

**Room Monitoring Section:**
- 🌡️ Temperature & Humidity time-series
- 💨 Air Quality Index gauge

**Motor Monitoring Section:**
- 🚦 Motor status (ON/OFF) indicator
- ⚙️ Motor RPM stat panel
- 📊 Detailed charts untuk RPM, temperature, dan vibration

### HiveMQ Control Center

1. Buka browser: **http://localhost:8080**
2. Tidak perlu login (development mode)
3. Dapat melihat:
   - Connected clients
   - Message statistics
   - Topic subscriptions

### InfluxDB UI

1. Buka browser: **http://localhost:8086**
2. Login dengan credentials:
   - **Username**: `admin`
   - **Password**: `adminpassword`
3. Dapat query data menggunakan Flux language
4. Explore buckets dan measurements

## 📁 Struktur Project

```
codespaces-blank/
├── config/
│   ├── __init__.py
│   └── config.py              # Shared configuration
├── publisher/
│   └── publisher.py           # MQTT publisher (simulator)
├── subscriber/
│   └── subscriber.py          # MQTT subscriber (InfluxDB writer)
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── influxdb.yml   # InfluxDB datasource config
│       └── dashboards/
│           ├── dashboard.yml   # Dashboard provider config
│           └── iot-monitoring.json  # Pre-configured dashboard
├── docker-compose.yml         # Docker services definition
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## ⚙️ Konfigurasi

### Environment Variables

Edit file `.env` untuk mengubah konfigurasi:

```bash
# MQTT Configuration
MQTT_BROKER=localhost       # Use 'localhost' when running on host, 'hivemq' inside Docker
MQTT_PORT=1883              # Port MQTT
MQTT_KEEPALIVE=60           # Keepalive interval (seconds)

# MQTT Topics
TOPIC_ENERGY=iot/energy     # Topic untuk energy monitoring
TOPIC_ROOM=iot/room         # Topic untuk room monitoring
TOPIC_MOTOR=iot/motor       # Topic untuk motor monitoring

# InfluxDB Configuration
INFLUXDB_URL=http://localhost:8086  # Use 'localhost' on host, 'influxdb' inside Docker
INFLUXDB_TOKEN=my-super-secret-auth-token
INFLUXDB_ORG=iot-org
INFLUXDB_BUCKET=iot-data

# Publisher Configuration
PUBLISH_INTERVAL=5          # Interval publish data (seconds)

# Logging Level
LOG_LEVEL=INFO             # DEBUG | INFO | WARNING | ERROR
```

**⚠️ Penting:** Default configuration (`.env.example`) sudah configured untuk menjalankan publisher/subscriber di **host machine** (bukan di dalam Docker container). Jika ingin run di dalam Docker container, ganti `localhost` menjadi hostname service (`hivemq`, `influxdb`).

### Sensor Simulation Ranges

Data yang disimulasikan (dalam `publisher/publisher.py`):

```python
# Energy Monitoring
- consumption_watts: 0 - 1000 W
- voltage_volts: 220 - 240 V
- current_amps: 0 - 5 A

# Room Monitoring
- temperature_celsius: 18 - 30 °C
- humidity_percent: 30 - 70 %
- air_quality_index: 0 - 100

# Motor Monitoring
- status: ON / OFF (random)
- rpm: 0 - 3000 (0 saat OFF)
- temperature_celsius: 20 - 80 °C (ON), 20 - 30 °C (OFF)
- vibration_level: 0 - 10 (0 saat OFF)
```

## 🔧 Troubleshooting

### Problem: Container tidak start

**Solution:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Problem: Publisher/Subscriber tidak bisa connect ke HiveMQ

**Error:** `[Errno -2] Name or service not known` atau `Connection refused`

**Root Cause:** Hostname `hivemq` hanya dapat diakses dari dalam Docker network.

**Solution:**

✅ **Default configuration sudah benar** - `.env` menggunakan `localhost`

Jika masih ada error, pastikan:
```bash
# 1. Check .env file
cat .env | grep MQTT_BROKER
# Should show: MQTT_BROKER=localhost

# 2. Recreate .env if needed
cp .env.example .env

# 3. Restart applications
make stop-apps
make run-bg
```

**Catatan Penting:**
- Gunakan `MQTT_BROKER=localhost` dan `INFLUXDB_URL=http://localhost:8086` saat run di **host machine**
- Gunakan `MQTT_BROKER=hivemq` dan `INFLUXDB_URL=http://influxdb:8086` saat run **inside Docker container**

### Problem: Data tidak muncul di Grafana

**Root Cause:** Datasource UID tidak cocok dengan yang diexpect dashboard

**Solution:**
```bash
# Restart Grafana untuk reload configuration
make restart-grafana

# Atau manual
docker-compose restart grafana
```

**Debug Checklist:**
1. ✅ Publisher berjalan dan publish data → `make logs-pub`
2. ✅ Subscriber berjalan dan menerima data → `make logs-sub`
3. ✅ InfluxDB connection berhasil → Check subscriber logs untuk "✓ Connected to InfluxDB"
4. ✅ Grafana datasource configured dengan uid: `influxdb`

**Verify Data in InfluxDB:**
```bash
# Query InfluxDB langsung
docker-compose exec influxdb influx query \
  'from(bucket:"iot-data") |> range(start: -1h) |> filter(fn: (r) => r["_measurement"] == "energy_monitoring")' \
  --org iot-org \
  --token my-super-secret-auth-token

# Count records per measurement
docker-compose exec influxdb influx query \
  'from(bucket:"iot-data") |> range(start: -1h) |> group(columns: ["_measurement"]) |> count()' \
  --org iot-org \
  --token my-super-secret-auth-token
```

**Force Refresh Dashboard:**
1. Open Grafana (http://localhost:3000)
2. Go to Dashboard Settings (gear icon) → JSON Model
3. Click "Save dashboard" (no changes needed)
4. Refresh browser (Ctrl+R atau F5)

### Problem: Permission denied di Docker volumes

**Solution:**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER .

# Atau hapus volumes dan recreate
docker-compose down -v
docker-compose up -d
```

### Problem: Python module not found

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt

# Atau gunakan virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 🛑 Menghentikan Services

### Stop Publisher/Subscriber

Tekan `Ctrl+C` di terminal yang menjalankan script.

### Stop Docker Services

```bash
# Stop containers (data tetap tersimpan)
docker-compose stop

# Stop dan remove containers (data tetap di volumes)
docker-compose down

# Stop, remove containers DAN hapus volumes (HAPUS SEMUA DATA)
docker-compose down -v
```

## 📝 Catatan Tambahan

### Data Persistence

- InfluxDB data disimpan di Docker volume `influxdb-data`
- HiveMQ data disimpan di Docker volume `hivemq-data`
- Grafana data disimpan di Docker volume `grafana-data`
- Data tidak hilang saat restart container (kecuali volume dihapus)

### Scaling

Untuk mensimulasikan multiple sensors:
1. Edit `publisher.py` dan tambahkan sensor ID
2. Jalankan multiple instances dengan sensor ID berbeda
3. Update Grafana query untuk filter by sensor ID

### Production Considerations

Untuk production deployment:
- ⚠️ Ganti semua default passwords
- 🔒 Enable MQTT authentication di HiveMQ
- 🔐 Configure TLS/SSL untuk MQTT dan InfluxDB
- 📊 Setup retention policies di InfluxDB
- 🔄 Configure backup untuk InfluxDB volumes
- 🚀 Use environment-specific `.env` files

## 📚 Referensi

- [HiveMQ Documentation](https://www.hivemq.com/docs/)
- [MQTT Protocol](https://mqtt.org/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Documentation](https://grafana.com/docs/)
- [paho-mqtt Python Client](https://github.com/eclipse/paho.mqtt.python)

## 👨‍💻 Author

Mini Project Sesi 20 - Edge Computing & IoT in Cloud

---

**Happy Monitoring! 🚀**
