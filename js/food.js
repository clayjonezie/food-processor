var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');
var main = require('./main_out');

var FoodEditForm = React.createClass({
    displayName: 'FoodEditForm',
    getInitialState: function () {
        return { food: null };
    },
    render: function () {
        console.log(this.state);
        if (this.state.food == null) {
            return (
                <p>loading</p>
            );
        } else {
            return (

            );
        }
    }
});

if (document.getElementById("food-edit-form")) {
    ReactDOM.render(
        <FoodEditForm />,
        document.getElementById("food-edit-form")
    );
}
