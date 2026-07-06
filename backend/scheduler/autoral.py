from .base import compute_results, add_arrivals


def _score(p, time, remaining, all_ready):

    # --- Urgência ---
    if p.deadline is not None:# se tiver deadline, ele calcula a folga entre a deadline e o tempo q o processo acabaria
        slack = (p.deadline - time) - remaining[p.pid]
        if remaining[p.pid] > 0:
            urgency = max(0.0, min(2.0, 1.0 - slack / max(remaining[p.pid], 1)))#normalizacao recomendada, deixa o score mais pesado em algumas circunstancias 
        else:
            urgency = 0.0#trivial
    else:# se nao tiver deadline, vira quase um SJF
        max_rem = max((remaining[q.pid] for q in all_ready), default=1)#entre todos os processo que tao na disputa
        urgency = 1.0 - remaining[p.pid] / max_rem if max_rem > 0 else 0.0# normalizacao pelo maior tempo restante

    # --- Prioridade normalizada (1 = mais alta, valores maiores = mais baixa) ---
    priorities = [q.priority for q in all_ready]#lista com as prioridades
    min_p, max_p = min(priorities), max(priorities)#menor e a maior
    if max_p == min_p:#caso seja tudo igual
        priority_score = 1.0
    else:
        priority_score = (max_p - p.priority) / (max_p - min_p)# mesmo esquema, normaliza pra ficar em termos de 0 a 1 

    # --- Aging: tempo esperando desde a chegada ---
    wait_approx = time - p.arrival#tempo de espera 
    max_wait = max((time - q.arrival) for q in all_ready) if all_ready else 1#mesma situacao de pegar o maior pra hora de normalizar 
    aging = wait_approx / max_wait if max_wait > 0 else 0.0#normalizacao

    return 0.50 * urgency + 0.30 * priority_score + 0.20 * aging#aqui sao os pesos, se quiser testas novos, so mudar 


def _score_detail(p, time, remaining, all_ready):
    #mesma coisa soq pra vizualizacao, serve pra alimentar o score log
    if p.deadline is not None:#urgencia
        slack = (p.deadline - time) - remaining[p.pid]
        urgency = max(0.0, min(2.0, 1.0 - slack / max(remaining[p.pid], 1))) if remaining[p.pid] > 0 else 0.0
    else:
        max_rem = max((remaining[q.pid] for q in all_ready), default=1)
        urgency = 1.0 - remaining[p.pid] / max_rem if max_rem > 0 else 0.0

    priorities = [q.priority for q in all_ready]#prioridade
    min_p, max_p = min(priorities), max(priorities)
    priority_score = 1.0 if max_p == min_p else (max_p - p.priority) / (max_p - min_p)

    wait = time - p.arrival#aging
    max_wait = max((time - q.arrival) for q in all_ready) if all_ready else 1
    aging = wait / max_wait if max_wait > 0 else 0.0

    total = 0.50 * urgency + 0.30 * priority_score + 0.20 * aging
    return {
        'pid':      p.pid,
        'urgency':  round(urgency, 2),
        'priority': round(priority_score, 2),
        'aging':    round(aging, 2),
        'total':    round(total, 2),
    }#a diferenca eh esse dicionario que eh devolvido com cada componente separado e com as informacoes , so pro front


def _log_decision(score_log, time, candidates, chosen, remaining):#tambem pra alimentar o score log, soq no momento da decisao
    score_log.append({# registra o q foi escolhido e os detalhes em ordem do maior pro menor score
        'time':    time,
        'scores':  sorted(
            [_score_detail(p, time, remaining, candidates) for p in candidates],
            key=lambda d: -d['total']
        ),
        'chosen':  chosen.pid,
    })


def run(processes, quantum, overhead, **kwargs):

    time = 0#inicia tempo atual do simulador
    gantt = []#inicia lista pra "monitorar" oque acontece pra fazer o gantt
    remaining = {p.pid: p.burst for p in processes}#dicionario que vincula o PID com o burst
    start_times = {p.pid: [] for p in processes}#dicionario que vincula o PID com os tempos que cada processo inicia, no caso ai ta vazio ainda
    end_times = {}#mesma coisa so que com o tempo que termina 
    score_log = []#lista para monitorar o historico do escalonador(score)

    pending = sorted(processes, key=lambda p: (p.arrival, p.pid)) # lista de pendentes em ordem de chegada e PID
    ready = []#lista de prontos 
    last_pid = None#PID do ultimo 
    context_switches = 0# contator de trocas de contexto
    preemptions = 0# contador de preempcoes

    add_arrivals(pending, ready, time)

    current = None

    while pending or ready or current:#enquanto exister processo 
        if not ready and current is None:# esquema pra verificar cpu ociosa
            if not pending:
                break
            next_t = min(p.arrival for p in pending)#variavel com o tempo de inicio o proximo processo
            gantt.append({'type': 'idle', 'pid': None, 'start': time, 'end': next_t})#registra a parte ociosa no gantt
            time = next_t#passa o tempo pro proximo tempo em que um processo vair estar pronto
            add_arrivals(pending, ready, time)#move o q tava em pendente para pronto
            last_pid = None

        if current is None and ready:#escolher quem vai rodar caso n tenha ngm rodando
            all_candidates = ready[:]# os q tao pronto sao os candidatos 
            current = max(all_candidates, key=lambda p: _score(p, time, remaining, all_candidates))# pega o q tem maior score 
            _log_decision(score_log, time, all_candidates, current, remaining)#printa a decisao
            ready.remove(current)#tira de prontos
            start_times[current.pid].append(time)#adiciona o momento q o processo iniciou

        if current is None:
            continue

        next_event = time + remaining[current.pid]#proxima vez q vai verificar vira quando o processo acabar 
        if pending:
            next_event = min(next_event, min(p.arrival for p in pending))#ou entao, eh a chegada do proximo processo for menor, vai ser ele 

        run_for = next_event - time#se der alguma bad, ele forcaa rodar ate o fim do processo
        if run_for <= 0:
            run_for = remaining[current.pid]
            next_event = time + run_for

        gantt.append({'type': 'execution', 'pid': current.pid,
                      'start': time, 'end': next_event})#registra na gantt
        time = next_event#atualiza o tempo da simulacoa pro proximo evento
        remaining[current.pid] -= run_for# atualiza o burst
        add_arrivals(pending, ready, time)#verifica se alguem chegou e passa pra ready

        if remaining[current.pid] <= 0:#atualiza o tempo que acabou e o last pid
            end_times[current.pid] = time
            last_pid = current.pid
            current = None
        else:#quando o processo nao terminou 
            if ready:# se tiver algum pronto, ele verifica preempcao
                all_candidates = ready + [current]
                best = max(all_candidates, key=lambda p: _score(p, time, remaining, all_candidates))#compara o score
                if best.pid != current.pid:#se for diferente eh pq teve preempcao
                    preemptions += 1
                    ready.append(current)#move pra ready
                    last_pid = current.pid
                    current = None#libera a cpa
                    if overhead > 0:#se tiver ovearhead, registra na gantt
                        gantt.append({'type': 'overhead', 'pid': last_pid,
                                      'start': time, 'end': time + overhead})
                        time += overhead#atualiza o tempo 
                        add_arrivals(pending, ready, time)#ve se chegou alguem pra atualizar
                    context_switches += 1#atualiza
                    all_c = ready[:]
                    current = max(all_c, key=lambda p: _score(p, time, remaining, all_c))# escolhe quem vai rodar
                    _log_decision(score_log, time, all_c, current, remaining)# printa a decisao
                    ready.remove(current)#tira de pronto
                    start_times[current.pid].append(time)#bota o tempo de inicio doq foi escolhido

    result = compute_results(processes, start_times, end_times, gantt, context_switches, preemptions)
    result['score_log'] = score_log
    return result
