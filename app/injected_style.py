INJECTED_STYLE = r"""
(() => {
  const css = `
    :root {
      --desktop-glass: rgba(12, 14, 18, 0.40);
      --desktop-message-glass: rgba(8, 10, 14, 0.58);
      --desktop-border: rgba(255, 255, 255, 0.16);
      --desktop-shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
    }

    html, body {
      background: transparent !important;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        radial-gradient(circle at top left, rgba(90, 170, 255, 0.14), transparent 30%),
        radial-gradient(circle at bottom right, rgba(110, 255, 210, 0.10), transparent 28%);
      z-index: 0;
    }

    main, nav, aside, header, form, section, article, [class*="panel"], [class*="sidebar"] {
      background-color: transparent !important;
    }

    [class*="bg-token"], [class*="bg-surface"], [class*="bg-\["], .bg-white, .bg-black {
      background-color: transparent !important;
    }

    [data-testid="conversation-turn"],
    [data-message-author-role],
    form,
    nav,
    aside {
      backdrop-filter: blur(18px) saturate(140%);
      -webkit-backdrop-filter: blur(18px) saturate(140%);
      background: var(--desktop-glass) !important;
      border: 1px solid var(--desktop-border) !important;
      box-shadow: var(--desktop-shadow);
      border-radius: 18px !important;
    }

    [data-testid="conversation-turn"],
    [data-message-author-role] {
      background: var(--desktop-message-glass) !important;
      padding: 10px 12px !important;
    }

  `;

  let styleTag = document.getElementById("desktop-glass-style");
  if (!styleTag) {
    styleTag = document.createElement("style");
    styleTag.id = "desktop-glass-style";
    document.head.appendChild(styleTag);
  }
  styleTag.textContent = css;

})();
"""
