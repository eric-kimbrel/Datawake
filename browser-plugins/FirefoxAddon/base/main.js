//Datawake Components
require("sdk/preferences/service").set("extensions.sdk.console.logLevel", "info");

// Set up the overly to run content scripts
// and setup datawakeinfo for each tab
var datawakeNewTabHelper = require("./datawake/overlay");
datawakeNewTabHelper.useDatawake();

// Set up the toggle button that loads the datawake panel
var buttonHelper = require("./datawake/panel-addon");
buttonHelper.useButton();

