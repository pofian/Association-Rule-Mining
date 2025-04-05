# Association Rule Mining

This project performs association rule mining on a dataset of donors, filtering and ranking rules that associate donor properties with age (e.g., *Propriety A ⇒ Donor is old*). It supports evaluation and intelligent compression of these rules based on statistical metrics and logical redundancy.

---

## 📊 Project Overview

Given:
- A dataset of **donors and their properties** (features).
- A set of **rules** (e.g., `property_A => old`).

This tool:
1. **Evaluates rules** on the dataset to determine:
   - True Positives
   - False Positives
   - True Negatives
   - False Negatives

2. **Calculates**:
   - **Phi Coefficient** (used as a correlation metric) - https://en.wikipedia.org/wiki/Phi_coefficient
   - **Precision**
   - **Sensitivity**

3. **Filters rules** based on custom thresholds:
   - Phi threshold - 0.2
   - Precision threshold - 0.5
   - Sensitivity threshold - 0.35
   - Precision threshold > Sensitivity threshold because it's more important to **avoid false positives** (young donors matching the rule) than to capture all old donors.

4. **Sorts rules** by descending **Phi Coefficient**, as it measures:
   - Two-way correlation between the rule and the target class.
   - Unlike precision and sensitivity, it considers **true negatives** as well.

5. **Eliminates redundant rules**:
   - If a rule’s **true positives** are a strict **subset** of another rule’s true positives, the less informative rule is discarded in favor of the stronger one.

---

## 📌 Why These Choices?

- **Phi Coefficient** used for ranking:
  - Captures bidirectional correlation and includes all 4 components of the confusion matrix.
- **Precision prioritized over Sensitivity**:
  - False positives (incorrectly labeling a young donor as old) are more damaging than missing some older donors.
- **Subset elimination**:
  - Prevents redundant rules and favors more generalizable ones.

## ⚙️ Usage

### 1. Compress an existing rule list
```bash
python3 compress.py
```

This will:
- Load the donor dataset and rule list.
- Evaluate and filter rules using precision, sensitivity, and phi coefficient.
- Sort and eliminate redundant rules.

### 2. Generate and compress synthetic rules (optional)
```bash
python3 compress.py synthetic
```

This will:
- **Generate** all possible rules with **up to 3 conditions**.
- Apply the same compression and filtering as above.

## 📦 Output

- **Filtered and ranked rules** are saved in:
  - `compressed_rules.txt`
  - `compressed_rules_detailed.txt`

- **Discarded rules** (those not passing thresholds or removed as redundant) are logged in the `logs/` directory for inspection.
