echo from distutils.core import setup> buildexe.py
echo import py2exe>> buildexe.py
echo setup(console=['forum24-mirror.py'])>> buildexe.py
C:\Python27\python.exe buildexe.py  py2exe
rmdir build /Q /S
del buildexe.py
mkdir dist\sites /Q
xcopy sites dist\sites /E /Q /Y /I
echo ..\forum24-mirror.exe config-drevlepravoslavie.py>dist\sites\drevlepravoslavie.cmd
echo ..\forum24-mirror.exe config-starovery.py>dist\sites\starovery.cmd
