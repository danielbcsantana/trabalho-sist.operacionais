from .base import compute_results, add_arrivals

def run(processes, quantum, overhead, **kwargs):
    time = 0 #inicia tempo atual do simulador
    gantt = []#inicia lista pra "monitorar" oque acontece pra fazer o gantt
    remaining = {p.pid: p.burst for p in processes}#dicionario que vincula o PID com o burst
    start_times = {p.pid: [] for p in processes}#dicionario que vincula o PID com os tempos que cada processo inicia, no caso ai ta vazio ainda
    end_times = {}#mesma coisa so que com o tempo que termina 

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid)) # lista de pendentes em ordem de chegada e PID
    ready = []#lista de prontos 
    last_pid = None #PID do ultimo 
    context_switches = 0# contador de trocas de contexto

    add_arrivals(pending, ready, time)#coloca todos os projetos em que o tempo de chegada foi ultrapassado ja em prontos

    while pending or ready:#enquanto tiver processo pendente ou pronto
        if not ready:# esquema pra verificar cpu ociosa
            next_t = min(p.arrival for p in pending)#variavel com o tempo de inicio o proximo processo
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})#registra a parte ociosa no gantt
            time = next_t #passa o tempo pro proximo tempo em que um processo vai estar pronto
            add_arrivals(pending, ready, time)#move o q tava em pendente para pronto
            last_pid = None
            continue

        # variavel para pegar o processo com menor tempo restante (burst). desempata pelo PID
        current = min(ready, key=lambda p: (remaining[p.pid], p.pid))
        ready.remove(current)#remove ele de ready

        start = time #pega o tempo atual
        start_times[current.pid].append(start)#salva no historico
        end = time + remaining[current.pid]#como eh nao-preemptivo, roda tudo de uma vez, somando o burst total
        gantt.append({'type': 'execution', 'pid': current.pid, 'start': start, 'end': end})#atualiza o gantt
        time = end#atualiza o tempo do simulador de uma vez so
        end_times[current.pid] = end#registra que acabou
        remaining[current.pid] = 0#atualiza oq falta do processo (como rodou tudo, zera)
        last_pid = current.pid
        add_arrivals(pending, ready, time)#chama a funcao pra puxar os processo que tao prontos depois desse salto de tempo

    return compute_results(processes, start_times, end_times, gantt, context_switches, 0)#calcula as metricas finais
