module.exports = {
    initDisplay: initDisplay,
    displayComments: displayComments,
    showOneCommet: showOneCommet,
    closeComments: closeComments
}

comm = require('./comm')

function initDisplay() {
    $('body').append("<div id='current-comment'></div>");
    $('body').append("<div id='pageslide'></div>");
}

function closeComments() {
  $.pageslide.close()
}

function displayComments(id) {
  server_data = comm.getServerData()
  get_data = {
    'node': id
  }
  var post_data = $.extend(get_data, server_data)
  delete post_data['page']

  $.ajax({
   type: 'GET',
   url: settings.opts.getCommentsURL,
   data: post_data,
   crossDomain: true,
   xhrFields: {
     withCredentials: true,
   },
   success: function(data) {
       handleComments(id, data)

   },
   error: function(request, textStatus, error) {
     showError('Oops, there was a problem retrieving the comments.');
   },
   dataType: 'json'
  });
}


function handleComments(id, data) {
    showComments(id, data.results)
}


function showComments(id, comment_data) {
  element = $('#current-comment').html("<h1> Comments </h1>")
  element.append("<div class='comment-list' id='current-comment-list'>")
  for (index in comment_data) {
      obj = comment_data[index]
      showOneCommet($(".comment-list"), obj)
  }
  element.append("</div>")
  var reply = '\
      <div class="reply-div" id="comment-reply-' + id + '>">\
        <form class= "comment-reply-form" id="comment-reply-form-' + id + '">\
          <textarea name="comment" cols="40"></textarea>\
          <input type="submit" value="Add Comment" />\
          <input type="hidden" name="node" value="' + id + '" />\
        </form>\
      </div>'

  element.append("<div class='comment-div' id='current-comment-reply'>")
  $(".comment-div").append(reply)
  element.append("</div>")

  element.append("<br><br><br>")
  element.append("<hr>")
  element.append("<br><br><br>")
  element.append("<h1>Floating Comments</h1>")
    element.append("<div class='floating-comment-list' id='floating-comment-list'>")
    for (index in comment_data) {
        obj = comment_data[index]
        showOneCommet($(".floating-comment-list"), obj)
        var attach = '\
            <div class="attach-div" id="comment-attach-' + id + '>">\
              <form class= "comment-attach-form" id="comment-attach-form' + id + '">\
                <input type="submit" value="Attach" />\
                <input type="hidden" name="node" value="' + id + '" />\
                <input type="hidden" name="comment" value="' + obj['pk'] + '" />\
              </form>\
            </div>'

    }
  element.append("<div class='floating-comment-div' id='floating-comment-reply'>")
  $(".floating-comment-div").append(attach)
  element.append("</div>")

    element.append("</div>")
  element.append("</div>")

  $.pageslide({direction: 'left', href:'#current-comment' })
}

function showOneCommet(element, comment) {
    console.log("Displaying")
    console.log(comment)
      to_append = "<span class='comment'>"
      to_append += comment['date'] + "<br>"
      to_append += comment['text']
      to_append += "</span>"
      element.append(to_append)
}

  function showError(message) {
    $(document.createElement('div')).attr({'class': 'popup-error'})
      .append($(document.createElement('div'))
               .attr({'class': 'error-message'}).text(message))
      .appendTo('body')
      .fadeIn("slow")
      .delay(2000)
      .fadeOut("slow");
  }

// Don't need this since its in the page.

/*
function setUpPageslide() {
    $.ajax({
        url: "https://api.grokthedocs.com/static/javascript/pageslide/jquery.pageslide.js",
        crossDomain: true,
        dataType: "script",
        cache: true,
        success: function () {
            console.log("Loaded pageslide")
            $('head').append('<link rel="stylesheet" href="https://api.grokthedocs.com/static/css/top.css" type="text/css" />');
            $('body').append("<div id='gtd-top'></div>");
        },
        error: function (e) {
            console.log("OMG FAIL:" + e)
        }

    });
}
*/