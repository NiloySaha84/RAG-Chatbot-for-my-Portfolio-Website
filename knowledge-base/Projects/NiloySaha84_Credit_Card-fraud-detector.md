# Credit Card Fraud Detection

## Project Overview
This project builds a **machine learning system to detect fraudulent credit card transactions**. It uses Python, Pandas, NumPy, and scikit-learn to analyze and model transaction data. The project demonstrates **data preprocessing, handling imbalanced classes, training classification models, and evaluating their performance**.  

---

## Dataset
- The dataset contains **50,000 sampled transactions** (original dataset contains 1,000,000).  
- Features include:  
  - `distance_from_home`  
  - `distance_from_last_transaction`  
  - `ratio_to_median_purchase_price` (transaction amount relative to median)  
  - `repeat_retailer`, `used_chip`, `used_pin_number`, `online_order`  
- Target: `fraud` → 0 = legitimate, 1 = fraudulent transaction.  

---

## Key Features
- Explored the dataset using descriptive statistics and visualization:  
  - Transaction class distribution  
  - Transaction amount distribution  
- Preprocessed data by scaling numeric features.  
- Split data into **80% training** and **20% testing**.  
- Used **Random Forest** and **Gradient Boosting** classifiers.  
- Evaluated models using **Precision, Recall, F1-score, and ROC-AUC**.  
- Implemented a **predict_fraud() function** to classify new transactions dynamically.  

---

## Results
- **Random Forest Classifier:** ROC-AUC > 0.99  
- **Gradient Boosting Classifier:** ROC-AUC > 0.99  
- The models successfully identify fraudulent transactions with **high accuracy and recall**, even with imbalanced data.  
