# Upstox Ready Algo

Ready-made Python algo bot for:
- paper trading
- win-rate tracking
- switch to live orders on Upstox
- deployment to VPS

## 1) Setup

One-click (recommended):

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

With real Upstox data in paper mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1 -DataSource upstox -Iterations 300
```

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
copy .env.example .env
```

Edit `.env` and set at least:
- `UPSTOX_ACCESS_TOKEN`
- `INSTRUMENT_KEY` (example: `NSE_INDEX|Nifty 50` or option instrument key)

## 2) Run paper trading (safe)

Simulated market data:

```bash
python -m upstox_ready_algo.cli --mode paper --data-source simulated --iterations 300
```

Paper trades on real Upstox LTP feed (no live orders):

```bash
python -m upstox_ready_algo.cli --mode paper --data-source upstox --iterations 300
```

Output files:
- `logs/trades.csv`
- `logs/summary.json` (includes win rate and net PnL)

## 3) Go live (real orders)

Start only after paper validation.

```bash
python -m upstox_ready_algo.cli --mode live --data-source upstox --iterations 300
```

## 4) Deploy on VPS

Linux:

```bash
bash deploy/run_live.sh
```

Windows server:

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\run_live.ps1
```

## 5) Risk settings

Tune in `.env`:
- `RISK_PER_TRADE_PCT`
- `MAX_DAILY_LOSS_PCT`
- `STOP_LOSS_PCT`
- `SHORT_WINDOW`, `LONG_WINDOW`

## Notes

- No strategy can guarantee profit.
- Start with small capital and monitor regularly.
- Keep API keys/tokens in `.env` only.

## 6) Isaac Sim ROS2 bridge (custom project node)

This repo now includes a project-owned ROS2 bridge node (separate from Isaac Sim installed packages).

Location:
- `src/upstox_ready_algo/ros2/isaac_bridge_node.py`

Run:

```bash
pip install -e .
upstox-isaac-bridge
```

Default topic mapping:
- `/cmd_vel` -> `/isaac/cmd_vel`
- `/isaac/joint_states` -> `/joint_states`

Override topics/queue size:

```bash
upstox-isaac-bridge --ros-args \
	-p cmd_vel_in:=/robot/cmd_vel \
	-p cmd_vel_out:=/sim/cmd_vel \
	-p joint_states_in:=/sim/joint_states \
	-p joint_states_out:=/robot/joint_states \
	-p queue_size:=20
```

Note:
- You must run this from a ROS2-enabled environment (`rclpy`, `geometry_msgs`, `sensor_msgs` available).
