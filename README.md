# Olist E-Commerce & Marketing Funnel

> **Language:** **English** | [Español (`README.es.md`)](README.es.md)
>
> **99,441 real Brazilian marketplace orders + 8,000 seller sales leads**, joined together to answer two simple business questions: why do almost all shoppers leave after one order, and why do more than half of signed sellers never make a sale?

---

## What I Found (In Plain Words)

1. **Late boxes wreck trust fast.**  
   When an order arrives on time (**92.0%** of delivered boxes, median **9.7 days**), buyers give an average **4.29 / 5** stars and only **6.57%** leave 1 star. When it arrives late (**8.0%**, `7,662` orders, median **29.1 days**), the average drops to **2.57 / 5** and **46.12%** leave 1 star—more than seven times worse.

2. **97 out of 100 buyers never come back.**  
   Across **96,096** unique shoppers, only **2,997** (**3.12%**) placed a second order. The store brought in **R$ 13.59M** in product sales plus **R$ 2.25M** in shipping (**R$ 16.01M** total paid), mostly on credit cards (**78.34%**, averaging **3.51** monthly payments), yet had to replace almost every buyer every month.

3. **More than half of "won" seller deals made R$ 0.**  
   Marketing brought **8,000** leads and sales closed **842** new stores (**10.53%**). Connecting those `seller_id` records to real customer orders shows only **380** stores (**45.13%**) ever sold an item (`4,518` orders, **R$ 676.85K** GMV)—leaving **462 signed stores (54.87%)** with zero sales.

4. **Big online stores carried the funnel; slow onboarding hurt the rest.**  
   Larger online merchants (`online_big`, `126` signed -> `79` selling, **62.70%** active) brought **R$ 290.93K** (**43%** of all funnel sales), while `offline` (`28.85%` active) and `industry` (`33.33%` active) lagged behind. The median new seller took **50.0 days** after signing just to reach their first shipment deadline.

5. **Shipping eats 20% of the bill outside the Southeast.**  
   In São Paulo (`41,375` orders), shipping adds **12.14%** to what the buyer pays and arrives in **8.7 days**. In northern and northeastern states like Maranhão (**20.85%** shipping, **20.38%** late), shipping eats a fifth of the ticket and arrives late 1 out of 5 times.

---

## How to Run

Both datasets are loaded via `kagglehub` (`olistbr/brazilian-ecommerce` and `olistbr/marketing-funnel-olist`):

```powershell
uv run --with "kagglehub[pandas-datasets]" python src/analyze_olist.py
node verify.mjs
```

Open [`index.html`](index.html) directly in a browser (no server needed) to explore the bilingual (**EN / ES**) light/dark dashboard.
