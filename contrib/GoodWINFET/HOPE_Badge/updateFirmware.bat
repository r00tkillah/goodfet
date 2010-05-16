cd dist
goodfet.exe erase
goodfet.exe flash openbeacontag.hex
goodfet.exe verify openbeacontag.hex
goodfet.exe run