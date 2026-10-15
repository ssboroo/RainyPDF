from pathlib import Path
FONT=Path(__file__).resolve().parents[1]/'assets'/'DejaVuSans.ttf'
def color(value='#172B4D'):
 value=value.lstrip('#')
 if len(value)!=6:raise ValueError('Өнгө буруу.')
 return tuple(int(value[i:i+2],16)/255 for i in (0,2,4))
