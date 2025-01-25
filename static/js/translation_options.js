window.onload = function() {
    var urlParams = new URLSearchParams(window.location.search);
    var lang = urlParams.get('lang');
    if (lang) {
      document.getElementById('lang-select').value = lang;
    }
  }