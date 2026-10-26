/* Local, fictional demonstrations. Presentation never writes to a server. */
(() => {
  'use strict';
  const root = document.querySelector('.landing-body');
  if (!root) return;

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const desktop = '(min-width: 1024px) and (min-height: 700px)';
  const finePointer = '(hover: hover) and (pointer: fine)';
  const header = root.querySelector('.lp-header');
  const ledger = root.querySelector('.lp-ledger');
  const payment = root.querySelector('#demo-payment');
  const receipt = root.querySelector('.lp-receipt');
  const balance = root.querySelector('#demo-balance');
  const recordButton = root.querySelector('#record-payment');
  const stageButtons = [...root.querySelectorAll('[data-stage]')];
  const batchList = root.querySelector('.lp-stock-list');
  const batches = [...batchList.querySelectorAll('[data-batch]')];
  const state = { stage: 'utang', manual: false, order: 'expiry' };
  const stageData = {
    utang: { paid: false, amount: '₱350.00', equation: '₱250.00 + ₱100.00 = ₱350.00', caption: 'Bawat utang, may sariling tala.' },
    bayad: { paid: true, amount: '₱200.00', equation: '₱350.00 − ₱150.00 = ₱200.00', caption: 'Bayad na ₱150. Bawas agad sa balanse.' },
    balance: { paid: true, amount: '₱200.00', equation: '₱350.00 − ₱150.00 = ₱200.00', caption: 'Bawat bayad, malinaw ang natitira.' }
  };
  let controller;
  let media;
  let lenis;
  let lenisTick;
  let observer;
  let refreshFrame;
  let flipAnimation;
  let gsapReady = false;
  let introductionPlayed = false;
  let suspended = true;
  let pendingHashAlignment = false;
  let paintLedgerMotion = null;

  function clearLedgerMotion() {
    if (!gsapReady) return;
    window.gsap.killTweensOf([payment, receipt, balance]);
    window.gsap.set([payment, receipt, balance], { clearProps: 'opacity,transform' });
  }

  function renderLedger(stage, { manual = false, animate = false, announce = false } = {}) {
    const previous = state.stage;
    clearLedgerMotion();
    state.stage = stage;
    if (manual) {
      state.manual = true;
      if (gsapReady) {
        window.gsap.killTweensOf([ledger, ...root.querySelectorAll('.lp-purchase')]);
        window.gsap.set([ledger, ...root.querySelectorAll('.lp-purchase')], { clearProps: 'clipPath,opacity,transform' });
      }
    }
    const data = stageData[stage];
    ledger.dataset.ledgerStage = stage;
    payment.setAttribute('aria-hidden', String(!data.paid));
    payment.hidden = !data.paid;
    root.querySelector('#demo-payment-empty').hidden = data.paid;
    receipt.classList.toggle('is-unpaid', !data.paid);
    balance.textContent = data.amount;
    root.querySelector('#demo-equation').textContent = data.equation;
    root.querySelector('#demo-caption').textContent = data.caption;
    root.querySelector('#demo-mode').textContent = state.manual ? 'Ikaw ang may kontrol. Reset para magsimula.' : 'Sample ledger · Demo only';
    stageButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.stage === stage)));
    recordButton.disabled = data.paid;
    recordButton.replaceChildren(document.createTextNode(data.paid ? 'Sample payment recorded ✓' : 'Record sample ₱150 payment ↗'));
    if (gsapReady) {
      if (animate && !reduce.matches && stage !== previous) {
        if (data.paid && !stageData[previous].paid) {
          window.gsap.from(payment, { y: 8, opacity: 0, duration: 0.26, ease: 'ledger-out' });
          window.gsap.from(receipt, { x: 24, y: 18, rotation: 13, opacity: 0, duration: 0.26, ease: 'ledger-out' });
        }
        window.gsap.from(balance, { opacity: 0.5, duration: 0.26, ease: 'ledger-out' });
      }
    }
    if (paintLedgerMotion) paintLedgerMotion();
    if (announce) root.querySelector('#demo-status').textContent = `${data.caption} Natitirang utang: ${data.amount}.`;
  }

  function sortStock(order, animate = true) {
    if (flipAnimation) { flipAnimation.progress(1).kill(); flipAnimation = null; }
    const flip = gsapReady && window.Flip && !reduce.matches && animate ? window.Flip.getState(batches) : null;
    state.order = order;
    const sorted = [...batches].sort((a, b) => order === 'expiry'
      ? Number(a.dataset.days) - Number(b.dataset.days)
      : Number(a.dataset.arrival) - Number(b.dataset.arrival));
    sorted.forEach(batch => batchList.appendChild(batch));
    root.querySelectorAll('[data-stock-order]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.stockOrder === order)));
    const caption = order === 'expiry' ? 'Nakaayos mula sa pinakamaagang expiry.' : 'Nakaayos ayon sa pagdating ng mga batch.';
    root.querySelector('#stock-caption').textContent = caption;
    if (animate) root.querySelector('#stock-status').textContent = `${caption} Ang expired na stock ay hiwalay at hindi ibinebenta.`;
    if (flip) flipAnimation = window.Flip.from(flip, { duration: 0.28, ease: 'ledger-move', scale: false, onComplete: () => { flipAnimation = null; } });
  }

  function scheduleRefresh() {
    cancelAnimationFrame(refreshFrame);
    refreshFrame = requestAnimationFrame(() => {
      if (!suspended && gsapReady) window.ScrollTrigger.refresh();
      if (!suspended && pendingHashAlignment) {
        pendingHashAlignment = false;
        const target = anchorTarget(window.location.hash);
        if (target) scrollToTarget(target, false);
      }
    });
  }

  function stopSmoothScroll() {
    if (lenisTick && window.gsap) window.gsap.ticker.remove(lenisTick);
    if (lenis) lenis.destroy();
    lenis = null;
    lenisTick = null;
  }

  function revealHeading(element, hero = false) {
    const gsap = window.gsap;
    if (!window.SplitText) {
      return gsap.from(element, { y: 16, opacity: 0, duration: 0.6, ease: 'ledger-out', scrollTrigger: hero ? undefined : { trigger: element, start: 'top 90%', once: true } });
    }
    window.SplitText.create(element, {
      type: 'lines', mask: 'lines', autoSplit: true, aria: 'auto',
      onSplit(split) {
        const animation = gsap.from(split.lines, {
          yPercent: 105, duration: 0.6, stagger: hero ? 0.08 : 0.06,
          ease: 'ledger-out',
          scrollTrigger: hero ? undefined : { trigger: element, start: 'top 90%', once: true },
          onComplete: () => { gsap.set(split.lines, { clearProps: 'transform' }); }
        });
        if (hero && introductionPlayed) animation.progress(1);
        return animation;
      }
    });
  }

  function setupHero() {
    if (introductionPlayed || window.scrollY >= 100 || window.location.hash) return;
    const { gsap } = window;
    revealHeading(root.querySelector('[data-hero-heading]'), true);
    gsap.timeline({ id: 'landing-hero-intro', defaults: { ease: 'ledger-out' } })
      .from('.lp-hero-enter', { y: 16, opacity: 0, duration: 0.5, stagger: 0.08 }, 0)
      .from('.lp-preview-image-wrap', { clipPath: 'inset(0 0 100% 0)', duration: 0.85, ease: 'ledger-move' }, 0)
      .from('.lp-hero-receipt', { y: 26, rotation: 14, opacity: 0, duration: 0.7 }, 0.2)
      .from('.lp-hero-expiry', { x: -24, opacity: 0, duration: 0.65 }, 0.35);
    introductionPlayed = true;
  }

  function ledgerFitsViewport() {
    return root.querySelector('.lp-ledger-pin').offsetHeight <= window.innerHeight - header.offsetHeight - 24;
  }

  function setupHandoff(conditions) {
    if (!conditions.desktop || !ledgerFitsViewport() || !window.Flip) return () => {};
    const { gsap, Flip } = window;
    const source = root.querySelector('.lp-preview-window');
    const pin = root.querySelector('.lp-ledger-pin');
    const scene = root.querySelector('.lp-ledger-scene');
    const proxy = document.createElement('div');
    proxy.className = 'lp-handoff-proxy';
    proxy.setAttribute('aria-hidden', 'true');
    proxy.setAttribute('inert', '');
    // Only noninteractive artwork is copied. Live controls remain in place.
    proxy.append(source.querySelector('.lp-window-bar').cloneNode(true));
    proxy.append(source.querySelector('.lp-preview-image-wrap').cloneNode(true));
    // A snapshot must not inherit the source's still-running entrance mask.
    proxy.querySelectorAll('[style]').forEach(element => element.removeAttribute('style'));
    proxy.querySelector('img').alt = '';
    proxy.querySelector('img').removeAttribute('fetchpriority');
    const caption = document.createElement('div');
    caption.className = 'lp-preview-caption';
    caption.textContent = 'Bawat tala, nasa tamang lugar.';
    proxy.append(caption);
    root.append(proxy);
    const fragments = [...root.querySelectorAll('.lp-hero-receipt,.lp-hero-expiry')];
    let geometry;
    function measure() {
      const sourceBounds = source.getBoundingClientRect();
      const targetBounds = ledger.getBoundingClientRect();
      const pinBounds = pin.getBoundingClientRect();
      const spacer = pin.parentElement.classList.contains('pin-spacer') ? pin.parentElement : pin;
      const pinTop = spacer.getBoundingClientRect().top + window.scrollY;
      const start = Math.max(0, sourceBounds.top + window.scrollY - header.offsetHeight - 16);
      const end = Math.max(start + 1, pinTop - header.offsetHeight - 16);
      const targetTop = pinTop + targetBounds.top - pinBounds.top - Number(gsap.getProperty(scene, 'y'));
      gsap.set(proxy, { width: sourceBounds.width, height: sourceBounds.height });
      const fit = Flip.fit(proxy, ledger, { scale: true, getVars: true });
      geometry = {
        start, end, fits: ledgerFitsViewport(),
        from: { x: sourceBounds.left, y: sourceBounds.top + window.scrollY - start },
        to: { x: targetBounds.left, y: targetTop - end, scaleX: fit.scaleX, scaleY: fit.scaleY }
      };
    }
    measure();
    let timeline;
    let lastActive = null;
    function syncVisibility() {
      const trigger = timeline && timeline.scrollTrigger;
      const focused = root.querySelector('#ledger-demo').contains(document.activeElement) || source.contains(document.activeElement);
      const active = Boolean(trigger && trigger.progress > 0.005 && trigger.progress < 0.985 && !focused && geometry.fits);
      if (active === lastActive) return;
      lastActive = active;
      proxy.style.visibility = active ? 'visible' : 'hidden';
      source.style.opacity = active ? '0' : '1';
      source.style.pointerEvents = active ? 'none' : '';
      fragments.forEach(fragment => { fragment.style.visibility = active ? 'hidden' : ''; });
    }
    timeline = gsap.timeline({
      onUpdate: syncVisibility,
      scrollTrigger: {
        id: 'landing-handoff', trigger: '.lp-hero',
        start: () => geometry.start, end: () => geometry.end,
        scrub: 0.35, invalidateOnRefresh: true,
        onRefreshInit: measure, onRefresh: syncVisibility, onUpdate: syncVisibility
      }
    });
    gsap.set(proxy, { clipPath: 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)' });
    timeline.fromTo(proxy, {
      x: () => geometry.from.x, y: () => geometry.from.y,
      scaleX: 1, scaleY: 1, opacity: 1
    }, {
      x: () => geometry.to.x, y: () => geometry.to.y,
      scaleX: () => geometry.to.scaleX, scaleY: () => geometry.to.scaleY,
      duration: 1, ease: 'none'
    }, 0)
      .fromTo(proxy, { clipPath: 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)' }, {
        clipPath: 'polygon(0% 0%, 100% 0%, 100% 0%, 0% 0%)', duration: 0.42, ease: 'none', immediateRender: false
      }, 0.58)
      .to(proxy, { opacity: 0, duration: 0.18, ease: 'none' }, 0.82);
    root.addEventListener('focusin', syncVisibility);
    return () => {
      root.removeEventListener('focusin', syncVisibility);
      source.style.removeProperty('opacity');
      source.style.removeProperty('pointer-events');
      fragments.forEach(fragment => fragment.style.removeProperty('visibility'));
      proxy.remove();
    };
  }

  function setupLedger(conditions) {
    const { gsap } = window;
    revealHeading(root.querySelector('#ledger-title'));
    const scene = root.querySelector('.lp-ledger-scene');
    const purchases = [...root.querySelectorAll('.lp-purchase')];
    const rule = root.querySelector('.lp-balance-rule');
    if (!conditions.desktop) {
      gsap.timeline({ scrollTrigger: { id: 'landing-ledger-entry', trigger: scene, start: 'top 88%', once: true } })
        .from(ledger, { clipPath: 'inset(0 0 100% 0 round 10px)', duration: 0.65, ease: 'ledger-move' })
        .from(purchases, { y: 12, opacity: 0, duration: 0.45, stagger: 0.08, ease: 'ledger-out' }, 0.2)
        .from(rule, { scaleY: 0, duration: 0.5, ease: 'ledger-out' }, 0.4);
      return () => {};
    }
    const progression = { value: 0 };
    let pinEnabled = ledgerFitsViewport();
    const rowSetters = purchases.map(row => ({ y: gsap.quickSetter(row, 'y', 'px'), opacity: gsap.quickSetter(row, 'opacity'), clip: gsap.quickSetter(row, 'clipPath') }));
    const frameY = gsap.quickSetter(scene, 'y', 'px');
    const ruleScale = gsap.quickSetter(rule, 'scaleY');
    const clamp = gsap.utils.clamp(0, 1);
    paintLedgerMotion = () => {
      rowSetters.forEach((set, index) => {
        const amount = state.manual || !pinEnabled ? 1 : clamp((progression.value - index * 0.035) / 0.15);
        set.y(12 * (1 - amount));
        set.opacity(0.35 + amount * 0.65);
        set.clip(`inset(0 0 ${(1 - amount) * 100}% 0)`);
      });
      ruleScale(state.manual || !pinEnabled ? 1 : clamp((progression.value - 0.55) / 0.2));
      frameY(pinEnabled ? -18 * clamp((progression.value - 0.8) / 0.2) : 0);
    };
    let lastStage = null;
    const timeline = gsap.timeline({ scrollTrigger: {
      id: 'landing-ledger', trigger: '.lp-ledger-pin',
      start: () => `top top+=${header.offsetHeight + 16}`,
      end: () => `+=${window.innerHeight}`, pin: true, scrub: 0.35, invalidateOnRefresh: true,
      onRefresh(self) {
        pinEnabled = ledgerFitsViewport();
        if (!pinEnabled) self.disable(true);
        if (paintLedgerMotion) paintLedgerMotion();
      }
    }}).to(progression, { value: 1, duration: 1, ease: 'none', onUpdate() {
      const next = progression.value < 0.35 ? 'utang' : progression.value < 0.55 ? 'bayad' : 'balance';
      if (next !== lastStage) {
        lastStage = next;
        if (!state.manual) renderLedger(next, { animate: true });
      }
      if (paintLedgerMotion) paintLedgerMotion();
    }});
    paintLedgerMotion();
    let resizeFrame;
    function recheckPin() {
      cancelAnimationFrame(resizeFrame);
      resizeFrame = requestAnimationFrame(() => {
        pinEnabled = ledgerFitsViewport();
        const trigger = timeline.scrollTrigger;
        if (pinEnabled && !trigger.enabled) trigger.enable(false, true);
        else if (!pinEnabled && trigger.enabled) trigger.disable(true);
        if (paintLedgerMotion) paintLedgerMotion();
      });
    }
    window.addEventListener('resize', recheckPin);
    return () => {
      window.removeEventListener('resize', recheckPin);
      cancelAnimationFrame(resizeFrame);
      paintLedgerMotion = null;
      gsap.set([...purchases, rule, scene], { clearProps: 'opacity,transform,clipPath' });
    };
  }

  function setupStock(conditions) {
    const { gsap } = window;
    revealHeading(root.querySelector('#stock-title'));
    const backdrop = root.querySelector('.lp-stock-backdrop');
    const stage = root.querySelector('.lp-stock-stage');
    gsap.timeline({ scrollTrigger: {
      id: 'landing-stock-backdrop', trigger: stage, start: 'top 88%', end: 'bottom 14%',
      scrub: 0.35, invalidateOnRefresh: true
    }}).fromTo(backdrop, { scaleX: 1 }, { scaleX: () => window.innerWidth / stage.offsetWidth, duration: 0.28, ease: 'none' })
      .to(backdrop, { scaleX: () => window.innerWidth / stage.offsetWidth, duration: 0.44, ease: 'none' })
      .to(backdrop, { scaleX: 1, duration: 0.28, ease: 'none' });
    gsap.timeline({ scrollTrigger: { id: 'landing-stock-assembly', trigger: '.lp-stock-toolbar', start: 'top 90%', once: true }, defaults: { ease: 'ledger-out' } })
      .from('.lp-stock-toolbar', { y: 12, opacity: 0, duration: 0.5 })
      .from('.lp-shelf-art img', { y: conditions.desktop ? 28 : 18, rotation: index => index % 2 ? 6 : -6, opacity: 0, duration: 0.7, stagger: 0.09 }, 0.15)
      .from('.lp-shelf-rule', { scaleX: 0, transformOrigin: 'left', duration: 0.6, stagger: 0.09 }, 0.15)
      .from('.lp-expired-art', { x: -12, opacity: 0, duration: 0.5 }, 0.4);
  }

  function setupDaily() {
    const { gsap } = window;
    revealHeading(root.querySelector('#daily-title'));
    const timeline = gsap.timeline({ scrollTrigger: { id: 'landing-daily', trigger: '.lp-day-scene', start: 'top 86%', once: true }, defaults: { ease: 'ledger-out' } });
    timeline.from('.lp-tape', { clipPath: 'inset(0 0 100% 0)', duration: 0.85, ease: 'ledger-move' }, 0)
      .from('.lp-tape-row', { y: 12, opacity: 0, duration: 0.45, stagger: 0.08 }, 0.18)
      .from('.lp-day-total', { y: 16, opacity: 0, duration: 0.6, stagger: 0.12 }, 0.55)
      .from('.lp-day-settlement', { y: 24, opacity: 0, duration: 0.6 }, 1);
    if (window.DrawSVGPlugin) timeline.fromTo('.lp-flow-lines path', { drawSVG: '0%' }, {
      drawSVG: '100%', duration: 0.85, stagger: 0.15, ease: 'ledger-move',
      onComplete: () => gsap.set('.lp-flow-lines path', { clearProps: 'strokeDashoffset,strokeDasharray' })
    }, 0.7);
  }

  function setupClosing() {
    const { gsap } = window;
    revealHeading(root.querySelector('#faq-title'));
    gsap.from('.lp-faq-list', { y: 12, opacity: 0, duration: 0.5, ease: 'ledger-out', scrollTrigger: { id: 'landing-faq', trigger: '.lp-faq-list', start: 'top 90%', once: true } });
    revealHeading(root.querySelector('#closing-title'));
    gsap.timeline({ scrollTrigger: { id: 'landing-closing', trigger: '.lp-closing-inner', start: 'top 90%', once: true }, defaults: { ease: 'ledger-out' } })
      .from('.lp-closing-mark', { x: 28, rotation: -8, opacity: 0, duration: 0.8 })
      .from('.lp-closing-actions', { y: 12, opacity: 0, duration: 0.55 }, 0.2);
  }

  function revealFocusedControl(event) {
    if (!gsapReady) return;
    // Keyboard focus takes precedence over any entrance hiding a live control.
    const scenes = [
      ['.lp-hero-actions', 'landing-hero-intro'],
      ['#ledger-demo', 'landing-ledger-entry'],
      ['.lp-stock-controls', 'landing-stock-assembly'],
      ['#faq', 'landing-faq'],
      ['.lp-closing-actions', 'landing-closing']
    ];
    for (const [selector, id] of scenes) {
      if (!event.target.closest(selector)) continue;
      const animation = window.ScrollTrigger.getById(id)?.animation || window.gsap.getById(id);
      if (animation) animation.progress(1);
    }
  }

  function buildMotion() {
    const { gsap, ScrollTrigger } = window;
    if (!gsap || !ScrollTrigger) return;
    gsap.registerPlugin(ScrollTrigger);
    for (const name of ['SplitText', 'Flip', 'DrawSVGPlugin', 'CustomEase']) {
      if (window[name]) gsap.registerPlugin(window[name]);
    }
    const styles = getComputedStyle(root);
    if (window.CustomEase) {
      const bezier = token => styles.getPropertyValue(token).trim().replace('cubic-bezier(', '').replace(')', '');
      window.CustomEase.create('ledger-out', bezier('--ease-out'));
      window.CustomEase.create('ledger-move', bezier('--ease-in-out'));
    } else {
      gsap.registerEase('ledger-out', gsap.parseEase('power3.out'));
      gsap.registerEase('ledger-move', gsap.parseEase('power3.inOut'));
    }
    gsapReady = true;
    media = gsap.matchMedia();
    media.add({ desktop, fine: finePointer, reduce: '(prefers-reduced-motion: reduce)' }, context => {
      const conditions = context.conditions;
      root.dataset.motion = conditions.reduce ? 'reduced' : 'full';
      if (conditions.reduce) {
        renderLedger(state.stage);
        return;
      }
      const cleanups = [];
      setupHero();
      cleanups.push(setupHandoff(conditions));
      cleanups.push(setupLedger(conditions));
      setupStock(conditions);
      setupDaily();
      setupClosing();
      if (conditions.fine) {
        root.querySelectorAll('[data-magnetic]').forEach(button => {
          const content = button.firstElementChild;
          const x = gsap.quickTo(content, 'x', { duration: 0.2, ease: 'ledger-out' });
          const y = gsap.quickTo(content, 'y', { duration: 0.2, ease: 'ledger-out' });
          function move(event) {
            const bounds = button.getBoundingClientRect();
            x(gsap.utils.clamp(-4, 4, (event.clientX - bounds.left - bounds.width / 2) * 0.08));
            y(gsap.utils.clamp(-4, 4, (event.clientY - bounds.top - bounds.height / 2) * 0.08));
          }
          function leave() { x(0); y(0); }
          button.addEventListener('pointermove', move);
          button.addEventListener('pointerleave', leave);
          button.addEventListener('blur', leave);
          cleanups.push(() => {
            button.removeEventListener('pointermove', move);
            button.removeEventListener('pointerleave', leave);
            button.removeEventListener('blur', leave);
            gsap.killTweensOf(content);
            gsap.set(content, { clearProps: 'transform' });
          });
        });
      }
      if (conditions.desktop && conditions.fine && window.Lenis) {
        lenis = new window.Lenis({ autoRaf: false, lerp: 0.1, smoothWheel: true, syncTouch: false });
        lenis.on('scroll', ScrollTrigger.update);
        lenisTick = time => lenis.raf(time * 1000);
        gsap.ticker.add(lenisTick);
        gsap.ticker.lagSmoothing(0);
      }
      scheduleRefresh();
      return () => {
        cleanups.forEach(cleanup => cleanup());
        stopSmoothScroll();
        if (flipAnimation) { flipAnimation.progress(1).kill(); flipAnimation = null; }
        clearLedgerMotion();
      };
    });
  }

  function anchorTarget(hash) {
    if (!hash) return null;
    try { return document.getElementById(decodeURIComponent(hash.slice(1))); }
    catch { return null; }
  }

  function scrollToTarget(target, focus, smooth = false) {
    const complete = () => {
      if (!focus) return;
      if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
      target.focus({ preventScroll: true });
    };
    const offset = header.offsetHeight + 24;
    const destination = target.getBoundingClientRect().top + window.scrollY - offset;
    // Numeric targets avoid applying CSS scroll-margin/padding a second time.
    if (lenis) lenis.scrollTo(destination, { duration: 0.65, immediate: !smooth, onComplete: complete });
    else { window.scrollTo({ top: destination, behavior: 'instant' }); complete(); }
  }

  function navigateToAnchor(event) {
    const anchor = event.target.closest('a[href^="#"]');
    if (!anchor || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = anchorTarget(anchor.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    const hash = anchor.getAttribute('href');
    if (window.location.hash !== hash) history.pushState(null, '', hash);
    scrollToTarget(target, true, true);
  }

  function suspend() {
    if (suspended) return;
    suspended = true;
    controller.abort();
    if (observer) observer.disconnect();
    cancelAnimationFrame(refreshFrame);
    if (media) media.revert();
    media = null;
    stopSmoothScroll();
    gsapReady = false;
    delete root.dataset.motionReady;
  }

  function start(restored = false) {
    if (!suspended) return;
    suspended = false;
    controller = new AbortController();
    const options = { signal: controller.signal };
    stageButtons.forEach(button => button.addEventListener('click', () => renderLedger(button.dataset.stage, { manual: true, animate: true, announce: true }), options));
    recordButton.addEventListener('click', () => {
      if (stageData[state.stage].paid) return;
      renderLedger('bayad', { manual: true, animate: true, announce: true });
    }, options);
    root.querySelector('#reset-ledger').addEventListener('click', () => {
      state.manual = false;
      renderLedger('utang', { announce: true });
    }, options);
    root.querySelectorAll('[data-stock-order]').forEach(button => button.addEventListener('click', () => sortStock(button.dataset.stockOrder), options));
    root.addEventListener('click', navigateToAnchor, options);
    root.addEventListener('focusin', revealFocusedControl, options);
    window.addEventListener('popstate', () => { pendingHashAlignment = Boolean(window.location.hash); scheduleRefresh(); }, options);
    reduce.addEventListener('change', () => renderLedger(state.stage), options);
    root.querySelectorAll('details').forEach(details => details.addEventListener('toggle', scheduleRefresh, options));
    document.addEventListener('visibilitychange', () => {
      if (!gsapReady) return;
      if (document.hidden) clearLedgerMotion();
      else scheduleRefresh();
    }, options);
    root.querySelector('.lp-preview-image-wrap img').addEventListener('load', scheduleRefresh, options);
    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          root.querySelectorAll('.lp-nav a').forEach(anchor => {
            if (anchor.hash === `#${entry.target.id}`) anchor.setAttribute('aria-current', 'location');
            else anchor.removeAttribute('aria-current');
          });
        });
      }, { rootMargin: '-15% 0px -65% 0px', threshold: 0 });
      root.querySelectorAll('.lp-hero,#ledger-demo,#inventory-story,#daily-overview,#faq,.lp-closing').forEach(section => observer.observe(section));
    }
    renderLedger(state.stage);
    sortStock(state.order, false);
    root.querySelectorAll('.lp-stage-controls,.lp-ledger-actions,.lp-stock-controls').forEach(element => { element.hidden = false; });
    try {
      buildMotion();
    } catch (error) {
      // The page remains usable even if an animation plugin fails to initialize.
      if (media) media.revert();
      media = null;
      stopSmoothScroll();
      gsapReady = false;
      root.dataset.motion = 'fallback';
      console.warn('Landing motion unavailable; using the accessible static presentation.', error);
    }
    root.dataset.motionReady = 'true';
    if (!restored) pendingHashAlignment = Boolean(window.location.hash);
    if (document.fonts) document.fonts.ready.then(() => {
      if (!restored) pendingHashAlignment = Boolean(window.location.hash);
      scheduleRefresh();
    });
    scheduleRefresh();
  }

  window.addEventListener('pagehide', suspend);
  window.addEventListener('pageshow', event => { if (event.persisted) { start(true); scheduleRefresh(); } });
  start();
})();
