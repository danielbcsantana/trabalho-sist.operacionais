from .base import compute_results, add_arrivals


def run(processes, quantum, overhead, **kwargs):
    time = 0#inicia tempo atual do simulador
    gantt = []#inicia lista pra "monitorar" oque acontece pra fazer o gantt
    remaining = {p.pid: p.burst for p in processes}#dicionario que vincula o PID com o burst
    start_times = {p.pid: [] for p in processes}#dicionario que vincula o PID com os tempos que cada processo inicia, no caso ai ta vazio ainda
    end_times = {}#mesma coisa so que com o tempo que termina 

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid))# lista de pendentes em ordem de chegada e PID
    ready = []#lista de prontos 
    last_pid = None #PID do ultimo 
    context_switches = 0# contator de trocas de contexto

    add_arrivals(pending, ready, time)#o processo que tiver nesse tempo, vai pra pronto

    while pending or ready:#enquanto exister processo
        if not ready:# esquema pra verificar cpu ociosa
            next_t = min(p.arrival for p in pending)#variavel com o tempo de inicio o proximo processo
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})#registra a parte ociosa no gantt
            time = next_t#passa o tempo pro proximo tempo em que um processo vair estar pronto
            add_arrivals(pending, ready, time)#move o q tava em pendente para pronto
            last_pid = None
            continue

        current = ready.pop(0)#da pop no q ta pronto

        start = time#o start dele vira o tempo da simulacao 
        start_times[current.pid].append(start)#vincula ao pid do processo 
        end = time + remaining[current.pid]# termino do processo, simples pois eh fifo
        gantt.append({'type': 'execution', 'pid': current.pid, 'start': start, 'end': end})#atualiza gantt
        time = end#atualiza o tempo da simulacao para o fim do processo 
        end_times[current.pid] = end#mesma coisa soq com o final
        remaining[current.pid] = 0#arualiza oq sobre para 0 pq acabou o processo
        last_pid = current.pid
        add_arrivals(pending, ready, time)

    return compute_results(processes, start_times, end_times, gantt, context_switches, 0)
