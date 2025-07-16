# Data-Driven Speed Limit Recommendations for Philippine Roads Using Machine Learning

This repository contains the full code, models, and documentation for the research project **_Data-Driven Speed Limit Recommendations for Philippine Roads Using Machine Learning_**.  
The project proposes an evidence-based framework that uses real-world road, traffic, and crash data to recommend safe, context-aware speed limits for road segments across the Philippines.

---

## Project Overview

Traditional speed limits in the Philippines are still based on **Republic Act No. 4136 (1964)**, which applies fixed limits regardless of traffic volume, road design, or crash history.  
This research applies a modern, data-driven approach that leverages **machine learning** and **statistical models** to recommend adaptive, location-specific speed limits that improve road safety and mobility.

---

## Key Features

- **Feature Engineering**  
  Includes interaction terms, polynomial features, density ratios, and composite binary flags that reflect real-world traffic and geometric risk factors.

- **Multicollinearity Reduction**  
  Uses **Variance Inflation Factor (VIF)** analysis to remove redundant features and stabilize modeling.

- **Modeling Framework**  
  Implements **XGBoost Regression** for predictive accuracy and **Poisson GLM** for statistical interpretability and policy relevance.

- **Speed Recommendations**  
  Generates segment-specific speed limits optimized to reduce predicted crash rates by up to 100%, using root-finding algorithms and policy-aware constraints.

- **Sensitivity Analysis**  
  Assesses how changes in input conditions (e.g., AADT, lane count) affect speed recommendations, ensuring model robustness.

- **Non-Speed Risk Assessment**  
  Identifies road segments with high crash risks due to non-speed factors (e.g., curvature, population density) and recommends engineering interventions.


