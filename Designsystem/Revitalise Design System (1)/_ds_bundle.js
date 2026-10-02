/* @ds-bundle: {"format":4,"namespace":"RevitaliseDesignSystem_a4dff3","components":[{"name":"Accordion","sourcePath":"components/content/Accordion.jsx"},{"name":"Badge","sourcePath":"components/content/Badge.jsx"},{"name":"Card","sourcePath":"components/content/Card.jsx"},{"name":"StatTile","sourcePath":"components/content/StatTile.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"CookieBanner","sourcePath":"components/feedback/CookieBanner.jsx"},{"name":"Notice","sourcePath":"components/feedback/Notice.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"NewsletterForm","sourcePath":"components/forms/NewsletterForm.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Footer","sourcePath":"components/navigation/Footer.jsx"},{"name":"Navbar","sourcePath":"components/navigation/Navbar.jsx"}],"sourceHashes":{"components/content/Accordion.jsx":"a49836e7796d","components/content/Badge.jsx":"5e9611c00072","components/content/Card.jsx":"62f7f21685cc","components/content/StatTile.jsx":"32f8daba5c8f","components/core/Button.jsx":"e17b3a9ab274","components/feedback/CookieBanner.jsx":"e8e42d40f059","components/feedback/Notice.jsx":"e57e0adbd9ca","components/forms/Checkbox.jsx":"24f0cbd9acee","components/forms/Input.jsx":"86be5d8808a8","components/forms/NewsletterForm.jsx":"76757c7a3c03","components/forms/Radio.jsx":"4e51c3b2d9e1","components/navigation/Footer.jsx":"58f37fd8fc79","components/navigation/Navbar.jsx":"d03d34522afd","ui_kits/marketing-site/FaqScreen.jsx":"c180d69d4bba","ui_kits/marketing-site/FundingScreen.jsx":"87165c51f4f1","ui_kits/marketing-site/HomeScreen.jsx":"bac819242a57","ui_kits/marketing-site/MarketingSiteApp.jsx":"8e65df5e0888","ui_kits/trustee-review-portal/AppFrame.jsx":"754d578c3a9e","ui_kits/trustee-review-portal/ApplicationDetail.jsx":"b2d0bac5ed61","ui_kits/trustee-review-portal/ApplicationsList.jsx":"abe299d36e8f","ui_kits/trustee-review-portal/GroupScreens.jsx":"b1a82b71defa","ui_kits/trustee-review-portal/RoundOverview.jsx":"957d4d1b25ef","ui_kits/trustee-review-portal/Shared.jsx":"133ea2ab3504","ui_kits/trustee-review-portal/TrusteePortalApp.jsx":"d56bed9102c6"},"inlinedExternals":[],"unexposedExports":[]} */

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
// Mirrors App.tsx: skip link, header (logo + signed-in sentence), persistent "Screen navigation" bar.
function NavButton({
  selected,
  onClick,
  children
}) {
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-current": selected ? 'page' : undefined,
    onClick: onClick,
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-sm)',
      fontWeight: 700,
      minHeight: '44px',
      padding: '0 18px',
      borderRadius: 'var(--radius-pill)',
      border: 'none',
      cursor: 'pointer',
      background: selected ? 'var(--brand-primary)' : 'transparent',
      color: selected ? '#fff' : 'var(--ink-900)',
      transition: 'background var(--duration-fast) var(--ease-standard)'
    }
  }, children);
}
function AppFrame({
  view,
  setView,
  children
}) {
  const onGroups = view.name === 'groups' || view.name === 'groupDetail';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-body)',
      minHeight: '100vh',
      background: 'var(--grey-50)'
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      position: 'sticky',
      top: 0,
      zIndex: 5,
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-4)',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: 'var(--space-4) clamp(16px, 4vw, 48px)',
      background: 'var(--white)',
      boxShadow: '0 1px 0 rgba(43,43,43,.05), 0 4px 16px rgba(43,43,43,.06)'
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logo/revitalise-logo.png",
    alt: "Revitalise Respite Holidays",
    style: {
      height: '44px',
      width: 'auto'
    }
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      color: 'var(--text-muted)'
    }
  }, "Signed in as ", /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "Emily Sheardown"), ".")), /*#__PURE__*/React.createElement("main", {
    id: "main",
    style: {
      padding: 'var(--space-8) clamp(16px, 4vw, 48px)',
      maxWidth: '1200px',
      margin: '0 auto',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-6)'
    }
  }, /*#__PURE__*/React.createElement("nav", {
    "aria-label": "Screen navigation",
    className: "rv-nav rv-card",
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '4px',
      padding: '6px',
      borderRadius: 'var(--radius-pill)',
      alignSelf: 'flex-start',
      maxWidth: '100%'
    }
  }, /*#__PURE__*/React.createElement(NavButton, {
    selected: view.name === 'landing',
    onClick: () => setView({
      name: 'landing'
    })
  }, "Round overview"), /*#__PURE__*/React.createElement(NavButton, {
    selected: onGroups,
    onClick: () => setView({
      name: 'groups'
    })
  }, "Group applications"), /*#__PURE__*/React.createElement(NavButton, {
    selected: view.name === 'list',
    onClick: () => setView({
      name: 'list'
    })
  }, "Individual applications"), view.name === 'detail' && /*#__PURE__*/React.createElement(NavButton, {
    selected: true,
    onClick: () => {}
  }, "Application detail")), children));
}
window.AppFrame = AppFrame;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/AppFrame.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/ApplicationDetail.jsx
try { (() => {
// Mirrors pages/ApplicationDetailPage.tsx (Revision 15) + CasePanels.tsx + domain/applicationDetailLayout.ts
// (the Trustee Pack's five sections, every row, Pack labels) + VerdictSection.tsx.
// Presentation groups each section's rows by kind (facts, costs, free-text answers, scale answers) for scanning.
const NR = 'Not recorded';
const WITHHELD_NOTE = 'This answer has not been released for trustee review yet.';
const WITHHELD_FULL = 'Every free-text answer is withheld until the process owner has checked its anonymisation and released it, so this is the expected state rather than a fault.';
function SubHeading({
  children
}) {
  return /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      fontWeight: 700,
      letterSpacing: '.02em',
      color: 'var(--ink-700)'
    }
  }, children);
}
function Block({
  heading,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }
  }, heading && /*#__PURE__*/React.createElement(SubHeading, null, heading), children);
}

// Free-text Pack rows (always redacted): the question, then a compact withheld tile.
function Answers({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
      gap: 'var(--space-3)'
    }
  }, items.map(([id, q]) => /*#__PURE__*/React.createElement("div", {
    key: id,
    "data-field": id,
    style: {
      borderRadius: '14px',
      border: '1.5px dashed var(--lavender-200)',
      background: 'linear-gradient(135deg, rgba(237,232,241,.45), rgba(253,241,248,.45))',
      padding: 'var(--space-4) var(--space-5)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontWeight: 700,
      color: 'var(--text-heading)',
      fontSize: 'var(--text-sm)',
      textWrap: 'pretty'
    }
  }, q), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      alignSelf: 'flex-start',
      background: 'var(--white)',
      color: window.RV.purple,
      fontWeight: 700,
      fontSize: '13px',
      borderRadius: '999px',
      padding: '3px 10px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '7px',
      height: '7px',
      borderRadius: '50%',
      background: window.RV.purple
    }
  }), "Withheld until released"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: '13px',
      color: 'var(--ink-700)'
    }
  }, WITHHELD_NOTE))));
}
function CostReceipt({
  lines,
  total,
  after
}) {
  const row = (label, value, strong) => /*#__PURE__*/React.createElement("div", {
    key: label,
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 'var(--space-4)',
      padding: '10px 0',
      borderTop: strong ? '2px solid var(--grey-200)' : '1px solid var(--grey-100)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: strong ? 'var(--text-heading)' : 'var(--ink-700)',
      fontWeight: strong ? 700 : 400
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontVariantNumeric: 'tabular-nums',
      fontWeight: 700,
      color: value === NR ? 'var(--ink-600)' : 'var(--text-heading)',
      fontStyle: value === NR ? 'italic' : 'normal',
      whiteSpace: 'nowrap'
    }
  }, value));
  return /*#__PURE__*/React.createElement("div", {
    style: {
      borderRadius: '14px',
      background: 'var(--grey-50)',
      padding: 'var(--space-2) var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: '-1px'
    }
  }, lines.map(([l, v]) => row(l, v))), row(total[0], total[1], true), after.map(([l, v]) => row(l, v)));
}

// Scale answers (wellbeing): question left, answer pill right.
function AnswerList({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column'
    }
  }, items.map(([id, q, a], i) => /*#__PURE__*/React.createElement("div", {
    key: id,
    "data-field": id,
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: 'var(--space-2) var(--space-4)',
      padding: '12px 0',
      borderTop: i ? '1px solid var(--grey-100)' : 'none'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-body)',
      flex: '1 1 260px'
    }
  }, q), /*#__PURE__*/React.createElement("span", {
    style: {
      background: 'var(--lavender-100)',
      color: window.RV.purple,
      fontWeight: 700,
      fontSize: '13px',
      borderRadius: '999px',
      padding: '4px 12px',
      whiteSpace: 'nowrap'
    }
  }, a))));
}
function ScoreBar({
  id,
  label,
  score
}) {
  return /*#__PURE__*/React.createElement("div", {
    "data-field": id,
    style: {
      borderRadius: '14px',
      background: 'var(--grey-50)',
      padding: 'var(--space-4) var(--space-5)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      gap: 'var(--space-4)',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)'
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-xl)',
      color: 'var(--text-heading)'
    }
  }, score == null ? NR : `${score} / 60`)), /*#__PURE__*/React.createElement("div", {
    style: {
      height: '10px',
      borderRadius: '999px',
      background: 'var(--grey-100)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      height: '100%',
      width: `${(score || 0) / 60 * 100}%`,
      borderRadius: '999px',
      background: `linear-gradient(90deg, ${window.RV.purple}, var(--brand-primary))`
    }
  })));
}
function Scale({
  id,
  question,
  value
}) {
  return /*#__PURE__*/React.createElement("div", {
    "data-field": id,
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-body)'
    }
  }, question), /*#__PURE__*/React.createElement("div", {
    role: "img",
    "aria-label": `Answer: ${value} out of 10`,
    style: {
      display: 'flex',
      gap: '6px',
      flexWrap: 'wrap'
    }
  }, Array.from({
    length: 11
  }, (_, n) => /*#__PURE__*/React.createElement("span", {
    key: n,
    style: {
      width: '34px',
      height: '34px',
      borderRadius: '50%',
      display: 'grid',
      placeItems: 'center',
      fontSize: '13px',
      fontWeight: 700,
      background: n === value ? 'var(--brand-primary)' : 'var(--grey-50)',
      color: n === value ? 'var(--white)' : 'var(--ink-600)',
      border: n === value ? 'none' : '1px solid var(--grey-200)'
    }
  }, n))));
}
function Restricted({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, items.map(([id, q]) => /*#__PURE__*/React.createElement("div", {
    key: id,
    "data-field": id,
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: 'var(--space-2) var(--space-4)',
      borderRadius: '12px',
      border: '1.5px dashed var(--grey-200)',
      padding: '10px var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-heading)',
      fontWeight: 700,
      fontSize: 'var(--text-sm)',
      flex: '1 1 240px'
    }
  }, q), /*#__PURE__*/React.createElement("span", {
    style: {
      background: 'var(--grey-100)',
      color: 'var(--ink-700)',
      fontWeight: 700,
      fontSize: '13px',
      borderRadius: '999px',
      padding: '4px 12px'
    }
  }, "Restricted"))), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: '13px',
      color: 'var(--ink-700)'
    }
  }, "Restricted \u2014 this field is protected by column-level security and is not requested by this app."));
}
function Chips({
  items
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '6px',
      marginTop: '2px'
    }
  }, items.map(c => /*#__PURE__*/React.createElement("span", {
    key: c,
    style: {
      background: 'var(--white)',
      border: '1px solid var(--grey-200)',
      borderRadius: '999px',
      padding: '2px 10px',
      fontSize: '13px',
      fontWeight: 700
    }
  }, c)));
}
function ApplicationDetail({
  application,
  fromGroup,
  onBackToGroup
}) {
  const Button = window.PButton;
  const {
    Panel,
    Definitions,
    PageTitle,
    ActionRow,
    RV
  } = window;
  const [verdict, setVerdict] = React.useState('Approve');
  const a = application;
  const [start = NR, end = NR] = (a.dates || '').split(' to ');
  const exc = a.circ && a.circ !== 'None';
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(PageTitle, null, "Application ", a.ref), /*#__PURE__*/React.createElement(ActionRow, null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Print this case"), fromGroup && /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: onBackToGroup
  }, "Back to group ", fromGroup.code)), /*#__PURE__*/React.createElement(window.HeroBand, {
    badgeLabel: "Score",
    badgeValue: a.score ?? '—',
    eyebrow: "Summary",
    heading: a.score == null ? 'Not scored yet' : `${a.score} out of 60 circumstance points`
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-2)',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement(window.StatusPill, {
    status: a.status
  }), /*#__PURE__*/React.createElement(window.FactChips, {
    items: [['Review round', a.round], ['Application ID', a.ref], ['Are you?', 'A disabled person']]
  })), /*#__PURE__*/React.createElement(window.FactChips, {
    items: [['Start Date', start], ['End Date', end], ['Total requested inc. exceptional funding', exc ? '£1,250.00' : '£1,000.00'], ['Exceptional Funding Amount', exc ? '£250.00' : NR]]
  })), /*#__PURE__*/React.createElement(Panel, {
    eyebrow: "The break",
    eyebrowColor: RV.purple,
    heading: "Application Details"
  }, /*#__PURE__*/React.createElement(Definitions, {
    items: [{
      label: 'Type of Break',
      value: 'Holiday accommodation (hotel, cottage, caravan, holiday park)'
    }, {
      label: 'Location of Activity',
      value: 'Seaside cottage, Northumberland'
    }, {
      label: 'Start Date',
      value: start
    }, {
      label: 'End Date',
      value: end
    }, {
      label: 'Exceptional Circumstance',
      value: exc ? a.circ : NR
    }]
  }), /*#__PURE__*/React.createElement(Block, {
    heading: "Costs"
  }, /*#__PURE__*/React.createElement(CostReceipt, {
    lines: [['Accommodation or Activity Cost', '£850.00'], ['Travel Costs', '£120.00'], ['Other Costs', '£30.00']],
    total: ['Total Estimated Cost', '£1,000.00'],
    after: [['Amount Requesting Revitalise Individual', '£1,000.00'], ['Exceptional Amount Requested', exc ? '£250.00' : NR]]
  })), /*#__PURE__*/React.createElement(Block, {
    heading: "In their words"
  }, /*#__PURE__*/React.createElement(Answers, {
    items: [...(a.circ === 'Other (please specify)' ? [['D11a', 'Other exceptional circumstance']] : []), ['D12', 'Please briefly explain how this break would benefit you'], ['D13', 'Please briefly explain why you’re unable to fund this break yourself?']]
  }))), /*#__PURE__*/React.createElement(Panel, {
    eyebrow: "Who they are",
    eyebrowColor: RV.purple,
    heading: "About Applicant"
  }, /*#__PURE__*/React.createElement(Definitions, {
    items: [{
      label: 'Are you?',
      value: 'A disabled person'
    }, {
      label: 'Do you or the person you support have a disability as defined by the Equality Act 2010?',
      value: 'Yes'
    }, {
      label: 'Please select all conditions or illnesses that apply?',
      value: /*#__PURE__*/React.createElement(Chips, {
        items: ['Physical disability', 'Other (please specify)']
      })
    }, {
      label: 'As a carer, what type of care and support do you personally provide?',
      value: NR
    }, {
      label: 'As a carer, on average how many hours of support do you provide a week?',
      value: NR
    }]
  }), /*#__PURE__*/React.createElement(Block, {
    heading: "In their words"
  }, /*#__PURE__*/React.createElement(Answers, {
    items: [['A3a', 'Other condition notes'], ['A4', 'Brief Confirmation'], ['A6', 'Brief Description of Care Support Received or Provided']]
  }))), /*#__PURE__*/React.createElement(Panel, {
    eyebrow: "How they are doing",
    eyebrowColor: RV.purple,
    heading: "Current Circumstances"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-8)'
    }
  }, /*#__PURE__*/React.createElement(ScoreBar, {
    id: "C1",
    label: "Overall Current Circumstances Score (Out of 60)",
    score: a.score
  }), /*#__PURE__*/React.createElement(Block, {
    heading: "Life satisfaction"
  }, /*#__PURE__*/React.createElement(Scale, {
    id: "C2",
    question: "Overall, how satisfied are you with your life nowadays? (0 being not at all)",
    value: 2
  })), /*#__PURE__*/React.createElement(Block, {
    heading: "In the last 2 weeks\u2026"
  }, /*#__PURE__*/React.createElement(AnswerList, {
    items: [['C3', 'I’ve been feeling optimistic about the future', 'Rarely'], ['C4', 'I’ve been feeling useful', 'Some of the time'], ['C5', 'I’ve been feeling relaxed', 'None of the time'], ['C6', 'I’ve been dealing with problems well', 'Rarely'], ['C7', 'I’ve been thinking clearly', 'Some of the time'], ['C8', 'I’ve been feeling close to other people', 'Rarely'], ['C9', 'I’ve been able to make up my own mind about things', 'Often']]
  })), /*#__PURE__*/React.createElement(Block, {
    heading: "In the last year\u2026"
  }, /*#__PURE__*/React.createElement(AnswerList, {
    items: [['C10', 'Go out and do something you enjoy', 'Disagree'], ['C11', 'Enjoy other people’s company', 'Agree'], ['C12', 'Have a break when you’ve needed one', 'Strongly disagree']]
  })))), /*#__PURE__*/React.createElement(Panel, {
    eyebrow: "Money",
    eyebrowColor: RV.purple,
    heading: "Financial Eligibility"
  }, /*#__PURE__*/React.createElement(Definitions, {
    items: [{
      label: 'Approximate Household Income',
      value: '£10,000 – £14,999'
    }, {
      label: 'Do you savings over £6,000?',
      value: 'No'
    }]
  }), /*#__PURE__*/React.createElement(Block, {
    heading: "Not visible to trustees"
  }, /*#__PURE__*/React.createElement(Restricted, {
    items: [['F1', 'Do you currently receive means tested benefits?'], ['F2', 'Benefit Provider'], ['F3', 'Are you currently working?']]
  })), /*#__PURE__*/React.createElement(Block, {
    heading: "In their words"
  }, /*#__PURE__*/React.createElement(Answers, {
    items: [['F5', 'If you have significant care costs, please briefly explain']]
  }))), /*#__PURE__*/React.createElement(Panel, {
    eyebrow: "From the team",
    eyebrowColor: RV.purple,
    heading: "Staff recommendation"
  }, /*#__PURE__*/React.createElement(window.StateMessage, {
    heading: "No staff recommendation recorded",
    explanation: "No staff recommendation has been written against this application's review record. The rest of the case can still be decided from."
  })), /*#__PURE__*/React.createElement(Panel, {
    eyebrow: "Your decision",
    heading: "Your verdict"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      color: 'var(--text-body)',
      fontSize: 'var(--text-sm)'
    }
  }, "You are recording the ", /*#__PURE__*/React.createElement("strong", null, "Trustee 1"), " verdict for ", a.ref, "."), /*#__PURE__*/React.createElement(window.VerdictChoices, {
    name: "verdict",
    value: verdict,
    onChange: setVerdict
  }), /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      fontSize: 'var(--text-sm)',
      color: 'var(--text-heading)'
    }
  }, "Notes (optional)", /*#__PURE__*/React.createElement("textarea", {
    rows: 3,
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      padding: '12px 14px',
      borderRadius: '12px',
      border: '1.5px solid var(--grey-200)',
      background: 'var(--grey-50)'
    }
  })), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Button, {
    variant: "primary"
  }, "Save verdict")))));
}
window.ApplicationDetail = ApplicationDetail;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/ApplicationDetail.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/ApplicationsList.jsx
try { (() => {
// Mirrors pages/ApplicationsListPage.tsx + ApplicationFilters.tsx + ApplicationsTable.tsx.
const EMPTY_FILTERS = {
  round: '',
  status: '',
  min: '',
  max: '',
  text: ''
};
function applyFilters(rows, f) {
  return rows.filter(r => (!f.round || r.round === f.round) && (!f.status || r.status === f.status) && (f.min === '' || (r.score ?? -1) >= Number(f.min)) && (f.max === '' || (r.score ?? 1e9) <= Number(f.max)) && (!f.text || r.ref.toLowerCase().includes(f.text.toLowerCase())));
}
const fieldStyle = {
  display: 'flex',
  flexDirection: 'column',
  gap: '6px',
  fontSize: 'var(--text-sm)',
  color: 'var(--text-heading)',
  width: '200px'
};
const controlStyle = {
  fontFamily: 'var(--font-body)',
  fontSize: 'var(--text-base)',
  minHeight: '44px',
  padding: '0 14px',
  borderRadius: '12px',
  border: '1.5px solid var(--grey-200)',
  color: 'var(--text-heading)',
  background: 'var(--grey-50)',
  width: '100%',
  boxSizing: 'border-box'
};
function ApplicationFilters({
  filters,
  onChange
}) {
  const Button = window.PButton;
  const rows = window.APPLICATIONS;
  const statuses = [...new Set(rows.map(r => r.status))].sort();
  const rounds = [...new Set(rows.map(r => r.round))];
  const set = k => e => onChange({
    ...filters,
    [k]: e.target.value
  });
  return /*#__PURE__*/React.createElement("div", {
    className: "rv-card",
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)',
      padding: 'var(--space-6) var(--space-8)',
      borderRadius: '16px'
    }
  }, /*#__PURE__*/React.createElement(window.Eyebrow, {
    color: window.RV.purple
  }, "Filter the round"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-4)',
      alignItems: 'flex-end'
    }
  }, /*#__PURE__*/React.createElement("label", {
    style: fieldStyle
  }, "Review round", /*#__PURE__*/React.createElement("select", {
    value: filters.round,
    onChange: set('round'),
    style: controlStyle
  }, /*#__PURE__*/React.createElement("option", {
    value: ""
  }, "All rounds available to you"), rounds.map(r => /*#__PURE__*/React.createElement("option", {
    key: r
  }, r)))), /*#__PURE__*/React.createElement("label", {
    style: fieldStyle
  }, "Status", /*#__PURE__*/React.createElement("select", {
    value: filters.status,
    onChange: set('status'),
    style: controlStyle
  }, /*#__PURE__*/React.createElement("option", {
    value: ""
  }, "All statuses"), statuses.map(s => /*#__PURE__*/React.createElement("option", {
    key: s
  }, s)))), /*#__PURE__*/React.createElement("label", {
    style: {
      ...fieldStyle,
      width: '120px'
    }
  }, "Score from", /*#__PURE__*/React.createElement("input", {
    type: "number",
    value: filters.min,
    onChange: set('min'),
    style: controlStyle
  })), /*#__PURE__*/React.createElement("label", {
    style: {
      ...fieldStyle,
      width: '120px'
    }
  }, "Score to", /*#__PURE__*/React.createElement("input", {
    type: "number",
    value: filters.max,
    onChange: set('max'),
    style: controlStyle
  })), /*#__PURE__*/React.createElement("label", {
    style: {
      ...fieldStyle,
      width: '260px'
    }
  }, "Application reference contains", /*#__PURE__*/React.createElement("input", {
    value: filters.text,
    onChange: set('text'),
    style: controlStyle
  })), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    onClick: () => onChange(EMPTY_FILTERS)
  }, "Clear filters")));
}
const thStyle = {
  textAlign: 'left',
  padding: 'var(--space-4) var(--space-4)',
  background: 'var(--grey-50)',
  fontFamily: 'var(--font-body)',
  fontWeight: 700,
  fontSize: '12px',
  letterSpacing: '.06em',
  textTransform: 'uppercase',
  color: 'var(--ink-700)',
  verticalAlign: 'bottom'
};
const tdStyle = {
  padding: 'var(--space-4)',
  verticalAlign: 'middle'
};
const tableCardStyle = {
  overflowX: 'auto',
  overflowY: 'hidden'
};
const captionStyle = {
  textAlign: 'left',
  color: 'var(--ink-700)',
  fontSize: 'var(--text-sm)',
  padding: 'var(--space-6) var(--space-6) var(--space-4)',
  background: 'var(--white)'
};
const COLUMNS = [['ref', 'Application'], ['score', 'Circumstance score', true], ['circ', 'Exceptional circumstance'], ['dates', 'Preferred dates'], ['status', 'Status']];
function ApplicationsTable({
  rows,
  caption,
  sort,
  onSort,
  onOpen,
  onRecordVerdict
}) {
  const Button = window.PButton;
  return /*#__PURE__*/React.createElement("div", {
    className: "rv-card",
    style: tableCardStyle
  }, /*#__PURE__*/React.createElement("table", {
    className: "rv-table",
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      fontSize: 'var(--text-base)'
    }
  }, /*#__PURE__*/React.createElement("caption", {
    style: captionStyle
  }, caption), /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", {
    style: {
      borderBottom: '1px solid var(--border-default)'
    }
  }, COLUMNS.map(([k, label, num]) => {
    const dir = sort && sort.key === k ? sort.dir : null;
    return /*#__PURE__*/React.createElement("th", {
      key: k,
      scope: "col",
      "aria-sort": dir || 'none',
      style: {
        ...thStyle,
        textAlign: num ? 'right' : 'left'
      }
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      onClick: () => onSort && onSort(k),
      style: {
        background: 'none',
        border: 'none',
        padding: 0,
        font: 'inherit',
        color: 'inherit',
        cursor: onSort ? 'pointer' : 'default',
        display: 'inline-flex',
        gap: '6px',
        alignItems: 'center'
      }
    }, label, /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        fontSize: '10px',
        color: 'var(--brand-primary)'
      }
    }, dir === 'asc' ? '▲' : dir === 'desc' ? '▼' : '')));
  }), /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: thStyle
  }, "Decision"))), /*#__PURE__*/React.createElement("tbody", null, rows.map(r => /*#__PURE__*/React.createElement("tr", {
    key: r.id,
    style: {
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("th", {
    scope: "row",
    style: {
      ...tdStyle,
      textAlign: 'left'
    }
  }, /*#__PURE__*/React.createElement(window.RowLink, {
    label: `${r.ref}, open the full case`,
    onClick: () => onOpen(r)
  }, r.ref)), /*#__PURE__*/React.createElement("td", {
    style: {
      ...tdStyle,
      textAlign: 'right'
    }
  }, /*#__PURE__*/React.createElement(window.ScoreChip, {
    score: r.score
  })), /*#__PURE__*/React.createElement("td", {
    style: {
      ...tdStyle,
      color: r.circ === 'None' || r.circ === 'Not recorded' ? 'var(--ink-600)' : 'var(--text-heading)'
    }
  }, r.circ), /*#__PURE__*/React.createElement("td", {
    style: tdStyle
  }, r.dates), /*#__PURE__*/React.createElement("td", {
    style: tdStyle
  }, /*#__PURE__*/React.createElement(window.StatusPill, {
    status: r.status
  })), /*#__PURE__*/React.createElement("td", {
    style: tdStyle
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    "aria-label": `Record verdict for ${r.ref}`,
    onClick: () => onRecordVerdict(r)
  }, "Record verdict")))))));
}
function sortRows(rows, sort) {
  const out = [...rows];
  out.sort((a, b) => {
    const x = a[sort.key] ?? -1,
      y = b[sort.key] ?? -1;
    return (x > y ? 1 : x < y ? -1 : 0) * (sort.dir === 'asc' ? 1 : -1);
  });
  return out;
}
function ApplicationsList({
  onOpenCase
}) {
  const Button = window.PButton;
  const [filters, setFilters] = React.useState(EMPTY_FILTERS);
  const [sort, setSort] = React.useState({
    key: 'score',
    dir: 'desc'
  });
  const [verdictFor, setVerdictFor] = React.useState(null);
  const all = window.APPLICATIONS;
  const rows = sortRows(applyFilters(all, filters), sort);
  const caption = rows.length === all.length ? `${all.length} applications under review.` : `${rows.length} of ${all.length} applications shown by the current filters.`;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement(window.Eyebrow, null, "Round 5"), /*#__PURE__*/React.createElement(window.PageTitle, null, "Applications under review")), /*#__PURE__*/React.createElement(ApplicationFilters, {
    filters: filters,
    onChange: setFilters
  }), /*#__PURE__*/React.createElement(window.ActionRow, null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Print this list")), rows.length === 0 ? /*#__PURE__*/React.createElement(window.StateMessage, {
    heading: "No applications match these filters",
    explanation: "Clear or widen the filters above to see the applications under review again."
  }) : /*#__PURE__*/React.createElement(ApplicationsTable, {
    rows: rows,
    caption: caption,
    sort: sort,
    onSort: k => setSort(s => ({
      key: k,
      dir: s.key === k && s.dir === 'asc' ? 'desc' : 'asc'
    })),
    onOpen: onOpenCase,
    onRecordVerdict: setVerdictFor
  }), verdictFor && /*#__PURE__*/React.createElement(window.VerdictDialog, {
    application: verdictFor,
    onClose: () => setVerdictFor(null)
  }));
}
Object.assign(window, {
  ApplicationsList,
  ApplicationFilters,
  ApplicationsTable,
  applyFilters,
  EMPTY_FILTERS,
  thStyle,
  tdStyle,
  tableCardStyle,
  captionStyle
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/ApplicationsList.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/GroupScreens.jsx
try { (() => {
// Mirrors pages/GroupsListPage.tsx + GroupsTable.tsx and pages/GroupDetailPage.tsx (EF-43).
function GroupsList({
  onOpenGroup
}) {
  const Button = window.PButton;
  const [filters, setFilters] = React.useState(window.EMPTY_FILTERS);
  const groups = window.deriveGroups(window.applyFilters(window.APPLICATIONS, filters));
  const {
    thStyle,
    tdStyle,
    tableCardStyle,
    captionStyle
  } = window;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement(window.Eyebrow, null, "Round 5"), /*#__PURE__*/React.createElement(window.PageTitle, null, "Group applications")), /*#__PURE__*/React.createElement(window.ApplicationFilters, {
    filters: filters,
    onChange: setFilters
  }), /*#__PURE__*/React.createElement(window.ActionRow, null, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Print this list")), groups.length === 0 ? /*#__PURE__*/React.createElement(window.StateMessage, {
    heading: "No groups match these filters",
    explanation: "Clear or widen the filters above to see the groups under review again."
  }) : /*#__PURE__*/React.createElement("div", {
    className: "rv-card",
    style: tableCardStyle
  }, /*#__PURE__*/React.createElement("table", {
    className: "rv-table",
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      fontSize: 'var(--text-base)'
    }
  }, /*#__PURE__*/React.createElement("caption", {
    style: captionStyle
  }, groups.length, " group", groups.length === 1 ? '' : 's', " of linked applications."), /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", {
    style: {
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: thStyle
  }, "Group"), /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: {
      ...thStyle,
      textAlign: 'right'
    }
  }, "Members"), /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: {
      ...thStyle,
      textAlign: 'right'
    }
  }, "Group total requested"), /*#__PURE__*/React.createElement("th", {
    scope: "col",
    style: thStyle
  }, "Shared dates"))), /*#__PURE__*/React.createElement("tbody", null, groups.map(g => /*#__PURE__*/React.createElement("tr", {
    key: g.code,
    style: {
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("th", {
    scope: "row",
    style: {
      ...tdStyle,
      textAlign: 'left'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '12px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      width: '36px',
      height: '36px',
      borderRadius: '12px',
      background: 'linear-gradient(135deg, var(--lavender-100), var(--pink-50))',
      display: 'grid',
      placeItems: 'center',
      fontFamily: 'var(--font-display)',
      color: 'var(--brand-primary)',
      fontSize: '15px'
    }
  }, g.code.slice(-2)), /*#__PURE__*/React.createElement(window.RowLink, {
    label: `Group ${g.code}, open the group's applications`,
    onClick: () => onOpenGroup(g)
  }, g.code))), /*#__PURE__*/React.createElement("td", {
    style: {
      ...tdStyle,
      textAlign: 'right'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '10px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      display: 'inline-flex'
    }
  }, g.members.map((m, i) => /*#__PURE__*/React.createElement("span", {
    key: m.id,
    style: {
      width: '22px',
      height: '22px',
      borderRadius: '50%',
      border: '2px solid #fff',
      marginLeft: i ? '-7px' : 0,
      background: ['var(--brand-primary)', window.RV.purple, window.RV.teal, 'var(--pink-300)'][i % 4]
    }
  }))), /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, g.memberCount))), /*#__PURE__*/React.createElement("td", {
    style: {
      ...tdStyle,
      textAlign: 'right',
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      color: 'var(--text-heading)'
    }
  }, window.gbp(g.total)), /*#__PURE__*/React.createElement("td", {
    style: tdStyle
  }, g.shared)))))));
}
function GroupDetail({
  group,
  onOpenCase
}) {
  const [verdictFor, setVerdictFor] = React.useState(null);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(window.PageTitle, null, "Group ", group.code), /*#__PURE__*/React.createElement(window.HeroBand, {
    badgeLabel: "Members",
    badgeValue: group.memberCount,
    eyebrow: "Group summary",
    heading: `${window.gbp(group.total)} requested together`
  }, /*#__PURE__*/React.createElement(window.FactChips, {
    items: [['Group code', group.code], ['Members', String(group.memberCount)], ['Group total requested', window.gbp(group.total)], ['Shared dates', group.shared]]
  })), /*#__PURE__*/React.createElement(window.Eyebrow, {
    color: window.RV.purple
  }, "Applications in this group"), /*#__PURE__*/React.createElement(window.ApplicationsTable, {
    rows: group.members,
    caption: `${group.memberCount} application${group.memberCount === 1 ? '' : 's'} in group ${group.code}.`,
    onOpen: onOpenCase,
    onRecordVerdict: setVerdictFor
  }), verdictFor && /*#__PURE__*/React.createElement(window.VerdictDialog, {
    application: verdictFor,
    onClose: () => setVerdictFor(null)
  }));
}
Object.assign(window, {
  GroupsList,
  GroupDetail
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/GroupScreens.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/RoundOverview.jsx
try { (() => {
// Mirrors pages/LandingPage.tsx + RoundStatistics.tsx + RoundFinancePanel.tsx — playful presentation layer.
const RV_PURPLE = '#49345b',
  RV_PURPLE_FADED = '#6a5774',
  RV_TEAL = '#14adbb';
const PALETTE = ['var(--brand-primary)', RV_PURPLE, RV_TEAL, 'var(--pink-300)', RV_PURPLE_FADED];
function Eyebrow({
  children,
  color = 'var(--brand-primary)'
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: 'var(--text-xs, 12px)',
      fontWeight: 700,
      letterSpacing: '.08em',
      textTransform: 'uppercase',
      color
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      background: color
    }
  }), children);
}
function Card({
  eyebrow,
  eyebrowColor,
  heading,
  children,
  style
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: "rv-card rv-lift",
    style: {
      padding: 'var(--space-8)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-5)',
      borderRadius: '16px',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, eyebrow && /*#__PURE__*/React.createElement(Eyebrow, {
    color: eyebrowColor
  }, eyebrow), /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-xl)',
      color: 'var(--text-heading)',
      margin: 0
    }
  }, heading)), children);
}
function RoundHero() {
  const opened = 1,
    closed = 30,
    today = 30;
  const pct = Math.round((today - opened) / (closed - opened) * 100);
  return /*#__PURE__*/React.createElement("section", {
    className: "rv-card",
    style: {
      borderRadius: '20px',
      padding: 'var(--space-8)',
      background: 'linear-gradient(135deg, var(--lavender-100) 0%, var(--pink-50) 100%)',
      display: 'grid',
      gridTemplateColumns: 'auto minmax(0, 1fr)',
      gap: 'var(--space-8)',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: '120px',
      height: '120px',
      borderRadius: '50%',
      background: 'var(--white)',
      boxShadow: '0 6px 20px rgba(73,52,91,.14)',
      display: 'grid',
      placeItems: 'center',
      textAlign: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: '12px',
      fontWeight: 700,
      letterSpacing: '.08em',
      textTransform: 'uppercase',
      color: RV_PURPLE
    }
  }, "Round"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: '52px',
      lineHeight: 1,
      color: 'var(--brand-primary)'
    }
  }, "5"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)',
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-1)'
    }
  }, /*#__PURE__*/React.createElement(Eyebrow, {
    color: RV_PURPLE
  }, "This round"), /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-2xl)',
      color: 'var(--text-heading)',
      margin: 0
    }
  }, "Open from 1 Sep to 30 Sep 2026")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      height: '10px',
      borderRadius: '999px',
      background: 'rgba(255,255,255,.8)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: `${pct}%`,
      height: '100%',
      borderRadius: '999px',
      background: `linear-gradient(90deg, ${RV_PURPLE} 0%, var(--brand-primary) 100%)`
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)'
    }
  }, /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "Opened"), " 1 Sep 2026"), /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, "Closed"), " 30 Sep 2026")))));
}
function ProgressTiles({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
      gap: 'var(--space-4)'
    }
  }, items.map(([label, value, color, tint]) => /*#__PURE__*/React.createElement("div", {
    key: label,
    style: {
      borderRadius: '14px',
      padding: 'var(--space-5)',
      background: tint,
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '28px',
      height: '6px',
      borderRadius: '999px',
      background: color
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: '40px',
      lineHeight: 1.05,
      color: 'var(--text-heading)'
    }
  }, value), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)'
    }
  }, label))));
}
function Bars({
  rows,
  n
}) {
  const total = n || rows.reduce((s, r) => s + r[1], 0);
  const max = Math.max(1, ...rows.map(r => r[1]));
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)'
    }
  }, rows.map(([label, v], i) => /*#__PURE__*/React.createElement("div", {
    key: label,
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '6px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 'var(--space-3)',
      fontSize: 'var(--text-sm)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--text-heading)',
      fontWeight: 700
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      color: 'var(--ink-700)'
    }
  }, /*#__PURE__*/React.createElement("strong", {
    style: {
      color: 'var(--text-heading)'
    }
  }, v), " \xB7 ", pct(v, total), "%")), /*#__PURE__*/React.createElement("div", {
    style: {
      height: '12px',
      borderRadius: '999px',
      background: 'var(--grey-100)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: `${v / max * 100}%`,
      minWidth: v ? '12px' : 0,
      height: '100%',
      borderRadius: '999px',
      background: PALETTE[i % PALETTE.length]
    }
  })))));
}
const pct = (n, t) => t ? Math.round(n / t * 1000) / 10 : 0;
function Counted({
  n
}) {
  return /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-600)'
    }
  }, "Counted over ", n, " applications in this round.");
}
function ChartBlock({
  title,
  n,
  rows,
  series,
  children
}) {
  const [open, setOpen] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)',
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      color: 'var(--text-heading)',
      margin: 0
    }
  }, title), n != null && /*#__PURE__*/React.createElement(Counted, {
    n: n
  }), children, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(window.RowLink, {
    onClick: () => setOpen(o => !o)
  }, open ? 'Hide the data table' : 'Show the data table')), open && /*#__PURE__*/React.createElement("table", {
    style: {
      width: '100%',
      borderCollapse: 'collapse',
      fontSize: 'var(--text-sm)'
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", {
    style: {
      borderBottom: '1px solid var(--border-default)'
    }
  }, /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'left',
      padding: '6px 8px',
      color: 'var(--text-heading)'
    }
  }, "Category"), (series || ['Applications']).map(s => /*#__PURE__*/React.createElement("th", {
    key: s,
    style: {
      textAlign: 'right',
      padding: '6px 8px',
      color: 'var(--text-heading)'
    }
  }, s)), !series && /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: 'right',
      padding: '6px 8px',
      color: 'var(--text-heading)'
    }
  }, "Share of round"))), /*#__PURE__*/React.createElement("tbody", null, rows.map(r => /*#__PURE__*/React.createElement("tr", {
    key: r[0],
    style: {
      borderBottom: '1px solid var(--grey-100)'
    }
  }, /*#__PURE__*/React.createElement("td", {
    style: {
      padding: '6px 8px'
    }
  }, r[0]), series ? r[1].map((v, i) => /*#__PURE__*/React.createElement("td", {
    key: i,
    style: {
      textAlign: 'right',
      padding: '6px 8px'
    }
  }, v, "%")) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("td", {
    style: {
      textAlign: 'right',
      padding: '6px 8px'
    }
  }, r[1]), /*#__PURE__*/React.createElement("td", {
    style: {
      textAlign: 'right',
      padding: '6px 8px'
    }
  }, pct(r[1], n), "%")))))));
}

// Vertical columns with rounded tops — maps to Recharts <BarChart><Bar radius={[8,8,0,0]}/>.
function Columns({
  rows,
  n,
  color = 'var(--brand-primary)',
  height = 180
}) {
  const [hover, setHover] = React.useState(null);
  const max = Math.max(1, ...rows.map(r => r[1]));
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      height: height + 'px',
      display: 'flex',
      alignItems: 'flex-end',
      gap: '6px',
      padding: '0 2px',
      backgroundImage: 'repeating-linear-gradient(to top, var(--grey-100) 0 1px, transparent 1px ' + height / 4 + 'px)',
      borderBottom: '1.5px solid var(--grey-200)'
    }
  }, rows.map(([label, v], i) => /*#__PURE__*/React.createElement("div", {
    key: label,
    onMouseEnter: () => setHover(i),
    onMouseLeave: () => setHover(null),
    style: {
      flex: 1,
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-end',
      alignItems: 'center',
      position: 'relative'
    }
  }, hover === i && /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      bottom: `calc(${v / max * 100}% + 8px)`,
      background: 'var(--ink-900)',
      color: '#fff',
      fontSize: '12px',
      fontWeight: 700,
      padding: '4px 8px',
      borderRadius: '8px',
      whiteSpace: 'nowrap',
      zIndex: 2
    }
  }, label, " \xB7 ", pct(v, n), "%"), /*#__PURE__*/React.createElement("div", {
    style: {
      width: '100%',
      maxWidth: '44px',
      height: `${v / max * 100}%`,
      minHeight: v ? '4px' : 0,
      borderRadius: '8px 8px 3px 3px',
      background: color,
      opacity: hover === null || hover === i ? 1 : 0.55,
      transition: 'opacity var(--duration-fast)'
    }
  })))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '6px',
      padding: '0 2px'
    }
  }, rows.map(([label]) => /*#__PURE__*/React.createElement("span", {
    key: label,
    style: {
      flex: 1,
      textAlign: 'center',
      fontSize: '12px',
      color: 'var(--ink-700)',
      lineHeight: 1.25
    }
  }, label))));
}

// Grouped columns (one colour per question) — Recharts <BarChart> with several <Bar>s.
function GroupedColumns({
  categories,
  series,
  colors,
  height = 200
}) {
  const max = Math.max(1, ...series.flatMap(s => s.values));
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      height: height + 'px',
      display: 'flex',
      alignItems: 'flex-end',
      gap: '14px',
      backgroundImage: 'repeating-linear-gradient(to top, var(--grey-100) 0 1px, transparent 1px ' + height / 4 + 'px)',
      borderBottom: '1.5px solid var(--grey-200)',
      padding: '0 4px'
    }
  }, categories.map((c, ci) => /*#__PURE__*/React.createElement("div", {
    key: c,
    style: {
      flex: 1,
      height: '100%',
      display: 'flex',
      alignItems: 'flex-end',
      justifyContent: 'center',
      gap: '3px'
    }
  }, series.map((s, si) => /*#__PURE__*/React.createElement("div", {
    key: s.name,
    title: `${s.name}: ${s.values[ci]}%`,
    style: {
      flex: 1,
      maxWidth: '18px',
      height: `${s.values[ci] / max * 100}%`,
      minHeight: s.values[ci] ? '4px' : 0,
      borderRadius: '6px 6px 2px 2px',
      background: colors[si]
    }
  }))))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: '14px',
      padding: '0 4px'
    }
  }, categories.map(c => /*#__PURE__*/React.createElement("span", {
    key: c,
    style: {
      flex: 1,
      textAlign: 'center',
      fontSize: '12px',
      color: 'var(--ink-700)',
      lineHeight: 1.25
    }
  }, c))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-2) var(--space-4)'
    }
  }, series.map((s, i) => /*#__PURE__*/React.createElement("span", {
    key: s.name,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)',
      background: 'var(--grey-50)',
      borderRadius: '999px',
      padding: '4px 12px 4px 8px'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '10px',
      height: '10px',
      borderRadius: '50%',
      background: colors[i]
    }
  }), s.name))));
}

// Donut — Recharts <Pie innerRadius outerRadius paddingAngle cornerRadius>.
function Donut({
  rows,
  n
}) {
  let acc = 0;
  const stops = rows.map(([, v], i) => {
    const a = acc;
    acc += v / n * 100;
    return `${PALETTE[i]} ${a}% ${acc}%`;
  }).join(', ');
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-6)',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: '160px',
      height: '160px',
      borderRadius: '50%',
      background: `conic-gradient(${stops})`,
      display: 'grid',
      placeItems: 'center',
      flex: 'none'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: '100px',
      height: '100px',
      borderRadius: '50%',
      background: '#fff',
      display: 'grid',
      placeItems: 'center',
      textAlign: 'center',
      boxShadow: 'inset 0 1px 4px rgba(43,43,43,.06)'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: '28px',
      color: 'var(--text-heading)',
      lineHeight: 1
    }
  }, n), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: '11px',
      color: 'var(--ink-600)'
    }
  }, "applications")))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)',
      flex: '1 1 200px'
    }
  }, rows.map(([label, v], i) => /*#__PURE__*/React.createElement("div", {
    key: label,
    style: {
      display: 'flex',
      gap: 'var(--space-3)',
      alignItems: 'baseline'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '10px',
      height: '10px',
      borderRadius: '50%',
      background: PALETTE[i],
      flex: 'none',
      transform: 'translateY(1px)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      color: 'var(--text-heading)',
      minWidth: '56px'
    }
  }, pct(v, n), "%"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)'
    }
  }, label)))));
}
function MoneyTiles({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
      gap: 'var(--space-3)'
    }
  }, items.map(([label, value]) => {
    const absent = value === 'Not recorded';
    return /*#__PURE__*/React.createElement("div", {
      key: label,
      style: {
        borderRadius: '14px',
        padding: 'var(--space-4) var(--space-5)',
        background: absent ? 'transparent' : 'var(--grey-50)',
        border: absent ? '1.5px dashed var(--grey-200)' : '1.5px solid transparent',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontSize: 'var(--text-sm)',
        color: 'var(--ink-700)'
      }
    }, label), /*#__PURE__*/React.createElement("span", {
      style: absent ? {
        fontSize: 'var(--text-base)',
        color: 'var(--ink-600)',
        fontStyle: 'italic'
      } : {
        fontFamily: 'var(--font-display)',
        fontSize: '26px',
        color: 'var(--text-heading)',
        lineHeight: 1.15
      }
    }, value));
  }));
}
function RoundOverview({
  onOpenList
}) {
  const Button = window.PButton;
  const {
    PageTitle,
    ActionRow
  } = window;
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement(PageTitle, null, "Round overview \u2014 5"), /*#__PURE__*/React.createElement("p", {
    style: {
      color: 'var(--text-body)',
      margin: 0
    }
  }, "This portal shows the one grant round currently open for review. There is no round to choose.")), /*#__PURE__*/React.createElement(ActionRow, null, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    onClick: onOpenList
  }, "Open the applications list"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary"
  }, "Refresh figures")), /*#__PURE__*/React.createElement(RoundHero, null), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      gap: 'var(--space-2)',
      marginTop: 'var(--space-4)'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-2xl)',
      color: 'var(--text-heading)',
      margin: 0
    }
  }, "Figures of this round"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)',
      background: 'var(--white)',
      borderRadius: '999px',
      padding: '6px 14px',
      boxShadow: '0 1px 3px rgba(43,43,43,.08)'
    }
  }, "Computed on 30 Sep 2026 at 15:42")), /*#__PURE__*/React.createElement(Card, {
    eyebrow: "Round progress",
    heading: "48 applications in 59 days"
  }, /*#__PURE__*/React.createElement(ProgressTiles, {
    items: [['Applications received', '48', 'var(--brand-primary)', 'var(--pink-50)'], ['Applications per day', '0.81', RV_PURPLE, 'var(--lavender-100)'], ['Days the round has been open', '59', RV_TEAL, '#e7f6f8']]
  })), /*#__PURE__*/React.createElement(Card, {
    eyebrow: "Exceptional circumstances",
    heading: "1 in 4 applications cite an exceptional circumstance"
  }, /*#__PURE__*/React.createElement(ProgressTiles, {
    items: [['Applications citing any exceptional circumstance', '12', 'var(--brand-primary)', 'var(--pink-50)'], ['Share of the round citing any exceptional circumstance', '25.0%', RV_PURPLE, 'var(--lavender-100)'], ['Average exceptional funding requested', '£640', RV_TEAL, '#e7f6f8']]
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-600)'
    }
  }, "The average exceptional funding requested is shown only where enough applications citing exceptional circumstances carry a figure."), /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Exceptional circumstance cited",
    n: 48,
    rows: [['Palliative care', 5], ['Carer breakdown or urgent need', 4], ['Severe financial hardship', 2], ['Other (please specify)', 1]]
  }, /*#__PURE__*/React.createElement(Bars, {
    n: 48,
    rows: [['Palliative care', 5], ['Carer breakdown or urgent need', 4], ['Severe financial hardship', 2], ['Other (please specify)', 1]]
  }))), /*#__PURE__*/React.createElement(Card, {
    eyebrow: "Who applied in this round",
    eyebrowColor: RV_PURPLE,
    heading: "The people behind the applications"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 380px), 1fr))',
      gap: 'var(--space-8) var(--space-10, 40px)'
    }
  }, /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Gender",
    n: 48,
    rows: [['Female', 26], ['Male', 19], ['Non-binary', 2], ['Describes themselves another way', 0], ['Prefer not to say', 1]]
  }, /*#__PURE__*/React.createElement(Bars, {
    n: 48,
    rows: [['Female', 26], ['Male', 19], ['Non-binary', 2], ['Describes themselves another way', 0], ['Prefer not to say', 1]]
  })), /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Age range",
    n: 48,
    rows: [['Under 18', 1], ['18 to 24', 3], ['25 to 34', 5], ['35 to 44', 6], ['45 to 54', 8], ['55 to 64', 10], ['65 to 74', 9], ['75 and over', 5], ['Not known', 1]]
  }, /*#__PURE__*/React.createElement(Columns, {
    n: 48,
    color: RV_PURPLE,
    rows: [['Under 18', 1], ['18–24', 3], ['25–34', 5], ['35–44', 6], ['45–54', 8], ['55–64', 10], ['65–74', 9], ['75+', 5], ['Not known', 1]]
  })), /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Applicant type",
    n: 48,
    rows: [['A disabled person', 29], ['A carer applying on behalf of a disabled person', 12], ['A carer applying for yourself', 7]]
  }, /*#__PURE__*/React.createElement(Donut, {
    n: 48,
    rows: [['A disabled person', 29], ['A carer applying on behalf of a disabled person', 12], ['A carer applying for yourself', 7]]
  })), /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Ethnic group",
    n: 48,
    rows: [['White', 34], ['Asian or Asian British', 6], ['Black, African, Caribbean or Black British', 4], ['Mixed or Multiple ethnic groups', 2], ['Other ethnic group', 1], ['Prefer not to say', 1]]
  }, /*#__PURE__*/React.createElement(Bars, {
    n: 48,
    rows: [['White', 34], ['Asian or Asian British', 6], ['Black, African, Caribbean or Black British', 4], ['Mixed or Multiple ethnic groups', 2], ['Other ethnic group', 1], ['Prefer not to say', 1]]
  })))), /*#__PURE__*/React.createElement(Card, {
    eyebrow: "Level of need",
    heading: "How applicants have been feeling"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 380px), 1fr))',
      gap: 'var(--space-8) var(--space-10, 40px)'
    }
  }, /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Wellbeing, last year (all questions)",
    series: ['Question 8', 'Question 9', 'Question 10'],
    rows: [['Strongly Disagree', [10, 8, 6]], ['Disagree', [21, 19, 15]], ['Neutral', [25, 27, 23]], ['Agree', [29, 31, 35]], ['Strongly Agree', [13, 12, 19]], ['Not sure', [2, 3, 2]]]
  }, /*#__PURE__*/React.createElement(GroupedColumns, {
    colors: ['var(--brand-primary)', RV_PURPLE, RV_TEAL],
    categories: ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree', 'Not sure'],
    series: [{
      name: 'Wellbeing question 8, last year',
      values: [10, 21, 25, 29, 13, 2]
    }, {
      name: 'Wellbeing question 9, last year',
      values: [8, 19, 27, 31, 12, 3]
    }, {
      name: 'Wellbeing question 10, last year',
      values: [6, 15, 23, 35, 19, 2]
    }]
  })), /*#__PURE__*/React.createElement(ChartBlock, {
    title: "Life satisfaction, 0 to 10",
    n: 48,
    rows: [['0', 2], ['1', 1], ['2', 3], ['3', 5], ['4', 6], ['5', 9], ['6', 8], ['7', 6], ['8', 4], ['9', 2], ['10', 2]]
  }, /*#__PURE__*/React.createElement(Columns, {
    n: 48,
    height: 200,
    rows: [['0', 2], ['1', 1], ['2', 3], ['3', 5], ['4', 6], ['5', 9], ['6', 8], ['7', 6], ['8', 4], ['9', 2], ['10', 2]]
  })))), /*#__PURE__*/React.createElement(Card, {
    eyebrow: "Financial position",
    eyebrowColor: RV_PURPLE,
    heading: "The round's financial position"
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)',
      display: 'flex',
      gap: '8px',
      alignItems: 'center',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      background: 'var(--lavender-100)',
      color: RV_PURPLE,
      fontWeight: 700,
      borderRadius: '999px',
      padding: '4px 12px'
    }
  }, "Entered by hand"), "These figures are as at 26 Sep 2026. The application figures above were computed just now."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(Eyebrow, {
    color: "var(--ink-600)"
  }, "This round"), /*#__PURE__*/React.createElement(MoneyTiles, {
    items: [['Committed or spent to date', '£50,000.00'], ['People supported', '1,000'], ['Individuals supported', 'Not recorded'], ['People reached by group grants', '200'], ['Suggested maximum spend for this round', '£550,000.00'], ['Monthly disbursement', 'Not recorded']]
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-3)'
    }
  }, /*#__PURE__*/React.createElement(Eyebrow, {
    color: "var(--ink-600)"
  }, "Charity-wide"), /*#__PURE__*/React.createElement(MoneyTiles, {
    items: [['Grant-giving capacity (charity-wide)', '£70,000.00'], ['Remaining legacy fund (charity-wide)', '£100,000.00']]
  }))));
}
window.RoundOverview = RoundOverview;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/RoundOverview.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/Shared.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
// Shared primitives mirroring src/components/Panel.tsx (Panel, Definitions, StateMessage, StatTileRow) + mock data.
const {
  Notice: _Notice,
  StatTile: _StatTile,
  Button: _DSButton,
  Radio: _Radio
} = window.RevitaliseDesignSystem_a4dff3;
// Kit-scoped button: DS Button + gradient/shadow treatment from index.html (.rv-btn).
function PButton({
  variant = 'primary',
  className,
  ...rest
}) {
  return /*#__PURE__*/React.createElement(_DSButton, _extends({
    variant: variant,
    className: ['rv-btn', 'rv-btn-' + variant, className].filter(Boolean).join(' ')
  }, rest));
}
const _Button = PButton;
const h2Style = {
  fontFamily: 'var(--font-display)',
  fontSize: 'var(--text-xl)',
  color: 'var(--text-heading)',
  margin: '0 0 var(--space-4)'
};
const h3Style = {
  fontFamily: 'var(--font-display)',
  fontSize: 'var(--text-lg)',
  color: 'var(--text-heading)',
  margin: 0
};
const RV = {
  purple: '#49345b',
  purpleFaded: '#6a5774',
  teal: '#14adbb',
  tealTint: '#e7f6f8'
};
function Eyebrow({
  children,
  color = 'var(--brand-primary)'
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '12px',
      fontWeight: 700,
      letterSpacing: '.08em',
      textTransform: 'uppercase',
      color
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      background: color
    }
  }), children);
}
function Panel({
  heading,
  eyebrow,
  eyebrowColor,
  children
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: "rv-card rv-lift",
    style: {
      padding: 'var(--space-8)',
      borderRadius: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-5)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, eyebrow && /*#__PURE__*/React.createElement(Eyebrow, {
    color: eyebrowColor
  }, eyebrow), /*#__PURE__*/React.createElement("h2", {
    style: {
      ...h2Style,
      margin: 0
    }
  }, heading)), children);
}

// Hero band — same treatment as the Round overview's round header.
function HeroBand({
  badgeLabel,
  badgeValue,
  eyebrow,
  heading,
  children
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: "rv-card",
    style: {
      borderRadius: '20px',
      padding: 'var(--space-8)',
      background: 'linear-gradient(135deg, var(--lavender-100) 0%, var(--pink-50) 100%)',
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-8)',
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: '120px',
      height: '120px',
      borderRadius: '50%',
      background: 'var(--white)',
      boxShadow: '0 6px 20px rgba(73,52,91,.14)',
      display: 'grid',
      placeItems: 'center',
      textAlign: 'center',
      flex: 'none'
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: '12px',
      fontWeight: 700,
      letterSpacing: '.08em',
      textTransform: 'uppercase',
      color: RV.purple
    }
  }, badgeLabel), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: String(badgeValue).length > 3 ? '30px' : '46px',
      lineHeight: 1.05,
      color: 'var(--brand-primary)'
    }
  }, badgeValue))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)',
      flex: '1 1 320px',
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-1)'
    }
  }, /*#__PURE__*/React.createElement(Eyebrow, {
    color: RV.purple
  }, eyebrow), /*#__PURE__*/React.createElement("h2", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-2xl)',
      color: 'var(--text-heading)',
      margin: 0
    }
  }, heading)), children));
}
function FactChips({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-2)'
    }
  }, items.map(([label, value]) => /*#__PURE__*/React.createElement("span", {
    key: label,
    style: {
      display: 'inline-flex',
      flexDirection: 'column',
      gap: '2px',
      background: 'rgba(255,255,255,.85)',
      borderRadius: '12px',
      padding: '8px 14px',
      boxShadow: '0 1px 3px rgba(73,52,91,.08)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: '12px',
      color: 'var(--ink-600)'
    }
  }, label), /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 700,
      color: 'var(--text-heading)',
      fontSize: 'var(--text-sm)'
    }
  }, value))));
}
const STATUS_TONES = {
  'Eligible for Panel': ['var(--pink-50)', 'var(--pink-800)', 'var(--brand-primary)'],
  'Under Review': ['var(--lavender-100)', RV.purple, RV.purple],
  'Borderline': [RV.tealTint, '#00505a', RV.teal],
  'Auto-reject': ['var(--grey-100)', 'var(--ink-700)', 'var(--ink-400)']
};
function StatusPill({
  status
}) {
  const [bg, fg, dot] = STATUS_TONES[status] || STATUS_TONES['Auto-reject'];
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      background: bg,
      color: fg,
      fontWeight: 700,
      fontSize: '13px',
      borderRadius: '999px',
      padding: '4px 12px 4px 10px',
      whiteSpace: 'nowrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '7px',
      height: '7px',
      borderRadius: '50%',
      background: dot
    }
  }), status);
}
function ScoreChip({
  score,
  max = 60
}) {
  if (score == null) return /*#__PURE__*/React.createElement("span", {
    style: {
      fontStyle: 'italic',
      color: 'var(--ink-600)',
      fontSize: 'var(--text-sm)'
    }
  }, "Not scored");
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: '10px',
      justifyContent: 'flex-end'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: '56px',
      height: '6px',
      borderRadius: '999px',
      background: 'var(--grey-100)',
      overflow: 'hidden'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'block',
      height: '100%',
      width: `${score / max * 100}%`,
      borderRadius: '999px',
      background: `linear-gradient(90deg, ${RV.purple}, var(--brand-primary))`
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'var(--text-lg)',
      color: 'var(--text-heading)',
      minWidth: '24px',
      textAlign: 'right'
    }
  }, score));
}
function Definitions({
  items
}) {
  return /*#__PURE__*/React.createElement("dl", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
      gap: 'var(--space-3)',
      margin: 0
    }
  }, items.map(i => {
    const absent = ABSENT.includes(i.value);
    return /*#__PURE__*/React.createElement("div", {
      key: i.label,
      style: {
        borderRadius: '14px',
        padding: 'var(--space-4) var(--space-5)',
        background: absent ? 'transparent' : 'var(--grey-50)',
        border: absent ? '1.5px dashed var(--grey-200)' : '1.5px solid transparent',
        display: 'flex',
        flexDirection: 'column',
        gap: '4px'
      }
    }, /*#__PURE__*/React.createElement("dt", {
      style: {
        fontSize: 'var(--text-sm)',
        color: 'var(--ink-700)'
      }
    }, i.label), /*#__PURE__*/React.createElement("dd", {
      style: {
        margin: 0,
        color: absent ? 'var(--ink-600)' : 'var(--text-heading)',
        fontWeight: absent ? 400 : 700,
        fontStyle: absent ? 'italic' : 'normal',
        fontSize: 'var(--text-base)'
      }
    }, i.value));
  }));
}
function StateMessage({
  heading,
  explanation
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "note",
    style: {
      borderRadius: '14px',
      border: '1.5px dashed var(--lavender-200)',
      background: 'linear-gradient(135deg, rgba(237,232,241,.5), rgba(253,241,248,.5))',
      padding: 'var(--space-5) var(--space-6)',
      display: 'flex',
      flexDirection: 'column',
      gap: '6px'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontWeight: 700,
      color: 'var(--text-heading)'
    }
  }, heading), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      color: 'var(--ink-700)',
      textWrap: 'pretty'
    }
  }, explanation));
}
// Selectable verdict choice cards (wrap the radio semantics in a styled label).
const VERDICT_TONES = {
  Approve: 'var(--brand-primary)',
  Defer: RV.purple,
  Reject: 'var(--ink-600)'
};
function VerdictChoices({
  name,
  value,
  onChange
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "radiogroup",
    "aria-label": "Verdict",
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
      gap: 'var(--space-3)'
    }
  }, ['Approve', 'Defer', 'Reject'].map(v => {
    const on = value === v,
      c = VERDICT_TONES[v];
    return /*#__PURE__*/React.createElement("label", {
      key: v,
      style: {
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        borderRadius: '14px',
        padding: '14px 16px',
        minHeight: '44px',
        background: on ? 'var(--white)' : 'var(--grey-50)',
        border: on ? `2px solid ${c}` : '2px solid transparent',
        boxShadow: on ? '0 4px 14px rgba(43,43,43,.08)' : 'none',
        transition: 'all var(--duration-fast) var(--ease-standard)'
      }
    }, /*#__PURE__*/React.createElement("input", {
      type: "radio",
      name: name,
      checked: on,
      onChange: () => onChange(v),
      style: {
        accentColor: c,
        width: '18px',
        height: '18px',
        margin: 0
      }
    }), /*#__PURE__*/React.createElement("span", {
      style: {
        fontWeight: 700,
        color: 'var(--text-heading)'
      }
    }, v));
  }));
}
const ABSENT = ['Not recorded', 'Not available'];
function StatTileRow({
  items
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
      gap: 'var(--space-4)'
    }
  }, items.map(i => /*#__PURE__*/React.createElement(_StatTile, {
    key: i.label,
    label: i.label,
    value: i.value,
    absent: ABSENT.includes(i.value)
  })));
}
function PageTitle({
  children
}) {
  return /*#__PURE__*/React.createElement("h1", {
    style: {
      fontFamily: 'var(--font-display)',
      fontSize: 'clamp(28px, 6vw, 44px)',
      lineHeight: 1.2,
      color: 'var(--text-heading)',
      margin: 0,
      overflowWrap: 'break-word'
    }
  }, children);
}
function ActionRow({
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 'var(--space-3)'
    }
  }, children);
}
function RowLink({
  children,
  onClick,
  label
}) {
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-label": label,
    onClick: onClick,
    style: {
      background: 'none',
      border: 'none',
      padding: 0,
      font: 'inherit',
      fontWeight: 700,
      color: 'var(--link-default, #cc0078)',
      textDecoration: 'underline',
      cursor: 'pointer'
    }
  }, children);
}
function VerdictDialog({
  application,
  onClose
}) {
  const [v, setV] = React.useState('Approve');
  return /*#__PURE__*/React.createElement("div", {
    role: "dialog",
    "aria-modal": "true",
    style: {
      position: 'fixed',
      inset: 0,
      background: 'rgba(20,10,30,0.45)',
      display: 'grid',
      placeItems: 'center',
      zIndex: 10,
      padding: 'var(--space-4)'
    },
    onClick: onClose
  }, /*#__PURE__*/React.createElement("div", {
    onClick: e => e.stopPropagation(),
    style: {
      background: '#fff',
      borderRadius: 'var(--radius-lg)',
      padding: 'var(--space-6)',
      width: 'min(520px, 100%)',
      borderRadius: '20px',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-4)',
      boxShadow: 'var(--shadow-lg, 0 12px 40px rgba(0,0,0,.2))'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--space-2)'
    }
  }, /*#__PURE__*/React.createElement(Eyebrow, null, "Record verdict"), /*#__PURE__*/React.createElement("h2", {
    style: {
      ...h2Style,
      margin: 0
    }
  }, application.ref)), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 'var(--text-sm)',
      color: 'var(--text-body)'
    }
  }, "You are recording the ", /*#__PURE__*/React.createElement("strong", null, "Trustee 1"), " verdict."), /*#__PURE__*/React.createElement(VerdictChoices, {
    name: "dlg-verdict",
    value: v,
    onChange: setV
  }), /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      fontSize: 'var(--text-sm)',
      color: 'var(--text-heading)'
    }
  }, "Notes (optional)", /*#__PURE__*/React.createElement("textarea", {
    rows: 3,
    style: {
      fontFamily: 'var(--font-body)',
      fontSize: 'var(--text-base)',
      padding: '12px 14px',
      borderRadius: '12px',
      border: '1.5px solid var(--grey-200)',
      background: 'var(--grey-50)'
    }
  })), /*#__PURE__*/React.createElement(ActionRow, null, /*#__PURE__*/React.createElement(_Button, {
    variant: "primary",
    onClick: onClose
  }, "Save verdict"), /*#__PURE__*/React.createElement(_Button, {
    variant: "secondary",
    onClick: onClose
  }, "Cancel"))));
}
const APPLICATIONS = [{
  id: 'a1',
  ref: 'REV-2026-1057',
  score: 60,
  circ: 'Terminal illness',
  dates: '5 Oct 2026 to 12 Oct 2026',
  status: 'Eligible for Panel',
  round: '5',
  group: 'GRP-014'
}, {
  id: 'a2',
  ref: 'REV-2026-1060',
  score: 21,
  circ: 'None',
  dates: '17 Oct 2026 to 19 Oct 2026',
  status: 'Borderline',
  round: '5',
  group: null
}, {
  id: 'a3',
  ref: 'REV-2026-1061',
  score: 20,
  circ: 'Recent bereavement',
  dates: '7 Dec 2026 to 14 Dec 2026',
  status: 'Under Review',
  round: '5',
  group: 'GRP-014'
}, {
  id: 'a4',
  ref: 'REV-2026-1068',
  score: 10,
  circ: 'None',
  dates: '5 Oct 2026 to 9 Oct 2026',
  status: 'Auto-reject',
  round: '5',
  group: null
}, {
  id: 'a5',
  ref: 'REV-2026-1065',
  score: null,
  circ: 'Not recorded',
  dates: '9 Nov 2026 to 16 Nov 2026',
  status: 'Eligible for Panel',
  round: '5',
  group: 'GRP-017'
}, {
  id: 'a6',
  ref: 'REV-2026-1072',
  score: 44,
  circ: 'Carer breakdown',
  dates: '9 Nov 2026 to 16 Nov 2026',
  status: 'Eligible for Panel',
  round: '5',
  group: 'GRP-017'
}, {
  id: 'a7',
  ref: 'REV-2026-1074',
  score: 38,
  circ: 'None',
  dates: '5 Oct 2026 to 12 Oct 2026',
  status: 'Under Review',
  round: '5',
  group: 'GRP-014'
}];
const REQUESTED = {
  a1: 1000,
  a3: 850,
  a5: 1200,
  a6: 1100,
  a7: 900
};
function deriveGroups(rows) {
  const map = {};
  rows.filter(r => r.group).forEach(r => {
    (map[r.group] = map[r.group] || []).push(r);
  });
  return Object.keys(map).sort().map(code => {
    const members = map[code];
    const shared = members.every(m => m.dates === members[0].dates) ? members[0].dates : 'Dates differ between members';
    return {
      code,
      members,
      memberCount: members.length,
      total: members.reduce((s, m) => s + (REQUESTED[m.id] || 0), 0),
      shared
    };
  });
}
const gbp = n => '£' + n.toLocaleString('en-GB', {
  minimumFractionDigits: 2
});
Object.assign(window, {
  RV,
  Eyebrow,
  HeroBand,
  FactChips,
  StatusPill,
  ScoreChip,
  VerdictChoices,
  PButton,
  Panel,
  Definitions,
  StateMessage,
  StatTileRow,
  PageTitle,
  ActionRow,
  RowLink,
  VerdictDialog,
  APPLICATIONS,
  deriveGroups,
  gbp,
  h3Style
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/trustee-review-portal/Shared.jsx", error: String((e && e.message) || e) }); }

// ui_kits/trustee-review-portal/TrusteePortalApp.jsx
try { (() => {
// Mirrors App.tsx view state: landing | list | groups | groupDetail | detail(fromGroup).
function TrusteePortalApp() {
  const [view, setView] = React.useState({
    name: 'landing'
  });
  const go = v => {
    setView(v);
    window.scrollTo(0, 0);
  };
  return /*#__PURE__*/React.createElement(window.AppFrame, {
    view: view,
    setView: go
  }, view.name === 'landing' && /*#__PURE__*/React.createElement(window.RoundOverview, {
    onOpenList: () => go({
      name: 'list'
    })
  }), view.name === 'list' && /*#__PURE__*/React.createElement(window.ApplicationsList, {
    onOpenCase: a => go({
      name: 'detail',
      application: a,
      fromGroup: null
    })
  }), view.name === 'groups' && /*#__PURE__*/React.createElement(window.GroupsList, {
    onOpenGroup: g => go({
      name: 'groupDetail',
      group: g
    })
  }), view.name === 'groupDetail' && /*#__PURE__*/React.createElement(window.GroupDetail, {
    group: view.group,
    onOpenCase: a => go({
      name: 'detail',
      application: a,
      fromGroup: view.group
    })
  }), view.name === 'detail' && /*#__PURE__*/React.createElement(window.ApplicationDetail, {
    key: view.application.id,
    application: view.application,
    fromGroup: view.fromGroup,
    onBackToGroup: () => go({
      name: 'groupDetail',
      group: view.fromGroup
    })
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
