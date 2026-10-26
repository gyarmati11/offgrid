"""3D render futtatása headless Chromiumban → JPG + vetített pontok."""
import base64, io, json, os, sys, time
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def render(mode, out_jpg, ss=1.5, dist=33, project_points=None):
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 800, "height": 600})
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        t = time.time()
        pg.goto(f"file://{HERE}/v2.html?mode={mode}&ss={ss}&dist={dist}", timeout=600000)
        pg.wait_for_function("window.DONE || window.__err", timeout=600000) if not errs else None
        if errs:
            print("\n".join(errs)[:3000]); b.close(); sys.exit(1)
        info = pg.evaluate("window.DONE")
        url = pg.evaluate("document.getElementById('c').toDataURL('image/png')")
        pts = pg.evaluate("(P)=>P.map(pl=>pl.map(q=>window.PROJECT(q)))", project_points) if project_points else None
        b.close()
    img = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1]))).convert("RGB")
    img = img.resize((1600, 1100), Image.LANCZOS)
    img.save(out_jpg, quality=90, optimize=True, progressive=True)
    print(f"{mode}: {info['tris']} háromszög, {time.time()-t:.1f}s → {out_jpg} ({os.path.getsize(out_jpg)//1024} KB)")
    return pts


if __name__ == "__main__":
    mode = sys.argv[1]
    render(mode, sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.5, float(sys.argv[4]) if len(sys.argv) > 4 else 33)
