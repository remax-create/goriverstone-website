/* Riverstone Homes shared site script.
   1. Remembers how a visitor found the site (first page, outside referrer, ad tags)
      and which page they were on before the form, so every lead says where it came from.
   2. Fills the hidden lead-source fields on the "contact" form right before it sends.
   3. Adds a bar stuck to the bottom of phone screens: Call us + Start your build.

   Include on every page:  <script src="/js/site.js" defer></script>
   Optional: data-topic="A barndominium" preselects that topic on the Start your build link.
   Optional: data-nobar on the script tag hides the phone bar (start and thanks pages). */
(function () {
  var me = document.currentScript || document.querySelector('script[src$="/js/site.js"]');
  var CALL = 'tel:+17703243680';
  var store = (function () { try { var s = window.sessionStorage; s.setItem('_t', '1'); s.removeItem('_t'); return s; } catch (e) { return null; } })();
  var get = function (k) { try { return store ? store.getItem(k) || '' : ''; } catch (e) { return ''; } };
  var set = function (k, v) { try { if (store) store.setItem(k, v); } catch (e) {} };
  var here = function () { return location.pathname + location.search + location.hash; };

  /* ---------- 1. Track the visit ---------- */
  var cameFrom = get('rs_last');            // page they were on just before this one
  if (!get('rs_first')) {
    set('rs_first', here());
    var ref = document.referrer, host = '';
    try { host = ref ? new URL(ref).hostname : ''; } catch (e) {}
    if (host && host !== location.hostname) set('rs_ref', host.replace(/^www\./, ''));
    var q = new URLSearchParams(location.search), tags = [];
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'fbclid', 'gclid'].forEach(function (k) {
      if (q.get(k)) tags.push(k === 'fbclid' ? 'Facebook ad click' : k === 'gclid' ? 'Google ad click' : k.replace('utm_', '') + '=' + q.get(k));
    });
    if (tags.length) set('rs_tags', tags.join(', '));
  }
  // Remember this page (with the blog post #hash) for the next page view
  var remember = function () { set('rs_last', here()); };
  window.addEventListener('pagehide', remember);
  document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('a[href]')) remember(); }, true);

  /* ---------- 2. Fill the hidden lead-source fields ---------- */
  var fill = function (form) {
    if (!form || form.getAttribute('name') !== 'contact') return;
    var page = location.pathname + location.hash;
    var before = cameFrom && cameFrom !== here() ? cameFrom : '';
    var source = 'Form on ' + page + (before ? ' | came from ' + before : '');
    var first = get('rs_first') || page;
    var outside = get('rs_ref') || 'direct or unknown';
    if (get('rs_tags')) outside += ' (' + get('rs_tags') + ')';
    var put = function (n, v) { var i = form.querySelector('input[name="' + n + '"]'); if (i) i.value = v; };
    put('lead-source', source);
    put('first-page', first);
    put('referrer', outside);
  };
  document.addEventListener('submit', function (e) { fill(e.target); }, true);
  document.addEventListener('DOMContentLoaded', function () { fill(document.querySelector('form[name="contact"]')); });

  /* ---------- 3. Phone bar: Call us + Start your build ---------- */
  if (me && me.hasAttribute('data-nobar')) return;
  var topic = (me && me.getAttribute('data-topic')) || 'A building consultation';
  var css = '.rs-mbar{display:none}' +
    '@media (max-width:760px){' +
    '.rs-mbar{display:grid;grid-template-columns:1fr 1.35fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:80;' +
    'padding:10px max(12px,env(safe-area-inset-left,0px)) calc(10px + env(safe-area-inset-bottom,0px)) max(12px,env(safe-area-inset-right,0px));' +
    'background:rgba(27,40,35,.97);box-shadow:0 -6px 20px rgba(0,0,0,.18);transition:transform .25s ease}' +
    '.rs-mbar a{display:flex;align-items:center;justify-content:center;gap:.5rem;min-height:48px;border-radius:2px;text-decoration:none;' +
    'font:600 .82rem/1 "Hanken Grotesk","Helvetica Neue",system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase}' +
    '.rs-mbar .c{color:#f2f0ea;border:1px solid rgba(242,240,234,.4)}' +
    '.rs-mbar .s{color:#fff;background:#9c7a45}' +
    '.rs-mbar svg{width:16px;height:16px;flex:none}' +
    '.rs-mbar.away{transform:translateY(110%)}' +
    'body.has-mbar{padding-bottom:calc(70px + env(safe-area-inset-bottom,0px))}}';
  var phone = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>';
  var arrow = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>';
  var addBar = function () {
    if (document.querySelector('.rs-mbar')) return;
    var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    var bar = document.createElement('nav');
    bar.className = 'rs-mbar'; bar.setAttribute('aria-label', 'Call or start your build');
    bar.innerHTML = '<a class="c" href="' + CALL + '">' + phone + 'Call us</a>' +
      '<a class="s" href="/start.html?topic=' + encodeURIComponent(topic) + '">Start your build' + arrow + '</a>';
    document.body.appendChild(bar);
    document.body.classList.add('has-mbar');
    // Step aside while the visitor is already on a form, so it never covers the fields or the Send button
    var formArea = document.getElementById('contact') || document.querySelector('form.inquiry');
    if ('IntersectionObserver' in window && formArea) {
      new IntersectionObserver(function (es) {
        bar.classList.toggle('away', es[es.length - 1].isIntersecting);
      }, { threshold: 0.05 }).observe(formArea);
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', addBar); else addBar();
})();
