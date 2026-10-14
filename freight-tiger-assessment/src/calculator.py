import pandas as pd
import numpy as np


def compute_weekly_baselines(shipments_csv_path: str) -> pd.DataFrame:
    shipments = pd.read_csv(shipments_csv_path)
    shipments['shipment_date'] = pd.to_datetime(shipments['shipment_date'])
    shipments['week_of'] = shipments['shipment_date'].dt.to_period('W-SUN').dt.start_time
    shipments['route'] = shipments['origin'] + '-' + shipments['destination']

    # Aggregating weekly total cost and quantity * distance
    weekly = shipments.groupby(['route', 'route_type', 'week_of']).agg(
        total_cost=('freight_cost_inr', 'sum'),
        total_qty_x_dist=('quantity_tonnes', lambda x: (x * shipments.loc[x.index, 'distance_km']).sum())
    ).reset_index()

    weekly['cost_per_tonne_km'] = weekly['total_cost'] / weekly['total_qty_x_dist']
    weekly = weekly.sort_values(['route', 'week_of']).reset_index(drop=True)

    # Trailing 8-week history baseline (strictly before current week)
    own_hist = []
    for route, group in weekly.groupby('route'):
        group = group.sort_values('week_of').reset_index(drop=True)
        for i in range(len(group)):
            prior = group.loc[max(0, i - 8):i - 1, 'cost_per_tonne_km']
            avg = prior.mean() if len(prior) > 0 else np.nan
            own_hist.append((group.loc[i, 'route'], group.loc[i, 'week_of'], avg))

    own_hist_df = pd.DataFrame(own_hist, columns=['route', 'week_of', 'own_history_avg'])
    weekly = weekly.merge(own_hist_df, on=['route', 'week_of'], how='left')

    # Peer baseline (same route_type, same week, excluding self)
    peer_hist = []
    for (rtype, week), group in weekly.groupby(['route_type', 'week_of']):
        for _, row in group.iterrows():
            others = group[group['route'] != row['route']]
            peer_avg = others['cost_per_tonne_km'].mean() if len(others) > 0 else np.nan
            peer_hist.append((row['route'], row['week_of'], peer_avg))

    peer_hist_df = pd.DataFrame(peer_hist, columns=['route', 'week_of', 'peer_avg'])
    weekly = weekly.merge(peer_hist_df, on=['route', 'week_of'], how='left')

    # Calculating percentage differences
    weekly['pct_vs_own'] = ((weekly['cost_per_tonne_km'] - weekly['own_history_avg']) / weekly['own_history_avg']) * 100
    weekly['pct_vs_peer'] = ((weekly['cost_per_tonne_km'] - weekly['peer_avg']) / weekly['peer_avg']) * 100

    return weekly