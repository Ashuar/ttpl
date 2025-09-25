(() => {
  // ../ttpl/ttpl/public/js/ttpl.bundle.js
  frappe.provide("frappe.utils");
  frappe.utils.get_number_system = function(country) {
    return [
      {
        divisor: 1e12,
        symbol: __("T", null, "Number system")
      },
      {
        divisor: 1e9,
        symbol: __("B", null, "Number system")
      },
      {
        divisor: 1e6,
        symbol: __("M", null, "Number system")
      },
      {
        divisor: 1e3,
        symbol: __("K", null, "Number system")
      }
    ];
  };
})();
//# sourceMappingURL=ttpl.bundle.RYJW646W.js.map
