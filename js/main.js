// main.js

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');

var WeekView = React.createClass({
    getInitialState: function() {
        return {week: []};
    },
    loadFromServer: function() {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            cache: false,
            success: function(data) {
                this.setState({week: data.week});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        })
    },
    componentDidMount: function() {
        this.loadFromServer();
    },
    render: function() {
        var days = this.state.week.map(function(day) {
            return (
                <DayView entries={day.entries} date={day.date} key={day.date}/>
            );
        });
        return (
            <div className="week-view">
                {days}
            </div>
        );
    }
});

var DayView = React.createClass({
    render: function() {
        var entries = this.props.entries.map(function(entry) {
            return (
                <EntryView entry={entry} />
            );
        });
        return (
            <div className="day-view">
                <h1>{this.props.date}</h1>
                {entries}
            </div>
        );
    }
});

var EntryView = React.createClass({
    render: function() {
        return (
            <p>an entry</p>
        );
    }
});

ReactDOM.render(
    <WeekView url="/api/week" />,
    document.getElementById('week-view')
);
