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

    add_arrivals(pending, ready, time)

    while pending or ready:
        if not ready:
            next_t = min(p.arrival for p in pending)
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})
            time = next_t
            add_arrivals(pending, ready, time)
            last_pid = None
            continue

        # SJF: pick shortest remaining burst, break ties by pid
        current = min(ready, key=lambda p: (remaining[p.pid], p.pid))
        ready.remove(current)

        if last_pid is not None:
            if overhead > 0:
                gantt.append({'type': 'overhead', 'pid': last_pid,
                              'start': time, 'end': time + overhead})
                time += overhead
                add_arrivals(pending, ready, time)
            context_switches += 1

        start = time
        start_times[current.pid].append(start)
        end = time + remaining[current.pid]
        gantt.append({'type': 'execution', 'pid': current.pid, 'start': start, 'end': end})
        time = end
        end_times[current.pid] = end
        remaining[current.pid] = 0
        last_pid = current.pid
        add_arrivals(pending, ready, time)

    return compute_results(processes, start_times, end_times, gantt, context_switches, 0)
