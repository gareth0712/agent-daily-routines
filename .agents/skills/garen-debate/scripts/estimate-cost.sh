#!/usr/bin/env bash
# estimate-cost.sh — estimate token cost for a garen-debate run
#
# Usage:
#   bash estimate-cost.sh <n_defenders> <max_rounds>
#
# Arguments:
#   n_defenders   Number of defender agents (3-6 recommended)
#   max_rounds    Maximum number of debate rounds (1-7; hard cap is 7)
#
# Output:
#   Token estimate + USD cost range based on Sonnet pricing
#
# Example:
#   bash estimate-cost.sh 4 5

set -euo pipefail

N_DEF="${1:-3}"
MAX_R="${2:-5}"

# --- Assumptions per agent call ---
# Defenders in later rounds read all proposals before writing.
# Average input grows as proposals accumulate across rounds.
INPUT_TOK_PER_CALL=15000   # avg: defender reads all proposals (grows with rounds)
OUTPUT_TOK_PER_CALL=600    # 250-word cap + overhead

# PRICING NOTE: hardcoded to Sonnet 4.5 ($3 input / $15 output per million tokens, USD).
# UPDATE when switching models. Pricing changes per model version.
# Check current pricing: https://anthropic.com/pricing
INPUT_PRICE=3
OUTPUT_PRICE=15

# Total calls: each defender runs once per round, plus 1 judge call at the end
TOTAL_CALLS=$(( N_DEF * MAX_R + 1 ))
TOTAL_INPUT=$(( TOTAL_CALLS * INPUT_TOK_PER_CALL ))
TOTAL_OUTPUT=$(( TOTAL_CALLS * OUTPUT_TOK_PER_CALL ))

# Cost calculation (requires bc)
if command -v bc &>/dev/null; then
  COST_LOW=$(echo "scale=2; ($TOTAL_INPUT / 1000000 * $INPUT_PRICE) + ($TOTAL_OUTPUT / 1000000 * $OUTPUT_PRICE)" | bc)
  COST_HIGH=$(echo "scale=2; $COST_LOW * 1.5" | bc)  # 50% buffer for context growth across rounds
else
  # Fallback: integer arithmetic (less precise)
  COST_LOW_INT=$(( (TOTAL_INPUT * INPUT_PRICE + TOTAL_OUTPUT * OUTPUT_PRICE) / 1000000 ))
  COST_HIGH_INT=$(( COST_LOW_INT * 3 / 2 ))
  COST_LOW="~${COST_LOW_INT}"
  COST_HIGH="~${COST_HIGH_INT}"
fi

echo "========================================"
echo " garen-debate cost estimate"
echo "========================================"
echo " Defenders:             $N_DEF"
echo " Max rounds:            $MAX_R"
echo " Total agent calls:     $TOTAL_CALLS  (${N_DEF} defenders × ${MAX_R} rounds + 1 judge)"
echo " Est. input tokens:     $TOTAL_INPUT"
echo " Est. output tokens:    $TOTAL_OUTPUT"
echo " Cost range (USD):      \$${COST_LOW} – \$${COST_HIGH}"
echo "========================================"
echo ""
echo "Note: 50% buffer applied for context growth across rounds."
echo "Actual cost depends on proposal length and number of rounds actually run."
echo "(Debate stops early if ≥2 defenders signal <NO_NEW_POINTS> or <CONCEDE>.)"
