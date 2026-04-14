<img width="1536" height="1024" alt="Futuristic penguin with IOL logo" src="https://github.com/user-attachments/assets/974d5e40-6ba2-4657-a2ef-5924e2b09993" />
# 🧠 Intelligent OS Layer (IOL)

An advanced, predictive, and self-learning background process governor designed to act as a real-time intelligence layer on top of a Linux OS. 

IOL replaces reactive system optimizations with predictive algorithms and time-sliced process execution, using less than 2% overhead to ensure your UI remains completely unblocked during aggressive multi-core workload bursts.

## ⚡ Core Features

- **🔮 Predictive Workload Engine**: Monitors CPU moving averages and accelerating system deltas to detect and pre-throttle workload spikes *before* they hang up the system.
- **🧬 Behavioral Learning**: Uses a local SQLite dictionary to learn your continuous interactive habits. Over time, applications you heavily prioritize in the foreground gain custom priority protection scores explicitly.
- **🔥 Thermal Intelligence**: Native integration with Linux hardware (`/sys/class/thermal`) to anticipate hardware BIOS throttling states by intercepting execution ahead of safety boundaries.
- **⏱️ Time-Sliced Asynchronous Schedulers**: Non-blocking `asyncio` execution wrappers chunk heavy background daemons down to configurable slice bounds (e.g. `100ms`).

## 🧱 Architecture Layout

```text
iol/
├── main.py                     # Non-blocking async orchestrator
├── config_example.yaml         # Central configurable thresholds
├── monitor/telemetry.py        # psutil wrappers for async reads
├── prediction/trends.py        # CPU acceleration detection logic
├── learning/behavior.py        # SQLite behavior logic
├── thermal/sensors.py          # Native hardware zone readers
├── scheduler/timeslicer.py     # Suspend/Resume micro-chunking logic
├── decision/brain.py           # Core brain synthesizing signals 
├── executor/controller.py      # Safe renice & bash process suspend
└── storage/db.py               # SQLite runtime 
```

## 🚀 Setup Instructions

Ensure you have a recent Linux build installed (`Ubuntu`, `Kali`, `Arch`, `Termux`). `IOL` directly interacts with the `nice`/`renice` execution models and UNIX `SIGSTOP`/`SIGCONT` suspend constraints. 

1. **Install python requirements**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize Daemon Configurations**:
   Read and update `config_example.yaml`. By default, IOL boots under `dry_run: true` to demonstrate logic paths without actively stalling valid operating routines on first runs.

3. **Deploy Core Intelligence Daemon**:
   ```bash
   # Sudo is implicitly required to allow intercept of background processes via os.kill() and psutil.nice().
   sudo ./venv/bin/python main.py --config config_example.yaml --debug
   ```

## 🧪 Included Tools

An aggressive synthetic CPU runtime test (`stress_test.py`) is bundled directly inside the directory to verify the Core Brain predictive heuristic mappings. 

Activate IOL in one terminal, then start the test payload in another:
```bash
./venv/bin/python stress_test.py
```
You can watch the Decision Engine calculate the thermal & runtime acceleration of the payload in real-time, then pre-throttle utilizing chunk bounds.

## 🔒 Safety Assurances
IOL comes standard with extensive Desktop Environment (`gnome`, `kde plasma`, `Xorg`, `pipewire` etc.) whitelists. Critical system daemons (`systemd`, `sshd`) are strictly blocked from receiving CPU suspension interventions. 

## Flow Diagram
<img width="1031" height="796" alt="image" src="https://github.com/user-attachments/assets/99a6561e-af42-41a7-b027-bb37b05f48ff" />

