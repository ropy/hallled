import React from 'react';
import ReactDOM from 'react-dom';
import { CustomPicker } from 'react-color';
import $ from 'jquery';

class HallLedColorPicker extends React.Component {
    componentDidMount() {
      console.log("HallLedColorPicker did mount");
        $( "#hue" ).slider({
            orientation: "horizontal",
            range: "min",
            max: 360,
            step:1,
            value: 1,
            slide: function(){},
            change: function(){}
        });
    }

    render() {
        return (
            <div id="colorpicker">

                <div id="hue"></div>
                <div id="saturation"></div>
                <div id="lightning"></div>
                <div id="modulo"></div>
            </div>

        );
    }
}

ReactDOM.render(
    <HallLedColorPicker  />,
    document.getElementById('colorpicker')
);

export default CustomPicker(HallLedColorPicker);
