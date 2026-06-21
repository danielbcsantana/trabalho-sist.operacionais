import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify
from flask_cors import CORS

from models.processo import Processo
from scheduler import fcfs, sjf, round_robin, priority, edf, autoral

app = Flask(__name__)
CORS(app)

ALGORITHMS = {
    'fcfs': fcfs.run,
    'sjf': sjf.run,
    'round_robin': round_robin.run,
    'priority': priority.run,
    'edf': edf.run,
    'autoral': autoral.run,
}

ALGORITHM_LABELS = {
    'fcfs': 'FIFO / FCFS',
    'sjf': 'SJF',
    'round_robin': 'Round Robin',
    'priority': 'Prioridade Preemptiva',
    'edf': 'EDF',
    'autoral': 'APS (Autoral)',
}


def parse_processes(data_list):
    processes = []
    for item in data_list:
        dl = item.get('deadline')
        processes.append(Processo(
            pid=str(item['pid']),
            arrival=int(item['chegada']),
            burst=int(item['execucao']),
            deadline=int(dl) if dl not in (None, '', 0) else None,
            priority=int(item.get('prioridade', 1)),
            num_pages=int(item.get('num_paginas', 0)),
        ))
    return processes


@app.route('/simular', methods=['POST'])
def simular():
    data = request.get_json(force=True)

    if not data.get('processos'):
        return jsonify({'error': 'Nenhum processo fornecido.'}), 400

    try:
        processes = parse_processes(data['processos'])
    except (KeyError, ValueError) as e:
        return jsonify({'error': f'Dados inválidos: {e}'}), 400

    if not processes:
        return jsonify({'error': 'Lista de processos vazia.'}), 400

    quantum = max(1, int(data.get('quantum', 2)))
    overhead = max(0, int(data.get('sobrecarga', 0)))
    algorithm = data.get('algoritmo', 'fcfs')

    if algorithm == 'todos':
        results = {}
        for name, func in ALGORITHMS.items():
            try:
                result = func(list(processes), quantum, overhead)
                result['algorithm'] = name
                result['label'] = ALGORITHM_LABELS[name]
                results[name] = result
            except Exception as ex:
                results[name] = {'error': str(ex), 'algorithm': name, 'label': ALGORITHM_LABELS[name]}
        return jsonify({'tipo': 'todos', 'resultados': results})

    func = ALGORITHMS.get(algorithm)
    if not func:
        return jsonify({'error': f'Algoritmo desconhecido: {algorithm}'}), 400

    try:
        result = func(processes, quantum, overhead)
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

    result['algorithm'] = algorithm
    result['label'] = ALGORITHM_LABELS[algorithm]
    return jsonify(result)


@app.route('/casos', methods=['GET'])
def list_casos():
    casos_dir = os.path.join(os.path.dirname(__file__), '..', 'casos')
    import json, glob
    casos = []
    for f in sorted(glob.glob(os.path.join(casos_dir, '*.json'))):
        with open(f) as fp:
            casos.append({'nome': os.path.basename(f), 'dados': json.load(fp)})
    return jsonify(casos)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
