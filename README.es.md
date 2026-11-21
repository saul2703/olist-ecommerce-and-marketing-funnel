# Olist E-Commerce y Embudo de Vendedores (`99,441` Pedidos)

> **Idioma:** [English (`README.md`)](README.md) | **Español**
>
> **99,441 pedidos reales en Brasil + 8,000 prospectos de vendedores**, unidos para responder dos preguntas simples de negocio: por qué casi ningún cliente vuelve a comprar y por qué más de la mitad de las tiendas firmadas nunca vende nada.

---

## Lo Que Encontré (En Palabras Sencillas)

1. **Los paquetes tardíos destruyen la confianza rápido.**  
   Cuando el pedido llega a tiempo (**92.0%** de entregas, mediana **9.7 días**), los clientes dan **4.29 / 5** estrellas y solo **6.57%** deja 1 estrella. Cuando llega tarde (**8.0%**, `7,662` pedidos, mediana **29.1 días**), el promedio cae a **2.57 / 5** y **46.12%** deja 1 estrella—más de siete veces peor.

2. **97 de cada 100 compradores no vuelve nunca.**  
   De **96,096** compradores únicos, solo **2,997** (**3.12%**) hicieron una segunda compra. El sitio vendió **R$ 13.59M** en productos más **R$ 2.25M** de envío (**R$ 16.01M** cobrados en total, **78.34%** con tarjeta de crédito a **3.51** cuotas en promedio), pero perdió casi toda recompra.

3. **Más de la mitad de tiendas "ganadas" vendió R$ 0.**  
   Marketing trajo **8,000** prospectos y ventas firmó **842** tiendas (**10.53%**). Al cruzar su `seller_id` con pedidos reales, solo **380** tiendas (**45.13%**) lograron vender algo (`4,518` pedidos, **R$ 676.85K** en ventas)—mientras **462 tiendas firmadas (54.87%)** se quedaron en cero.

4. **Las tiendas digitales grandes sostuvieron el embudo.**  
   Los comercios digitales grandes (`online_big`, `126` firmados -> `79` vendiendo, **62.70%** activas) aportaron **R$ 290.93K** (**43%** de las ventas del embudo), frente a `offline` (**28.85%** activas) e `industry` (**33.33%**). La mediana de demora desde la firma hasta el primer envío fue de **50.0 días**.

5. **El envío se lleva el 20% de la cuenta fuera del sureste.**  
   En São Paulo (`41,375` pedidos), el envío representa **12.14%** del pago total y llega en **8.7 días**. En estados del norte y noreste como Maranhão (**20.85%** de envío, **20.38%** tardíos), el flete consume una quinta parte del monto y 1 de cada 5 cajas llega tarde.

---

## Cómo Ejecutarlo

Ambos conjuntos de datos se cargan directo con `kagglehub` ([`olistbr/brazilian-ecommerce`](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) y [`olistbr/marketing-funnel-olist`](https://www.kaggle.com/datasets/olistbr/marketing-funnel-olist)):

```powershell
uv run --with "kagglehub[pandas-datasets]" python src/analyze_olist.py
node verify.mjs
```

Abre [`index.html`](index.html) en cualquier navegador para usar el dashboard bilingüe (**EN / ES**) con tema claro/oscuro.
