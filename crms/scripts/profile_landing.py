"""Record real scroll walkthroughs and measure a local 4x-CPU Chrome profile."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from check_landing import ARTIFACTS, local_server, ready


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mobile', action='store_true')
    args = parser.parse_args()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    with local_server() as address, sync_playwright() as playwright:
        for name in ('chromium', 'firefox', 'webkit'):
            browser_type = getattr(playwright, name)
            browser = browser_type.launch(channel='chrome') if name == 'chromium' and not Path(browser_type.executable_path).exists() else browser_type.launch()
            context = browser.new_context(
                viewport={'width': 390, 'height': 844} if args.mobile else {'width': 1366, 'height': 768},
                has_touch=args.mobile,
                record_video_dir=str(ARTIFACTS / 'videos'),
                record_video_size={'width': 390, 'height': 844} if args.mobile else {'width': 1366, 'height': 768},
            )
            page = context.new_page()
            page.add_init_script('''
                window.landingMetrics = {lcp:0, cls:0, longTasks:[]};
                try { new PerformanceObserver(list => {
                    list.getEntries().forEach(entry => { landingMetrics.lcp = entry.startTime; });
                }).observe({type:'largest-contentful-paint', buffered:true}); } catch {}
                try { new PerformanceObserver(list => {
                    list.getEntries().forEach(entry => { if(!entry.hadRecentInput) landingMetrics.cls += entry.value; });
                }).observe({type:'layout-shift', buffered:true}); } catch {}
                try { new PerformanceObserver(list => {
                    list.getEntries().forEach(entry => landingMetrics.longTasks.push(entry.duration));
                }).observe({type:'longtask', buffered:true}); } catch {}
            ''')
            if name == 'chromium' and not args.mobile:
                client = context.new_cdp_session(page)
                client.send('Emulation.setCPUThrottlingRate', {'rate': 4})
            ready(page, address)
            page.wait_for_function("performance.now() > 1600 && document.fonts.status === 'loaded'")
            prefix = name + ('-mobile' if args.mobile else '')
            page.screenshot(path=str(ARTIFACTS / f'{prefix}-hero.png'))
            frames = page.evaluate('''async () => {
                const frames = [];
                let previous = performance.now();
                const frame = () => new Promise(resolve => requestAnimationFrame(time => {
                    frames.push(time - previous); previous = time; resolve();
                }));
                const end = document.documentElement.scrollHeight - innerHeight;
                for(let y=0; y<=end; y+=28) { scrollTo(0,y); await frame(); }
                for(let y=end; y>=0; y-=56) { scrollTo(0,y); await frame(); }
                return frames.slice(2);
            }''')
            metrics = page.evaluate('landingMetrics')
            metrics['cpuThrottle'] = 4 if name == 'chromium' and not args.mobile else 1
            metrics['frameCount'] = len(frames)
            metrics['frameMedianMs'] = round(sorted(frames)[len(frames)//2], 2)
            metrics['framesOver33ms'] = sum(frame > 33.4 for frame in frames)
            (ARTIFACTS / f'{prefix}-performance.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
            video = page.video
            page.close()
            context.close()
            video.save_as(str(ARTIFACTS / f'{prefix}-walkthrough.webm'))
            browser.close()
            print(f'{prefix}: {json.dumps(metrics)}', flush=True)


if __name__ == '__main__':
    main()
