// main.js

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');

var FoodLookupField = React.createClass({
    displayName: 'FoodLookupField',

    getInitialState: function () {
        return { food: null };
    },
    componentDidMount: function () {
        var component = this;
        $('input.food-lookup-field').autocomplete({
            serviceUrl: '/api/food_lookup',
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
        $('input.food-lookup-field').val('');
    },
    render: function () {
        if (this.props.food != null) {
            $("input.food-lookup-field").val(this.props.food.description);
        }
        return React.createElement('input', { style: { width: "100%" },
            className: 'food-lookup-field',
            type: 'text',
            placeholder: 'Raw Apple'
        });
    }
});

var EntrySuggestions = React.createClass({
    displayName: 'EntrySuggestions',

    getInitialState: function () {
        return { suggestions: [] };
    },
    componentDidMount: function () {
        this.fetchFromServer();
    },
    fetchFromServer: function () {
        var url = '/api/suggestions';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({ suggestions: data.suggestions });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    suggestionClicked: function (e) {
        var key = $(e.target).attr('data-key');
        this.props.onSelection(this.state.suggestions[key]);
    },
    render: function () {
        var suggestions = this.state.suggestions.map(function (suggestion, i) {
            return React.createElement(
                'li',
                { key: i },
                React.createElement(
                    'a',
                    { role: 'button', 'data-key': i, onClick: this.suggestionClicked },
                    suggestion.food_desc
                )
            );
        }.bind(this));
        return React.createElement(
            'ul',
            null,
            suggestions
        );
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
        this.setState({ count: e.target.value });
    },
    handleMeasureChange: function (e) {
        this.setState({ measure_id: e.target.value });
    },
    fetchMeasures: function (food_id, measure_id) {
        var url = '/api/food/' + food_id + '/measures';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                var new_measure_id = measure_id;
                if (new_measure_id == null) {
                    new_measure_id = data.measures[0].id;
                }
                this.setState({ measures: data.measures,
                    measure_id: new_measure_id });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    handleSuggestionSelection: function (suggestion) {
        this.fetchMeasures(suggestion['food_id'], suggestion['measure_id']);
        this.setState({ food: { description: suggestion['food_desc'],
                id: suggestion['food_id'] },
            count: suggestion['count'] });
    },
    handleSubmit: function (e) {
        e.preventDefault();

        if (parseFloat(this.state.count) == NaN) {
            alert("count must be a number");
            return;
        } else {
            this.setState({ count: parseFloat(this.state.count) });
        }

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
        }.bind(this));

        var select;
        if (options.length != 0) {
            select = React.createElement(
                'select',
                { style: { width: "100%" }, value: this.state.measure_id,
                    onChange: this.handleMeasureChange },
                options
            );
        } else {
            select = React.createElement('div', { style: { width: "100%" } });
        }
        return React.createElement(
            'div',
            null,
            React.createElement(
                'div',
                { className: 'row' },
                React.createElement(
                    'div',
                    { className: 'col-md-12' },
                    React.createElement(
                        'h2',
                        null,
                        'What have you eaten?'
                    )
                )
            ),
            React.createElement(
                'div',
                { className: 'row' },
                React.createElement(
                    'form',
                    { className: 'entryForm', onSubmit: this.handleSubmit },
                    React.createElement(
                        'div',
                        { className: 'col-md-7' },
                        React.createElement(FoodLookupField, { ref: 'food_lookup_field',
                            onSelect: this.handleFoodChange,
                            food: this.state.food })
                    ),
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
            ),
            React.createElement(
                'div',
                { className: 'row suggestions' },
                React.createElement(EntrySuggestions, { onSelection: this.handleSuggestionSelection })
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
        this.refs.DayGoalsChart.loadFromServer();
        this.refs.DayMacrosChart.loadFromServer();
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
            var loadFromServer = this.loadFromServer;
            days = this.state.week.map(function (day) {
                return React.createElement(DayView, {
                    tags: day.tags,
                    date: day.date,
                    key: day.date,
                    refresh: loadFromServer
                });
            });
        }

        return React.createElement(
            'div',
            { className: 'week-view' },
            React.createElement(DayGoalsChart, { ref: 'DayGoalsChart' }),
            React.createElement(DayMacrosChart, { ref: 'DayMacrosChart' }),
            days
        );
    }
});

var DayView = React.createClass({
    displayName: 'DayView',

    render: function () {
        if (this.props.tags.length == 0) {
            return null;
        }
        var refresh = this.props.refresh;
        var tags = this.props.tags.map(function (tag) {
            return React.createElement(TagView, { tag: tag, key: tag.at, refresh: refresh });
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
                    tags
                )
            )
        );
    }
});

var TagView = React.createClass({
    displayName: 'TagView',
    remove: function () {
        var url = '/api/entry/delete';
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'json',
            cache: false,
            data: this.props.tag,
            success: function (response) {
                this.props.refresh();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
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
                tag["food"]["description"],
                React.createElement(
                    'a',
                    { style: { float: 'right' }, onClick: this.remove },
                    '(delete)'
                )
            )
        );
    }
});

var DayGoalsChart = React.createClass({
    displayName: 'DayGoalsChart',
    componentDidMount: function () {
        // this.loadFromServer();
    },
    drawChart: function (data) {
        var margin = { top: 20, right: 30, bottom: 30, left: 40 },
            width = 960 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var y = d3.scale.linear().range([height, 0]).domain([0, 1]);
        var x = d3.scale.linear().range([width, 0]).domain([0, 1]);
        var barWidth = width / data.length;
        var yAxis = d3.svg.axis().scale(y).orient("left").tickFormat(function (d) {
            return d * 100;
        });
        var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks([]);

        d3.select("#DayGoalsChart").selectAll("*").remove();

        var chart = d3.select("#DayGoalsChart").attr("width", width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom).append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        chart.append("g").attr("class", "y axis").call(yAxis).append("text").attr("transform", "rotate(-90)").attr("y", 6).attr("z", 190090).attr("dy", ".71em").style("text-anchor", "end").text("Percent of Goal");

        chart.append("g").attr("class", "x axis").call(xAxis).attr("transform", "translate(0, " + height + ")");

        var bar = chart.selectAll().data(data).enter().append("g").attr("class", "bar").attr("transform", function (d, i) {
            return "translate(" + i * barWidth + ", 0)";
        });

        bar.append("rect").attr("y", function (d) {
            return Math.max(0, y(d.value));
        }).attr("height", function (d) {
            return Math.min(height - y(d.value), height);
        }).attr("width", barWidth - 1).attr("fill", function (d) {
            // l scales from 31 to 100
            var l = 50 + (1 - Math.min(1, d.value)) * 50;
            return "hsl(234, 70%, " + l + "%)";
        });

        bar.append("text").attr("width", barWidth).attr("x", barWidth / 2).attr("y", function (d) {
            return Math.min(Math.max(0, y(d.value)), height - 16);
        }).attr("dy", "1em").text(function (d) {
            return d.current.toFixed(1) + "/" + d.total + " " + d.unit;
        });
        bar.append("text").attr("x", barWidth / 2).attr("y", height).attr("dy", "1em").text(function (d) {
            return d.label;
        });
    },
    loadFromServer: function () {
        var url = '/api/graphs/day_nutrients';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (response) {
                this.setState({ data: response.data });
                this.drawChart(this.state.data);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        return React.createElement('svg', { id: 'DayGoalsChart', height: '400', width: '400' });
    }
});

var DayMacrosChart = React.createClass({
    displayName: 'DayMacrosChart',
    drawChart: function () {
        var key_height = 50;
        var chart_height = 100;
        var width = 960,
            height = chart_height + key_height;
        d3.select("#DayMacrosChart").selectAll("*").remove();

        var graph = d3.select("#DayMacrosChart").attr("width", width).attr("height", height);

        var key = graph.append("g").attr("height", key_height).attr("width", width);
        var chart = graph.append("g").attr("height", chart_height).attr("width", width).attr("transform", "translate(0, " + key_height + ")");

        var key_node_height = 10,
            key_node_padding = 5,
            text_height = 16;
        key.append("rect").attr("height", 10).attr("width", 10).attr("x", 0).attr("y", key_node_padding + (text_height - key_node_height) / 2).attr("class", "carbohydrate key");
        key.append("text").attr("x", key_node_height + key_node_height).attr("y", key_node_padding).attr("dy", "1em").text("carbohydrate");
        key.append("rect").attr("height", 10).attr("width", 10).attr("x", 0).attr("y", key_node_height + key_node_padding * 2 + (text_height - key_node_height) / 2).attr("class", "protein key");
        key.append("text").attr("x", key_node_height + key_node_height).attr("y", key_node_padding * 2 + key_node_height).attr("dy", "1em").text("protein");
        key.append("rect").attr("height", 10).attr("width", 10).attr("x", 0).attr("y", key_node_height * 2 + key_node_padding * 3 + (text_height - key_node_height) / 2).attr("class", "fat key");
        key.append("text").attr("x", key_node_height + key_node_height).attr("y", key_node_padding * 3 + key_node_height * 2).attr("dy", "1em").text("fat");

        console.log(this.state.data);

        var total_cals = this.state.data["total"]["calories"];
        var carbohydrate_width = width * this.state.data["carbohydrate"]["calories"] / total_cals;
        var protein_width = width * this.state.data["protein"]["calories"] / total_cals;
        var fat_width = width * this.state.data["fat"]["calories"] / total_cals;

        chart.append("rect").attr("height", chart_height).attr("width", carbohydrate_width).attr("x", 0).attr("class", "carbohydrate");
        chart.append("rect").attr("height", chart_height).attr("width", protein_width).attr("x", carbohydrate_width).attr("class", "protein");
        chart.append("rect").attr("height", chart_height).attr("width", fat_width).attr("x", carbohydrate_width + protein_width).attr("class", "fat");
    },
    loadFromServer: function () {
        var url = '/api/graphs/day_macros';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (response) {
                this.setState({ data: response.data });
                this.drawChart({ data: response.data });
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function () {
        return React.createElement('svg', { id: 'DayMacrosChart', height: '100', width: '400' });
    }
});

var home_week_view = ReactDOM.render(React.createElement(WeekView, { url: '/api/week' }), document.getElementById('week-view'));

ReactDOM.render(React.createElement(EntryForm, { url: '/api/entry', week_view: home_week_view }), document.getElementById('entry-form'));