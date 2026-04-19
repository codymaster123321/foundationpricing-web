---
title: "Our Methodology & Data Sources"
description: "Understand the algorithms, USDA soil indices, and demographic data we use to calculate accurate, localized foundation repair market estimates."
layout: "../layouts/LegalLayout.astro"
---

# Our Algorithmic Methodology & Data Sources

To generate our hyper-local foundation repair cost estimates and geotechnical risk profiles, our platform relies strictly on verifiable, government-issued datasets. By synthesizing geological and economic data, we create a realistic market baseline for your specific ZIP code.

## 1. Geotechnical Risk Assessment (USDA Soil Data)
The primary driver of foundation failure in the United States is expansive clay soil. We query the **United States Department of Agriculture (USDA) Natural Resources Conservation Service (NRCS)** databases to determine the predominant soil taxonomy in your area. 
* **The Shrink-Swell Index (Linear Extensibility):** We map areas with high concentrations of smectite and montmorillonite clays. Soils with high linear extensibility require deep-driven steel piers or chemical stabilization, which significantly alters baseline repair costs.
* **Drought Data:** We cross-reference soil profiles with current regional drought monitors to identify areas experiencing rapid soil desiccation and active differential settlement.

## 2. Architectural and Economic Context (US Census Bureau)
A home's age and local real estate market dictate both the likelihood of structural failure and the economic necessity of repair. We utilize demographic APIs from the **US Census Bureau** to aggregate:
* **Median Year Built:** Older homes (pre-1980s) often suffer from degraded concrete and require different retrofitting techniques than modern, poorly compacted slab-on-grade builds.
* **Median Home Value:** Repair costs often scale with regional economics. Furthermore, understanding the median home value helps us calculate the potential equity loss if structural issues are left unrepaired.

## 3. Algorithmic Price Modeling
Our proprietary calculator combines the physical dimensions of the structural damage (Linear Feet) with the identified geological risks and historical regional labor indices. This generates a dynamic `+/- 10%` localized price range. 

*Please note: Our methodology is designed to provide a pre-inspection market estimate. It does not account for hidden sub-slab plumbing leaks, interior cosmetic damage, or specific structural anomalies. Only a licensed structural engineer can provide a final, certified scope of work.*