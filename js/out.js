// main.js

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');

var FoodLookupField = React.createClass({
    displayName: 'FoodLookupField',

    getInitialState: function () {
        return { food: null };
    },
    componentDidMount: function () {
        var component = this;
        $('input.food-lookup-field').autocomplete({
            serviceUrl: '/api/food-lookup',
            type: 'POST',
            dataType: 'json',
            deferRequestBy: 300,
            onSearchStart: function () {
                // should provide feedback
                console.log("searchiing");
            },
            onSearchComplete: function (query, suggestions) {
                console.log("dne searchiing");
            },
            onSelect: function (suggestion) {
                var food_id = suggestion.data['food-id'];
                var food_desc = suggestion.value;
                component.props.onSelect({ description: food_desc, id: food_id });
            }
        });
    },
    reset: function () {
        console.log("resetting");
        $('input.food-lookup-field').val('');
    },
    render: function () {
        return React.createElement('input', { style: { width: "100%" },
            className: 'food-lookup-field',
            type: 'text',
            placeholder: 'Raw Apple' });
    }
});

var EntryForm = React.createClass({
    displayName: 'EntryForm',

    getInitialState: function () {
        return { count: 1, food: null, measures: [], measure_id: null };
    },
    handleFoodChange: function (food_obj) {
        this.fetchMeasures(food_obj.id);
        this.setState({ food: food_obj });
    },
    handleCountChange: function (e) {
        this.setState({ count: parseFloat(e.target.value) });
    },
    handleMeasureChange: function (e) {
        console.log('measure change');
        console.log(e);
        this.setState({ measure_id: e.target.value });
    },
    fetchMeasures: function (food_id) {
        var url = '/api/food/' + food_id + '/measures';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({ measures: data.measures,
                    measure_id: data.measures[0].id });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    handleSubmit: function (e) {
        e.preventDefault();

        $.ajax({
            type: 'post',
            url: this.props.url,
            dataType: 'json',
            success: function (data) {
                this.props.week_view.loadFromServer();
                this.setState(this.getInitialState());
                this.refs.food_lookup_field.reset();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this),
            data: this.state
        });
    },
    render: function () {
        var options = this.state.measures.map(function (o) {
            return React.createElement(
                'option',
                { value: o.id,
                    onChange: this.handleMeasureChange,
                    key: o.id },
                o.description
            );
        });

        var select;
        if (options.length != 0) {
            select = React.createElement(
                'select',
                { style: { width: "100%" },
                    onChange: this.handleMeasureChange },
                options
            );
        } else {
            select = React.createElement('div', { style: { width: "100%" } });
        }
        return React.createElement(
            'div',
            { className: 'row' },
            React.createElement(
                'form',
                { className: 'entryForm', onSubmit: this.handleSubmit },
                React.createElement(
                    'div',
                    { className: 'col-md-1' },
                    React.createElement('input', {
                        type: 'text',
                        size: '2',
                        value: this.state.count,
                        onChange: this.handleCountChange
                    })
                ),
                React.createElement(
                    'div',
                    { className: 'col-md-7' },
                    React.createElement(FoodLookupField, { ref: 'food_lookup_field',
                        onSelect: this.handleFoodChange })
                ),
                React.createElement(
                    'div',
                    { className: 'col-md-3' },
                    select
                ),
                React.createElement(
                    'div',
                    { className: 'col-md-1' },
                    React.createElement('input', {
                        style: { width: "100%" },
                        type: 'submit',
                        value: 'Post' })
                )
            )
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
            if (this.state.week[d].tags.length > 0) {
                empty = false;
                break;
            }
        }

        var days;
        if (empty) {
            days = React.createElement('p', null, 'Nothing to show!');
        } else {
            days = this.state.week.map(function (day) {
                return React.createElement(DayView, { tags: day.tags, date: day.date, key: day.date });
            });
            console.log(days);
        }
        return React.createElement('div', { className: 'week-view' }, days);
    }
});

var DayView = React.createClass({
    displayName: 'DayView',

    render: function () {
        console.log("got prop tags: ");
        console.log(this.props.tags);
        if (this.props.tags.length == 0) {
            return null;
        }
        var tags = this.props.tags.map(function (tag) {
            return React.createElement(TagView, { tag: tag, key: tag.at });
        });

        console.log('tags');
        console.log(tags);
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
                    tags
                )
            )
        );
    }
});

var TagView = React.createClass({
    displayName: 'TagView',
    render: function () {
        var tag = this.props.tag;
        return React.createElement(
            'tr',
            null,
            React.createElement(
                'td',
                { key: tag["id"] },
                tag["count"],
                '  ',
                tag["measure"]["description"],
                ' x  ',
                tag["food"]["description"]
            )
        );
    }
});

var home_week_view = ReactDOM.render(React.createElement(WeekView, { url: '/api/week' }), document.getElementById('week-view'));

ReactDOM.render(React.createElement(EntryForm, { url: '/api/entry', week_view: home_week_view }), document.getElementById('entry-form'));
