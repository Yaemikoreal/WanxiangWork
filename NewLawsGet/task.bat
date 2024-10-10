@echo off
:: 启动时最大化窗口并执行命令
cmd /C "mode con: cols=120 lines=30 & title 自动运行日志 & python E:\JXdata\Python\wan\activate_and_run.py & pause"