from .base import compute_results, add_arrivals #add arrivals pega processos que chegaram e os coloca na fila de prontos. Compute results calcula as métricas.


def _deadline_key(p): #função separada só pra ordenar por deadline (usada tanto no min() de escolha quanto no de preempção)
    """Sort key: processes without deadline go last."""
    return (p.deadline if p.deadline is not None else float('inf'), p.pid) #se o processo não tiver deadline, vira infinito (assim ele nunca "ganha" de quem tem deadline definida). pid é o desempate, igual no priority.py


def run(processes, quantum, overhead, **kwargs):
    """Preemptive EDF — Earliest Deadline First."""
    time = 0 #tempo simulado no sistema operacional
    gantt = [] # ficará guardado o histórico para desenhar o gantt
    remaining = {p.pid: p.burst for p in processes} # dicionario que cuida do tempo que falta de cada processo (necessário pois o burst é um dado original do processo (remaining vai atualizando))
    start_times = {p.pid: [] for p in processes} # como o algortimo é preemptivo, é possível que seja necessário guardar mais de um inicio para cada processo (dicionario com cada projeto com sua lista)
    end_times = {} # lista de tempos em que os processos acabam

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid)) #ordena os precessos na lista de pendentes com base em tempo de chegada e em caso de empate pid (aqui os procesos não chegaram necessariamente)
    ready = [] # fila de prontos (ja chegaram, não terminaram e estão esperando cpu)
    last_pid = None # o ultimo processo que foi executado
    context_switches = 0 #numero de troca de contextos
    preemptions = 0 #numero de preempções

    add_arrivals(pending, ready, time) #Moves processes from pending to ready if arrival <= time. Mutates both lists.

    current = None #processo atualmente em execução na cpu

    while pending or ready or current: #enquanto ainda existir um processo que não terminou continue rodando
        if not ready and current is None: #se não tem processo corrente e nenhum em ready
            if not pending: #se nao tem nenhum em pending também (processo futuro) acabe o loop
                break
            next_t = min(p.arrival for p in pending) #qual o menor tempo de chegada em pending?
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t}) #adiciona conteudo a lista gantt
            time = next_t #tempo da simulação vira o tempo de chegada
            add_arrivals(pending, ready, time) #Moves processes from pending to ready if arrival <= time. Mutates both lists.
            last_pid = None #zera o ultimo processo antes de começar mais um ciclo

        if current is None and ready: #se o processo corrente for nulo e existe um processo pronto na lista ready[]
            current = min(ready, key=_deadline_key) #diferença do priority.py: aqui escolhe quem tem a deadline mais próxima, não a melhor prioridade
            ready.remove(current) #remove da lista de ready o valor que está em current
            start_times[current.pid].append(time) #adiciona o tempo de inicio de execução do novo processo.

        if current is None: #segurança que não vamos acessar "current.pid" de um processo inexistente
            continue

        # qual será o proximo evento importante?
        next_event = time + remaining[current.pid] # tempo atual + tempo que falta do pid corrente
        if pending: #ainda existem processos futuros?
            next_event = min(next_event, min(p.arrival for p in pending)) #mesma ideia do priority.py, só que resumida numa linha só: compara com a proxima chegada

        run_for = next_event - time #quanto tempo a simulação deverá correr, proximo evento - o tempo atual

        #esse if ocorre quando não temos mais processos pendenetes ou seja não há risco de preempção e o processo pode rodar naturalmente
        if run_for <= 0: #se o intervalo de execução for menor = 0 ignorar conta
            run_for = remaining[current.pid] #e rodar o tempo restante
            next_event = time + run_for #tempo atual + quanto falta pra executar

        gantt.append({'type': 'execution', 'pid': current.pid, #registra uma execução na cpu
                      'start': time, 'end': next_event})
        time = next_event #adianta o tempo para o tempo do proximo evento
        remaining[current.pid] -= run_for #atualiza o tempo restante para quanto faltava - quanto andou
        add_arrivals(pending, ready, time) #atualiza a lista pois o tempo mudou

        if remaining[current.pid] <= 0: #verificar se o processo terminou
            end_times[current.pid] = time #caso tenha terminado atualizar tempo de termino
            last_pid = current.pid #colocar o ultimo processo como atual
            current = None #limpar processo atual
        else: #caso nao tenha terminado
            if ready: #se tiver alguem pronto, verifica se rola preempção
                best = min(ready, key=_deadline_key) #quem tem a deadline mais próxima dentre os processos em ready?
                cur_dl = current.deadline if current.deadline is not None else float('inf') #normaliza a deadline do processo atual (mesma lógica do _deadline_key, só que feita aqui na mão)
                best_dl = best.deadline if best.deadline is not None else float('inf') #normaliza a deadline do "melhor" candidato, do mesmo jeito
                if best_dl < cur_dl: # se a deadline do melhor processo em ready for mais próxima que a atual, rola preempção
                    preemptions += 1
                    ready.append(current) #coloca o processo atual na lista de ready
                    last_pid = current.pid #coloca o processo atual como ultimo processo
                    current = None #atualiza processo atual para nulo
                    if overhead > 0: #tratamento de overhead
                        gantt.append({'type': 'overhead', 'pid': last_pid,
                                      'start': time, 'end': time + overhead})
                        time += overhead #adiciona o overhead ao tempo
                        add_arrivals(pending, ready, time) #como mexeu no tempo é preciso checar a lista novamente
                    context_switches += 1 #trocas de contexto (já que o processo inicial não acabou)
                    current = min(ready, key=_deadline_key) #processo corrente vira o de deadline mais próxima em ready
                    ready.remove(current) #processo corrente é removido de ready
                    start_times[current.pid].append(time) #adiciona um novo instante a lista de start_times

    return compute_results(processes, start_times, end_times, gantt, context_switches, preemptions) #calcula tudo e entrega informações relevantes a partir dos dados gerados pelo escalonamento
