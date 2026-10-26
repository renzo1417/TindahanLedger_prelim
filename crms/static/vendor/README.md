# Landing animation dependencies

Browser distributions are checked into this directory to keep the Django page
buildless and independent of runtime CDNs. Run `scripts/vendor_landing_assets.py`
from the `crms` directory to reproduce these files.

- **GSAP 3.15.0:** Core, ScrollTrigger, SplitText, Flip, DrawSVGPlugin, CustomEase.
  Distributed by GreenSock under its [standard no-charge license](https://gsap.com/standard-license/).
  Original copyright and license notices are retained in each distribution.
  Source: https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/
- **Lenis 1.3.26:** Browser distribution and recommended CSS.
  MIT license retained in `lenis/LICENSE`.
  Source: https://github.com/darkroomengineering/lenis/tree/v1.3.26
- Font subsets live in `../fonts/landing`, accompanied by each family's SIL Open
  Font License. Families: Plus Jakarta Sans, Newsreader, JetBrains Mono.

The hero image is a local, anonymous capture of the existing overview's sample
data, not a capture of a real store's records.
