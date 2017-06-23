"use strict";
var page = require('webpage').create(),
    system = require('system'),
    address, output, size;

if (system.args.length < 3) {
    console.log('Usage: rasterize.js URL filename [paperwidth*paperheight|paperformat] [zoom]');
    console.log('  paper (pdf output) examples: "5in*7.5in", "10cm*20cm", "A4", "Letter"');
    console.log('  image (png/jpg output) examples: "1920px" entire page, window width 1920px');
    console.log('                                   "800px*600px" window, clipped to 800x600');
    phantom.exit(1);
} else {
    address = system.args[1];
    output = system.args[2];
    page.viewportSize = { width: "12.5in", height: "17.2in" };
    page.paperSize = {  width: "12.5in", height: "17.2in", margin: '1in',
    footer: {
      height: "1in",
      contents: phantom.callback(function(pageNum, numPages) {
        return "<h1><span>" + pageNum + " / " + numPages + "</span></h1>";
        })
      }
    }
    //{ format: "Letter", orientation: 'portrait', margin: '1cm' };
    page.open(address, function (status) {
        if (status !== 'success') {
            console.log('Unable to load the address!');
            phantom.exit(1);
        } else {
            window.setTimeout(function () {
                page.render(output);
                phantom.exit();
            }, 200);
        }
    });
}
