/**
 * Created by ropu on 20.06.16.
 */

import React from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';

var ByteBox = React.createClass({
    getInitialState: function() {
        return {data: []};
    },
    componentDidMount: function() {
        // $.ajax({
        //     type: "GET",
        //     url: this.props.url,
        //     //data: this.state.data,
        //     dataType: 'json',
        //     cache: false,
        //     success: function(data) {
        //         console.log(data);
        //         this.setState({
        //             data: data,
        //             data_string: JSON.stringify(data)
        //         });
        //     }.bind(this),
        //     error: function(xhr, status, err) {
        //         console.error(this.props.url, status, err.toString());
        //     }.bind(this)
        // });
    },
    handleBytesChange: function(e) {
        this.setState({bytes: e.target.value});
    },
    handleSubmit: function(e) {
        e.preventDefault();

        $.ajax({
            url: this.props.post_url,
            type: 'POST',
            data: this.state.bytes,
            success: function(data) {
                this.setState({data: data});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });

        console.log(e.target);

        this.refs.bytes_input.value = ""; // Unset the value
        this.setState({bytes: ''});
    },

    render: function() {
        return (
            <div className="byteBox">
                <h4>Bytes</h4>

                <form className="byteForm" onSubmit={this.handleSubmit}>
                    <input type="text" ref="bytes_input" placeholder="bytes..." onChange={this.handleBytesChange} />
                    <input type="submit" value="Send" />
                </form>
            </div>
        );
    }
});

ReactDOM.render(
    <ByteBox url='/api/info' post_url='/api/pipe' />,
    document.getElementById('bytebox')
);


