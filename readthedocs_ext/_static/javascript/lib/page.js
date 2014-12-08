// Module exporting page-level variables for easy use
module.exports = {
	project: doc_slug,
	version: doc_version,
	page: getPageName()
}

function getPageName() {
	if (typeof page_name != "undefined") {
	  return page_name
	} else {
	  stripped = window.location.pathname.substring(1)
	  stripped = stripped.replace(".html", "")
	  stripped = stripped.replace(/\/$/, "")
	  return stripped
	}
}
