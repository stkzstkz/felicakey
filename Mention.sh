#!/bin/bash

cd /home/kazuki/FelicaKey

sudo systemctl stop Kagi && sudo ./KM4K.py 2
sudo systemctl start Kagi