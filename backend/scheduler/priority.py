from .base import compute_results, add_arrivals #add arrivals pega processos que chegaram e os coloca na fila de prontos. Compute results calcula a smétricas.


def run(processes, quantum, overhead, **kwargs):
    """Preemptive priority scheduling. Lower priority number = higher priority."""
    time = 0
    gantt = [] # ficará guardado o histórico para desenhar o gantt
    remaining = {p.pid: p.burst for p in processes} # dicionario que cuida do tempo que falta de cada processo (necessário pois o burst é um dado original do processo (remaining vai atualizando))
    start_times = {p.pid: [] for p in processes} # como o algortimo é preemptivo, é possível que seja necessário guardar mais de um inicio para cada processo (dicionario com cada projeto com sua lista)
    end_times = {} # lista de tempos em que os processos acabam

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid)) #ordena os precessos na lista de pendentes com base em tempo de chegada e em caso de empate pid (aqui os procesos não chegaram necessariamente)
    ready = [] # fila de prontos (ja chegaram, não terminaram e estão esperando cpu)
    last_pid = None # o ultimo processo que foi executado
    context_switches = 0 #numero de troca de contextos
    preemptions = 0 #numero de preempções

    add_arrivals(pending, ready, time) #quais processos ja deveriam ter chegado? move de pending pra ready

    current = None

    while pending or ready or current:
        if not ready and current is None:
            if not pending:
                break
            next_t = min(p.arrival for p in pending)
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})
            time = next_t
            add_arrivals(pending, ready, time)
            last_pid = None

        if current is None and ready:
            current = min(ready, key=lambda p: (p.priority, p.pid))
            ready.remove(current)
            start_times[current.pid].append(time)

        if current is None:
            continue

        # Simulate one time unit to detect preemptions at arrival events
        # Find the next arrival that might trigger a preemption
        next_event = time + remaining[current.pid]  # when current finishes
        if pending:
            next_arrival = min(p.arrival for p in pending)
            next_event = min(next_event, next_arrival)

        run_for = next_event - time
        if run_for <= 0:
            run_for = remaining[current.pid]
            next_event = time + run_for

        gantt.append({'type': 'execution', 'pid': current.pid,
                      'start': time, 'end': next_event})
        time = next_event
        remaining[current.pid] -= run_for
        add_arrivals(pending, ready, time)

        if remaining[current.pid] <= 0:
            end_times[current.pid] = time
            last_pid = current.pid
            current = None
        else:
            # Check if a higher-priority process arrived
            if ready:
                best = min(ready, key=lambda p: (p.priority, p.pid))
                if best.priority < current.priority:
                    # Preempt current
                    preemptions += 1
                    ready.append(current)
                    last_pid = current.pid
                    current = None
                    if overhead > 0:
                        gantt.append({'type': 'overhead', 'pid': last_pid,
                                      'start': time, 'end': time + overhead})
                        time += overhead
                        add_arrivals(pending, ready, time)
                    context_switches += 1
                    current = min(ready, key=lambda p: (p.priority, p.pid))
                    ready.remove(current)
                    start_times[current.pid].append(time)

    return compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
