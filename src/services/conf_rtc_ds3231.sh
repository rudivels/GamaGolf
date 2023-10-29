sleep 15
echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
hwclock -s -f /dev/rtc
hwclock -w
