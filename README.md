# YC Bench: a Live Benchmark for Forecasting Startup Outperformance in Y Combinator Batches

[Paper](https://hal.science/hal-05573226)

[![](https://dcbadge.limes.pink/api/server/ekrySuRBf4)](https://discord.gg/ekrySuRBf4)

Forecasting which startups will dominate a YC batch — **months before Demo Day**.

---

## Overview

YC Bench turns every Y Combinator batch into a rapid-evaluation environment for startup success prediction. Instead of waiting 7–10 years for exits or large funding rounds, we use the **Pre-Demo Day Score** — a short-term proxy metric that combines public traction signals and Google web mentions.

This repository contains all data, collection scripts, scoring code, and analysis for the **YC W26 batch** (196 startups).

## Repository Structure

```
ycbench/
├── yc_w26_startups.csv              # Main list of YC W26 companies
├── yc_mentions.csv                  # Google mentions during the batch
├── yc_mentions_early.csv            # Pre-application Google mentions (baseline)
├── YC_W26_Google_Mentions.ipynb     # Colab notebook for data collection & visualizations
├── yc_google.py                     # Google mentions scraping utilities
├── requirements.txt
├── scripts/
│   ├── scrape/                      # Data collection scripts
│   ├── processing/                  # Data cleaning pipelines
│   └── scoring/                     # Pre-Demo Day Score computation
├── fix_pipeline.sh
├── paper/                           # LaTeX paper
└── figures/                         # Charts from the paper
```

## Key Features

- Scripts to collect fresh Google mentions data
- Colab notebook for easy data collection and visualization
- Pre-computed mentions (during batch + pre-application baseline)
- Traction data integration
- Baseline model (pre-YC application Google mentions)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/benstaf/ycbench.git
cd ycbench
pip install -r requirements.txt
```

### 2. Explore with Colab (Recommended)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/benstaf/ycbench/blob/main/YC_W26_Google_Mentions.ipynb)


## Results — YC W26 Batch

A simple baseline using **Google mentions before the YC application deadline** achieved:

- **Precision@20**: 30.0%
- **Recall@11**: 55%
- **Lift over random**: 2.75×
- **Forecasting horizon**: ~5 months

Full details are available in the paper.

## Paper

**Title**: YC Bench: A Live Benchmark for Forecasting Startup Outperformance in Y Combinator Batches  
**Author**: Mostapha Benhenda

[📄 View the full paper (PDF)](paper/ycbench.pdf)

## Citation

```bibtex
@misc{benhenda2026ycbench,
  title={YC Bench: A Live Benchmark for Forecasting Startup Outperformance in Y Combinator Batches},
  author={Mostapha Benhenda},
  year={2026},
  url={https://github.com/benstaf/ycbench}
}
```

## Roadmap

- Support for future batches (S26, W27, ...)
- Learn optimal signal weights from historical data
- Expand traction dataset
- Public leaderboard for community models

## Contributing

Contributions are welcome! Especially:
- Improved scraping methods
- New predictive signals
- Better scoring logic
- Support for upcoming batches

Feel free to open issues or submit pull requests.

---

**Built to make startup forecasting faster and more rigorous.**  
Star the repo if you're working on this problem! 🚀
