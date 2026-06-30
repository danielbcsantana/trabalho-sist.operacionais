from .base import compute_results


def _weight(priority):
    return 1.25 ** (priority - 1)


def run(processes, quantum, overhead, **kwargs):
    """
    CFS-Sim: Completely Fair Scheduler (simplified).

    vruntime grows proportionally to priority weight:
        vruntime += Δt × 1.25^(priority - 1)
    Lower priority number → smaller weight → slower growth → more CPU time.

    No fixed quantum: the process with smallest vruntime is always selected.
    Slice size = 1 unit; preemption occurs whenever a ready process has a
    smaller vruntime than the currently running process.
    """
    time = 0
    gantt = []
    remaining = {p.pid: p.burst for p in processes}
    vruntime = {}
    priority_map = {p.pid: p.priority for p in processes}
    start_times = {p.pid: [] for p in processes}
    end_times = {}
    vr_log = []

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid))
    ready = []
    last_pid = None
    last_was_preempted = False
    context_switches = 0
    preemptions = 0

    def _arrive(p):
        if ready:
            vruntime[p.pid] = min(vruntime[r.pid] for r in ready)
        else:
            vruntime[p.pid] = float(time)
        ready.append(p)

    def _add_arrivals(t):
        arrived = [p for p in pending if p.arrival <= t]
        for p in arrived:
            pending.remove(p)
            _arrive(p)

    def _snapshot(chosen_pid):
        return sorted(
            [
                {
                    'pid':      pid,
                    'vruntime': round(vr, 2),
                    'weight':   round(_weight(priority_map[pid]), 2),
                }
                for pid, vr in vruntime.items()
                if remaining.get(pid, 0) > 0 or pid == chosen_pid
            ],
            key=lambda e: e['vruntime']
        )

    _add_arrivals(0)

    while pending or ready:
        if not ready:
            next_t = min(p.arrival for p in pending)
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})
            time = next_t
            _add_arrivals(time)
            last_pid = None
            continue

        current = min(ready, key=lambda p: (vruntime[p.pid], p.pid))
        ready.remove(current)

        # Overhead only when process changes due to preemption, not natural completion
        if last_pid is not None and last_pid != current.pid and last_was_preempted:
            if overhead > 0:
                gantt.append({'type': 'overhead', 'pid': last_pid,
                              'start': time, 'end': time + overhead})
                time += overhead
                _add_arrivals(time)
            context_switches += 1

        # Log and record start only when process changes
        if current.pid != last_pid:
            start_times[current.pid].append(time)
            vr_log.append({
                'time':     time,
                'chosen':   current.pid,
                'snapshot': _snapshot(current.pid),
            })

        # Dynamic slice of 1 unit — no fixed quantum
        slice_t = min(1, remaining[current.pid])
        gantt.append({'type': 'execution', 'pid': current.pid,
                      'start': time, 'end': time + slice_t})
        time += slice_t
        remaining[current.pid] -= slice_t
        vruntime[current.pid] += slice_t * _weight(current.priority)

        last_pid = current.pid
        _add_arrivals(time)

        if remaining[current.pid] <= 0:
            end_times[current.pid] = time
            last_was_preempted = False
        else:
            if ready:
                best_vr = min(vruntime[p.pid] for p in ready)
                if best_vr < vruntime[current.pid]:
                    preemptions += 1
                    last_was_preempted = True
                else:
                    last_was_preempted = False
            else:
                last_was_preempted = False
            ready.append(current)

    result = compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
    result['vr_log'] = vr_log
    return result
