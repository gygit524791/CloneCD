# Teccd
code clone detection  
2019 IEEE International Conference on Software Maintenance and Evolution (ICSME)  
see: https://ieeexplore.ieee.org/document/8918964

## Setup:
redis

### python:
1.numpy
2.sklearn
3.hashlib
4.Levenshtein

## Usage:
Setting parameters in config.properties file:
### Redis installation path:
redis.path
### Programing language:
ccd.fileType=java
### Minimum line of code:
ccd.methodLimitedLine=10
### Number of threads:
ccd.threadCount=8
### File path:
ccd.path=

## 1.Generate the method AST
Execute main method in Main.java

## 2.Detection
Execute method_compare method in main_lsh.py
