# Benchmarks

This directory contains performance benchmarks for the library.

## Run all benchmarks

```bash
pytest bench/ --benchmark-only


```
----------------------------------------------- benchmark: 5 tests ----------------------------------------------
Name (time in ns)               Min                  Mean                StdDev            OPS (Kops/s)          
-----------------------------------------------------------------------------------------------------------------
test_uuid_parse            379.1472 (1.0)        438.3783 (1.0)        321.1808 (1.0)        2,281.1348 (1.0)    
test_uuid4_generate        916.8871 (2.42)     1,393.4906 (3.18)       423.5204 (1.32)         717.6223 (0.31)   
test_typeid_parse        2,082.9029 (5.49)     2,396.6020 (5.47)       840.6535 (2.62)         417.2574 (0.18)   
test_typeid_generate     4,749.9780 (12.53)    5,237.8623 (11.95)    1,072.2349 (3.34)         190.9176 (0.08)   
test_typeid_workflow     7,125.0834 (18.79)    7,785.5831 (17.76)    1,302.2201 (4.05)         128.4425 (0.06)   
-----------------------------------------------------------------------------------------------------------------

Legend:
  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.
  OPS: Operations Per Second, computed as 1 / Mean
```
