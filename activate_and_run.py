import os
import subprocess
import sys

# 设置虚拟环境路径
virtual_env = r'E:\JXdata\新法速递\易柯宇交接：新法速递\新法速递\.venv'

# 尝试加载虚拟环境
if sys.platform == 'win32':
    activate_this = os.path.join(virtual_env, 'Scripts', 'activate.bat')
else:
    activate_this = os.path.join(virtual_env, 'bin', 'activate')

# 在 Windows 上，我们不能直接执行 activate.bat 来激活环境，
# 因为它只是设置了一些环境变量。我们需要手动设置这些变量。
if sys.platform == 'win32':
    python_exe = os.path.join(virtual_env, 'Scripts', 'python.exe')
    os.environ['PYTHONIOENCODING'] = 'utf-8'  # 设置 Python IO 编码为 UTF-8
else:
    python_exe = os.path.join(virtual_env, 'bin', 'python')

# 使用虚拟环境中的 Python 解释器运行脚本
subprocess.run([python_exe, r'E:\JXdata\Python\wan\NewLawsGet\TotalProcess.py'])