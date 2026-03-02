from __future__ import annotations

import argparse

from isaacsim import SimulationApp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch Isaac Sim with ROS2 bridge and load a sample scene.")
    parser.add_argument("--headless", action="store_true", help="Run without UI")
    parser.add_argument("--test-seconds", type=float, default=0.0, help="Auto-close after N seconds (for smoke tests)")
    parser.add_argument(
        "--stage-url",
        type=str,
        default="",
        help="Optional USD path/URL to open on startup. If omitted, opens ROS2 Carter sample scene.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = SimulationApp({"headless": args.headless})

    import omni.kit.app
    import omni.usd
    from isaacsim.storage.native import get_assets_root_path

    ext_manager = omni.kit.app.get_app().get_extension_manager()
    ext_manager.set_extension_enabled_immediate("isaacsim.ros2.bridge", True)

    assets_root = get_assets_root_path()
    if not assets_root:
        raise RuntimeError("Could not resolve Isaac Sim assets root path")

    stage_path = args.stage_url.strip() or f"{assets_root}/Isaac/Samples/ROS2/Scenario/carter_warehouse_navigation.usd"
    opened = omni.usd.get_context().open_stage(stage_path)
    print(f"ROS2_SAMPLE_STAGE={stage_path}")
    print(f"ROS2_SAMPLE_OPENED={opened}")

    elapsed = 0.0
    timestep = 1.0 / 60.0

    try:
        while app.is_running():
            app.update()
            if args.test_seconds > 0:
                elapsed += timestep
                if elapsed >= args.test_seconds:
                    break
    finally:
        app.close()


if __name__ == "__main__":
    main()
