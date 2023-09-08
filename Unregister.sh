#!/bin/bash

cd /home/kazuki/FelicaKey

sudo systemctl stop Kagi && sudo ./KM4K.py 1
sudo systemctl start Kagi
