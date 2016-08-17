import React from 'react';
import ReactDOM from 'react-dom';
import update from 'react-addons-update';

export class OptionsComponent extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            busy: false,
            sensors: {
                motionSensor: {
                    timeout: 30, // seconds before the light goes off
                    enabled: "1"
                }
            }
        }
    }

    componentDidMount() {
        console.log("OptionComponent did mount.");
        $.ajax({
            type: "GET",
            url: this.props.post_url,
            //data: this.state.data,
            dataType: 'json',
            cache: false,
            success: function(data) {
                console.log(data);
                this.setState(data);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    }

    handleChange(e) {
        let[objectName, propertyName] = e.target.name.split(".");
        var sensors;
        // var abc = update(this.state.abc, {
        //     xyz: {$set: 'foo'}
        // });
        if(typeof propertyName === "undefined") {
            sensors = update(this.state.sensors, {
                [objectName] : {$set: e.target.value}
            })
        } else {
            sensors = update(this.state.sensors, {
                [objectName] : {
                   [propertyName] : {$set: e.target.value}
                }
            }) ;
        }

        this.setState({
            sensors : sensors
        }, function () {
            this.submit();
        });

    }

    submit() {

        if(!this.state.busy) {
            var data = JSON.stringify(this.state);
            this.state.busy = true;
            $.ajax({
                url: this.props.post_url,
                type: 'POST',
                dataType: 'json',
                data: data,
                success: function(response) {
                    console.log("submitColor: success", response);
                    this.setState({response: response});
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
            <div className="optionsComponent">
                <h4>Options</h4>

                <form className="form-inline" onSubmit={this.handleChange.bind(this)}>
                    <h3>Motion Sensor</h3>
                    <div className="btn-group">
                        <label className="radio-inline">
                                <input type="radio" name="motionSensor.enabled"
                                       checked={this.state.sensors.motionSensor.enabled === "1"}
                                       onChange={this.handleChange.bind(this)}
                                       value="1"
                                />
                            Enabled
                        </label>
                        <label className="radio-inline">
                            <input type="radio" name="motionSensor.enabled"
                                   checked={this.state.sensors.motionSensor.enabled === "0"}
                                   onChange={this.handleChange.bind(this)}
                                   value="0"/>
                            Disabled
                        </label>
                        <br/>
                        <label for="usr">Timeout:</label>
                        <input type="text" className="form-control" name="motionSensor.timeout"
                               value={this.state.sensors.motionSensor.timeout}
                               onChange={this.handleChange.bind(this)}/>
                    </div>
                </form>
            </div>
        )
    }
}

ReactDOM.render(<OptionsComponent url='/api/info' post_url='/api/options' />, document.getElementById("options"));