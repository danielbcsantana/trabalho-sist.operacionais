from .base import compute_results, add_arrivals


def run(processes, quantum, overhead, **kwargs):
    """Preemptive priority scheduling. Lower priority number = higher priority."""
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
