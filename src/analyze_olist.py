"""
End-to-end analysis pipeline joining two Kaggle Olist datasets:
  1. olistbr/brazilian-ecommerce (orders, items, payments, reviews, customers, products, sellers)
  2. olistbr/marketing-funnel-olist (marketing qualified leads & closed seller deals)

Usage:
  uv run --with "kagglehub[pandas-datasets]" python src/analyze_olist.py
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import kagglehub
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_OUT = ROOT / "data" / "summary.json"


def load_tables() -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    ecomm_dir = Path(kagglehub.dataset_download("olistbr/brazilian-ecommerce"))
    funnel_dir = Path(kagglehub.dataset_download("olistbr/marketing-funnel-olist"))

    ecomm = {
        "orders": pd.read_csv(
            ecomm_dir / "olist_orders_dataset.csv",
            parse_dates=[
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ],
        ),
        "items": pd.read_csv(ecomm_dir / "olist_order_items_dataset.csv"),
        "payments": pd.read_csv(ecomm_dir / "olist_order_payments_dataset.csv"),
        "reviews": pd.read_csv(ecomm_dir / "olist_order_reviews_dataset.csv"),
        "customers": pd.read_csv(ecomm_dir / "olist_customers_dataset.csv"),
        "products": pd.read_csv(ecomm_dir / "olist_products_dataset.csv"),
        "sellers": pd.read_csv(ecomm_dir / "olist_sellers_dataset.csv"),
        "categories": pd.read_csv(ecomm_dir / "product_category_name_translation.csv"),
    }
    funnel = {
        "mql": pd.read_csv(
            funnel_dir / "olist_marketing_qualified_leads_dataset.csv",
            parse_dates=["first_contact_date"],
        ),
        "closed": pd.read_csv(
            funnel_dir / "olist_closed_deals_dataset.csv",
            parse_dates=["won_date"],
        ),
    }
    return ecomm, funnel


def build_summary(ecomm: dict[str, pd.DataFrame], funnel: dict[str, pd.DataFrame]) -> dict:
    orders = ecomm["orders"]
    items = ecomm["items"]
    payments = ecomm["payments"]
    reviews = ecomm["reviews"]
    customers = ecomm["customers"]
    products = ecomm["products"]
    sellers = ecomm["sellers"]
    categories = ecomm["categories"]
    mql = funnel["mql"]
    closed = funnel["closed"]

    # 1. Core Marketplace & Repeat Buyers
    cust_orders = orders.merge(customers[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id")
    buyer_counts = cust_orders.groupby("customer_unique_id")["order_id"].nunique()
    unique_buyers = int(len(buyer_counts))
    repeat_buyers = int((buyer_counts >= 2).sum())

    total_gmv = float(items["price"].sum())
    total_freight = float(items["freight_value"].sum())
    total_payments = float(payments["payment_value"].sum())

    # 2. Delivery Delay vs Review Score
    order_rev = reviews.groupby("order_id", as_index=False)["review_score"].mean()
    deliv = orders[orders["order_delivered_customer_date"].notna()].copy()
    deliv["late_days"] = (
        deliv["order_delivered_customer_date"] - deliv["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400.0
    deliv["actual_days"] = (
        deliv["order_delivered_customer_date"] - deliv["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400.0
    deliv["is_late"] = deliv["late_days"] > 0
    deliv_rev = deliv.merge(order_rev, on="order_id", how="inner")

    delivery_impact = []
    for is_late, grp in deliv_rev.groupby("is_late"):
        delivery_impact.append(
            {
                "bucket": "late" if is_late else "on_time",
                "orders": int(len(grp)),
                "share_pct": round(len(grp) / len(deliv_rev) * 100, 2),
                "avg_review": round(float(grp["review_score"].mean()), 2),
                "pct_1_star": round(float((grp["review_score"] <= 1.5).mean() * 100), 2),
                "pct_5_star": round(float((grp["review_score"] >= 4.5).mean() * 100), 2),
                "median_delivery_days": round(float(grp["actual_days"].median()), 1),
            }
        )

    # 3. Freight Burden & Delivery Time by Customer State
    order_late_map = deliv[["order_id", "is_late", "actual_days"]]
    oi_state = (
        items.merge(orders[["order_id", "customer_id"]], on="order_id")
        .merge(customers[["customer_id", "customer_state"]], on="customer_id")
        .merge(order_late_map, on="order_id", how="left")
    )
    state_grp = (
        oi_state.groupby("customer_state", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            items=("order_item_id", "count"),
            gmv=("price", "sum"),
            freight=("freight_value", "sum"),
            avg_delivery_days=("actual_days", "mean"),
            late_pct=("is_late", lambda s: float(s.dropna().mean() * 100) if s.notna().any() else 0.0),
        )
    )
    state_grp["freight_share_pct"] = state_grp["freight"] / (state_grp["gmv"] + state_grp["freight"]) * 100
    state_rows = []
    for _, r in state_grp.sort_values("orders", ascending=False).iterrows():
        state_rows.append(
            {
                "state": r["customer_state"],
                "orders": int(r["orders"]),
                "gmv": round(float(r["gmv"]), 2),
                "freight": round(float(r["freight"]), 2),
                "freight_share_pct": round(float(r["freight_share_pct"]), 2),
                "avg_delivery_days": round(float(r["avg_delivery_days"]), 1),
                "late_pct": round(float(r["late_pct"]), 2),
            }
        )

    # 4. Payment Mix & Installments
    pay_clean = payments[payments["payment_type"] != "not_defined"]
    pay_rows = []
    for ptype, grp in pay_clean.groupby("payment_type"):
        pay_rows.append(
            {
                "payment_type": ptype,
                "transactions": int(len(grp)),
                "orders": int(grp["order_id"].nunique()),
                "total_brl": round(float(grp["payment_value"].sum()), 2),
                "share_pct": round(float(grp["payment_value"].sum() / total_payments * 100), 2),
                "avg_value": round(float(grp["payment_value"].mean()), 2),
                "avg_installments": round(float(grp["payment_installments"].mean()), 2),
            }
        )
    pay_rows.sort(key=lambda x: x["total_brl"], reverse=True)

    # 5. Marketing Funnel -> Live Seller Revenue Bridge
    seller_perf = items.groupby("seller_id", as_index=False).agg(
        orders=("order_id", "nunique"),
        items=("order_item_id", "count"),
        gmv=("price", "sum"),
        freight=("freight_value", "sum"),
        first_ship_limit=("shipping_limit_date", "min"),
    )
    mql_clean = mql.copy()
    mql_clean["origin_clean"] = mql_clean["origin"].fillna("missing")
    closed_full = closed.merge(mql_clean[["mql_id", "origin_clean", "first_contact_date"]], on="mql_id", how="left").merge(
        seller_perf, on="seller_id", how="left"
    )
    closed_full["is_active"] = closed_full["gmv"].notna()
    closed_full["gmv"] = closed_full["gmv"].fillna(0.0)
    closed_full["orders"] = closed_full["orders"].fillna(0).astype(int)
    closed_full["won_to_first_days"] = (
        pd.to_datetime(closed_full["first_ship_limit"]) - closed_full["won_date"]
    ).dt.total_seconds() / 86400.0

    mql_by_origin = mql_clean.groupby("origin_clean")["mql_id"].count().to_dict()
    channel_rows = []
    for origin, grp in closed_full.groupby("origin_clean"):
        leads = int(mql_by_origin.get(origin, len(grp)))
        won = int(len(grp))
        active = int(grp["is_active"].sum())
        channel_rows.append(
            {
                "origin": origin,
                "mql_leads": leads,
                "closed_deals": won,
                "active_sellers": active,
                "lead_to_won_pct": round(won / leads * 100, 2) if leads else 0.0,
                "won_to_active_pct": round(active / won * 100, 2) if won else 0.0,
                "lead_to_active_pct": round(active / leads * 100, 2) if leads else 0.0,
                "gmv": round(float(grp["gmv"].sum()), 2),
                "orders": int(grp["orders"].sum()),
            }
        )
    channel_rows.sort(key=lambda x: x["gmv"], reverse=True)

    lead_type_rows = []
    closed_full["lead_type_clean"] = closed_full["lead_type"].fillna("missing")
    for lt, grp in closed_full.groupby("lead_type_clean"):
        won = int(len(grp))
        active = int(grp["is_active"].sum())
        lead_type_rows.append(
            {
                "lead_type": lt,
                "closed_deals": won,
                "active_sellers": active,
                "activation_pct": round(active / won * 100, 2) if won else 0.0,
                "gmv": round(float(grp["gmv"].sum()), 2),
                "orders": int(grp["orders"].sum()),
            }
        )
    lead_type_rows.sort(key=lambda x: x["gmv"], reverse=True)

    # 6. Top Categories & Seller Concentration
    prod_en = products.merge(categories, on="product_category_name", how="left")
    prod_en["category"] = prod_en["product_category_name_english"].fillna(
        prod_en["product_category_name"].fillna("uncategorized")
    )
    oi_cat = (
        items.merge(prod_en[["product_id", "category"]], on="product_id", how="left")
        .merge(order_rev, on="order_id", how="left")
        .merge(deliv[["order_id", "is_late"]], on="order_id", how="left")
    )
    cat_rows = []
    for cat_name, grp in oi_cat.groupby("category"):
        cat_rows.append(
            {
                "category": cat_name,
                "orders": int(grp["order_id"].nunique()),
                "items": int(len(grp)),
                "gmv": round(float(grp["price"].sum()), 2),
                "freight": round(float(grp["freight_value"].sum()), 2),
                "freight_pct": round(float(grp["freight_value"].sum() / (grp["price"].sum() + grp["freight_value"].sum()) * 100), 2),
                "avg_review": round(float(grp["review_score"].mean()), 2) if grp["review_score"].notna().any() else None,
                "late_pct": round(float(grp["is_late"].dropna().mean() * 100), 2) if grp["is_late"].notna().any() else 0.0,
            }
        )
    cat_rows.sort(key=lambda x: x["gmv"], reverse=True)

    s_gmv = seller_perf["gmv"].sort_values(ascending=False).reset_index(drop=True)
    top_10_n = max(1, int(round(len(s_gmv) * 0.10)))
    top_10_share = float(s_gmv.iloc[:top_10_n].sum() / s_gmv.sum() * 100)

    # 7. Monthly Order Timeline
    orders_valid = orders[orders["order_status"] != "canceled"].copy()
    orders_valid["ym"] = orders_valid["order_purchase_timestamp"].dt.to_period("M").astype(str)
    oi_month = items.merge(orders_valid[["order_id", "ym"]], on="order_id", how="inner")
    m_orders = orders_valid.groupby("ym")["order_id"].nunique()
    m_rev = oi_month.groupby("ym")[["price", "freight_value"]].sum()
    monthly_rows = []
    for ym in sorted(m_orders.index):
        gmv_m = float(m_rev.loc[ym, "price"]) if ym in m_rev.index else 0.0
        fr_m = float(m_rev.loc[ym, "freight_value"]) if ym in m_rev.index else 0.0
        monthly_rows.append(
            {
                "month": ym,
                "orders": int(m_orders[ym]),
                "gmv": round(gmv_m, 2),
                "freight": round(fr_m, 2),
            }
        )

    active_closed = int(closed_full["is_active"].sum())
    total_closed = int(len(closed_full))
    return {
        "overview": {
            "total_orders": int(len(orders)),
            "delivered_orders": int((orders["order_status"] == "delivered").sum()),
            "order_items": int(len(items)),
            "unique_buyers": unique_buyers,
            "repeat_buyers": repeat_buyers,
            "repeat_buyer_pct": round(repeat_buyers / unique_buyers * 100, 2),
            "gmv_brl": round(total_gmv, 2),
            "freight_brl": round(total_freight, 2),
            "total_payments_brl": round(total_payments, 2),
            "total_sellers": int(len(sellers)),
            "top_10_pct_sellers_count": top_10_n,
            "top_10_pct_sellers_gmv_share": round(top_10_share, 2),
            "median_seller_gmv_brl": round(float(s_gmv.median()), 2),
            "mql_leads": int(len(mql)),
            "closed_deals": total_closed,
            "lead_to_deal_pct": round(total_closed / len(mql) * 100, 2),
            "active_funnel_sellers": active_closed,
            "inactive_funnel_sellers": total_closed - active_closed,
            "deal_activation_pct": round(active_closed / total_closed * 100, 2),
            "funnel_gmv_brl": round(float(closed_full["gmv"].sum()), 2),
            "funnel_orders": int(closed_full["orders"].sum()),
            "median_days_won_to_first_sale": round(float(closed_full["won_to_first_days"].median()), 1),
            "sp_freight_share_pct": next(r["freight_share_pct"] for r in state_rows if r["state"] == "SP"),
        },
        "delivery_impact": delivery_impact,
        "channels": channel_rows,
        "lead_types": lead_type_rows,
        "states": state_rows,
        "payments": pay_rows,
        "top_categories": cat_rows[:18],
        "monthly": monthly_rows,
    }


def main() -> None:
    ecomm, funnel = load_tables()
    summary = build_summary(ecomm, funnel)
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {DATA_OUT} ({DATA_OUT.stat().st_size:,} bytes)")
    print(json.dumps(summary["overview"], indent=2))


if __name__ == "__main__":
    main()
