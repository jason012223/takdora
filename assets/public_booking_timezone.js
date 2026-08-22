window.takdoraPublicBookingTimezone = function () {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "";
};
