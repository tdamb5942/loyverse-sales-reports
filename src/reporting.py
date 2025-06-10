import pandas as pd
from src.data_fetching import fetch_all_receipts, get_items_with_categories
import matplotlib.pyplot as plt
import seaborn as sns


def plot_total_sales(
    start_date: str,
    end_date: str,
    granularity: str = "day",
    breakdown_by_category: bool = False,
) -> None:
    """
    Visualises total sales between start_date and end_date.

    Parameters:
    - start_date (str): ISO date string, e.g., "2025-05-01"
    - end_date (str): ISO date string, e.g., "2025-06-01"
    - granularity (str): One of "day", "week", "month"
    - breakdown_by_category (bool): If True, show breakdown by item category
    """

    receipts_df = fetch_all_receipts(start_date, end_date)
    items_df = get_items_with_categories()

    # Explode line items
    receipts_df = receipts_df.explode("line_items").dropna(subset=["line_items"])
    line_items = [
        item
        for sublist in receipts_df["line_items"].dropna()
        if isinstance(sublist, list)
        for item in sublist
    ]
    line_items_df = pd.json_normalize(line_items)
    line_items_df["receipt_date"] = pd.to_datetime(receipts_df["receipt_date"].values)

    # Merge with item and category info
    line_items_df = line_items_df.merge(
        items_df[["id", "item_name", "category_name"]],
        left_on="item_id",
        right_on="id",
        how="left",
    )

    # Convert to desired granularity
    if granularity not in {"day", "week", "month"}:
        raise ValueError("granularity must be one of: day, week, month")
    freq_map = {"day": "D", "week": "W", "month": "M"}
    line_items_df["period"] = (
        line_items_df["receipt_date"]
        .dt.to_period(freq_map[granularity])
        .dt.to_timestamp()
    )

    # Convert total_money from str to float
    line_items_df["total_money"] = pd.to_numeric(
        line_items_df["total_money"], errors="coerce"
    )

    # Group and aggregate
    group_cols = ["period"]
    if breakdown_by_category:
        group_cols.append("category_name")
    sales_summary = line_items_df.groupby(group_cols)["total_money"].sum().reset_index()

    # Pivot if breaking down by category
    if breakdown_by_category:
        sales_summary = sales_summary.pivot(
            index="period", columns="category_name", values="total_money"
        ).fillna(0)

    plt.figure(figsize=(12, 6))
    if breakdown_by_category:
        sales_summary = (
            sales_summary.reset_index()
            if isinstance(sales_summary.index, pd.PeriodIndex)
            else sales_summary
        )
        sales_summary = sales_summary.melt(
            id_vars="period", var_name="category_name", value_name="total_money"
        )
        sns.barplot(
            data=sales_summary,
            x="period",
            y="total_money",
            hue="category_name",
            estimator=sum,
        )
    else:
        sns.lineplot(data=sales_summary, x="period", y="total_money", marker="o")

    plt.title("Total Sales")
    plt.xlabel(granularity.capitalize())
    plt.ylabel("Sales")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
