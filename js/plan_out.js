var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');

var GoalView = React.createClass({
    displayName: 'GoalView',

    render: function () {
        return React.createElement(
            'p',
            null,
            'goal'
        );
    }
});

ReactDOM.render(React.createElement(GoalView, null), document.getElementById("goal-view"));
