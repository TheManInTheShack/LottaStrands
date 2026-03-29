@ECHO off

cls

ECHO ----------------------------------------------------------------------------------------------------
ECHO Preparing data
ECHO ----------------------------------------------------------------------------------------------------
COPY ..\lib\utilities.py 1>NUL
COPY ..\lib\excel_tools.py 1>NUL
COPY ..\lib\graph_tools.py 1>NUL
COPY ..\lib\text_tools.py 1>NUL
COPY ..\app\parse.py 1>NUL
COPY ..\app\ingest.py 1>NUL
COPY ..\lib\primes.txt 1>NUL

IF EXIST ..\data\work\corpus.json           COPY  ..\data\work\corpus.json         corpus.json 1>NUL
IF EXIST ..\data\work\clean_input.xlsx      COPY  ..\data\work\clean_input.xlsx    clean_input.xlsx 1>NUL
IF EXIST ..\data\work\narrative_map.xlsx    COPY  ..\data\work\narrative_map.xlsx  narrative_map.xlsx 1>NUL
CALL parse.py
CALL ingest.py

DEL utilities.py 1>NUL
DEL excel_tools.py 1>NUL
DEL graph_tools.py 1>NUL
DEL text_tools.py 1>NUL
DEL parse.py 1>NUL
DEL ingest.py 1>NUL
DEL primes.txt 1>NUL

IF EXIST clean_input.xlsx    MOVE clean_input.xlsx ..\data\work\clean_input.xlsx 1>NUL
IF EXIST narrative_map.xlsx  MOVE narrative_map.xlsx ..\data\work\narrative_map.xlsx 1>NUL
IF EXIST corpus.json         MOVE corpus.json ..\data\work\corpus.json 1>NUL


REM ECHO ----------------------------------------------------------------------------------------------------
REM ECHO Running dashboard
REM ECHO ----------------------------------------------------------------------------------------------------
REM COPY ..\lib\utilities.py 1>NUL
REM COPY ..\lib\dash_tools.py 1>NUL
REM COPY ..\app\interface\index.py 1>NUL
REM COPY ..\app\interface\app.py 1>NUL
REM COPY ..\app\interface\initialize.py 1>NUL
REM COPY ..\app\interface\page_splash.py 1>NUL
REM COPY ..\app\interface\page_read.py 1>NUL
REM COPY ..\app\interface\page_view.py 1>NUL

REM CALL index.py

REM DEL utilities.py 1>NUL
REM DEL dash_tools.py 1>NUL
REM DEL index.py 1>NUL
REM DEL app.py 1>NUL
REM DEL initialize.py 1>NUL
REM DEL page_splash.py 1>NUL
REM DEL page_read.py 1>NUL
REM DEL page_view.py 1>NUL

