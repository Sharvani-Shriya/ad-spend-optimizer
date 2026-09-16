"""
optimizer.py

Contains the core "business logic" of this project: the budget reallocation
algorithm. Kept in its own file, separate from the API routing in main.py,
so it's easy to point to a single, self-contained function when explaining
it (e.g. in an interview).

ALGORITHM OVERVIEW
-------------------
1. Group all campaigns by channel (Search, Social, Display, Video).
2. For each channel, compute:
     - total spend  = sum of spend across that channel's campaigns
     - total revenue = sum of revenue across that channel's campaigns
     - ROAS (Return on Ad Spend) = total revenue / total spend
3. ROAS is used as the ranking metric (not raw clicks or conversions)
   because it directly measures money-in vs money-out per channel,
   which is the actual decision advertisers care about. Two channels
   can have similar conversion counts but very different ROAS if their
   spend or average order value differs — ROAS captures that, raw
   conversion count doesn't.
4. Identify the channel with the LOWEST ROAS (underperformer) and the
   channel with the HIGHEST ROAS (top performer).
5. Suggest moving REALLOCATION_PCT (15%) of the underperformer's total
   spend toward the top performer.
6. Edge cases handled explicitly:
     - A channel with zero spend is skipped when computing ROAS
       (avoids divide-by-zero) and treated as having undefined ROAS.
     - If fewer than 2 channels have valid (non-zero-spend) data,
       no suggestion can be made.
     - If the "lowest" and "highest" ROAS channel are the same
       (only one channel present), no reallocation is suggested.
"""

from collections import defaultdict

REALLOCATION_PCT = 0.15  # move 15% of the weak channel's spend


def compute_channel_roas(campaigns: list[dict]) -> dict[str, dict]:
    """Aggregates campaigns by channel and computes ROAS per channel.

    Returns a dict like:
        {
            "Search": {"total_spend": 113000, "total_revenue": 378000, "roas": 3.35},
            "Display": {"total_spend": 103000, "total_revenue": 64000, "roas": 0.62},
            ...
        }
    Channels with zero total spend are excluded (ROAS is undefined).
    """
    totals: dict[str, dict] = defaultdict(lambda: {"total_spend": 0.0, "total_revenue": 0.0})

    for c in campaigns:
        totals[c["channel"]]["total_spend"] += c["spend"]
        totals[c["channel"]]["total_revenue"] += c["revenue"]

    channel_roas = {}
    for channel, vals in totals.items():
        if vals["total_spend"] > 0:
            roas = vals["total_revenue"] / vals["total_spend"]
            channel_roas[channel] = {
                "total_spend": vals["total_spend"],
                "total_revenue": vals["total_revenue"],
                "roas": round(roas, 2),
            }
        # channels with zero spend are simply left out — ROAS undefined

    return channel_roas


def suggest_reallocation(campaigns: list[dict]) -> dict:
    """Suggests shifting budget from the lowest-ROAS channel to the
    highest-ROAS channel.

    Returns a dict with structured fields (from_channel, to_channel,
    amount, reason) and a human-readable sentence, or a message
    explaining why no suggestion could be made.
    """
    channel_roas = compute_channel_roas(campaigns)

    # Edge case: not enough channels with valid spend to compare
    if len(channel_roas) < 2:
        return {
            "suggestion_available": False,
            "message": "Not enough channels with spend data to compare. "
                       "Need at least 2 channels with non-zero spend.",
        }

    # Find lowest and highest ROAS channels
    lowest_channel = min(channel_roas, key=lambda ch: channel_roas[ch]["roas"])
    highest_channel = max(channel_roas, key=lambda ch: channel_roas[ch]["roas"])

    # Edge case: all channels tied on ROAS (or somehow the same channel wins both)
    if lowest_channel == highest_channel:
        return {
            "suggestion_available": False,
            "message": "All channels are performing similarly — no clear "
                       "reallocation opportunity right now.",
        }

    low_roas = channel_roas[lowest_channel]["roas"]
    high_roas = channel_roas[highest_channel]["roas"]
    low_spend = channel_roas[lowest_channel]["total_spend"]

    reallocation_amount = round(low_spend * REALLOCATION_PCT, 2)

    reason = (
        f"{lowest_channel} is returning {low_roas}x ROAS, well below "
        f"{highest_channel}'s {high_roas}x. Shifting spend toward the "
        f"stronger channel should improve overall return without "
        f"increasing total budget."
    )

    human_readable = (
        f"Shift ₹{reallocation_amount:,.0f} (15% of {lowest_channel}'s budget) "
        f"from {lowest_channel} (ROAS {low_roas}x) to {highest_channel} "
        f"(ROAS {high_roas}x)."
    )

    return {
        "suggestion_available": True,
        "from_channel": lowest_channel,
        "to_channel": highest_channel,
        "amount": reallocation_amount,
        "from_channel_roas": low_roas,
        "to_channel_roas": high_roas,
        "reason": reason,
        "human_readable": human_readable,
        "channel_breakdown": channel_roas,
    }
