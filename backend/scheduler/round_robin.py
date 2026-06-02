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
            continue

        current = ready.pop(0)

        if last_pid is not None:
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
        else:
            # Quantum expired — preemption
            preemptions += 1
            ready.append(current)

    return compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
