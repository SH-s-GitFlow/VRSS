# :earth_asia: KCGSA VRSS 알고리즘 개발 
1. [KCGSA VRSS 알고리즘 리스트](#clipboard-kcgsa-vrss-알고리즘-리스트)
   - [해양 기상정보 관련 알고리즘](#ocean-해양-기상정보-관련-알고리즘)
   - [선박 관련 알고리즘](#ship-선박-관련-알고리즘)
3. [KCGSA VRSS 알고리즘 플로우차트](#repeat-kcgsa-vrss-알고리즘-flowchart)
   
## :clipboard: KCGSA VRSS 알고리즘 리스트
### :ocean: 해양 기상정보 관련 알고리즘  
| 알고리즘 ID | 이름                | 설명 & oper. 조건                                                               | Input Data                                                      | Output Data                                                                                        |
|-------------|---------------------|---------------------------------------------------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| W01         | ECMWF_API.py        | ECMWF 수치모델 예보자료 수집 [Time-driven] 1h에 한 번씩 run                     | -                                                               | raw 예보데이터 /  grib2 파일                                                                        |
| W02         | ECMWF_Re_API.py     | ECMWF 재분석자료 수집 [Time-driven] 7일에 한 번씩 run                           | -                                                               | raw 재분석데이터 / grib2 파일                                                                        | X (but W01과 유사)            |
| W03         | Ready2use_ECMWF.py  | 수치모델 자료 내삽 및 격자화 처리 [Event-driven] W01이 업데이트 될 때마다 run   | W01 output (grib 2파일)                                         | 보정 전 해양기상격자 / DB [현재는 xarray로 출력] (필수포함)항목: lat, lon, time, parameter, value |
| W04         | Wind_ext.py         | 해상풍 추출 [Event-driven] SAR L1D data가 들어왔을 때 마다 run                  | SAR L1D data (metadata 포함), W01 output (SAR 시계열 데이터)     | (1) 풍속_고해상도 ver. / DB [현재는 xarray로 출력] (2) 풍속_중해상도 ver. / DB                     |
| W05         | Wave_ext.py         | 해양 파라미터 추출 [Event-driven] SAR L1A data가 들어왔을 때 마다 run           | SAR L1A data                                                    | 파랑정보 / DB [현재는 json 으로 출력] (필수포함)항목: lat, lon, time, wave height                   |
| W06         | Corrmap_update.py   | 재분석 및 위성자료를 활용한 보정 맵 업데이트 [Time-driven] 7일에 한 번씩 run    | W02 output, W03 output, W04 output - (2), 위성 데이터            | 해양기상격자 보정 맵 / DB                                                                            |
| W07         | Corr.py             | 보정맵을 이용한 수치모델 파라미터 보정 [Event-driven] W03이 업데이트 될 때마다 run | W03 output, W06 output                                          | 보정된 해양기상격자 / DB                                                                             |
| W08         | Nav_risk.py         | 종합항해위험도 산출 [Event-driven] W07이 업데이트 되었을 때마다 run             | W07 output                                                      | 종합항해위험도 격자 / DB                                                                             |

### :ship: 선박 관련 알고리즘 
| 알고리즘 ID | 이름                | 설명 & oper. 조건                                                               | Input Data                                                      | Output Data                                                                                        |
|-------------|---------------------|---------------------------------------------------------------------------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| S01         | SAR_shipdet.py      | SAR 이동선박 ROI 추출                                                          | SAR L1D data, 선박탐지 pth 모델                                  | 선박탐지결과 위치&방향 정보 / DB [현재는 json 으로 출력]                                            |
| S02         | SAR_velocityEstim.py| SAR 선박 속도추정                                                              | SAR L1A data, SAR L1D metadata, S01 output                      | (1) 재초점화 선박 패치 array / 파일 [tif], (2) 속도 / DB                                          |
| S03         | SARAIS_match.py     | AIS 시간보정                                                                   | SAR L1D data, 1시간 통합 AIS 자료                                | SAR 영상과의 매칭을 위해 시간보정 된 AIS / DB[현재는 json으로 출력]                                 |
| S04         | SARAIS_identify.py  | SAR 미식별선박 추정                                                            | S01 output, S03 output                                           | 식별 및 미식별 선박 list / DB[현재는 json으로 출력]                                                 |
| S05         | SAR_shipmultcls.py  | 미식별 선박 분류 [Event-driven] S02 결과가 나왔을 때 run                        | S02 output -(1) (재초점화 선박 패치 array tif 파일)              | 선종 식별 결과 / DB [현재는 csv 파일로 저장]                                                       |
| S06         | SAR_velocityPred.py | 선박항로예측 – 선박자세기반                                                     | S02 output -(2) (선박탐지결과 위치정보 +속도 json)               | 10분 간격의 1시간 후 까지의 선박 위치정보 / DB [현재는 json으로 출력]                                |
| S07         | InferenceVisual.py  | 선박항로예측 – AIS 기반 [Event-driven] UI 화면에서 선박 클릭시                  | 2시간 통합 AIS 자료                                             | 1시간 후 예측 항로 / DB (필수포함)항목: MMSI, datetime, lat, lon, velocity                         |
| S08         |                     | 선박항로예측 – 목적지 기반                                                      |                                                                 |                                                                                                    |
| S09         |                     | 수치모델자료 수집 및 처리 - NOAA                                               |                                                                 |                                                                                                    |
| S10         |                     | AIS 선박 분포 및 과거정보 생성                                                  |                                                                 |                                                                                                    |
| S11         |                     | 개별선박의 항해위험도 도출                                                      |                                                                 |                                                                                                    |
| S12         |                     | 선박 통계수집, 보고서 생성       


## :repeat: KCGSA VRSS 알고리즘 flowchart
<p align="center">
<img src="https://github.com/user-attachments/assets/ff72eb45-52b1-41a3-8b78-8a4d8016037d" width="650" height="800">
 </p>
