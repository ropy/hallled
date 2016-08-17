import React from 'react';
import ReactDOM from 'react-dom';
import { SliderPicker } from 'react-color';
import ReactSlider from 'react-slider';

export class HallLedColorPicker extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            color: {
                hsl: {
                    hue:1,
                    saturation:127,
                    lightning:127
                }
            },
            busy: false,
            mod: 50 // inverse
        };
    }


    componentDidMount() {
        console.log("HallLedColorPicker did mount");

        this.getColor();


    }

    initSliders() {
        $( "#hue" ).slider({
            orientation: "horizontal",
            range: "min",
            max: 360,
            step:1,
            value: this.state.color.hsl.hue,
            slide: this.handleHueChange.bind(this),
            change: this.handleHueChange.bind(this)
        });

        $( "#saturation" ).slider({
            orientation: "horizontal",
            range: "min",
            max: 1,
            step:0.01,
            value: this.state.color.hsl.saturation,
            slide: this.handleHueChange.bind(this),
            change: this.handleHueChange.bind(this)
        });

        $( "#lightning" ).slider({
            orientation: "horizontal",
            range: "min",
            max: 1,
            step:0.01,
            value: this.state.color.hsl.lightning,
            slide: this.handleHueChange.bind(this),
            change: this.handleHueChange.bind(this)
        });

        $( "#modulo" ).slider({
            orientation: "horizontal",
            range: "min",
            min: 1,
            max: 50,
            value: 51-this.state.mod,
            slide: this.handleHueChange.bind(this),
            change: this.handleHueChange.bind(this)
        });

        this.handleHueChange();
    }

    getColor() {
        $.ajax({
            type: "GET",
            url: this.props.post_url,
            //data: this.state.data,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log(data);
                this.setState(data, this.initSliders);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    }

    handleHueChange() {
        // console.log("handleHueChange props: ", this);
        var hue = $( "#hue" ).slider( "value" ),
            saturation = $( "#saturation" ).slider( "value" ),
            lightning = $( "#lightning" ).slider( "value"),
            modulo = $( "#modulo" ).slider( "value");
        
        // var abc = update(this.state.abc, {
        //     xyz: {$set: 'foo'}
        // });
        this.setState( {
            color : {
                hsl:{
                    hue:hue,
                    saturation:saturation,
                    lightning:lightning
                }
            },
            mod: 50-modulo
        }, function () {
            // console.log(50-modulo);
            var color = tinycolor({h: hue, s: 0.99, l: 0.5});
            $( "#saturation" ).css( "background" , "linear-gradient(to right, lightgrey , #" + color.toHex() + ")");
            $( "#lightning" ).css( "background" , "linear-gradient(to right, black , #" + color.toHex() + ")");
            this.submitColor();
        });

    }

    submitColor() {
        console.log("submit: state is ", this.state);
        if(!this.state.busy) {
            var data = JSON.stringify(this.state);
            this.state.busy = true;
            $.ajax({
                url: this.props.post_url,
                type: 'POST',
                dataType: 'json',
                data: data,
                success: function(data) {
                    console.log("submitColor: success", data);
                    this.setState({data: data});
                    this.setState({busy: false});
                }.bind(this),
                    error: function(xhr, status, err) {
                    console.log("submitColor: success");
                    console.error(this.props.url, status, err.toString());
                    this.setState({busy: false});
                }.bind(this)
            });
        }
    }


    render() {
        return (
            <div>
                <div id="hue"></div>
                <div id="saturation"></div>
                <div id="lightning"></div>
                <div id="modulo"></div>
            </div>
        );
    }
}

ReactDOM.render(
    <HallLedColorPicker  url='/api/info' post_url='/api/led/hslm' />,
    document.getElementById('colorpicker')
);

/**
 *                 <!-- <SliderPicker
 //     color={ this.state.selectedColor }
 //     onChangeComplete={ this.handleChange.bind(this) }
 //     onChange={ this.handleChange.bind(this) }
 // /-->
 **/