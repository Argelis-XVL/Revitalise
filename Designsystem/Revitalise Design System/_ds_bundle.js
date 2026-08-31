/* @ds-bundle: {"format":4,"namespace":"RevitaliseDesignSystem_a4dff3","components":[{"name":"Accordion","sourcePath":"components/content/Accordion.jsx"},{"name":"Badge","sourcePath":"components/content/Badge.jsx"},{"name":"Card","sourcePath":"components/content/Card.jsx"},{"name":"StatTile","sourcePath":"components/content/StatTile.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"CookieBanner","sourcePath":"components/feedback/CookieBanner.jsx"},{"name":"Notice","sourcePath":"components/feedback/Notice.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"NewsletterForm","sourcePath":"components/forms/NewsletterForm.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Footer","sourcePath":"components/navigation/Footer.jsx"},{"name":"Navbar","sourcePath":"components/navigation/Navbar.jsx"}],"sourceHashes":{"components/content/Accordion.jsx":"a49836e7796d","components/content/Badge.jsx":"5e9611c00072","components/content/Card.jsx":"62f7f21685cc","components/content/StatTile.jsx":"32f8daba5c8f","components/core/Button.jsx":"e17b3a9ab274","components/feedback/CookieBanner.jsx":"e8e42d40f059","components/feedback/Notice.jsx":"e57e0adbd9ca","components/forms/Checkbox.jsx":"24f0cbd9acee","components/forms/Input.jsx":"86be5d8808a8","components/forms/NewsletterForm.jsx":"76757c7a3c03","components/forms/Radio.jsx":"4e51c3b2d9e1","components/navigation/Footer.jsx":"58f37fd8fc79","components/navigation/Navbar.jsx":"d03d34522afd","ui_kits/marketing-site/FaqScreen.jsx":"c180d69d4bba","ui_kits/marketing-site/FundingScreen.jsx":"87165c51f4f1","ui_kits/marketing-site/HomeScreen.jsx":"bac819242a57","ui_kits/marketing-site/MarketingSiteApp.jsx":"8e65df5e0888","ui_kits/trustee-review-portal/AppFrame.jsx":"0c12efd5f41e","ui_kits/trustee-review-portal/ApplicationDetail.jsx":"1be45d52a540","ui_kits/trustee-review-portal/ApplicationsList.jsx":"48cf386c2f3b","ui_kits/trustee-review-portal/RoundOverview.jsx":"33a9808783a8","ui_kits/trustee-review-portal/TrusteePortalApp.jsx":"2205c8712676"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.RevitaliseDesignSystem_a4dff3 = window.RevitaliseDesignSystem_a4dff3 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/content/Accordion.jsx
try { (() => {
const {
  useState
} = React;
function Accordion({
  items = []
}) {
  const [open, setOpen] = useState(null);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)',
      fontFamily: 'var(--font-body)',
      maxWidth: '720px'
    }
  }, items.map((item, i) => /*#__PURE__*/React.createElement("div", {
    key: i
  }, /*#__PURE__*/React.createElement("button", {
    onClick: () => setOpen(open === i ? null : i),
    style: {
      width: '100%',
      textAlign: 'left',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      background: 'var(--surface-muted)',
      border: 'none',
      borderRadius: 'var(--radius-sm)',
      padding: 'var(--space-4) var(--space-5)',
      fontSize: 'var(--text-base)',
      color: 'var(--text-heading)',
      cursor: 'pointer',
      fontFamily: 'inherit',
      fontWeight: 'var(--weight-regular)'
    }
  }, item.question, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--brand-primary)',
      fontSize: '18px',
      transform: open === i ? 'rotate(90deg)' : 'none',
      transition: 'transform var(--duration-base) var(--ease-standard)'
    }
  }, "\u203A")), open === i && /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-4) var(--space-5)',
      color: 'var(--text-body)'
    }
  }, item.answer))));
}
Object.assign(__ds_scope, { Accordion });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Accordion.jsx", error: String((e && e.message) || e) }); }

// components/content/Badge.jsx
try { (() => {
const GLYPHS = {
  facebook: 'M13.5 9H15V6h-1.5C11.6 6 10.5 7.1 10.5 8.6V10H9v2.5h1.5V18h2.5v-5.5H15L15.5 10h-2v-1c0-.55.05-1 1-1z',
  instagram: 'M12 8.5A3.5 3.5 0 1 0 12 15.5 3.5 3.5 0 1 0 12 8.5zM12 10a2 2 0 1 1 0 4 2 2 0 1 1 0-4zM16.5 6.5a1 1 0 1 1 0 2 1 1 0 1 1 0-2zM8 6h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2z',
  linkedin: 'M7 9h2.2v8H7V9zm1.1-3.4A1.3 1.3 0 1 1 8.1 8.2 1.3 1.3 0 1 1 8.1 5.6zM11 9h2.1v1.1h.03c.29-.55 1-1.13 2.07-1.13 2.22 0 2.63 1.46 2.63 3.36V17h-2.2v-3.36c0-.8-.02-1.84-1.12-1.84-1.12 0-1.3.88-1.3 1.78V17H11V9z'
};
function Badge({
  network = 'facebook',
  size = 40
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      width: size,
      height: size,
      borderRadius: 'var(--radius-circle)',
      background: 'var(--brand-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement("svg", {
    width: size * 0.55,
    height: size * 0.55,
    viewBox: "0 0 24 24",
    fill: "#fff"
  }, /*#__PURE__*/React.createElement("path", {
    d: GLYPHS[network]
  })));
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Badge.jsx", error: String((e && e.message) || e) }); }

// components/content/Card.jsx
try { (() => {
function Card({
  image,
  title,
  children,
  footer
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-card)',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--border-default)',
      boxShadow: 'var(--shadow-card)',
      overflow: 'hidden',
      fontFamily: 'var(--font-body)'
    }
  }, image && /*#__PURE__*/React.createElement("img", {
    src: image,
    alt: "",
    style: {
      width: '100%',
      height: '160px',
      objectFit: 'cover'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-6)'
    }
  }, title && /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-xl)',
      marginBottom: 'var(--space-2)'
    }
  }, title), /*#__PURE__*/React.createElement("div", {
    style: {
      color: 'var(--text-body)'
    }
  }, children), footer && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-4)'
    }
  }, footer)));
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Card.jsx", error: String((e && e.message) || e) }); }

// components/content/StatTile.jsx
try { (() => {
function StatTile({
  label,
  value,
  sublabel
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-4) var(--space-5)',
      fontFamily: 'var(--font-body)',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--text-xs)',
      fontWeight: 'var(--weight-semibold)',
      color: 'var(--text-muted)',
      textTransform: 'none'
    }
  }, label, sublabel && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      fontWeight: 400
    }
  }, sublabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-2xl)',
      fontWeight: 700,
      color: 'var(--text-heading)',
      marginTop: 'var(--space-1)'
    }
  }, value));
}
Object.assign(__ds_scope, { StatTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/StatTile.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Button({
  variant = 'primary',
  size = 'md',
  children,
  disabled,
  icon,
  ...rest
}) {
  const pad = size === 'sm' ? '10px 20px' : size === 'lg' ? '16px 36px' : '13px 28px';
  const fontSize = size === 'sm' ? 'var(--text-sm)' : 'var(--text-base)';
  const base = {
    fontFamily: 'var(--font-body)',
    fontWeight: 'var(--weight-bold)',
    fontSize,
    padding: pad,
    borderRadius: 'var(--radius-pill)',
    border: '2px solid transparent',
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'background var(--duration-base) var(--ease-standard), color var(--duration-base) var(--ease-standard)'
  };
  const styles = {
    primary: {
      background: 'var(--brand-primary)',
      color: 'var(--text-on-brand)'
    },
    secondary: {
      background: 'transparent',
      color: 'var(--brand-primary)',
      border: '2px solid var(--brand-primary)'
    },
    ghost: {
      background: 'transparent',
      color: 'var(--brand-primary)',
      textDecoration: 'underline',
      padding: '4px 2px',
      borderRadius: 0
    }
  };
  return /*#__PURE__*/React.createElement("button", _extends({
    style: {
      ...base,
      ...styles[variant]
    },
    disabled: disabled
  }, rest), icon, children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/feedback/CookieBanner.jsx
try { (() => {
function CookieBanner() {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: '#fff',
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-lg)',
      padding: 'var(--space-6)',
      maxWidth: '360px',
      fontFamily: 'var(--font-body)'
    }
  }, /*#__PURE__*/React.createElement("h4", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-2)'
    }
  }, "We value your privacy"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      fontSize: 'var(--text-sm)',
      marginTop: 0
    }
  }, "We use cookies to enhance your browsing experience. By clicking \"Accept All\", you consent to our use of cookies."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-2)',
      marginTop: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "secondary",
    size: "sm"
  }, "Customise"), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "secondary",
    size: "sm"
  }, "Reject All"), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "primary",
    size: "sm"
  }, "Accept All")));
}
Object.assign(__ds_scope, { CookieBanner });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/CookieBanner.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Notice.jsx
try { (() => {
const TONES = {
  muted: {
    bg: 'var(--surface-muted)',
    fg: 'var(--text-body)',
    title: 'var(--text-heading)'
  },
  info: {
    bg: 'var(--pink-50)',
    fg: 'var(--ink-700)',
    title: 'var(--pink-700)'
  },
  warning: {
    bg: '#fdf5e6',
    fg: 'var(--ink-700)',
    title: 'var(--warning)'
  }
};
function Notice({
  tone = 'muted',
  title,
  children
}) {
  const t = TONES[tone] || TONES.muted;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: t.bg,
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-5) var(--space-6)',
      fontFamily: 'var(--font-body)'
    }
  }, title && /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 'var(--weight-bold)',
      color: t.title,
      marginBottom: 'var(--space-2)',
      fontSize: 'var(--text-base)'
    }
  }, title), /*#__PURE__*/React.createElement("div", {
    style: {
      color: t.fg,
      fontSize: 'var(--text-sm)',
      lineHeight: 'var(--leading-normal)'
    }
  }, children));
}
Object.assign(__ds_scope, { Notice });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Notice.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
function Checkbox({
  label,
  checked,
  onChange
}) {
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      color: 'var(--text-body)',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: checked,
    onChange: onChange,
    style: {
      width: '18px',
      height: '18px',
      accentColor: 'var(--brand-primary)'
    }
  }), label);
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Input({
  label,
  placeholder,
  required,
  type = 'text',
  ...rest
}) {
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-sm)',
      color: 'var(--text-heading)'
    }
  }, label && /*#__PURE__*/React.createElement("span", null, label, required && '*'), /*#__PURE__*/React.createElement("input", _extends({
    type: type,
    placeholder: placeholder,
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      padding: '12px 14px',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-default)',
      color: 'var(--text-body)',
      outline: 'none'
    }
  }, rest)));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/NewsletterForm.jsx
try { (() => {
function NewsletterForm() {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: '#fff',
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-8)',
      maxWidth: '420px',
      fontFamily: 'var(--font-body)'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-xl)',
      marginBottom: 'var(--space-2)'
    }
  }, "Sign Up For Revitalise E-News"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      marginTop: 0,
      marginBottom: 'var(--space-6)'
    }
  }, "Be the first to know all the latest from Revitalise! Join our online community today."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-4)',
      marginBottom: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Input, {
    label: "First name",
    required: true
  }), /*#__PURE__*/React.createElement(__ds_scope.Input, {
    label: "Last name",
    required: true
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Input, {
    label: "Your email",
    required: true,
    type: "email"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-sm)',
      padding: 'var(--space-4)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)',
      marginBottom: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--text-sm)',
      color: 'var(--text-muted)'
    }
  }, "I am interested in the following:"), /*#__PURE__*/React.createElement(__ds_scope.Checkbox, {
    label: "Grants"
  }), /*#__PURE__*/React.createElement(__ds_scope.Checkbox, {
    label: "Fundraising"
  })), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "primary"
  }, "Sign me up!"));
}
Object.assign(__ds_scope, { NewsletterForm });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/NewsletterForm.jsx", error: String((e && e.message) || e) }); }

// components/forms/Radio.jsx
try { (() => {
function Radio({
  label,
  checked,
  onChange,
  name
}) {
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      color: 'var(--text-body)',
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "radio",
    name: name,
    checked: checked,
    onChange: onChange,
    style: {
      width: '18px',
      height: '18px',
      accentColor: 'var(--brand-primary)'
    }
  }), label);
}
Object.assign(__ds_scope, { Radio });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Radio.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Footer.jsx
try { (() => {
function Footer() {
  return /*#__PURE__*/React.createElement("footer", {
    style: {
      background: 'var(--surface-muted)',
      padding: 'var(--space-12) var(--space-6)',
      fontFamily: 'var(--font-body)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr 1.4fr',
      gap: 'var(--space-8)',
      maxWidth: 'var(--container-max)',
      margin: '0 auto'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h4", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-3)'
    }
  }, "Explore"), ['Home', 'About Us', 'What We Fund', 'Support Us', 'Case Studies', 'Contact Us', 'FAQs', 'Donate', 'Apply For Funding'].map(l => /*#__PURE__*/React.createElement("div", {
    key: l,
    style: {
      padding: 'var(--space-2) 0',
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#"
  }, l)))), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h4", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-3)'
    }
  }, "Legal"), ['Privacy Policy', 'Cookie Policy'].map(l => /*#__PURE__*/React.createElement("div", {
    key: l,
    style: {
      padding: 'var(--space-2) 0',
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#"
  }, l)))), /*#__PURE__*/React.createElement(__ds_scope.NewsletterForm, null)), /*#__PURE__*/React.createElement("p", {
    style: {
      textAlign: 'center',
      color: 'var(--text-muted)',
      fontSize: 'var(--text-xs)',
      marginTop: 'var(--space-10)'
    }
  }, "\xA9 Copyright Revitalise Respite Holidays 2026. Registered charity number 295072. Company number 2044219."));
}
Object.assign(__ds_scope, { Footer });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Footer.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Navbar.jsx
try { (() => {
const NAV = ['Home', 'About Us', 'What We Fund', 'Support Us', 'Case Studies', 'Contact Us'];
function Navbar() {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-body)',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 'var(--space-2)',
      padding: 'var(--space-2) var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Badge, {
    network: "facebook",
    size: 28
  }), /*#__PURE__*/React.createElement(__ds_scope.Badge, {
    network: "instagram",
    size: 28
  }), /*#__PURE__*/React.createElement(__ds_scope.Badge, {
    network: "linkedin",
    size: 28
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 'var(--space-4) var(--space-6)',
      borderTop: '1px solid var(--border-default)',
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/revitalise-logo.png",
    alt: "Revitalise",
    style: {
      height: '36px'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "primary",
    size: "sm"
  }, "Apply Now"), /*#__PURE__*/React.createElement(__ds_scope.Button, {
    variant: "primary",
    size: "sm"
  }, "Donate Today"))), /*#__PURE__*/React.createElement("nav", {
    style: {
      display: 'flex',
      gap: 'var(--space-6)',
      padding: 'var(--space-3) var(--space-6)',
      fontSize: 'var(--text-sm)',
      fontWeight: 'var(--weight-semibold)'
    }
  }, NAV.map(item => /*#__PURE__*/React.createElement("a", {
    key: item,
    href: "#",
    style: {
      color: 'var(--text-heading)',
      textDecoration: 'underline'
    }
  }, item))));
}
Object.assign(__ds_scope, { Navbar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Navbar.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing-site/FaqScreen.jsx
try { (() => {
const {
  Accordion
} = window.RevitaliseDesignSystem_a4dff3;
const FAQS = [{
  question: 'Who is eligible for these grants?',
  answer: 'Any disabled adult or family carer over the age of 18 can apply for a grant towards a break or experience that would make a meaningful difference to them.'
}, {
  question: 'When do you open for applications?',
  answer: 'Applications are open year-round and each month we have a maximum amount of grants we can distribute.'
}, {
  question: 'How can I apply?',
  answer: 'Online, via email, or by paper application — quarterly phone application windows are also available.'
}, {
  question: 'Who makes the decision on who gets funding?',
  answer: 'Applications are reviewed and approved by our Trustees on a monthly basis.'
}, {
  question: 'Do I need to have booked my holiday before applying?',
  answer: 'No — you can apply first, and we pay the provider directly once your grant is approved.'
}];
function FaqScreen() {
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      height: '220px'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/photography/guests-icecream.jpeg",
    style: {
      width: '100%',
      height: '100%',
      objectFit: 'cover',
      display: 'block'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      left: 0,
      top: '50%',
      transform: 'translateY(-50%)',
      background: 'var(--brand-primary)',
      padding: 'var(--space-8) var(--space-10)'
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      color: '#fff',
      fontSize: 'var(--text-3xl)'
    }
  }, "Frequently Asked Questions"))), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-16) var(--space-6)',
      display: 'flex',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement(Accordion, {
    items: FAQS
  })));
}
window.FaqScreen = FaqScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing-site/FaqScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing-site/FundingScreen.jsx
try { (() => {
const {
  Button
} = window.RevitaliseDesignSystem_a4dff3;
function FundingScreen() {
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--surface-band)',
      textAlign: 'center',
      padding: 'var(--space-20) var(--space-6)',
      fontFamily: 'var(--font-body)'
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-3xl)',
      marginBottom: 'var(--space-4)'
    }
  }, "Receive Funding"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      fontSize: 'var(--text-lg)',
      maxWidth: '560px',
      margin: '0 auto var(--space-8)'
    }
  }, "Applications are open year-round and each month we have a maximum amount of grants we can distribute."), /*#__PURE__*/React.createElement(Button, {
    variant: "primary"
  }, "Apply Now")), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: '900px',
      margin: '0 auto',
      padding: 'var(--space-16) var(--space-6)',
      fontFamily: 'var(--font-body)'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-2xl)',
      marginBottom: 'var(--space-6)'
    }
  }, "How much we fund"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--space-8)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-3xl)',
      color: 'var(--brand-primary)'
    }
  }, "\xA3500"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)'
    }
  }, "per person, for holidays and respite breaks")), /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--space-8)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-3xl)',
      color: 'var(--brand-primary)'
    }
  }, "\xA3100"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)'
    }
  }, "per person, for day activities")))));
}
window.FundingScreen = FundingScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing-site/FundingScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing-site/HomeScreen.jsx
try { (() => {
const {
  Button
} = window.RevitaliseDesignSystem_a4dff3;
function HomeScreen() {
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/photography/guests-group-garden.jpeg",
    style: {
      width: '100%',
      height: '440px',
      objectFit: 'cover',
      display: 'block'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      left: 0,
      bottom: '48px',
      background: 'var(--brand-primary)',
      padding: 'var(--space-10)',
      maxWidth: '520px'
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      color: '#fff',
      fontSize: 'var(--text-3xl)',
      marginBottom: 'var(--space-3)'
    }
  }, "Revitalise"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: '#fff',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-6)'
    }
  }, "Funding vital respite for disabled people & carers."), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    style: {
      background: '#fff',
      color: 'var(--brand-primary)'
    }
  }, "Apply Now"))), /*#__PURE__*/React.createElement("div", {
    style: {
      maxWidth: '900px',
      margin: '0 auto',
      padding: 'var(--space-16) var(--space-6)',
      fontFamily: 'var(--font-body)'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-2xl)',
      marginBottom: 'var(--space-5)'
    }
  }, "Revitalise Is A National Charity Providing Respite Grants To Disabled Adults And Their Family Carers"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      lineHeight: 'var(--leading-normal)',
      fontSize: 'var(--text-lg)'
    }
  }, "For over 60 years, we provided our own respite holidays via specialist respite centres. In 2024, we took the difficult decision to close our centres due to the severe impact of the cost-of-living crisis."), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      lineHeight: 'var(--leading-normal)',
      fontSize: 'var(--text-lg)'
    }
  }, "Today, we continue the legacy of our founder, Joan Brander MBE, by ensuring that disabled people and their carers can have the respite breaks, holidays and life experiences they need.")));
}
window.HomeScreen = HomeScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing-site/HomeScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/marketing-site/MarketingSiteApp.jsx
try { (() => {
const {
  useState
} = React;
const {
  Navbar,
  Footer,
  CookieBanner
} = window.RevitaliseDesignSystem_a4dff3;
const {
  HomeScreen,
  FaqScreen,
  FundingScreen
} = window;
function MarketingSiteApp() {
  const [screen, setScreen] = useState('home');
  const [cookieVisible, setCookieVisible] = useState(true);
  const screens = {
    home: HomeScreen,
    faq: FaqScreen,
    funding: FundingScreen
  };
  const Screen = screens[screen];
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      minHeight: '100vh'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-2)',
      padding: 'var(--space-3) var(--space-6)',
      background: 'var(--ink-900)'
    }
  }, Object.keys(screens).map(k => /*#__PURE__*/React.createElement("button", {
    key: k,
    onClick: () => setScreen(k),
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-sm)',
      fontWeight: 700,
      padding: '6px 14px',
      borderRadius: 'var(--radius-pill)',
      border: 'none',
      cursor: 'pointer',
      background: screen === k ? 'var(--brand-primary)' : '#fff',
      color: screen === k ? '#fff' : 'var(--ink-900)'
    }
  }, k === 'home' ? 'Home' : k === 'faq' ? 'FAQ' : 'Apply For Funding'))), /*#__PURE__*/React.createElement(Navbar, null), /*#__PURE__*/React.createElement(Screen, null), /*#__PURE__*/React.createElement(Footer, null), cookieVisible && /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'fixed',
      left: 'var(--space-6)',
      bottom: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    onClick: () => setCookieVisible(false),
    style: {
      cursor: 'pointer'
    }
  }, /*#__PURE__*/React.createElement(CookieBanner, null))));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(MarketingSiteApp, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/marketing-site/MarketingSiteApp.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/AppFrame.jsx
try { (() => {
const {
  Button
} = window.RevitaliseDesignSystem_a4dff3;
function AppFrame({
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-body)',
      minHeight: '100vh',
      background: '#fff'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 'var(--space-5) var(--space-8)',
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/revitalise-logo-tagline-sans.png",
    alt: "Revitalise",
    style: {
      height: '44px'
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 'var(--text-sm)',
      color: 'var(--text-muted)'
    }
  }, "Signed in as ", /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "svc_grantapplications"))), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 'var(--space-8)',
      maxWidth: '1200px',
      margin: '0 auto'
    }
  }, children));
}
window.AppFrame = AppFrame;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/AppFrame.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/ApplicationDetail.jsx
try { (() => {
const {
  Button,
  Notice,
  Radio
} = window.RevitaliseDesignSystem_a4dff3;
function Section({
  title,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-4)'
    }
  }, title), children);
}
function Field({
  label,
  value
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-4)',
      fontSize: 'var(--text-base)',
      padding: 'var(--space-1) 0'
    }
  }, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)',
      minWidth: '220px'
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-body)'
    }
  }, value));
}
function ApplicationDetail({
  id,
  onBack
}) {
  const [verdict, setVerdict] = React.useState('Approve');
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm",
    onClick: onBack
  }, "Back to the list"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm"
  }, "Print this case")), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-3xl)',
      color: 'var(--text-heading)'
    }
  }, "Application ", id), /*#__PURE__*/React.createElement(Section, {
    title: "Anonymised narrative"
  }, /*#__PURE__*/React.createElement(Notice, {
    tone: "muted",
    title: "Anonymised narrative withheld"
  }, "This narrative has not been released for trustee review yet. Every narrative is withheld until the process owner has checked the anonymisation and released it \u2014 the rest of the case can still be decided from.")), /*#__PURE__*/React.createElement(Section, {
    title: "Circumstance score"
  }, /*#__PURE__*/React.createElement(Field, {
    label: "Score",
    value: "60"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Status",
    value: "Eligible for Panel"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Review round",
    value: "2"
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      fontSize: 'var(--text-sm)',
      marginTop: 'var(--space-3)'
    }
  }, "Circumstance score: 60 out of 60 \xB7 Scored on 2026-08-21 11:32 UTC. Wellbeing subtotal 50 points, life-satisfaction 10 points inverted. Thresholds: knockout at or below 20, borderline 21\u201330, income ceiling \xA325,000.")), /*#__PURE__*/React.createElement(Section, {
    title: "Holiday details"
  }, /*#__PURE__*/React.createElement(Field, {
    label: "Type of break",
    value: "Holiday accommodation (hotel, cottage, caravan, holiday park)"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Preferred dates",
    value: "5 Oct 2026 to 12 Oct 2026"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Break location",
    value: "Seaside cottage, Northumberland"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Total funding requested",
    value: "\xA31,000.00"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Total costs",
    value: "\xA31,000.00"
  })), /*#__PURE__*/React.createElement(Section, {
    title: "Care-support description"
  }, /*#__PURE__*/React.createElement(Field, {
    label: "Applicant type",
    value: "A disabled person"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Hours of support per week",
    value: "10 - 19 hours"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(Notice, {
    tone: "muted",
    title: "Care-support description withheld"
  }, "This description has not been released for trustee review yet \u2014 the rest of the case can still be decided from."))), /*#__PURE__*/React.createElement(Section, {
    title: "Staff recommendation"
  }, /*#__PURE__*/React.createElement(Notice, {
    tone: "muted",
    title: "No staff recommendation recorded"
  }, "No staff recommendation has been written against this application's review record.")), /*#__PURE__*/React.createElement(Section, {
    title: "Your verdict"
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      fontSize: 'var(--text-sm)'
    }
  }, "You are recording the ", /*#__PURE__*/React.createElement("strong", null, "Trustee 1"), " verdict for ", id, "."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)',
      marginBottom: 'var(--space-4)'
    }
  }, ['Approve', 'Defer', 'Reject'].map(v => /*#__PURE__*/React.createElement(Radio, {
    key: v,
    name: "verdict",
    label: v,
    checked: verdict === v,
    onChange: () => setVerdict(v)
  }))), /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      fontSize: 'var(--text-sm)',
      color: 'var(--text-heading)',
      marginBottom: 'var(--space-4)'
    }
  }, "Notes (optional)", /*#__PURE__*/React.createElement("textarea", {
    rows: 3,
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      padding: '12px 14px',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-default)'
    }
  })), /*#__PURE__*/React.createElement(Button, {
    variant: "primary"
  }, "Save verdict")));
}
window.ApplicationDetail = ApplicationDetail;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/ApplicationDetail.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/ApplicationsList.jsx
try { (() => {
const {
  Button,
  Input
} = window.RevitaliseDesignSystem_a4dff3;
const ROWS = [{
  id: 'REV-2026-1057',
  score: '60',
  region: 'North East',
  dates: '5 Oct 2026 to 12 Oct 2026',
  status: 'Eligible for Panel'
}, {
  id: 'REV-2026-1060',
  score: '21',
  region: 'East Midlands',
  dates: '17 Oct 2026 to 19 Oct 2026',
  status: 'Borderline'
}, {
  id: 'REV-2026-1061',
  score: '20',
  region: 'West Midlands',
  dates: '7 Dec 2026 to 14 Dec 2026',
  status: 'Under Review'
}, {
  id: 'REV-2026-1068',
  score: '10',
  region: 'Northern Ireland',
  dates: '5 Oct 2026 to 9 Oct 2026',
  status: 'Auto-reject'
}, {
  id: 'REV-2026-1065',
  score: 'Not scored',
  region: 'South West',
  dates: '9 Nov 2026 to 16 Nov 2026',
  status: 'Eligible for Panel'
}];
function Select({
  label
}) {
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      fontSize: 'var(--text-sm)',
      color: 'var(--text-heading)'
    }
  }, label, /*#__PURE__*/React.createElement("select", {
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      padding: '12px 14px',
      borderRadius: 'var(--radius-sm)',
      border: '1px solid var(--border-default)',
      color: 'var(--text-body)'
    }
  }, /*#__PURE__*/React.createElement("option", null, "All ", label.toLowerCase())));
}
function ApplicationsList({
  onBack,
  onOpenCase
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("a", {
    href: "#",
    onClick: e => {
      e.preventDefault();
      onBack();
    },
    style: {
      fontWeight: 700
    }
  }, "\u2190 Back to the round overview"), /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-3xl)',
      color: 'var(--text-heading)',
      marginTop: 'var(--space-2)'
    }
  }, "Applications under review")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-4)',
      alignItems: 'flex-end'
    }
  }, /*#__PURE__*/React.createElement(Select, {
    label: "Review round"
  }), /*#__PURE__*/React.createElement(Select, {
    label: "Status"
  }), /*#__PURE__*/React.createElement(Select, {
    label: "Region"
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Score from"
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Score to"
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Application reference contains"
  }), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm"
  }, "Clear filters")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm"
  }, "Print this list"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-muted)',
      fontSize: 'var(--text-sm)'
    }
  }, "5 applications under review.")), /*#__PURE__*/React.createElement("table", {
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      fontSize: 'var(--text-base)'
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", {
    style: {
      borderBottom: '2px solid var(--border-strong)'
    }
  }, ['Application', 'Circumstance score', 'Region', 'Preferred dates', 'Status', 'Decision'].map(h => /*#__PURE__*/React.createElement("th", {
    key: h,
    style: {
      textAlign: 'left',
      padding: 'var(--space-3) var(--space-2)',
      fontFamily: 'var(--font-display)',
      color: 'var(--text-heading)'
    }
  }, h)))), /*#__PURE__*/React.createElement("tbody", null, ROWS.map(r => /*#__PURE__*/React.createElement("tr", {
    key: r.id,
    style: {
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("td", {
    style: {
      padding: 'var(--space-3) var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    onClick: e => {
      e.preventDefault();
      onOpenCase(r.id);
    },
    style: {
      fontWeight: 700
    }
  }, r.id)), /*#__PURE__*/React.createElement("td", {
    style: {
      padding: 'var(--space-3) var(--space-2)'
    }
  }, r.score), /*#__PURE__*/React.createElement("td", {
    style: {
      padding: 'var(--space-3) var(--space-2)'
    }
  }, r.region), /*#__PURE__*/React.createElement("td", {
    style: {
      padding: 'var(--space-3) var(--space-2)'
    }
  }, r.dates), /*#__PURE__*/React.createElement("td", {
    style: {
      padding: 'var(--space-3) var(--space-2)'
    }
  }, r.status), /*#__PURE__*/React.createElement("td", {
    style: {
      padding: 'var(--space-3) var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    size: "sm",
    onClick: () => onOpenCase(r.id)
  }, "Record verdict")))))));
}
window.ApplicationsList = ApplicationsList;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/ApplicationsList.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/RoundOverview.jsx
try { (() => {
const {
  Button,
  Notice,
  StatTile
} = window.RevitaliseDesignSystem_a4dff3;
function RoundOverview({
  onOpenList
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-3xl)',
      color: 'var(--text-heading)',
      marginBottom: 'var(--space-2)'
    }
  }, "Round overview \u2014 2"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      fontSize: 'var(--text-base)',
      margin: 0
    }
  }, "This portal shows the one grant round currently open for review. There is no round to choose.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    onClick: onOpenList
  }, "Open the applications list"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Refresh figures")), /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-4)'
    }
  }, "This round"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)',
      fontSize: 'var(--text-base)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "Round"), " \xA0 2"), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "Opened"), " \xA0 2 Aug 2026"), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "Closed"), " \xA0 31 Aug 2026"))), /*#__PURE__*/React.createElement(Notice, {
    tone: "muted",
    title: "Round figures are unavailable"
  }, "The round-statistics flow is not bound to this app. ", /*#__PURE__*/React.createElement("code", null, "pa app add flow --flow-id <id>"), " has not been run, so there is no generated service to call. The flow must exist and be on in the environment first. No figures are shown rather than a partial set. Use Refresh figures to try again \u2014 the applications list is unaffected."), /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--radius-md)',
      padding: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      marginBottom: 'var(--space-1)'
    }
  }, "The round's financial position"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontStyle: 'italic',
      color: 'var(--text-muted)',
      fontSize: 'var(--text-sm)',
      marginTop: 0,
      marginBottom: 'var(--space-5)'
    }
  }, "These figures are entered by hand and are as at 26 Aug 2026."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement(StatTile, {
    label: "Committed or spent to date",
    value: "\xA350,000.00"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "People supported",
    value: "1,000"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "Individuals supported",
    value: "Not recorded"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "People reached by group grants",
    value: "200"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "Suggested maximum spend for this round",
    value: "\xA3550,000.00"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "Monthly disbursement",
    value: "Not recorded"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "Grant-giving capacity (charity-wide)",
    value: "\xA370,000.00"
  }), /*#__PURE__*/React.createElement(StatTile, {
    label: "Remaining legacy fund (charity-wide)",
    value: "\xA3100,000.00"
  }))));
}
window.RoundOverview = RoundOverview;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/RoundOverview.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/TrusteePortalApp.jsx
try { (() => {
const {
  useState
} = React;
function TrusteePortalApp() {
  const [screen, setScreen] = useState('overview');
  const [caseId, setCaseId] = useState(null);
  return /*#__PURE__*/React.createElement(window.AppFrame, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 'var(--space-2)',
      marginBottom: 'var(--space-6)'
    }
  }, ['overview', 'list', 'detail'].map(s => /*#__PURE__*/React.createElement("button", {
    key: s,
    onClick: () => setScreen(s),
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-sm)',
      fontWeight: 700,
      padding: '6px 14px',
      borderRadius: 'var(--radius-pill)',
      border: 'none',
      cursor: 'pointer',
      background: screen === s ? 'var(--brand-primary)' : 'var(--grey-100)',
      color: screen === s ? '#fff' : 'var(--ink-900)'
    }
  }, s === 'overview' ? 'Round overview' : s === 'list' ? 'Applications list' : 'Application detail'))), screen === 'overview' && /*#__PURE__*/React.createElement(window.RoundOverview, {
    onOpenList: () => setScreen('list')
  }), screen === 'list' && /*#__PURE__*/React.createElement(window.ApplicationsList, {
    onBack: () => setScreen('overview'),
    onOpenCase: id => {
      setCaseId(id);
      setScreen('detail');
    }
  }), screen === 'detail' && /*#__PURE__*/React.createElement(window.ApplicationDetail, {
    id: caseId || 'REV-2026-1057',
    onBack: () => setScreen('list')
  }));
}
ReactDOM.createRoot(document.getElementById('root')).render(/*#__PURE__*/React.createElement(TrusteePortalApp, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/TrusteePortalApp.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Accordion = __ds_scope.Accordion;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.StatTile = __ds_scope.StatTile;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.CookieBanner = __ds_scope.CookieBanner;

__ds_ns.Notice = __ds_scope.Notice;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.NewsletterForm = __ds_scope.NewsletterForm;

__ds_ns.Radio = __ds_scope.Radio;

__ds_ns.Footer = __ds_scope.Footer;

__ds_ns.Navbar = __ds_scope.Navbar;

})();
