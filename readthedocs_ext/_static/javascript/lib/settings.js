var baseURL = "{{ websupport2_base_url }}";
var staticURL = "{{ websupport2_static_url }}";

// Template rendering failed
if (baseURL.lastIndexOf("{{", 0) === 0) {
  var rootURL = "http://localhost:8000";
  var baseURL = "http://localhost:8000/websupport";
  var staticURL = "http://localhost:8000/static";
}

var metadata = {}

var opts = {
  // Dynamic Content
  metadataURL: baseURL + '/_get_metadata',
  optionsURL: baseURL + '/_get_options',

  // Static Content
  loadingImage: staticURL + '/_static/ajax-loader.gif',
};


module.exports = {
  metadata: metadata,
  opts: opts,
  staticURL: staticURL,
  baseURL: baseURL
}
