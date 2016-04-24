/**
 * Created by ropu on 30.01.16.
 */
var busy = false;

/** command, operator, value **/
var led_post_coa = function(c, o, a) {
    if(!busy) {
        busy = true;
        jQuery.ajax(
            {type: "POST",
                url: 'api/led/' + c + '/' + o + '/' + a, //python function
                data: {command: c, operator: o, amount: a},//data sent to server
                dataType: 'json',
                error: function(msg){
                    busy=false;
                    $("#ajaxerror").html(msg);
                },
                success: function(data){
                    busy=false;
                },
                timeout: 1000}
        )
    }
};

/** red, green, blue, modulo **/
var led_post_rgbm = function(r,g,b, modulo) {
    if(!busy) {
        busy = true;
        jQuery.ajax(
            {type: "POST",
                url: 'api/led/rgbm/' + r + '/' + g + '/' + b + '/' + modulo, //python function
                //data: {red: rgba.r, green: rgba.g,  b: rgba.b, a: rgba.a},//data sent to server
                dataType: 'json',
                error: function(msg){
                    busy=false;
                    $("#ajaxerror").html(msg);
                },
                success: function(data){
                    busy=false;
                },
                timeout: 1000}
        )
    }
};

/** hue, saturation, modulo, modulo **/
var led_post_hslm = function(h,s,l, modulo) {
    if(!busy) {
        busy = true;
        jQuery.ajax(
            {type: "POST",
                url: 'api/led/hslm/' + h + '/' + s + '/' + l + '/' + modulo, //python function
                //data: {red: rgba.r, green: rgba.g,  b: rgba.b, a: rgba.a},//data sent to server
                dataType: 'json',
                error: function(msg){
                    busy=false;
                    $("#ajaxerror").html(msg);
                },
                success: function(data){
                    busy=false;
                },
                timeout: 1000}
        )
    }
};

var loadLastState = function(url) {
    jQuery.ajax(
        {type: "GET",
            url: '/api/info', //python function
            dataType: 'json',
            error: function(msg){
                busy=false;
                $("#ajaxerror").html(msg);
            },
            success: function(data){
                setupSliders(data);
            },
            timeout: 1000}
    )
}

/**
*   the on slide function for sliders. triggered each time the slider is moved.
*/
function onSlide() {
    var hue = $( "#hue" ).slider( "value" ),
        saturation = $( "#saturation" ).slider( "value" ),
        lightning = $( "#lightning" ).slider( "value" ),
        modulo = $( "#modulo" ).slider( "value");

        refreshSwatch();

        led_post_hslm(hue, saturation, lightning, modulo);
}

/**
* the change function. triggered when a slider is released, i.e. the value changes
*/
function onChange() {
    var hue = $( "#hue" ).slider( "value" ),
        saturation = $( "#saturation" ).slider( "value" ),
        lightning = $( "#lightning" ).slider( "value"),
        modulo = $( "#modulo" ).slider( "value");

        refreshSwatch();
}

/*
* refresh the preview window
*/
function refreshSwatch() {
    var hue = $( "#hue" ).slider( "value" ),
        saturation = $( "#saturation" ).slider( "value" ),
        lightning = $( "#lightning" ).slider( "value" );

        var color = tinycolor({h: hue, s: 0.99, l: 0.5});

        $( "#saturation" ).css( "background" , "linear-gradient(to right, lightgrey , #" + color.toHex() + ")");
        $( "#lightning" ).css( "background" , "linear-gradient(to right, black , #" + color.toHex() + ")");
}

/** setup the sliders **/
function setupSliders(data) {

    $( "#hue" ).slider({
        orientation: "horizontal",
        range: "min",
        max: 360,
        step:1,
        value: data.h,
        slide: onSlide,
        change: onChange
    });

    $( "#saturation" ).slider({
        orientation: "horizontal",
        range: "min",
        max: 1,
        step:0.01,
        value:data.s,
        slide: onSlide,
        change: onChange
    });

    $( "#lightning" ).slider({
        orientation: "horizontal",
        range: "min",
        max: 1,
        step:0.01,
        value: data.l,
        slide: onSlide,
        change: onChange
    });

    $( "#modulo" ).slider({
        orientation: "horizontal",
        range: "min",
        min: 1,
        max: 50,
        value: data.m,
        slide: onSlide,
        change: onChange
    });
};

/** page load finished **/
jQuery(window).load(function () {
    // init sliders from last state
    loadLastState();
});
