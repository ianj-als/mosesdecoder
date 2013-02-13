candle EnFrModelInstall.wxs
light EnFrModelInstall.wixobj -ext WixUIExtension
setupbld -out EnFrModelInstall.exe -mi EnFrModelInstall.msi -setup "C:\Program Files (x86)\WiX Toolset v3.7\bin\setup.exe" -title "Model Install"

candle EnFrModel.wxs -ext WixBalExtension -ext WiXUtilExtension
light EnFrModel.wixobj -ext WixBalExtension -ext WiXUtilExtension