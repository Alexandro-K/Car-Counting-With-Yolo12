# Car Counting With Yolo12 
In this project i use CCTV from Binamarga to make car counting program.

## Description
This project use Yolo version 12 with medium size to detect vehicles, There are 2 opposite road. in this project the vehicles that are getting detected are car, truck, bus, and motorbike. The data added to a dataframe for every 1 minute and the program will stop after 3 minutes. Giving the data for each minute, the average and the total.

## Project Demo
https://github.com/user-attachments/assets/b482dfa0-86b1-41e9-81dd-71b9d7a9930d

## Project Report Example
|Waktu           |Total Bagian Kiri|Total Bagian Kanan|Rata-rata Keseluruhan|
|----------------|-----------------|------------------|---------------------|
|07-10-2025 13:04|1.0              |3.0               |                     |
|07-10-2025 13:05|2.0              |3.0               |                     |
|07-10-2025 13:06|0.0              |4.0               |                     |
|AVERAGE         |1.0              |3.33              |4.33                 |
|TOTAL           |3.0              |10.0              |13.0                 |

## Getting Started
### Dependencies
* Python 3.10
* Windows 10+ / Linux / Mac OS
* Library python:
```
pip install -r requirements.txt
```

### Installing
* **Clone this Repository**
```
git clone https://github.com/Alexandro-K/Car-Counting-With-Yolo12.git
cd Car-Counting-With-Yolo12
```
* **Create the venv**
```
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # Linux/Mac
```

### Executing Program
**Run the main program:**
```
python main.py
```

## Help
**Common problems:**
* Problem: Can't import ultralytics
  
Run:
```
pip install ultralytics --upgrade
```
  
## Authors
**Alexandro Kalindra Enggarrinoputra** [Alexandro-K](https://github.com/Alexandro-K)

## Version History
* 0.1
  * Initial Release
 
## License
-

## Acknowledments
**Inspirations:**
* [Object Detection 101 Course](https://youtu.be/WgPbbWmnXJ8?si=1caWK9bWBk37FpEV)
