#!/bin/bash

cd /home/kazuki/FelicaKey

sudo systemctl stop Kagi && sudo ./KM4K.py 0
sudo systemctl start Kagi
