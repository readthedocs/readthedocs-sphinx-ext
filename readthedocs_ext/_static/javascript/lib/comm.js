module.exports = {
  initMetaData: initMetaData,
  addComment: addComment,
  initOptions: initOptions
}

settings = require('./settings')
page = require('./page')
display = require('./display')

function getServerData(format) {
  return {
    "project": page.project,
    "version":  page.version,
    "page": page.page
  }
}

function initOptions() {
  var get_data = getServerData()

  $.ajax({
   type: 'GET',
   url: settings.opts.optionsURL,
   data: get_data,
   crossDomain: true,
   xhrFields: {
     withCredentials: true,
   },
   success: function(data, textStatus, request) {
    settings.opts = jQuery.extend(settings.opts, data);
   },
   error: function(request, textStatus, error) {
     showError('Oops, there was a problem retrieving the comment options.');
   },
  });
}


function initMetaData() {
  var get_data = getServerData()

  $.ajax({
   type: 'GET',
   url: settings.opts.metadataURL,
   data: get_data,
   crossDomain: true,
   xhrFields: {
     withCredentials: true,
   },
   success: function(data) {
      settings.metadata = data
      displayCommentIcon()
   },
   error: function(request, textStatus, error) {
     showError('Oops, there was a problem retrieving comment metadata.');
   },
  });
}

function displayCommentIcon() {
  // Only show data on the toc trees
  for (id in settings.metadata) {
      count = settings.metadata[id]
      console.log(id + ": " + count)
      var title = count + ' comment' + (count == 1 ? '' : 's');
      var image = count > 0 ? settings.opts.commentBrightImage : settings.opts.commentImage;
      var addcls = count == 0 ? ' nocomment' : '';
      addCommentIcon(id, title, image, addcls)
  }
}

function addCommentIcon(id, title, image, addcls) {
  $("#" + id)
      .append(
        $(document.createElement('a')).attr({
          href: '#',
          'class': 'sphinx-comment-open' + addcls,
          id: 'comment-open-' + id
        })
        .append($(document.createElement('img')).attr({
          src: image,
          alt: 'comment',
          title: title
        }))

      )
      .append(
        $(document.createElement('a')).attr({
          href: '#',
          'class': 'sphinx-comment-close hidden',
          id: 'comment-close-' + id
        })
        .append($(document.createElement('img')).attr({
          src: settings.opts.closeCommentImage,
          alt: 'close',
          title: 'close'
        }))
      );
}


function addComment(form) {
  var node_id = form.find('input[name="node"]').val();
  var text = form.find('textarea[name="comment"]').val();

  if (text == '') {
    showError('Please enter a comment.');
    return;
  }

  // Disable the form that is being submitted.
  form.find('textarea,input').attr('disabled', 'disabled');


  var server_data = getServerData();
  var comment_data = {
      node: node_id,
      text: text,
    };
  var post_data = $.extend(server_data, comment_data)


  // Send the comment to the server.
  $.ajax({
    type: "POST",
    url: settings.opts.addCommentURL,
    dataType: 'json',
    data: post_data,
    success: function(data, textStatus, error) {
      form.find('textarea')
        .val('')
        .add(form.find('input'))
        .removeAttr('disabled');
      display.showOneCommet($(".comment-list"), data)
      var comment_element = $('#' + node_id);
      comment_element.find('img').attr({'src': settings.opts.commentBrightImage});
      comment_element.find('a').removeClass('nocomment');
    },
    error: function(request, textStatus, error) {
      form.find('textarea,input').removeAttr('disabled');
      showError('Oops, there was a problem adding the comment.');
    }
  });
}


