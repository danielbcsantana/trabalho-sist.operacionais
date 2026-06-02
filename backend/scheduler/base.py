def compute_results(processes, start_times, end_times, gantt, context_switches, preemptions):
    """Computes per-process results and global metrics from raw simulation data."""
    proc_results = {}
    for p in processes:
        end = end_times.get(p.pid)
        starts = start_times.get(p.pid, [])
        turnaround = (end - p.arrival) if end is not None else None
        wait = max(0, turnaround - p.burst) if turnaround is not None else None
        deadline_met = None
        if p.deadline is not None and end is not None:
            deadline_met = bool(end <= p.deadline)
        proc_results[p.pid] = {
            'pid': p.pid,
            'arrival': p.arrival,
            'burst': p.burst,
            'deadline': p.deadline,
            'priority': p.priority,
            'start_times': starts,
            'end_time': end,
            'wait_time': wait,
            'turnaround': turnaround,
            'deadline_met': deadline_met,
        }

    total_time = max((e['end'] for e in gantt), default=0)
    idle_time = sum(e['end'] - e['start'] for e in gantt if e['type'] == 'idle')
    n = len(processes)

    waits = [r['wait_time'] for r in proc_results.values() if r['wait_time'] is not None]
    turnarounds = [r['turnaround'] for r in proc_results.values() if r['turnaround'] is not None]

    metrics = {
        'avg_wait': round(sum(waits) / n, 4) if n > 0 else 0,
        'avg_turnaround': round(sum(turnarounds) / n, 4) if n > 0 else 0,
        'throughput': round(n / total_time, 4) if total_time > 0 else 0,
        'cpu_idle_percent': round(idle_time / total_time * 100, 2) if total_time > 0 else 0,
        'num_preemptions': preemptions,
        'num_context_switches': context_switches,
    }

    return {'gantt': merge_gantt(gantt), 'processes': proc_results, 'metrics': metrics}


def merge_gantt(gantt):
    """Merge consecutive execution events of the same process into one block."""
    if not gantt:
        return gantt
    merged = [gantt[0].copy()]
    for ev in gantt[1:]:
        last = merged[-1]
        if (ev['type'] == 'execution'
                and last['type'] == 'execution'
                and ev['pid'] == last['pid']
                and ev['start'] == last['end']):
            last['end'] = ev['end']
        else:
            merged.append(ev.copy())
    return merged


def add_arrivals(pending, ready, time):
    """Moves processes from pending to ready if arrival <= time. Mutates both lists."""
    arrived = [p for p in pending if p.arrival <= time]
    for p in arrived:
        pending.remove(p)
        ready.append(p)
