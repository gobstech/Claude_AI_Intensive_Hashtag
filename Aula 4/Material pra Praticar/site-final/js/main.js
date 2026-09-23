(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isCoarse = window.matchMedia("(pointer: coarse)").matches;
  var hasGSAP = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";

  if (hasGSAP) {
    gsap.registerPlugin(ScrollTrigger);
  }

  /* ---------- smooth scroll (Lenis) ---------- */
  var lenis = null;
  if (!reduceMotion && !isCoarse && typeof window.Lenis !== "undefined") {
    try {
      lenis = new window.Lenis({
        duration: 1.05,
        easing: function (t) { return 1 - Math.pow(1 - t, 3); },
        smoothWheel: true,
        wheelMultiplier: 1,
      });
      if (hasGSAP) {
        lenis.on("scroll", ScrollTrigger.update);
        gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
        gsap.ticker.lagSmoothing(0);
      } else {
        requestAnimationFrame(function raf(time) { lenis.raf(time); requestAnimationFrame(raf); });
      }
    } catch (e) { lenis = null; }
  }

  /* ---------- nav ---------- */
  var nav = document.querySelector(".nav");
  var navToggle = document.querySelector(".nav__toggle");
  var navMobile = document.querySelector(".nav__mobile");

  function onScrollNav() {
    if (window.scrollY > 40) nav.classList.add("is-scrolled");
    else nav.classList.remove("is-scrolled");
  }
  onScrollNav();
  window.addEventListener("scroll", onScrollNav, { passive: true });

  if (navToggle && navMobile) {
    navToggle.addEventListener("click", function () {
      var open = navMobile.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.style.overflow = open ? "hidden" : "";
    });
    navMobile.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        navMobile.classList.remove("is-open");
        document.body.style.overflow = "";
      });
    });
  }

  /* ---------- progress bar ---------- */
  var progressFill = document.querySelector(".progress__fill");
  function onScrollProgress() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var pct = max > 0 ? (window.scrollY / max) * 100 : 0;
    if (progressFill) progressFill.style.width = pct + "%";
  }
  onScrollProgress();
  window.addEventListener("scroll", onScrollProgress, { passive: true });

  /* ---------- generic reveal (IntersectionObserver) ---------- */
  var revealEls = document.querySelectorAll("[data-reveal],[data-reveal-scale]");
  if (revealEls.length) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var delay = entry.target.getAttribute("data-delay") || 0;
            setTimeout(function () { entry.target.classList.add("in-view"); }, Number(delay));
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
    );
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- case media zoom-in on view ---------- */
  var cases = document.querySelectorAll(".case");
  if (cases.length) {
    var ioCase = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            ioCase.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.25 }
    );
    cases.forEach(function (el) { ioCase.observe(el); });
  }

  /* ---------- count-up stats ---------- */
  var stats = document.querySelectorAll("[data-count]");
  if (stats.length) {
    var ioStats = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var target = parseFloat(el.getAttribute("data-count"));
          var decimals = el.getAttribute("data-decimals") ? Number(el.getAttribute("data-decimals")) : 0;
          ioStats.unobserve(el);
          if (reduceMotion) {
            el.textContent = target.toLocaleString("pt-BR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
            return;
          }
          el.textContent = (0).toLocaleString("pt-BR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
          var start = null;
          var duration = 1400;
          function step(ts) {
            if (!start) start = ts;
            var p = Math.min((ts - start) / duration, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            var val = target * eased;
            el.textContent = val.toLocaleString("pt-BR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
            if (p < 1) requestAnimationFrame(step);
            else el.textContent = target.toLocaleString("pt-BR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
          }
          requestAnimationFrame(step);
        });
      },
      { threshold: 0.6 }
    );
    stats.forEach(function (el) { ioStats.observe(el); });
  }

  /* ---------- story sticky text active state ---------- */
  var storyBlocks = document.querySelectorAll(".story__block");
  if (storyBlocks.length) {
    var ioStory = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          entry.target.classList.toggle("is-active", entry.isIntersecting);
        });
      },
      { threshold: 0.5, rootMargin: "-20% 0px -20% 0px" }
    );
    storyBlocks.forEach(function (el) { ioStory.observe(el); });
  }

  /* ---------- hero load-in ---------- */
  window.addEventListener("load", function () {
    document.body.classList.add("is-loaded");
  });

  /* ---------- GSAP scroll-linked effects (desktop only, no reduced motion) ---------- */
  if (hasGSAP && !reduceMotion) {
    // parallax on interlude image
    document.querySelectorAll(".interlude img").forEach(function (img) {
      gsap.to(img, {
        yPercent: 12,
        ease: "none",
        scrollTrigger: {
          trigger: img.closest(".interlude"),
          start: "top bottom",
          end: "bottom top",
          scrub: true,
        },
      });
    });

    // before/after scroll-linked wipe
    var ba = document.querySelector(".ba__after");
    if (ba) {
      gsap.fromTo(
        ba,
        { clipPath: "inset(0 100% 0 0)" },
        {
          clipPath: "inset(0 0% 0 0)",
          ease: "none",
          scrollTrigger: {
            trigger: ".ba__frame",
            start: "top 75%",
            end: "bottom 40%",
            scrub: true,
          },
        }
      );
    }

    ScrollTrigger.matchMedia({
      "(min-width: 960px)": function () {
        // subtle parallax on case images
        document.querySelectorAll(".case__media img").forEach(function (img) {
          gsap.fromTo(
            img,
            { yPercent: -6 },
            {
              yPercent: 6,
              ease: "none",
              scrollTrigger: {
                trigger: img.closest(".case"),
                start: "top bottom",
                end: "bottom top",
                scrub: true,
              },
            }
          );
        });
      },
    });
  }
})();
