# LME Copper Short-Squeeze Monitor — Live 2025

**Real-time, production-grade squeeze detector**  
**25 Nov 2025 live reading:** 177.5 / 325 → Low-to-Elevated Risk (post-refill regime)

<img width="1102" height="420" alt="Image" src="https://github.com/user-attachments/assets/901e1d4b-48fb-41d6-9fcc-98f7560e6003" />

### What it does
- Combines four proven squeeze pillars into one composite (0–325)  
- Percentile-based, no arbitrary weights  
- Correctly called both the 2021 and 2025 squeezes  
- Now correctly flags the 2025 post-refill easing

### Live pillars (25 Nov 2025)
| Pillar                | Percentile   | Points |
|-----------------------|--------------|--------|
| Backwardation (5Y)    | 80.9th       | 80.9   |
| Inventory tightness (10Y) | 3.3th    | 3.3    |
| CFTC net shorts (8Y)  | 93.3th       | 93.3   |
| COMEX-LME basis bonus | <90th → 0/25 | 0      |
| **Composite**         |              | **177.5** |

### What-if engine (one line)
```python
monitor.ind.compute_percentiles_from_raw({
    'inventory_tonnes': 220000,
    'net_shorts': 160000
})
```
→ 220.2 / 325 → High squeeze risk

See [methodology.md](methodology.md) • Open [Dashboard_Demo.ipynb](Dashboard_Demo.ipynb) to run live
</br>All data fetched live from LME, CME, CFTC — no API keys needed.  
</br>Offline version (cached CSVs) in `/data` folder.
