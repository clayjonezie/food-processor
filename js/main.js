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
                component.props.onSelect({description: food_desc, id: food_id});
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
        return (
            <input style={{width: "100%"}}
                   className="food-lookup-field"
                   type="text"
                   placeholder="Raw Apple"
            />
        );
    }
});

var EntrySuggestions = React.createClass({
    getInitialState: function() {
        return { suggestions: [] };
    },
    componentDidMount: function() {
        this.fetchFromServer();
    },
    fetchFromServer: function() {
        var url = '/api/suggestions';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (data) {
                this.setState({suggestions: data.suggestions});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    suggestionClicked: function(e) {
        var key = $(e.target).attr('data-key');
        this.props.onSelection(this.state.suggestions[key]);
    },
    render: function() {
        var suggestions = this.state.suggestions.map(function(suggestion, i) {
            return (
                <li key={i}><a role="button" data-key={i} onClick={this.suggestionClicked}>
                    {suggestion.food_desc}</a></li>
            );
        }.bind(this));
        return (
            <ul>{suggestions}</ul>
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
        this.setState({food: food_obj});
    },
    handleCountChange: function (e) {
        this.setState({ count: e.target.value });
    },
    handleMeasureChange: function (e) {
        this.setState({ measure_id: e.target.value });
    },
    fetchMeasures: function(food_id, measure_id) {
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
                this.setState({measures: data.measures,
                               measure_id: new_measure_id});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    handleSuggestionSelection: function(suggestion) {
        this.fetchMeasures(suggestion['food_id'], suggestion['measure_id']);
        this.setState({food: {description: suggestion['food_desc'],
                              id: suggestion['food_id']},
                       count: suggestion['count']})
    },
    handleSubmit: function (e) {
        e.preventDefault();

        if (parseFloat(this.state.count) == NaN) {
            alert("count must be a number")
            return;
        } else {
            this.setState({count: parseFloat(this.state.count)})
        }

        $.ajax({
            type: 'post',
            url: this.props.url,
            dataType: 'json',
            success: function(data) {
                this.props.week_view.loadFromServer();
                this.setState(this.getInitialState());
                this.refs.food_lookup_field.reset();
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this),
            data: this.state
        })
    },
    render: function () {
        var options = this.state.measures.map(function (o) {
            return (
                <option value={o.id}
                        onChange={this.handleMeasureChange}
                        key={o.id}>
                    {o.description}</option>
            );
        }.bind(this));

        var select;
        if (options.length != 0) {
            select =
                <select style={{width:"100%"}} value={this.state.measure_id}
                    onChange={this.handleMeasureChange}>
                {options}
            </select>
        } else {
            select = <div style={{width:"100%"}}></div>
        }
        return (
            <div>
                <div className="row">
                    <div className="col-md-12"><h2>What have you had to eat?</h2></div>
                </div>
                <div className="row">
                    <form className="entryForm" onSubmit={this.handleSubmit}>
                        <div className="col-md-7">
                            <FoodLookupField ref="food_lookup_field"
                                             onSelect={this.handleFoodChange}
                                             food={this.state.food} />
                        </div>
                        <div className="col-md-1">
                            <input
                                type="text"
                                size="2"
                                value={this.state.count}
                                onChange={this.handleCountChange}
                            />
                        </div>
                        <div className="col-md-3">
                            {select}
                        </div>
                        <div className="col-md-1">
                            <input
                                style={{width: "100%"}}
                                type="submit"
                                value="Post" />
                        </div>
                    </form>
                </div>
                <div className="row suggestions">
                    <EntrySuggestions onSelection={this.handleSuggestionSelection} />
                </div>
            </div>
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
            days = React.createElement(
                'p',
                null,
                'Nothing to show!'
            );
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

        return (
           <div className="week-view">
               <DayGoalsChart ref="DayGoalsChart"/>
               {days}
           </div>
        )
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
            return (<TagView tag={tag} key={tag.at} refresh={refresh} />);
        });

        return (
            <div className="day-view">
                <h2>{Moment(this.props.date).format("dddd, MMMM Do")}</h2>
                <table className="table table-bordered"><tbody>
                    {tags}
                </tbody></table>
            </div>
        );
    }
});

var TagView = React.createClass({
    displayName: 'TagView',
    remove: function() {
        var url = '/api/entry/delete'
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
        })
    },
    render: function () {
        var tag = this.props.tag;
        return (
            <tr><td key={tag["id"]}>{tag["count"]} &nbsp;
                {tag["measure"]["description"]} x &nbsp;
                {tag["food"]["description"]}
            <a style={{float: 'right'}} onClick={this.remove}>(delete)</a>
            </td></tr>
        );
    }
});

var DayGoalsChart = React.createClass({
    displayName: 'DayGoalsChart',
    componentDidMount: function () {
        // this.loadFromServer();
    },
    drawChart: function(data) {
        var margin = {top: 20, right: 30, bottom: 30, left: 40},
            width = 960 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var y = d3.scale.linear().range([height, 0]).domain([0, 1]);
        var x = d3.scale.linear().range([width, 0]).domain([0, 1]);
        var barWidth = width / data.length;
        var yAxis = d3.svg.axis().scale(y).orient("left").tickFormat(function(d) {
            return d * 100;
        });
        var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks([]);

        d3.select("#DayGoalsChart").selectAll("*").remove();

        var chart = d3.select("#DayGoalsChart")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        chart.append("g").attr("class", "y axis").call(yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Percent of Goal");

        chart.append("g").attr("class", "x axis").call(xAxis)
            .attr("transform", "translate(0, " + height + ")");

        var bar = chart.selectAll().data(data).enter().append("g").attr("class", "bar")
            .attr("transform", function(d, i) {return "translate(" + i * barWidth + ", 0)"; });

        bar.append("rect")
            .attr("y", function(d) { return y(d.value); })
            .attr("height", function(d) { return height - y(d.value); })
            .attr("width", barWidth - 1);

        bar.append("text")
            .attr("x", barWidth / 2)
            .attr("y", height)
            .attr("dy", "1em")
            .text(function(d) { return d.current.toFixed(1) + "/" + d.total + "(" + d.unit + ") " + d.label; });
    },
    loadFromServer: function() {
        var url = '/api/graphs/day_nutrients';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function (response) {
                this.setState({data: response.data});
                this.drawChart(this.state.data);
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function() {
        return <svg id="DayGoalsChart" height="400" width="400"></svg>
    }
});

var home_week_view = ReactDOM.render(
    <WeekView url="/api/week" />,
    document.getElementById('week-view')
);

ReactDOM.render(
    <EntryForm url="/api/entry" week_view={home_week_view} />,
    document.getElementById('entry-form')
);
