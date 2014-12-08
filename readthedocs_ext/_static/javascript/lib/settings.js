var baseURL = "{{ websupport2_base_url }}";
var staticURL = "{{ websupport2_static_url }}";

var metadata = {}

var opts = {
  processVoteURL: baseURL + '/_process_vote',
  addCommentURL: baseURL + '/_add_comment',
  getCommentsURL: baseURL + '/_get_comments',
  acceptCommentURL: baseURL + '/_accept_comment',
  deleteCommentURL: baseURL + '/_delete_comment',
  metadataURL: baseURL + '/_get_metadata',
  optionsURL: baseURL + '/_get_options',

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
  staticURL: staticURL
}

