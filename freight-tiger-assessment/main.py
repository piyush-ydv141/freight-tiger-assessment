from src.calculator import compute_weekly_baselines
from src.rag_engine import generate_explanations

if __name__ == "__main__":
    print("Step 1: Calculating metrics and baselines...")
    weekly_df = compute_weekly_baselines('data/shipment_records.csv')
    
    print("Step 2: Matching notes and generating output...")
    final_df = generate_explanations(weekly_df, 'data/context_notes.csv')
    
    final_df.to_csv('output/final_submission.csv', index=False)
    print("✅ Completed! Saved output to output/final_submission.csv")