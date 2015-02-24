// Module exporting page-level variables for easy use
module.exports = {
	project: READTHEDOCS_DATA['project'],
	version: READTHEDOCS_DATA['version'],
	page: getPageName(),
	commit: getCommit()
}

function getPageName() {
	if ('page' in READTHEDOCS_DATA) {
	  return READTHEDOCS_DATA['page']
	} else {
	  stripped = window.location.pathname.substring(1)
	  stripped = stripped.replace(".html", "")
	  stripped = stripped.replace(/\/$/, "")
	  return stripped
	}
}

function getCommit() {
	if ('commit' in READTHEDOCS_DATA) {
	  return READTHEDOCS_DATA['commit']
	} else {
		return "unknown-commit"
	}
}
