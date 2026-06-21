from .base import compute_results, add_arrivals


def run(processes, quantum, overhead, **kwargs):
    time = 0
    gantt = []
    remaining = {p.pid: p.burst for p in processes}
    start_times = {p.pid: [] for p in processes}
    end_times = {}

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid))
    ready = []
    last_pid = None
    last_was_preempted = False   # True só quando o processo anterior foi interrompido pelo quantum
    context_switches = 0
    preemptions = 0

    add_arrivals(pending, ready, time)

    while pending or ready:
        if not ready:
            next_t = min(p.arrival for p in pending)
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})
            time = next_t
            add_arrivals(pending, ready, time)
            last_pid = None
            last_was_preempted = False
            continue

        current = ready.pop(0)

        # Sobrecarga só quando o processo anterior foi preemptado (ainda tinha tempo restante)
        if last_pid is not None and last_was_preempted:
            if overhead > 0:
                gantt.append({'type': 'overhead', 'pid': last_pid,
                              'start': time, 'end': time + overhead})
                time += overhead
                add_arrivals(pending, ready, time)
            context_switches += 1

        slice_t = min(quantum, remaining[current.pid])
        start = time
        start_times[current.pid].append(start)
        gantt.append({'type': 'execution', 'pid': current.pid,
                      'start': start, 'end': start + slice_t})
        time = start + slice_t
        remaining[current.pid] -= slice_t
        last_pid = current.pid

        add_arrivals(pending, ready, time)

        if remaining[current.pid] == 0:
            end_times[current.pid] = time
            last_was_preempted = False
        else:
            # Quantum expirou e processo ainda tem execução pendente → preempção real
            preemptions += 1
            last_was_preempted = True
            ready.append(current)

    return compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
