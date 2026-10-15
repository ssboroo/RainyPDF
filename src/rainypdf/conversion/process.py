"""Bounded child execution that never leaves its descendant process tree running."""
import subprocess
import psutil

def terminate_tree(process):
 try:parent=psutil.Process(process.pid);children=parent.children(recursive=True)
 except psutil.NoSuchProcess:children=[];parent=None
 for child in reversed(children):
  try:child.kill()
  except psutil.NoSuchProcess:pass
 if parent:
  try:parent.kill()
  except psutil.NoSuchProcess:pass
 psutil.wait_procs(children,timeout=3)
 if hasattr(process,'wait'):
  try:process.wait(timeout=3)
  except subprocess.TimeoutExpired:process.kill();process.wait()
 else:
  process.join(timeout=3)
  if process.is_alive():process.kill();process.join(timeout=2)

def run_tool(args,timeout=180,**kwargs):
 kwargs.setdefault('stdout',subprocess.PIPE);kwargs.setdefault('stderr',subprocess.PIPE)
 process=subprocess.Popen(args,**kwargs)
 try:
  stdout,stderr=process.communicate(timeout=timeout)
 except BaseException:
  terminate_tree(process);raise
 return subprocess.CompletedProcess(args,process.returncode,stdout,stderr)
