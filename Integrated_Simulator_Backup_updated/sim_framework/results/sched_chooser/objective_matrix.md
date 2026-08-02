# Scheduler selection: objective x workload mix

Array 8x8, dataflow OS. 6 objectives x 6 mixes, scored analytically in 8.0 ms with no RTL simulation and no synthesis run.

Timing columns are model rank scores; LUT/FF/power/Fmax are measured (Vivado OOC); throughput and turnaround_us are derived from both. Schedulers lacking a measured value are excluded from hardware objectives, never substituted.

## Workload mixes

| mix | name | tasks | per-task model cycles |
|---|---|---|---|
| mix1 | Workload mix 1 | 3 | 4,484, 42,708, 11,404 |
| mix2 | Workload mix 2 | 4 | 10,569, 1,876, 65,172, 6,420 |
| mix3 | Workload mix 3 | 3 | 64,532, 3,668, 131,412 |
| mix4 | Workload mix 4 | 4 | 57,108, 1,620, 1,876, 5,460 |
| mix5 | Workload mix 5 | 2 | 1,620, 131,412 |
| mix6 | Workload mix 6 | 6 | 1,620, 1,876, 4,484, 10,569, 64,532, 131,412 |

## Winner per (objective, mix)

| objective | mix1 | mix2 | mix3 | mix4 | mix5 | mix6 |
|---|---|---|---|---|---|---|
| turnaround | HRRN\* | SJF\* | SJF\* | SJF\* | AIMT\* | AIMT\* |
| turnaround_us | MLQ | MLQ | MLQ | LIFO | MLQ | MLQ |
| wait | HRRN\* | SJF\* | SJF\* | SJF\* | AIMT\* | AIMT\* |
| throughput | MLQ | MLQ | MLQ | MLQ | MLQ | MLQ |
| area | MLQ | MLQ | MLQ | MLQ | MLQ | MLQ |
| power | MLQ | MLQ | MLQ | MLQ | MLQ | MLQ |

\* tied at the top; name shown is the deterministic tie-break winner.

## Objective -> recommended scheduler

A scheduler is recommended when it is in the tied-at-best set for **every** mix swept. Where several policies are co-optimal the objective cannot separate them, so the pick is the one with the lowest measured area.

The candidate-set column holds the co-optimal policies when stability is *optimal on all N*; when stability is *workload-dependent* no policy is optimal everywhere and the column holds those optimal on the most mixes.

| objective | recommended | optimal on | stability | candidate set | what it ranks on |
|---|---|---|---|---|---|
| turnaround | **SRTF** | 6/6 | optimal on all 6 | SRTF, SJF | mean cycles from submission to completion (model) |
| turnaround_us | **MLQ** | 5/6 | workload-dependent | MLQ | mean wall-clock latency = model cycles / measured Fmax |
| wait | **SRTF** | 6/6 | optimal on all 6 | SRTF, SJF | mean cycles queued before first dispatch (model) |
| throughput | **MLQ** | 6/6 | optimal on all 6 | MLQ | tasks/s; reduces to measured Fmax (makespan is invariant) |
| area | **MLQ** | 6/6 | optimal on all 6 | MLQ | measured LUT count |
| power | **MLQ** | 6/6 | optimal on all 6 | MLQ | measured Vivado vectorless dynamic power |
