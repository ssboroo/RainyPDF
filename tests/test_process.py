import subprocess,sys,time,os
from pathlib import Path
import pytest
from rainypdf.conversion.process import run_tool

def test_timeout_kills_owned_descendant(tmp_path):
 import psutil
 child=tmp_path/'child.pid';wrapper=tmp_path/'wrapper.py'
 wrapper.write_text('import subprocess,sys,time\np=subprocess.Popen([sys.executable,"-c","import time;time.sleep(60)"])\nopen(sys.argv[1],"w").write(str(p.pid))\ntime.sleep(60)\n')
 with pytest.raises(subprocess.TimeoutExpired):run_tool([sys.executable,str(wrapper),str(child)],timeout=2)
 pid=int(child.read_text());time.sleep(.2)
 assert not psutil.pid_exists(pid) or psutil.Process(pid).status()==psutil.STATUS_ZOMBIE
