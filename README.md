# IoT-Enabled Supply Chain Monitoring

**Working title:** IoT-Enabled Cold-Chain Monitoring: Evaluating Environmental Risk, Detection Speed, and Supply-Chain Transparency

This repository contains a complete starter package for the Data Visualization final project: cleaned datasets, an analysis notebook, a Streamlit dashboard, and a presentation deck.

## Important dataset note

The uploaded shipment data is a **simulated prototype**, because the original `dashboard.py` generates records with `shipment.simulate()` and random seeds. For final submission, clearly label this prototype and add a credible real-world dataset. A recommended real-world logistics dataset is UCI's **Daily Demand Forecasting Orders** dataset, described by UCI as 60 days of real data from a large Brazilian logistics company.

## Dataset

This project uses a simulated IoT cold-chain shipment dataset generated from a prototype monitoring system. The simulated data reproduces realistic shipment conditions, including GPS location, temperature readings, alerts, journey progress, and carbon emissions, allowing the visualisation and analytics pipeline to be demonstrated consistently.


## Project structure

```text
IoT_Supply_Chain_Project/
├── data/
│   ├── raw/
│   └── processed/
├── dashboard/
│   └── app.py
├── notebooks/
│   └── IoT_Supply_Chain_Analysis.ipynb
├── presentation/
│   └── IoT_Supply_Chain_Presentation.pptx
├── src/
│   └── prepare_data.py
├── requirements.txt
└── README.md
```

## Technologies Used

- Python 3
- Pandas
- NumPy
- Plotly
- Streamlit
- Jupyter Notebook
- Git
- GitHub

## Run locally

```bash
pip install -r requirements.txt
python src/prepare_data.py
streamlit run dashboard/app.py
```

## Included processed data

- `clean_supply_chain_prototype.csv`: combined shipment-level IoT readings.
- `shipment_summary_prototype.csv`: shipment-level summary metrics.
- `batch_results.csv`: simulated real-time vs checkpoint detection experiment.

## Analytical questions in the notebook

1. How does temperature change across the journey by shipment?
2. At what journey stage do temperature breaches concentrate?
3. Which shipment has the longest unsafe exposure?
4. Which shipment has the highest maximum temperature and volatility?
5. Does temperature variability increase as transit progresses?
6. How does cumulative CO2 increase with journey distance?
7. Which readings produce unusually high interval emissions?
8. How much earlier does real-time monitoring detect risk than checkpoint monitoring?
9. How consistent is the detection-time advantage across runs?
10. Which shipments have the highest combined operational risk?

## Dashboard tabs

- Executive Overview
- Journey & Sensors
- Alerts & Risk
- Detection Speed
- Data Provenance

## Submission checklist

- Replace/supplement simulated prototype with a real-world dataset.
- Keep 10+ Plotly-only explanatory visuals.
- Deploy the Streamlit app from a public GitHub repository.
- Export presentation to PDF with dashboard screenshots and links.

## Author

Name: Abubakar Umar Dangi

Course: Data Visualisation

Project: IoT-Enabled Supply Chain Monitoring