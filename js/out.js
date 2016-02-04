// main.js

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');

var WeekView = React.createClass({
    displayName: 'WeekView',

    getInitialState: function () {
        return { week: [] };
    },
    loadFromServer: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({ week: data.week });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    componentDidMount: function () {
        this.loadFromServer();
    },
    render: function () {
        var days = this.state.week.map(function (day) {
            return React.createElement(DayView, { entries: day.entries, date: day.date, key: day.date });
        });
        return React.createElement(
            'div',
            { className: 'week-view' },
            days
        );
    }
});

var DayView = React.createClass({
    displayName: 'DayView',

    render: function () {
        var entries = this.props.entries.map(function (entry) {
            return React.createElement(EntryView, { entry: entry });
        });
        return React.createElement(
            'div',
            { className: 'day-view' },
            React.createElement(
                'h1',
                null,
                this.props.date
            ),
            entries
        );
    }
});

var EntryView = React.createClass({
    displayName: 'EntryView',

    render: function () {
        return React.createElement(
            'p',
            null,
            'an entry'
        );
    }
});

ReactDOM.render(React.createElement(WeekView, { url: '/api/week' }), document.getElementById('week-view'));
