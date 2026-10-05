import sys
import time
import threading
import mido
from evdev import UInput, InputDevice, ecodes as e
from evdev.util import list_devices

# FULL CHROMATIC ROBLOX PIANO MAP (MIDI 36 to 96)
ROBLOX_CHROMATIC_MAP = {
    36: (e.KEY_1, False), 37: (e.KEY_1, True),   # C, C#
    38: (e.KEY_2, False), 39: (e.KEY_2, True),   # D, D#
    40: (e.KEY_3, False),                        # E
    41: (e.KEY_4, False), 42: (e.KEY_4, True),   # F, F#
    43: (e.KEY_5, False), 44: (e.KEY_5, True),   # G, G#
    45: (e.KEY_6, False), 46: (e.KEY_6, True),   # A, A#
    47: (e.KEY_7, False),                        # B
    48: (e.KEY_8, False), 49: (e.KEY_8, True),   # C, C#
    50: (e.KEY_9, False), 51: (e.KEY_9, True),   # D, D#
    52: (e.KEY_0, False),                        # E
    53: (e.KEY_Q, False), 54: (e.KEY_Q, True),   # F, F#
    55: (e.KEY_W, False), 56: (e.KEY_W, True),   # G, G#
    57: (e.KEY_E, False), 58: (e.KEY_E, True),   # A, A#
    59: (e.KEY_R, False),                        # B
    60: (e.KEY_T, False), 61: (e.KEY_T, True),   # C, C#
    62: (e.KEY_Y, False), 63: (e.KEY_Y, True),   # D, D#
    64: (e.KEY_U, False),                        # E
    65: (e.KEY_I, False), 66: (e.KEY_I, True),   # F, F#
    67: (e.KEY_O, False), 68: (e.KEY_O, True),   # G, G#
    69: (e.KEY_P, False), 70: (e.KEY_P, True),   # A, A#
    71: (e.KEY_A, False),                        # B
    72: (e.KEY_S, False), 73: (e.KEY_S, True),   # C, C#
    74: (e.KEY_D, False), 75: (e.KEY_D, True),   # D, D#
    76: (e.KEY_F, False),                        # E
    77: (e.KEY_G, False), 78: (e.KEY_G, True),   # F, F#
    79: (e.KEY_H, False), 80: (e.KEY_H, True),   # G, G#
    81: (e.KEY_J, False), 82: (e.KEY_J, True),   # A, A#
    83: (e.KEY_K, False),                        # B
    84: (e.KEY_L, False), 85: (e.KEY_L, True),   # C, C#
    86: (e.KEY_Z, False), 87: (e.KEY_Z, True),   # D, D#
    88: (e.KEY_X, False),                        # E
    89: (e.KEY_C, False), 90: (e.KEY_C, True),   # F, F#
    91: (e.KEY_V, False), 92: (e.KEY_V, True),   # G, G#
    93: (e.KEY_B, False), 94: (e.KEY_B, True),   # A, A#
    95: (e.KEY_N, False), 96: (e.KEY_M, False)
}

# --- CONFIGURATION TUNING ---
PITCH_OFFSET = 0  
TARGET_VENDOR = 0x1a2c
TARGET_PRODUCT = 0x6004

HOTKEY_START = e.KEY_F8   
HOTKEY_PAUSE = e.KEY_F10
HOTKEY_STOP  = e.KEY_F12

STROKE_DELAY = 0.002  

# Global States
has_started = False
is_paused = False
stop_playback = False

def find_target_keyboard():
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        try:
            info = device.info
            if info.vendor == TARGET_VENDOR and info.product == TARGET_PRODUCT:
                if e.EV_KEY in device.capabilities() and HOTKEY_STOP in device.capabilities()[e.EV_KEY]:
                    return device
        except Exception:
            continue
    return None

def listen_for_hotkeys():
    global stop_playback, has_started, is_paused
    kbd = find_target_keyboard()
    if not kbd:
        for path in list_devices():
            try:
                dev = InputDevice(path)
                if e.EV_KEY in dev.capabilities() and HOTKEY_STOP in dev.capabilities()[e.EV_KEY]:
                    if "py-evdev-uinput" not in dev.name:
                        kbd = dev
                        break
            except Exception:
                continue
    if not kbd:
        return

    print(f"⌨️  Hotkeys bound to device: {kbd.name}")
    try:
        for event in kbd.read_loop():
            if stop_playback:
                break
            
            if event.type == e.EV_KEY and event.value == 1: 
                if event.code == HOTKEY_START and not has_started:
                    print("\n▶️  F8 Pressed! Starting song playback...")
                    has_started = True
                elif event.code == HOTKEY_PAUSE and has_started:
                    is_paused = not is_paused
                    state_msg = "⏸️  Playback PAUSED." if is_paused else "▶️  Playback RESUMED."
                    print(f"\n{state_msg}")
                elif event.code == HOTKEY_STOP:
                    print("\n🛑 F12 Pressed! Stopping and exiting...")
                    stop_playback = True
                    break
    except Exception:
        pass

def play_midi(file_path):
    global stop_playback, has_started, is_paused
    try:
        mid = mido.MidiFile(file_path)
    except Exception as error:
        print(f"Error loading file: {error}")
        return

    hotkey_thread = threading.Thread(target=listen_for_hotkeys, daemon=True)
    hotkey_thread.start()

    print("Initializing virtual keyboard device...")
    with UInput() as ui:
        print("\n⏳ WAITING FOR YOU: Click into Roblox, then press [F8] to start playing!")
        
        while not has_started:
            if stop_playback:
                return
            time.sleep(0.05)
        
        print(f"🎶 Playing infinitely... Controls: [F10] Pause/Resume | [F12] Stop")
        
        shift_is_held = False
        loop_count = 1

        # Keep running infinitely until the user hits F12
        while not stop_playback:
            print(f"\n🔁 Starting Loop #{loop_count}...")
            
            for msg in mid:
                if stop_playback:
                    break
                    
                while is_paused:
                    if stop_playback:
                        break
                    if shift_is_held:
                        ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                        shift_is_held = False
                        ui.syn()
                    time.sleep(0.02)
                
                if msg.time > 0:
                    time.sleep(msg.time)
                    
                if msg.type == 'set_tempo':
                    continue
                    
                if hasattr(msg, 'channel') and msg.channel == 9: 
                    continue

                if msg.type == 'note_on' and msg.velocity > 0:
                    adjusted_note = msg.note + PITCH_OFFSET
                    if adjusted_note in ROBLOX_CHROMATIC_MAP:
                        key, requires_shift = ROBLOX_CHROMATIC_MAP[adjusted_note]
                        
                        if requires_shift and not shift_is_held:
                            ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
                            shift_is_held = True
                            ui.syn()
                            time.sleep(STROKE_DELAY)
                        elif not requires_shift and shift_is_held:
                            ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                            shift_is_held = False
                            ui.syn()
                            time.sleep(STROKE_DELAY)
                            
                        ui.write(e.EV_KEY, key, 1)
                        ui.syn()
                        
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    adjusted_note = msg.note + PITCH_OFFSET
                    if adjusted_note in ROBLOX_CHROMATIC_MAP:
                        key, requires_shift = ROBLOX_CHROMATIC_MAP[adjusted_note]
                        
                        ui.write(e.EV_KEY, key, 0)
                        ui.syn()
                        
                        if requires_shift and shift_is_held:
                            time.sleep(STROKE_DELAY)
                            ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                            shift_is_held = False
                            ui.syn()
            
            # Clean up key states at the end of a loop iteration
            if shift_is_held:
                ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
                shift_is_held = False
                ui.syn()
                
            loop_count += 1
            time.sleep(0.5)  # Short half-second rest before restarting the file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python autoplay.py <path_to_midi_file.mid>")
        sys.exit(1)
    
    play_midi(sys.argv[1])

