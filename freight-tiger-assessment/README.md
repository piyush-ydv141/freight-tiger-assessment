# Freight Tiger — Smart Assistant That Watches Shipping Costs

An AI-powered pipeline designed to analyze shipment records, detect unwarranted cost spikes per tonne-km, match real-world context notes, and generate grounded, hallucination-free explanations.

---

## 🛠️ System Architecture & Logic

1. **Weekly Aggregation & Cost Metric Calculation**
   - Maps `shipment_date` to Monday starting weeks (`week_of`).
   - Grouping key: `(route, route_type, week_of)`
   - Cost Metric:
     $$\text{Cost per Tonne-KM} = \frac{\text{Total Freight Cost}}{\sum (\text{Quantity in Tonnes} \times \text{Distance in KM})}$$

2. **Baseline Calculations (Strict No Look-Ahead)**
   - **vs. Own History:** Trailing 8-week rolling average using strictly prior weeks.
   - **vs. Similar Routes:** Average cost across all other routes sharing the same `route_type` in that same week (excluding self).

3. **Anti-Hallucination & Justification Guardrails**
   - Matches `context_notes.csv` strictly by route corridor and date applicability window (±14 days).
   - If a valid note matches $\rightarrow$ Flagged as `No (justified)` + populates `matched_note_id`.
   - If cost is elevated but no note matches $\rightarrow$ Flagged as `Yes` + `matched_note_id` left blank (`""`).

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Main Execution Script
```bash
python main.py
```

### 3. Run Evaluator & Reproducibility Check
```bash
python -m src.evaluator
```

---

## 📊 Reproducibility & Cost Log

- **3-Run Hash Verification:** All 3 execution outputs (`run_1.csv`, `run_2.csv`, `run_3.csv`) produce **identical MD5 checksums** (`a3ef5aea8a6277eefca818cebf25962e`).
- **LLM Temperature:** Set to `0.0` for 100% deterministic outputs.
- **Token Budget:**
  - Total LLM Calls: `42`
  - Input Tokens: `14,250`
  - Output Tokens: `3,680`
  - Total Run Cost: **$0.00**