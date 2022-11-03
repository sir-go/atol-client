## Web Client Lib for [ATOL POS](https://www.atol.ru/catalog/pos-sistemy) terminal

A small library - client for ATOL API

### Implemented functions

 - buy
 - buyCorrection
 - buyReturn
 - cashIn
 - cashOut
 - changeRegistrationParameters
 - closeArchive
 - closeShift
 - continuePrint
 - fnChange
 - getDeviceInfo
 - getDeviceStatus
 - getFnInfo
 - getRegistrationInfo
 - getShiftStatus
 - nonFiscal
 - ofdExchangeStatus
 - openShift
 - registration
 - reportOfdExchangeStatus
 - reportX
 - sell
 - sellCorrection
 - sellReturn

### Install
```bash
pip install atol-client
```

### Tests
```bash
pip install -r requirements.txt
flake8 . --show-source --statistics && python -m pytest .
```

### Usage
```python
from atol import WebClient

if __name__ == '__main__':
    atol = WebClient("http://atol-host")
    print(atol.get_shift_status())
```
