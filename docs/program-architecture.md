# 程式架構

```text
                     Data Layer
                         │
             ┌───────────┴──────────┐
             ↓                      ↓
         yfinance                 FinLab
        價格資料            台股研究所需資料
             │                      │
             └───────────┬──────────┘
                         ↓
                  Normalized Data
                         ↓
                  Strategy Engine
                         ↓
                       Signal
                         ↓
                 Portfolio / Risk
                         ↓
                       Order
                         ↓
                        Fill
                         ↓
                     Position
                         ↓
                    Performance
```
