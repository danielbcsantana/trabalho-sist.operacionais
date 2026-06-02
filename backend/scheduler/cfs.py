from .base import compute_results, add_arrivals


def run(processes, quantum, overhead, **kwargs):
    """
    CFS-Sim: Completely Fair Scheduler (simplified).

    Each process has a vruntime that grows proportionally to its priority:
        vruntime += slice * priority
    Lower priority number (higher priority) → slower vruntime growth → more CPU time.
    The process with the smallest vruntime is always scheduled next.
    """
    time = 0
    gantt = []
    remaining = {p.pid: p.burst for p in processes}
    vruntime = {}
    start_times = {p.pid: [] for p in processes}
    end_times = {}

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid))
    ready = []
    last_pid = None
    context_switches = 0
    preemptions = 0
    proc_dict = {p.pid: p for p in processes}

    def _arrive(p):
        if ready:
            min_vr = min(vruntime.get(pid, 0) for pid in [r.pid for r in ready])
            vruntime[p.pid] = min_vr
        else:
            vruntime[p.pid] = time
        ready.append(p)

    def _add_arrivals(t):
        arrived = [p for p in pending if p.arrival <= t]
        for p in arrived:
            pending.remove(p)
            _arrive(p)

    _add_arrivals(0)

    while pending or ready:
        if not ready:
            next_t = min(p.arrival for p in pending)
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})
            time = next_t
            _add_arrivals(time)
            last_pid = None
            continue

        current = min(ready, key=lambda p: (vruntime.get(p.pid, 0), p.pid))
        ready.remove(current)

        if last_pid is not None:
            if overhead > 0:
                gantt.append({'type': 'overhead', 'pid': last_pid,
                              'start': time, 'end': time + overhead})
                time += overhead
                _add_arrivals(time)
            context_switches += 1

        slice_t = min(quantum, remaining[current.pid])
        start = time
        start_times[current.pid].append(start)
        gantt.append({'type': 'execution', 'pid': current.pid,
                      'start': start, 'end': start + slice_t})
        time = start + slice_t
        remaining[current.pid] -= slice_t

        # vruntime grows slower for high-priority (low number) processes
        vruntime[current.pid] = vruntime.get(current.pid, 0) + slice_t * current.priority

        last_pid = current.pid
        _add_arrivals(time)

        if remaining[current.pid] <= 0:
            end_times[current.pid] = time
        else:
            if ready:
                best_vr = min(vruntime.get(p.pid, 0) for p in ready)
                if best_vr < vruntime[current.pid]:
                    preemptions += 1
            ready.append(current)

    return compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
