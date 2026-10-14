import pandas as pd


def generate_explanations(weekly_df: pd.DataFrame, notes_csv_path: str) -> pd.DataFrame:
    notes = pd.read_csv(notes_csv_path)
    notes['date'] = pd.to_datetime(notes['date'])

    results = []
    for _, row in weekly_df.iterrows():
        route = row['route']
        week_dt = row['week_of']
        cost = round(row['cost_per_tonne_km'], 2)

        pct_own = row['pct_vs_own']
        pct_peer = row['pct_vs_peer']

        if pd.notnull(pct_own) and pct_own >= 0:
            vs_own_str = f"+{pct_own:.1f}% vs this route's past average"
        elif pd.notnull(pct_own):
            vs_own_str = f"{pct_own:.1f}% vs this route's past average"
        else:
            vs_own_str = "N/A"

        if pd.notnull(pct_peer) and pct_peer >= 0:
            vs_peer_str = f"+{pct_peer:.1f}% vs similar-length routes this week"
        elif pd.notnull(pct_peer):
            vs_peer_str = f"{pct_peer:.1f}% vs similar-length routes this week"
        else:
            vs_peer_str = "N/A"

        is_rising = (pd.notnull(pct_own) and pct_own > 10.0) or (pd.notnull(pct_peer) and pct_peer > 10.0)

        matching = notes[
            (notes['applies_to'].str.contains(route, case=False, na=False)) &
            (abs((notes['date'] - week_dt).dt.days) <= 14)
        ]

        if is_rising:
            if not matching.empty:
                note_row = matching.iloc[0]
                flagged = "No (justified)"
                matched_note_id = note_row['note_id']
                reason = f"Matches note {note_row['note_id']} dated {note_row['date'].strftime('%Y-%m-%d')}: {note_row['note']} The cost rise has a clear explanation."
            else:
                flagged = "Yes"
                matched_note_id = ""
                reason = "No matching note found for this route or date range. Cost rise looks unexplained and worth a human review."
        else:
            flagged = "No"
            matched_note_id = ""
            reason = "Cost is within normal baseline expectations."

        results.append({
            'route': route,
            'week_of': week_dt.strftime('%Y-%m-%d'),
            'cost_per_tonne_km': cost,
            'vs_own_history': vs_own_str,
            'vs_similar_routes': vs_peer_str,
            'flagged': flagged,
            'matched_note_id': matched_note_id,
            'reason': reason
        })

    return pd.DataFrame(results)