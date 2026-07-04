from .base import compute_results


def _weight(priority):
    return 1.25 ** (priority - 1)


def run(processes, quantum, overhead, **kwargs):
    """
    CFS-Sim: Completely Fair Scheduler (simplified).
        vruntime += Δt × 1.25^(priority - 1)
    """
    time = 0 #inicia tempo atual do simulador
    gantt = []#inicia lista pra "monitorar" oque acontece pra fazer o gantt
    remaining = {p.pid: p.burst for p in processes}#dicionario que vincula o PID com o burst
    vruntime = {}#dicionario pra armazenar o vruntime de cada processo 
    priority_map = {p.pid: p.priority for p in processes}#dicionario que vincula o PID com a prioridade 
    start_times = {p.pid: [] for p in processes}#dicionario que vincula o PID com os tempos que cada processo inicia, no caso ai ta vazio ainda
    end_times = {}#mesma coisa so que com o tempo que termina 
    vr_log = []#lista para monitorar o historico do escalonador

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid)) # lista de pendentes em ordem de chegada e PID
    ready = []#lista de prontos 
    last_pid = None #PID do ultimo 
    last_was_preempted = False#indica se o ultimo foi preemptado
    context_switches = 0# contator de trocas de contexto
    preemptions = 0# contador de preempcoes

    def _arrive(p): # funcao pra quando um processo chegar
        if ready:# dado um processo p, se tiver outros processos prontos , o mais novo recebe o menor vruntime deles, so pra evitar que um processo novo receba 0 ai 
            vruntime[p.pid] = min(vruntime[r.pid] for r in ready)
        else:
            vruntime[p.pid] = float(time)# se n tiver, o vrun inicial vira o tempo atual da simulacao
        ready.append(p)

    def _add_arrivals(t):#coloca todos os projetos em que o tempo de chegada foi ultrapassado ja em prontos 
        arrived = [p for p in pending if p.arrival <= t]
        for p in arrived:
            pending.remove(p)
            _arrive(p)

    def _snapshot(chosen_pid):#isso aqui eh basicamente um feedback do processo naquele momento pro log do vruntime
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

    while pending or ready:# 
        if not ready:# esquema pra verificar cpu ociosa
            next_t = min(p.arrival for p in pending)#variavel com o tempo de inicio o proximo processo
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})#registra a parte ociosa no gantt
            time = next_t #passa o tempo pro proximo tempo em que um processo vair estar pronto
            _add_arrivals(time)#move o q tava em pendente para pronto
            last_pid = None
            continue

        current = min(ready, key=lambda p: (vruntime[p.pid], p.pid))# variavel para pegar o processo com menor vruntime
        ready.remove(current)#remove ele de ready

        # Overhead 
        if last_pid is not None and last_pid != current.pid and last_was_preempted:#verifica condicoes basicas pra aplicar o overfead
            if overhead > 0:
                gantt.append({'type': 'overhead', 'pid': last_pid,# atualiza o gantt com o overhead
                              'start': time, 'end': time + overhead})
                time += overhead#atualiza o tempo de simulacao
                _add_arrivals(time)#chama a funcao pra puxar os processo que tao prontos
            context_switches += 1

        # aqui eh o log pra mostrar as escolhas, so mostra quando um processo acaba, nao toda hora ou a cada unidade de tempo
        if current.pid != last_pid:
            start_times[current.pid].append(time)
            vr_log.append({
                'time':     time,
                'chosen':   current.pid,
                'snapshot': _snapshot(current.pid),
            })

        # esquema do 'slice" em que os processos sao reavaliados
        slice_t = min(1, remaining[current.pid])#roda o menor entre 1 e o restante do processo , geralmente 1 mesmo 
        gantt.append({'type': 'execution', 'pid': current.pid,#atualiza o gantt
                      'start': time, 'end': time + slice_t})
        time += slice_t#atualiza o tempo do simulador
        remaining[current.pid] -= slice_t#atualiza oq falta do processo 
        vruntime[current.pid] += slice_t * _weight(current.priority)#atualiza o vruntime

        last_pid = current.pid
        _add_arrivals(time)

        if remaining[current.pid] <= 0:#verifica se o processo acabou
            end_times[current.pid] = time
            last_was_preempted = False#se acabbou, ele obviamente nao foi preemptado
        else:
            if ready:#caso esteja pronto,compara o vruntime menor com o que ta rodando
                best_vr = min(vruntime[p.pid] for p in ready)
                if best_vr < vruntime[current.pid]:#se for mais justo que o outro, entao substitui 
                    preemptions += 1
                    last_was_preempted = True#como o processo n acabou, ele preemptou
                else:
                    last_was_preempted = False
            else:
                last_was_preempted = False
            ready.append(current)

    result = compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
    result['vr_log'] = vr_log
    return result
