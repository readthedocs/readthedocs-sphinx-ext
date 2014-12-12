module.exports = {
	initEvents: initEvents
}

display = require('./display')

function initEvents() {
	$(document).on("click", "a.sphinx-comment-open", function(event) {
		event.preventDefault();
		display.displayComments($(this).attr('id').substring('comment-open-'.length));
	})
	$(document).on("click", "a.sphinx-comment-close", function(event) {
		event.preventDefault();
		display.closeComments($(this).attr('id').substring('comment-close-'.length));
	})

	$(document).on("submit", ".comment-reply-form", function(event) {
		event.preventDefault();
		comm.addComment($(this));
	})

	$(document).on("submit", ".comment-attach-form", function(event) {
		event.preventDefault();
		comm.attachComment($(this));
	})
}

