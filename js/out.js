// main.js

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');

var FoodLookupField = React.createClass({
    displayName: 'FoodLookupField',

    getInitialState: function () {
        return { food: { description: '', id: 0 } };
    },
    componentDidMount: function () {
        $('input.food-lookup-field').autocomplete({
            serviceUrl: '/api/food-lookup',
            type: 'POST',
            dataType: 'json',
            deferRequestBy: 300,
            onSearchStart: function () {
                // should provide feedback
            },
            onSearchComplete: function (query, suggestions) {},
            onSelect: function (suggestion) {
                var food_id = suggestion.data['food-id'];
                var food_desc = suggestion.value;

                this.props.onSelect();
            }
        });
    },
    render: function () {
        return React.createElement('input', { className: 'food-lookup-field',
            type: 'text',
            placeholder: 'Raw Apple' });
    }
});

var EntryForm = React.createClass({
    displayName: 'EntryForm',

    getInitialState: function () {
        return { count: 1, food: null, measures: [], measure: null };
    },
    handleFoodChange: function () {
        console.log("food change!");
    },
    handleCountChange: function (e) {
        this.setState({ count: parseFloat(e.target.value) });
    },
    handleMeasureChange: function (e) {
        console.log('measure change');
    },
    handleSubmit: function (e) {
        e.preventDefault();
        alert("submittttttttted to the server");
    },
    render: function () {
        var options = this.state.measures.map(function (o) {
            return React.createElement(
                'option',
                { value: o.id,
                    onChange: this.handleMeasureChange },
                o.description
            );
        });

        var select;
        if (options.length != 0) {
            select = React.createElement(
                'select',
                { onChange: this.handleMeasureChange },
                options
            );
        } else {
            select = null;
        }
        return React.createElement(
            'form',
            { className: 'entryForm', onSubmit: this.handleSubmit },
            React.createElement('input', {
                type: 'text',
                size: '2',
                value: this.state.count,
                onChange: this.handleCountChange
            }),
            React.createElement(FoodLookupField, null),
            select,
            React.createElement('input', {
                type: 'submit',
                value: 'Post' })
        );
    }
});

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

        var empty = true;
        for (var d in this.state.week) {
            if (this.state.week[d].entries.length > 0) {
                empty = false;
                break;
            }
        }

        var days;
        if (empty) {
            days = React.createElement('p', null, 'Nothing to show!');
        } else {
            days = this.state.week.map(function (day) {
                return React.createElement(DayView, { entries: day.entries, date: day.date, key: day.date });
            });
        }
        return React.createElement('div', { className: 'week-view' }, days);
    }
});

var DayView = React.createClass({
    displayName: 'DayView',

    render: function () {
        if (this.props.entries.length == 0) {
            return null;
        }
        var entries = this.props.entries.map(function (entry) {
            React.createElement(EntryView, { entry: entry, key: entry.at });
        });
        return React.createElement(
            'div',
            { className: 'day-view' },
            React.createElement(
                'h2',
                null,
                Moment(this.props.date).format("dddd, MMMM Do")
            ),
            React.createElement(
                'table',
                { className: 'table table-bordered' },
                React.createElement(
                    'tbody',
                    null,
                    entries
                )
            )
        );
    }
});

var EntryView = React.createClass({
    displayName: 'EntryView',

    render: function () {
        var e = this.props.entry;

        var tags = e["tags"].map(function (tag) {
            return React.createElement(
                'li',
                { key: tag["id"] },
                tag["count"],
                '  ',
                tag["measure"]["description"],
                ' x  ',
                tag["food"]["description"]
            );
        });
        return React.createElement(
            'tr',
            null,
            React.createElement(
                'td',
                null,
                Moment(e["at"]).format("h:mm a")
            ),
            React.createElement(
                'td',
                null,
                React.createElement(
                    'ul',
                    { style: { marginBottom: '0px' } },
                    tags
                )
            )
        );
    }
});

ReactDOM.render(React.createElement(WeekView, { url: '/api/week' }), document.getElementById('week-view'));
ReactDOM.render(React.createElement(EntryForm, { url: '/api/entry' }), document.getElementById('entry-form'));
