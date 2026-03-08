import asyncio
import logging
import json
import re
import app_paths
from behringer_mixer import mixer_api

# --- CONFIGURATION ---
DEFAULT_MIXER_IP = "192.168.1.126"
NUMBER_OF_CHANNELS = 32
OUTPUT_FILE = app_paths.get_data_file_path("wing_channels.json")


def sanitize(val):
    if not val or not isinstance(val, str):
        return val
    return re.sub(r"<.*?>|\[.*?\]", "", val).strip()


async def main(ip_address=DEFAULT_MIXER_IP):
    mixer = mixer_api.create("WING", ip=ip_address, logLevel=logging.WARNING)

    try:
        await mixer.start()
        print("Syncing mixer state...")
        await mixer.reload()
        state = mixer.state()

        full_data = []

        for i in range(1, NUMBER_OF_CHANNELS + 1):
            p_base = f"/ch/{i}/"

            channel_info = {
                k.replace(p_base, ""): v
                for k, v in state.items()
                if k.startswith(p_base)
            }

            # If still empty, provide a fallback name
            if not channel_info["config_name"]:
                channel_info["config_name"] = f"Channel {i}"

            full_data.append(channel_info)
            print(f"Fetched Ch {i}: {channel_info['config_name']}")

        with open(OUTPUT_FILE, "w") as f:
            json.dump(full_data, f, indent=4)

        print(f"\nSuccess! Detailed data saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await mixer.stop()


if __name__ == "__main__":
    asyncio.run(main())
