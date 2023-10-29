#!/bin/bash
config-pin P1.26 can
config-pin P1.28 can
config-pin P2.25 can
config-pin P2.27 can
config-pin P2_05 uart
config-pin P2_07 uart
config-pin P1.08 uart
config-pin P1.10 uart
config-pin P2.09 i2c
config-pin p2.11 i2c
sudo /sbin/ip link set can0 up type can bitrate 125000