
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
raw = ROOT / 'data' / 'raw'
out = ROOT / 'data' / 'processed'
out.mkdir(parents=True, exist_ok=True)

def main():
    files = sorted(raw.glob('shipment_A-*.csv'))
    frames = []
    for file in files:
        df = pd.read_csv(file)
        df['source_file'] = file.name
        df['data_type'] = 'simulated_prototype'
        frames.append(df)
    shipments = pd.concat(frames, ignore_index=True)
    shipments['timestamp'] = pd.to_datetime(shipments['timestamp'])
    shipments['temp_alert'] = shipments['temp_alert'].astype(bool)
    shipments['alert'] = shipments['temp_alert'].astype(int)
    shipments['temperature_difference_c'] = shipments['temperature_c'] - shipments['temp_threshold_c']
    shipments['journey_progress_pct'] = shipments['distance_km'] / shipments.groupby('shipment_id')['distance_km'].transform('max') * 100
    shipments['journey_stage'] = pd.cut(shipments['journey_progress_pct'], [-0.1,25,50,75,100.1], labels=['0-25%','25-50%','50-75%','75-100%'])
    shipments['hour_bucket'] = pd.cut(shipments['hour'], [-0.01,3,6,9,12.1], labels=['0-3h','3-6h','6-9h','9-12h'])
    shipments.to_csv(out / 'clean_supply_chain_prototype.csv', index=False)
    summary = []
    for sid, g in shipments.groupby('shipment_id'):
        alerts = g[g['temp_alert']]
        summary.append({
            'shipment_id': sid,
            'readings': len(g),
            'threshold_c': g['temp_threshold_c'].mode().iloc[0],
            'total_distance_km': g['distance_km'].max(),
            'total_co2_kg': g['cumulative_co2_kg'].max(),
            'mean_temperature_c': g['temperature_c'].mean(),
            'max_temperature_c': g['temperature_c'].max(),
            'temperature_variability_sd': g['temperature_c'].std(),
            'alert_readings': int(g['temp_alert'].sum()),
            'first_alert_hour': alerts['hour'].min() if len(alerts) else np.nan,
            'alert_duration_hours': len(alerts) * 5 / 60,
            'share_readings_in_alert_pct': g['temp_alert'].mean()*100
        })
    pd.DataFrame(summary).to_csv(out / 'shipment_summary_prototype.csv', index=False)
    pd.read_json(raw / 'batch_results.json').to_csv(out / 'batch_results.csv', index=False)

if __name__ == '__main__':
    main()
