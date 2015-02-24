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
  processVoteURL: baseURL + '/_process_vote',
  addCommentURL: rootURL + '/api/v2/comments/',
  attachCommentURL: baseURL + '/_attach_comment',
  getCommentsURL: rootURL + '/api/v2/comments/',
  acceptCommentURL: baseURL + '/_accept_comment',
  deleteCommentURL: baseURL + '/_delete_comment',
  metadataURL: baseURL + '/_get_metadata',
  optionsURL: baseURL + '/_get_options',

  // Static Content
  commentImage: staticURL + '/_static/comment.png',
  closeCommentImage: staticURL + '/_static/comment-close.png',
  loadingImage: staticURL + '/_static/ajax-loader.gif',
  commentBrightImage: staticURL + '/_static/comment-bright.png',
  upArrow: staticURL + '/_static/up.png',
  downArrow: staticURL + '/_static/down.png',
  upArrowPressed: staticURL + '/_static/up-pressed.png',
  downArrowPressed: staticURL + '/_static/down-pressed.png',

  voting: false,
  moderator: false
};


module.exports = {
  metadata: metadata,
  opts: opts,
  staticURL: staticURL,
  baseURL: baseURL
}

