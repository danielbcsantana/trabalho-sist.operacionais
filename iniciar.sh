#!/bin/bash
# Inicia o backend Flask na porta 5001
cd "$(dirname "$0")/backend"
echo "==================================="
echo " Simulador de Escalonamento de Processos"
echo " Backend: http://localhost:5001"
echo " Frontend: abra frontend/index.html no navegador"
echo "==================================="
python3 app.py
