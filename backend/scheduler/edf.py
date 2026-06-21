from .base import compute_results, add_arrivals


def _deadline_key(p):
    """Sort key: processes without deadline go last."""
    return (p.deadline if p.deadline is not None else float('inf'), p.pid)


def run(processes, quantum, overhead, **kwargs):
    """Preemptive EDF — Earliest Deadline First."""
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
            current = min(ready, key=_deadline_key)
            ready.remove(current)
            start_times[current.pid].append(time)

        if current is None:
            continue

        next_event = time + remaining[current.pid]
        if pending:
            next_event = min(next_event, min(p.arrival for p in pending))

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
            if ready:
                best = min(ready, key=_deadline_key)
                cur_dl = current.deadline if current.deadline is not None else float('inf')
                best_dl = best.deadline if best.deadline is not None else float('inf')
                if best_dl < cur_dl:
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
                    current = min(ready, key=_deadline_key)
                    ready.remove(current)
                    start_times[current.pid].append(time)

    return compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
