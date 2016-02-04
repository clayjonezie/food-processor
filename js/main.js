// main.js

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');

var EntryForm = React.createClass({
    getInitialState: function() {
        return {count: 1, food: null, measures: [], measure: null}
    },
    handleFoodChange: function(e) {
        console.log(e.target.value);
    },
    handleCountChange: function(e) {
        this.setState({count: parseFloat(e.target.value)})
    },
    handleMeasureChange: function(e) {
        console.log('measure change');
    },
    handleSubmit: function(e) {
        e.preventDefault();
        alert("submittttttttted to the server");
    },
    render: function() {
        var options = this.state.measures.map(function(o) {
            return (
                <option value={o.id}
                        onChange={this.handleMeasureChange}>
                    {o.description}</option>
            );
        });

        var select;
        if (options.length != 0) {
            select = <select onChange={this.handleMeasureChange}>
                {options}
            </select>
        } else {
            select = null;
        }
        return (
            <form className="entryForm" onSubmit={this.handleSubmit}>
                <input
                    type="text"
                    size="2"
                    value={this.state.count}
                    onChange={this.handleCountChange}
                />
                <input
                    type="text"
                    placeholder="Raw Apple"
                    value={this.state.food}
                    onChange={this.handleFoodChange}
                />
                {select}
                <input
                    type="submit"
                    value="Post" />
            </form>
        );
    }
});

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
        if (this.props.entries.length == 0) {
            return null;
        }
        var entries = this.props.entries.map(function(entry) {
            return (
                <EntryView entry={entry} key={entry.at} />
            );
        });
        return (
            <div className="day-view">
                <h2>{Moment(this.props.date).format("dddd, MMMM Do")}</h2>
                <table className="table table-bordered"><tbody>
                    {entries}
                </tbody></table>
            </div>
        );
    }
});

var EntryView = React.createClass({
    render: function() {
        var e = this.props.entry;

        var tags = e["tags"].map(function(tag) {
            return (
                <li key={tag["id"]}>{tag["count"]} &nbsp;
                    {tag["measure"]["description"]} x &nbsp;
                    {tag["food"]["description"]}</li>
            );
        });
        return (
            <tr>
                <td>{Moment(e["at"]).format("h:mm a")}</td>
                <td><ul style={{marginBottom: '0px'}}>{tags}</ul></td>
            </tr>
        );
    }
});

ReactDOM.render(
    <WeekView url="/api/week" />,
    document.getElementById('week-view')
);
ReactDOM.render(
    <EntryForm url="/api/entry" />,
    document.getElementById('entry-form')
);
