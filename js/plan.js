var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');

var GoalView = React.createClass({
    render: function() {
        return (
            <p>goal</p>
        );
    }
});

ReactDOM.render(
    <GoalView />,
    document.getElementById("goal-view")
);
