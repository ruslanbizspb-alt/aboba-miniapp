"""Рендер заставки в видео под бренд.
python3 render.py --accent 6D4AFF --name "Aboba Card" --mark A --out ../../intro
Нужны: playwright + chromium, ffmpeg. Выход: <out>.mp4 (H.264) и <out>.jpg (последний кадр — постер)."""
import argparse,os,subprocess,tempfile,time,urllib.parse
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--accent',default='6D4AFF');ap.add_argument('--name',default='Aboba Card');ap.add_argument('--mark',default='A')
ap.add_argument('--out',default='intro');ap.add_argument('--fps',type=int,default=60);ap.add_argument('--dur',type=float,default=3.2);ap.add_argument('--chrome',default=os.environ.get('CHROME'))
a=ap.parse_args();here=os.path.dirname(os.path.abspath(__file__))
q=urllib.parse.urlencode({'accent':a.accent,'name':a.name,'mark':a.mark})
tmp=tempfile.mkdtemp()
with sync_playwright() as p:
    kw={'args':['--no-sandbox']}
    if a.chrome: kw['executable_path']=a.chrome
    b=p.chromium.launch(**kw);pg=b.new_page(viewport={'width':390,'height':480},device_scale_factor=2)
    pg.goto('file://'+os.path.join(here,'stage.html')+'?'+q);pg.wait_for_function('document.fonts.status==="loaded"');time.sleep(.3)
    n=int(a.dur*a.fps)
    for i in range(n+1):
        pg.evaluate(f'seek({i*1000/a.fps})');pg.locator('#st').screenshot(path=f'{tmp}/f{i:04d}.png')
    b.close()
subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(a.fps),'-i',f'{tmp}/f%04d.png','-c:v','libx264','-preset','slow','-crf','24','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart','-an',a.out+'.mp4'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',f'{tmp}/f{n:04d}.png','-q:v','3',a.out+'.jpg'],check=True)
print('ok',a.out+'.mp4',os.path.getsize(a.out+'.mp4'))
