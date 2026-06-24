# Hub Acadêmico de Computação — UFBA

Portal centralizado de disciplinas do curso de Ciência da Computação da UFBA. Reúne conteúdo teórico, referências rápidas e simuladores interativos em um único lugar, desenvolvido e mantido pelos próprios alunos.

---

## Estrutura do Projeto

```
/
├── index.html                          # Portal principal (Hub Acadêmico)
├── iniciar.sh                          # Script de inicialização do backend
├── requirements.txt                    # Dependências Python
│
├── backend/                            # API Flask (simulador de SO)
│   ├── app.py                          # Servidor e rotas
│   ├── models/
│   │   └── processo.py                 # Dataclass Processo
│   └── scheduler/
│       ├── base.py                     # Métricas e utilitários compartilhados
│       ├── fcfs.py                     # FIFO / First Come First Served
│       ├── sjf.py                      # Shortest Job First
│       ├── round_robin.py              # Round Robin
│       ├── priority.py                 # Prioridade Preemptiva
│       ├── edf.py                      # Earliest Deadline First
│       ├── cfs.py                      # CFS-Sim (Completely Fair Scheduler)
│       └── autoral.py                  # APS — Adaptive Priority Scoring
│
├── casos/                              # Casos de teste em JSON
│   ├── caso_base.json                  # Caso rico com 5 processos para demonstração
│   ├── caso_spec.json                  # Caso base exato do enunciado do trabalho (3 processos)
│   ├── caso_deadline.json              # Caso com deadlines apertados (alguns estouram)
│   └── caso_ociosidade.json            # Caso com processos espaçados (valida CPU idle)
│
├── psb/                                # Disciplina: Programação de Software Básico
│   ├── index.html                      # Página da disciplina
│   └── img/                            # Imagens e diagramas
│
└── so/                                 # Disciplina: Sistemas Operacionais
    ├── index.html                      # Página da disciplina
    ├── img/                            # Imagens e diagramas
    └── simuladores/
        └── escalonamento/
            ├── index.html              # Interface do simulador
            ├── script.js               # Lógica de UI, Gantt e comunicação com a API
            └── style.css               # Estilos do simulador
```

---

## Como Rodar

O frontend é estático (HTML puro) e pode ser aberto diretamente no navegador. O backend Flask é necessário **apenas** para o simulador de escalonamento de SO.

### 1. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 2. Iniciar o backend

```bash
bash iniciar.sh
```

O script sobe a API Flask na porta `5001` e exibe os endereços de acesso no terminal.

### 3. Abrir no navegador

Abra os arquivos HTML diretamente, ou sirva a raiz com qualquer servidor estático:

```bash
# exemplo com Python
python3 -m http.server 8080
```

| Página | Caminho |
|---|---|
| Portal (Hub) | `index.html` |
| PSB | `psb/index.html` |
| Sistemas Operacionais | `so/index.html` |
| Simulador de Escalonamento | `so/simuladores/escalonamento/index.html` |

---

## Disciplinas Disponíveis

### PSB — Programação de Software Básico

Conteúdo teórico sobre o microcontrolador **ATmega328P** e linguagem **Assembly AVR**.

**Módulos de conteúdo:**

- **Introdução** — arquitetura RISC/Harvard, especificações do ATmega328P (32 KB de programa, 2 KB SRAM, 131 instruções, 32 registradores de propósito geral)
- **Registradores** — registradores de propósito geral (R0–R31), pares X/Y/Z para 16 bits, SREG (flags C, Z, N, V, S, H, T, I) e SP (Stack Pointer com SPH/SPL)
- **Pinagem (PDIP-28)** — VCC, AVcc, AREF, GND e suas funções
- **Instruções de Controle de Fluxo** — desvios incondicionais (JMP, RJMP, IJMP) e condicionais (CPI, CPC, CPSE, BRxx com variantes BREQ, BRNE, BRLO, BRSH, BRLT, BRGE, BRVS, BRVC)

**Referência rápida X86 → AVR:** tabela interativa com acordeão mostrando equivalências de MOV, ADD, SUB, INC, DEC, PUSH e POP em código AVR.

**Laboratório SimulIDE:** guia passo a passo para compilar código Assembly (via AVRA no Linux ou Microchip Studio no Windows), gerar o `.hex` e carregar no ATmega328P simulado. Inclui link para playlist no YouTube.

**Instruções de Base (exemplos práticos com circuitos):**

| # | Exemplo | Descrição |
|---|---|---|
| 01 | LED-VCC | Liga LED usando `LDI` + `OUT PORTD` com pino como VCC |
| 02 | LED-GND | Liga LED com pino como GND (lógica invertida) |
| 03 | Blink | LED piscando com rotina de atraso de ~1s (3 laços aninhados, 16 MHz) |
| 04 | Contador 4 bits | Conta de 0 a 15 em binário nos pinos de PORTD |
| 05 | Contador Decimal | Contador 0–9 com decodificação BCD em PORTB |

---

### SO — Sistemas Operacionais

Conteúdo teórico sobre os mecanismos que gerenciam hardware e fornecem serviços a programas de aplicação.

**Módulos de conteúdo:**

**Processos**
- O que é um processo (programa estático vs. instância em execução, analogia do cientista/receita de Tanenbaum)
- Componentes internos: código (text), dados (data/heap), pilha (stack) e PCB
- Multiprogramação e ilusão de paralelismo
- Estados: Running → Blocked → Ready → Running (diagrama de transições com imagem)
- Troca de contexto: o que é salvo (registradores, PC, SP, PSW), custo de cache/TLB
- Hierarquia de processos: `fork()`, `exec()`, `init`

**Threads**
- Diferença entre processo e thread (espaço de endereçamento isolado vs. compartilhado)
- Modelos: Many-to-One, One-to-One (Linux/Windows), Many-to-Many
- Sincronização: condições de corrida, Mutex, Semáforo, Monitor

**Algoritmos de Escalonamento** (com pseudocódigo Python para cada um):
- FIFO/FCFS — não preemptivo, efeito comboio
- SJF — não preemptivo, minimiza espera média, starvation de processos longos
- Prioridade — preemptivo, aging como solução para starvation
- Round Robin — quantum fixo, preemptivo, base dos sistemas de tempo compartilhado
- EDF — preemptivo, ótimo para tempo real, falha catastrófica sob sobrecarga

**Tabela comparativa:** FIFO, SJF, Prioridade, Round Robin e EDF lado a lado com preemptividade, espera média, starvation e uso típico.

---

## Simulador de Escalonamento (SO)

Ferramenta interativa que implementa e compara 7 algoritmos de escalonamento em uma CPU single-core simulada.

### Algoritmos

| Algoritmo | Tipo | Critério de seleção |
|---|---|---|
| FIFO / FCFS | Não preemptivo | Ordem de chegada |
| SJF | Não preemptivo | Menor burst restante |
| Round Robin | Preemptivo | Fila circular com quantum fixo |
| Prioridade | Preemptivo | Menor número = maior prioridade |
| EDF | Preemptivo | Deadline mais próximo |
| CFS-Sim | Preemptivo | Menor `vruntime` (tempo virtual) |
| APS (Autoral) | Preemptivo | Score composto: urgência (50%) + prioridade (30%) + aging (20%) |

### Entradas

**Por processo:** `id`, `chegada`, `execução`, `deadline` (opcional), `prioridade`, `páginas` (opcional, reservado)

**Globais:** `quantum` e `sobrecarga de contexto` (tempo de CPU ociosa adicionado em cada troca)

### Funcionamento

- A API Flask recebe os parâmetros via POST em `/simular` e devolve o gantt, métricas por processo e métricas globais
- Os casos de teste são servidos via GET em `/casos` e carregados automaticamente na sidebar
- O frontend desenha o Gantt em canvas HTML5 e renderiza a tabela de resultados

### CFS-Sim

Implementação simplificada do Completely Fair Scheduler do kernel Linux. Cada processo mantém um `vruntime` que cresce proporcionalmente à sua prioridade:

```
vruntime += Δt × 1.25^(prioridade - 1)
```

Processo com menor `vruntime` sempre recebe a CPU. Ao chegar, um novo processo recebe o `vruntime` mínimo da fila de prontos (evita starvation de processos existentes). Sem quantum fixo — a fatia de cada processo emerge do reequilíbrio entre `vruntime`s.

### APS — Adaptive Priority Scoring (algoritmo autoral)

Escalonador heurístico que recalcula um score multi-critério a cada evento:

- **Urgência (50%)** — slack entre deadline e burst restante; processos sem deadline usam heurística SJF
- **Prioridade (30%)** — normalizada entre os processos prontos
- **Aging (20%)** — tempo de espera acumulado, evita starvation

O processo com maior score é escalonado a seguir. Preempção ocorre quando um novo chegante altera o ranking.

### Saídas

**Gráfico de Gantt** (canvas, com scroll horizontal para timelines longas):

| Cor | Significado |
|---|---|
| Cor do processo | Execução normal |
| Cinza `#c5c6d2` | CPU ociosa (nenhum processo pronto) |
| Âmbar `#d97706` | Sobrecarga de contexto (troca de processo) |
| Vermelho `#dc2626` | Bloco executado após deadline estourado |
| Linha ouro `#bdab51` | Marcador de deadline absoluto (apenas EDF) |

**Modo passo-a-passo:** navega evento a evento pelo Gantt com botões Anterior / Próximo / Ver tudo. Eventos futuros aparecem esmaecidos como preview. Métricas e tabela só são reveladas ao concluir todos os passos.

**Métricas globais:** espera média, turnaround médio, throughput, % CPU ociosa, número de preempções e trocas de contexto.

**Tabela por processo:** `chegada`, `execução`, `deadline`, `prioridade`, `início(s)`, `término`, `espera`, `turnaround`, `deadline OK?`

**Modo comparação ("Comparar Todos"):** roda os 7 algoritmos simultaneamente, exibe abas com Gantt individual e tabela comparativa com ★ destacando o melhor valor em cada métrica.

### Casos de Teste

| Arquivo | Descrição |
|---|---|
| `caso_spec.json` | 3 processos exatos do enunciado do trabalho (referência de validação) |
| `caso_base.json` | 5 processos com chegadas e bursts variados, com deadlines |
| `caso_deadline.json` | 5 processos com deadlines apertados — alguns estouram dependendo do algoritmo |
| `caso_ociosidade.json` | 4 processos com grandes intervalos entre chegadas, força CPU idle |

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Frontend | HTML5, Tailwind CSS (via CDN), JavaScript vanilla |
| Canvas | HTML5 Canvas API (Gantt desenhado com 2D context) |
| Backend | Python 3, Flask, flask-cors |
| Fontes | Noto Serif (headlines), Work Sans (corpo), Material Symbols |

Sem framework JS, sem build step — o frontend abre direto no navegador.

---

## Time

Desenvolvido por alunos de Ciência da Computação da UFBA:

- [Daniel Santana](https://www.linkedin.com/in/danielbcsantana)
- [Davi Guimarães](https://www.linkedin.com/in/davi-guimarães-de-freitas-6b71652b9/)
- [Gabriel Barreto](https://www.linkedin.com/in/gabriel-barreto-batista)
- [Leone Castro](https://www.linkedin.com/in/leone-castro-98486038a/)
