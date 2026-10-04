# Variational Quantum Classification for Phishing-Website Detection

## A reproducibility-focused study of feature compression, class-sensitive training, simulated hardware noise, and zero-noise extrapolation

> **Project status:** research prototype / portfolio study. The implementation runs on a quantum simulator; it is not a production phishing detector and has not yet been validated on quantum hardware.

## Abstract

This project investigates whether a standalone variational quantum classifier (VQC) can identify phishing websites from the UCI Phishing Websites dataset. The study deliberately isolates a quantum classifier rather than embedding quantum inference inside a larger classical system. This makes the performance cost, class-specific behavior, and noise sensitivity of the quantum model directly observable.

The original 30 predictors are reduced to six using random-forest feature importance so that one feature can be encoded per qubit. A six-qubit VQC then combines a fully entangling `ZZFeatureMap` with a `RealAmplitudes` variational ansatz and is optimized with simultaneous perturbation stochastic approximation (SPSA). A class-weighted objective gives phishing samples three times the weight of legitimate samples. The trained parameters are subsequently evaluated under depolarizing-noise models and with a simple linear zero-noise extrapolation (ZNE) procedure.

In the currently committed notebook, logistic regression reaches **92.19%** test accuracy using all 30 features and **91.29%** using the selected six features. The ideal-simulator VQC reaches **73.83%** accuracy, with **42.9% phishing recall**. Under the simulator configuration used here, moderate injected noise changes the decision distribution and sometimes increases aggregate accuracy; this should not be interpreted as a physical advantage. At a base depolarizing probability of 0.0175, linear ZNE improves accuracy from **73.86% to 75.85%**. These results do not demonstrate quantum advantage. Instead, they illustrate the present limitations of an end-to-end standalone VQC and motivate hybrid systems that reserve quantum computation for carefully selected cases.

## Research question

> How much predictive performance does a compact, standalone six-qubit VQC retain relative to classical baselines for phishing detection, and how robust is that classifier to simulated gate noise?

The project is motivated by *Q-CaR-Phish*, which uses calibrated classical models for most traffic and sends only uncertain cases to quantum experts. The present work asks a complementary question: what happens when a trainable quantum model is evaluated independently, without a classical routing and fusion layer?

## Contributions

- An end-to-end VQC implementation for a real cybersecurity classification task.
- A qubit-budget-aware feature-selection pipeline that compresses 30 predictors to six.
- A comparison against logistic-regression baselines using identical train/test data.
- Explicit class-sensitive evaluation through confusion matrices, precision, recall, and F1-score.
- Reproducible seeding of Python, NumPy, and Qiskit random-number generators.
- A depolarizing-noise sweep performed with fixed trained parameters.
- A basic three-point linear ZNE experiment.
- A transparent audit separating notebook-verified results from results recorded only in the accompanying research notes.

## Dataset

The project uses the [UCI Phishing Websites dataset](https://archive.ics.uci.edu/dataset/327/phishing), a tabular binary-classification dataset derived from sources including PhishTank, MillerSmiles, and Google search operators.

| Property | Value |
|---|---:|
| Instances | 11,055 |
| Predictive features | 30 |
| Identifier columns | 1 (`id`, excluded) |
| Target | `Result` |
| Phishing (`-1`) | 4,898 (44.31%) |
| Legitimate (`1`) | 6,157 (55.69%) |
| Missing values | 0 |
| Duplicate rows | 0 |

The notebook uses a 70/30 split with `random_state=42`, producing 7,738 training observations and 3,317 test observations. The split is not explicitly stratified.

### Feature reduction

Near-term quantum models are constrained by qubit count and circuit depth. The notebook therefore trains a random forest on the training partition and retains the six features with the largest impurity-based importance:

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | `SSLfinal_State` | 0.307502 |
| 2 | `URL_of_Anchor` | 0.264289 |
| 3 | `having_Sub_Domain` | 0.069721 |
| 4 | `web_traffic` | 0.066930 |
| 5 | `Links_in_tags` | 0.042175 |
| 6 | `Prefix_Suffix` | 0.037801 |

The classical accuracy decreases from 92.19% with 30 features to 91.29% with six: a reduction of only 0.90 percentage points while using 80% fewer input features. Feature selection is fitted on the training partition, which avoids direct test-set leakage.

As an alternative, the notebook projects the 30 original predictors onto six principal components and trains a separate logistic-regression model on that representation. PCA reaches **90.38%** accuracy, compared with **91.29%** for the six individually selected features. The 0.91-point advantage, together with the greater interpretability of the original features, motivates the use of random-forest selection in the quantum pipeline. This comparison evaluates dimensionality-reduction strategies only; it does not establish that PCA is intrinsically unsuitable for quantum models.

## Methodology

### 1. Classical reference models

Logistic regression provides three transparent reference points:

1. All 30 features after standardization.
2. The selected six discrete features without additional standardization.
3. Six principal components fitted on the training partition.

These baselines are not intended to establish the best attainable classical performance. They quantify the information lost during feature compression and provide a minimum comparison for the VQC.

### 2. Quantum data encoding

Each selected feature is scaled to the interval \([0,\pi]\), then encoded into a six-qubit `ZZFeatureMap` with full entanglement. Restricting the angular range reduces avoidable aliasing caused by the periodicity of quantum rotation gates.

For input vector \(x\), feature encoding prepares a state

\[
|\phi(x)\rangle = U_{\phi}(x)|0\rangle^{\otimes 6},
\]

where \(U_{\phi}(x)\) contains data-dependent single-qubit phases and pairwise ZZ interactions.

### 3. Variational model

The feature map is followed by a two-layer, fully entangling `RealAmplitudes` ansatz. The model output is the expectation value of a Pauli-Z observable on one qubit:

\[
f_{\theta}(x)=
\langle 0|U_{\phi}^{\dagger}(x)
U_{\theta}^{\dagger} Z U_{\theta}
U_{\phi}(x)|0\rangle,
\]

with \(f_{\theta}(x)\in[-1,1]\). Classification uses

\[
\hat y=\operatorname{sign}(f_{\theta}(x)),
\]

where \(-1\) denotes phishing and \(+1\) denotes legitimate.

### 4. Optimization and class-sensitive loss

SPSA is used for 300 optimization iterations with mini-batches of 64 samples. SPSA estimates a search direction with only two noisy objective evaluations per iteration, making it attractive when circuit evaluations dominate runtime.

The training objective is a weighted mean-squared error:

\[
\mathcal{L}(\theta)=
\frac{\sum_i w_{y_i}\left(y_i-f_{\theta}(x_i)\right)^2}
{\sum_i w_{y_i}},
\qquad
w_{-1}=3,\;w_{+1}=1.
\]

This weighting reflects the asymmetric operational cost of missing a phishing website. The notebook seeds Python's `random`, NumPy, and Qiskit's `algorithm_globals` with 42. The PyTorch `DataLoader` generator is not separately seeded, so exact reproducibility should still be verified in a clean rerun.

### 5. Noise model

The trained parameters are frozen before noise analysis. Qiskit Aer applies depolarizing errors to all supported single-qubit rotation gates and to `cx` gates. In the sweep currently stored in the notebook, the same probability \(p\) is used for both one- and two-qubit errors:

\[
\mathcal{E}(\rho)=(1-p)\rho+p\frac{I}{d}.
\]

This is a controlled sensitivity experiment, not a calibrated model of a specific processor. Real devices have heterogeneous gate errors, readout error, relaxation, drift, connectivity restrictions, and compiler-dependent circuit changes.

### 6. Zero-noise extrapolation

At base noise \(p=0.0175\), the circuit is evaluated at scale factors \(s\in\{1.0,1.2,1.3\}\). For every test point, a line is fitted to the measured expectation values:

\[
f(s)=a s+b.
\]

The intercept \(b=f(0)\) is used as the estimated zero-noise expectation value before applying the sign decision rule. This is a minimal proof of concept; it does not include uncertainty estimates, repeated-shot analysis, or higher-order extrapolation.

## Results

### Classical and ideal-simulator comparison

| Model | Inputs | Test accuracy | Status |
|---|---:|---:|---|
| Logistic regression | 30 features | **92.19%** | Notebook-verified |
| Logistic regression | Selected 6 features | **91.29%** | Notebook-verified |
| Logistic regression | 6 principal components | **90.38%** | Notebook-verified |
| VQC, ideal Aer estimator | 6 qubits | **73.83%** | Notebook-verified |

The standalone VQC trails the full-feature classical baseline by **18.36 percentage points** and the six-feature baseline by **17.46 points**. The current experiment therefore provides no evidence of quantum advantage.

### Class-specific VQC performance

| True class | Predicted phishing | Predicted legitimate | Recall |
|---|---:|---:|---:|
| Phishing (`-1`) | 613 | 815 | 42.93% |
| Legitimate (`1`) | 53 | 1,836 | 97.19% |

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Phishing (`-1`) | 0.92 | 0.43 | 0.59 | 1,428 |
| Legitimate (`1`) | 0.69 | 0.97 | 0.81 | 1,889 |
| Macro average | 0.81 | 0.70 | 0.70 | 3,317 |

Accuracy alone obscures the central security weakness: the model misses **815 of 1,428 phishing sites**, or approximately 57.1%. The high phishing precision means that negative predictions are usually correct, but the decision boundary produces too few of them. For a security screening system, this false-negative rate is unacceptable without a safer routing or fallback mechanism.

### Noise sweep

| Depolarizing probability \(p\) | Predicted phishing | Predicted legitimate | Accuracy |
|---:|---:|---:|---:|
| 0.0000 | 666 | 2,651 | 73.83% |
| 0.0050 | 677 | 2,640 | 74.10% |
| 0.0100 | 768 | 2,549 | 75.82% |
| 0.0125 | 811 | 2,506 | 75.85% |
| 0.0150 | 851 | 2,466 | 77.06% |
| 0.0175 | 737 | 2,580 | 73.86% |
| 0.0200 | 705 | 2,612 | 72.90% |

The non-monotonic accuracy curve is possible because noise shifts expectation values across a fixed zero threshold. On this imbalanced decision distribution, that shift may accidentally correct more samples than it harms. It is **not** evidence that physical noise improves learning. A credible robustness claim requires repeated finite-shot simulations, confidence intervals, class-wise metrics at every noise level, and ideally validation on hardware-informed noise models.

### Zero-noise extrapolation

| Evaluation at base \(p=0.0175\) | Accuracy |
|---|---:|
| Raw noisy inference | 73.86% |
| Linear ZNE | **75.85%** |
| Absolute change | **+1.99 percentage points** |

The extrapolated classifier recovers performance relative to the raw noisy run but remains below the 77.06% observed at \(p=0.015\). Because the scale factors correspond to effective probabilities of 0.0175, 0.0210, and 0.02275, two samples lie beyond the region where the sweep already shows deterioration. The result should therefore be treated as an exploratory mitigation demonstration, not a conclusive ZNE benchmark.

## Interpretation

The strongest conclusion is architectural rather than competitive: **this experiment supports selective quantum augmentation, not wholesale replacement of classical detection**.

1. Six carefully selected features preserve most of the logistic-regression baseline, so feature compression is not the main explanation for the VQC gap.
2. The VQC's aggregate accuracy hides a large and operationally important phishing false-negative rate.
3. Noise affects both accuracy and the predicted-class distribution; a single accuracy curve is insufficient to diagnose robustness.
4. Basic mitigation can change decisions near the classification boundary, but its benefit must be validated across seeds, shots, and noise regimes.
5. A deployment-oriented system should retain a strong calibrated classical path and invoke quantum models only when their incremental value has been demonstrated.

This interpretation is consistent with the design motivation of Q-CaR-Phish, which routes only uncertain cases to quantum experts rather than applying quantum inference to every input.

## Reproducibility

### Environment

The notebook was last executed with the following local package versions:

```text
Python environment: .venv
numpy              2.5.3
pandas             3.0.6
scikit-learn       1.9.1
qiskit             2.5.2
qiskit-aer         0.17.2
qiskit-algorithms  0.4.0
torch              2.11.0
```

The notebook currently emits Qiskit deprecation warnings for the `ZZFeatureMap` and `RealAmplitudes` classes. Future maintenance should migrate to the corresponding `zz_feature_map` and `real_amplitudes` functions before Qiskit 3.0.

### Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install numpy==2.5.3 pandas==3.0.6 scikit-learn==1.9.1 \
  qiskit==2.5.2 qiskit-aer==0.17.2 qiskit-algorithms==0.4.0 torch==2.11.0 jupyter
jupyter notebook project.ipynb
```

Quantum simulation and SPSA optimization are computationally expensive. A full clean rerun may take substantially longer than the classical baselines.

### Repository structure

```text
.
├── README.md       # Technical report and reproduction guide
├── data.csv        # UCI Phishing Websites data used by the notebook
└── project.ipynb   # Preprocessing, VQC training, noise sweep, and ZNE
```

## Reproducibility audit and known discrepancies

The project notes record additional experiments that are **not reproduced by the saved outputs in the current notebook**, including an 81% class-weighted VQC result, approximately 62% phishing recall, a larger noise sweep up to \(p=0.3\), and a claimed saturation distribution of 698/2,619. They also record classical accuracies of 92.04% and 90.41%, whereas the notebook shows 92.19% and 91.29%.

Those observations may come from earlier or later runs with different parameters, random states, or code. They are scientifically useful hypotheses, but they should not be presented as repository-reproducible findings until the corresponding configuration, outputs, and ideally serialized results are committed. Accordingly, every numerical claim in the Results section above is taken from the current `project.ipynb` outputs.

## Limitations

- **Single split and single final seed.** There is no repeated stratified cross-validation or multi-seed mean ± standard deviation.
- **No held-out validation set.** Architecture and weighting decisions described in the research log may have been influenced by test-set observations.
- **Incomplete deterministic control.** Python, NumPy, and Qiskit are seeded, but the PyTorch data-loader generator is not explicitly seeded.
- **No direct QSVM/QSVC comparison.** The VQC is a deliberate trainable-model extension, but it is not the same quantum expert used by Q-CaR-Phish.
- **Basic classical baselines only.** Logistic regression is informative but does not represent the strongest classical phishing detector.
- **Simulator-only evaluation.** The study does not include finite-shot uncertainty or execution on physical hardware.
- **Simplified noise.** Equal, homogeneous one- and two-qubit depolarizing probabilities are not hardware-calibrated.
- **Preliminary mitigation.** ZNE is tested at one base noise level with only three scale factors and no uncertainty analysis.
- **Deprecated circuit constructors.** The current Qiskit classes require migration before Qiskit 3.0.

## Recommended next experiments

1. Add assertions that every preprocessing pipeline is paired with its fitted estimator, and report PCA explained-variance ratios.
2. Lock a configuration, seed every stochastic component, and run at least 10 seeds; report mean, standard deviation, and confidence intervals.
3. Add a validation split or nested cross-validation for layer count, class weight, and decision-threshold selection.
4. Compare VQC, QSVC/QSVM, random forest, calibrated SVC, and gradient boosting on identical splits.
5. Report phishing false-negative rate, balanced accuracy, macro F1, AUROC, and calibration—not accuracy alone.
6. Repeat the noise sweep with finite shots and multiple simulator seeds; include class-wise metrics and uncertainty bands.
7. Evaluate ZNE at several base-noise levels whose scaled points remain inside a characterized non-saturated region.
8. Test a hardware-derived noise model and, where feasible, a small representative subset on Aalto's Q20 hardware.
9. Implement a conformal or uncertainty-based router to measure whether the VQC adds value specifically on hard cases.
10. Save experiment configurations and machine-readable result tables so every reported figure can be regenerated automatically.

## Ethical and operational considerations

Phishing detection is a safety-critical, adversarial application. False negatives expose users to malicious sites, while false positives can block legitimate services. This prototype must not be deployed as a sole decision-maker. A production system would require current and geographically diverse data, continuous monitoring for concept drift, calibrated confidence estimates, adversarial testing, explainability and appeal mechanisms, privacy review, and a conservative classical fallback.

## References

1. R. Mohammad and L. McCluskey, “Phishing Websites,” UCI Machine Learning Repository, 2012. [Dataset and DOI](https://doi.org/10.24432/C51W2X).
2. K. Bhuvaneswari and R. Dhanalakshmi, “Q-CaR-Phish: a hybrid quantum–classical framework for reliable and low-latency phishing website detection,” *Journal of Computer Virology and Hacking Techniques*, vol. 22, article 47, 2026. [DOI](https://doi.org/10.1007/s11416-026-00633-0) · [Source notebook](https://github.com/bbhuvi1-hue/Quantum/blob/main/Qcarphish.ipynb).
3. Qiskit documentation, [ZZ feature map](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.zz_feature_map) and [real-amplitudes ansatz](https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.real_amplitudes).

## Citation

If this repository is used in academic work, cite both this project and the original UCI dataset. Add an author name, repository URL, release year, and version tag here before publication.

## License

No software license is currently included in this repository. Add an explicit license before redistribution. The UCI dataset is distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) and must retain its attribution.
