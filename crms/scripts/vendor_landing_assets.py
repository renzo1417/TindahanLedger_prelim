"""Fetch the pinned, public landing dependencies and self-hosted font subsets."""
import re
from pathlib import Path
from urllib.request import Request, urlopen

STATIC = Path(__file__).resolve().parents[1] / 'static'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'}


def fetch(url, destination):
    with urlopen(Request(url, headers=HEADERS), timeout=30) as response:
        content = response.read()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    print(f'{destination.relative_to(STATIC)}: {len(content)} bytes', flush=True)
    return content


def main():
    for plugin in ('gsap', 'ScrollTrigger', 'SplitText', 'Flip', 'DrawSVGPlugin', 'CustomEase'):
        fetch(f'https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/{plugin}.min.js', STATIC / 'vendor/gsap' / f'{plugin}.min.js')
    for filename in ('lenis.min.js', 'lenis.css'):
        fetch(f'https://cdn.jsdelivr.net/npm/lenis@1.3.26/dist/{filename}', STATIC / 'vendor/lenis' / filename)
    fetch('https://cdn.jsdelivr.net/npm/lenis@1.3.26/LICENSE', STATIC / 'vendor/lenis/LICENSE')
    for family, filename, folder, weights in (
        ('Plus+Jakarta+Sans', 'jakarta', 'plusjakartasans', '400..800'),
        ('Newsreader', 'newsreader', 'newsreader', '400..700'),
        ('JetBrains+Mono', 'mono', 'jetbrainsmono', '400..700'),
    ):
        css_url = f'https://fonts.googleapis.com/css2?family={family}:wght@{weights}&display=swap'
        with urlopen(Request(css_url, headers=HEADERS), timeout=30) as response:
            css = response.read().decode()
        latin = css.split('/* latin */')[-1]
        url = re.search(r'url\((https://[^)]+)\)', latin).group(1)
        content = fetch(url, STATIC / 'fonts/landing' / f'{filename}-latin.woff2')
        if content[:4] != b'wOF2':
            raise ValueError(f'{family}: expected a WOFF2 font')
        fetch(f'https://raw.githubusercontent.com/google/fonts/main/ofl/{folder}/OFL.txt', STATIC / 'fonts/landing' / f'{filename}-OFL.txt')


if __name__ == '__main__':
    main()
