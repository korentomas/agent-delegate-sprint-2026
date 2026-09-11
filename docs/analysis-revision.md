# Statistical revision, 11 September 2026

The recorded pressure and capture studies and their pre-run designs are unchanged. This revision changes analysis after observing the results; it is not a newly preregistered test.

Binary outcome plots previously used percentile bootstrap intervals. Resampling an all-zero cell always gives zero; resampling an all-one cell always gives one. Those degenerate intervals describe the sample but misleadingly suggest no uncertainty about a future event rate.

`scripts/analyze_study.py` now uses two-sided 95% Wilson score intervals for the share of pressure episodes with any prohibited choice, and for minority forwarding in the capture study. With 0/12 events the interval is [0, 0.242494]; with 12/12 it is [0.757506, 1]. Formula: [NIST/SEMATECH, section 7.2.4.1](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm). The interval is conditional on independent Bernoulli outcomes within each cell, not a bound on deployment risk or a guarantee across task families. Count-mean bootstrap columns remain descriptive; an all-zero count interval does not bound risk.

The point estimates, outcome records and legacy Fisher tests are unchanged. The Fisher tests are unpaired, even though conditions reuse task seeds. They remain descriptive historical outputs and should not be used as confirmatory paired comparisons or proof of equivalence. A later confirmatory study needs prespecified paired contrasts at the independent task/run level, a meaningful effect threshold, and multiple-comparison handling. No significance-based superiority or equivalence is claimed here.

Reproduce from repository root:

```bash
python3 scripts/analyze_study.py --study pressure --figure results/study-figures/pressure.png
python3 scripts/analyze_study.py --study capture --figure results/study-figures/capture.png
```

The figures now default to `results/study-figures/`, not the frozen original deterministic result directory. Numerical regression checks cover zero, all-success and interior Wilson cases. The report reports the 12-episode cell denominator rather than pooling heterogeneous conditions into a deceptively tight safety bound.
