
import subprocess
import sys


def run_adb_command(command):
    """Run a read-only ADB command and return its output."""
    try:
        result = subprocess.run(
            ["adb", "shell", *command],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        return "Error: Command timed out"

    except FileNotFoundError:
        return "Error: ADB is not installed or is not in PATH"


def check_connected_device():
    """Check whether exactly one Android device is connected."""
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )

    except FileNotFoundError:
        print("ERROR: ADB is not installed or is not in PATH.")
        print("Install Android Platform Tools and try again.")
        return False

    except subprocess.TimeoutExpired:
        print("ERROR: ADB did not respond in time.")
        return False

    if result.returncode != 0:
        print("ERROR: Unable to communicate with ADB.")
        print(result.stderr.strip())
        return False

    lines = result.stdout.strip().splitlines()

    # Ignore the heading and inspect the reported devices.
    devices = [
        line for line in lines[1:]
        if line.strip()
    ]

    connected_devices = [
        line for line in devices
        if "\tdevice" in line
    ]

    unauthorized_devices = [
        line for line in devices
        if "\tunauthorized" in line
    ]

    if not devices:
        print("ERROR: No Android device detected.")
        print("Connect your device and enable USB debugging.")
        print("Then verify the connection with: adb devices")
        return False

    if unauthorized_devices:
        print("ERROR: An Android device is connected but unauthorized.")
        print("Unlock your phone and approve the USB debugging prompt.")
        return False

    if not connected_devices:
        print("ERROR: No authorized Android device is available.")
        print("Check the device connection with: adb devices")
        return False

    if len(connected_devices) > 1:
        print("ERROR: Multiple Android devices are connected.")
        print("Connect only one device before running this audit.")
        return False

    return True


def main():
    print("==========================")
    print("  ANDROID SECURITY AUDIT")
    print("==========================")

    # Stop before running the audit if no usable device is available.
    if not check_connected_device():
        sys.exit(1)

    android_version = run_adb_command(
        ["getprop", "ro.build.version.release"]
    )
    print(f"Android Version: {android_version}")

    security_patch = run_adb_command(
        ["getprop", "ro.build.version.security_patch"]
    )
    print(f"Security Patch Level: {security_patch}")

    bootloader_locked = run_adb_command(
        ["getprop", "ro.boot.flash.locked"]
    )
    print(f"Bootloader Locked: {bootloader_locked}")

    verified_boot = run_adb_command(
        ["getprop", "ro.boot.verifiedbootstate"]
    )
    print(f"Verified Boot State: {verified_boot}")

    selinux_status = run_adb_command(["getenforce"])

    encryption_state = run_adb_command(
        ["getprop", "ro.crypto.state"]
    )

    encryption_type = run_adb_command(
        ["getprop", "ro.crypto.type"]
    )

    print(f"SELinux Status: {selinux_status}")
    print(f"Encryption State: {encryption_state}")
    print(f"Encryption Type: {encryption_type}")


if __name__ == "__main__":
    main()