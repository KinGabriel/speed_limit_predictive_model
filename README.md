This repository contains the full code, models, and documentation for the research project Data-Driven Speed Limit Recommendations for Philippine Roads Using Machine Learning
The project proposes an evidence-based framework that uses real-world road, traffic, and crash data to recommend safe, context-aware speed limits for road segments across the Philippines

Project Overview
Traditional speed limits in the Philippines are still based on Republic Act No. 4136 (1964), which applies fixed limits regardless of traffic volume, road design, or crash history. This research applies a modern, data-driven approach that leverages machine learning and statistical models to recommend adaptive, location-specific speed limits that improve safety and efficiency

Key Features
Feature Engineering: Interaction terms, nonlinear variables, densities, and composite flags to reflect real-world risks.
Multicollinearity Reduction: Variance Inflation Factor (VIF) filtering for stable modeling.
Modeling: XGBoost for high-performance predictions, and Poisson GLM for interpretability.
Speed Recommendations: Segment-level speed limits based on crash reduction targets.
Sensitivity Analysis: Tests model robustness to changes in AADT, lane count, and more.
Non-Speed Risk Assessment: Identifies high-risk segments due to geometry or exposure, even without speed issues.
