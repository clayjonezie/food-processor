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
                   className="food-lookup-field form-control"
                   type="text"
                   placeholder="Raw Apple"
            />
        );
    }
});

var EntrySuggestions = React.createClass({
    getInitialState: function() {
        return { suggestions: {plan: [], frequency: []} };
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
                var frequency_suggestions = data.suggestions.filter(function(suggestion) {
                    return suggestion['type'] == 'frequency';
                });
                var plan_suggestions = data.suggestions.filter(function(suggestion) {
                    return suggestion['type'] == 'plan';
                });

                this.setState({suggestions: {plan: plan_suggestions, frequency: frequency_suggestions}});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    suggestionClicked: function(e) {
        var key = $(e.target).attr('data-key');
        var arr = $(e.target).attr('data-arr');
        console.log(key);
        console.log(arr);
        this.props.onSelection(this.state.suggestions[arr][key]);
    },
    render: function() {
        var plan_suggestions = this.state.suggestions.plan.map(function(suggestion, i) {
            return (
                <tr key={i}><td data-key={i} data-arr="plan" onClick={this.suggestionClicked}>
                    {suggestion.food_desc}
                </td></tr>
            );
        }.bind(this));
        var frequency_suggestions = this.state.suggestions.frequency.map(function(suggestion, i) {
            return (
                <tr key={i}><td data-key={i} data-arr="frequency" onClick={this.suggestionClicked}>
                    {suggestion.food_desc}
                </td></tr>
            );
        }.bind(this));

        return (
            <div className="row">
                <div className="col-md-6">
                    <h4>From Today's Meal Plan</h4>
                    <table className="table table-bordered"><tbody>{plan_suggestions}</tbody></table>
                </div>
                <div className="col-md-6">
                    <h4>Frequently Entered</h4>
                    <table className="table table-bordered"><tbody>{frequency_suggestions}</tbody></table>
                </div>
            </div>
        );
    }
});

var FoodEntryForm = React.createClass({
    displayName: 'EntryForm',

    getInitialState: function () {
        return { count: 1, food: null, measures: [], measure_id: null };
    },
    handleFoodChange: function (food_obj) {
        this.fetchMeasures(food_obj.id);
        this.setState({food: food_obj});

        if (this.props.setValid) {
            this.props.setValid(this.state.food != null);
        }
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
    handleExternalSelection: function(selection) {
        this.fetchMeasures(selection['food_id'], selection['measure_id']);
        this.setState({food: {description: selection['food_desc'],
            id: selection['food_id']},
            count: selection['count']});
        this.props.setValid(true);
    },
    handleSubmit: function () {
        if (parseFloat(this.state.count) == NaN) {
            alert("count must be a number");
            return;
        } else {
            this.setState({count: parseFloat(this.state.count)})
        }

        this.props.onSubmit(this.state, function() {
            this.setState(this.getInitialState());
            this.refs.food_lookup_field.reset();
        }.bind(this), function(xhr, status, err) {
            // error
        }.bind(this));
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
                        className="form-control"
                    onChange={this.handleMeasureChange}>
                    {options}
                </select>
        } else {
            select = <div style={{width:"100%"}}></div>
        }
        return (
                <div>
                        <div className="col-md-7">
                            <FoodLookupField ref="food_lookup_field"
                                             onSelect={this.handleFoodChange}
                                             food={this.state.food} />
                        </div>
                        <div className="col-md-1">
                            <input
                                className="form-control"
                                type="text"
                                size="3"
                                value={this.state.count}
                                onChange={this.handleCountChange}
                            />
                        </div>
                        <div className="col-md-3">
                            {select}
                        </div>
                </div>
        );
    }
});

exports.FoodEntryForm = FoodEntryForm;

var FoodEntryView = React.createClass({
    getInitialState: function() {
        return {valid: false};
    },
    handleFoodEntryFormSubmit: function(state, successCallback, errorCallback) {
        $.ajax({
            type: 'post',
            url: this.props.url,
            dataType: 'json',
            success: function(data) {
                this.props.week_view.loadFromServer();
                successCallback();
            }.bind(this),
            error: function(xhr, status, err) {
                errorCallback(xhr, status, err);
            }.bind(this),
            data: state
        });
    },
    handleSuggestionSelection(selection) {
        this.refs.FoodEntryForm.handleExternalSelection(selection);
    },
    handleFoodPlanSelection(selection) {
        this.refs.FoodEntryForm.handleExternalSelection(selection);
    },
    handleSubmit: function(e) {
        e.preventDefault();
        this.refs.FoodEntryForm.handleSubmit();
    },
    setValid: function(valid) {
        this.setState({valid: valid});
    },
    render: function() {
        return (
            <div>
                <div className="row">
                    <div className="col-md-12"><h2>What have you eaten?</h2></div>
                </div>
                <form className="entryForm" onSubmit={this.handleSubmit}>
                    <div className="row">
                        <FoodEntryForm ref="FoodEntryForm" onSubmit={this.handleFoodEntryFormSubmit}
                                       setValid={this.setValid} />
                        <div className="col-md-1">
                            <input
                                className="form-control btn btn-primary"
                                style={{width: "100%"}}
                                type="submit"
                                value="Post"
                                disabled={!this.state.valid}
                            />
                        </div>
                    </div>
                    <EntrySuggestions ref="EntrySuggestions"
                                      onSelection={this.handleSuggestionSelection} />
                </form>
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
               <DayMacrosChart ref="DayMacrosChart" />
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
            .attr("z", 190090)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Percent of Goal");

        chart.append("g").attr("class", "x axis").call(xAxis)
            .attr("transform", "translate(0, " + height + ")");

        var bar = chart.selectAll().data(data).enter().append("g").attr("class", "bar")
            .attr("transform", function(d, i) {return "translate(" + i * barWidth + ", 0)"; });

        bar.append("rect")
            .attr("y", function(d) {
                return Math.max(0, y(d.value));
            })
            .attr("height", function(d) {
                return Math.min(height - y(d.value), height);
            })
            .attr("width", barWidth - 1)
            .attr("fill", function (d) {
                // l scales from 31 to 100
                var l = 50 + (1 - Math.min(1, d.value)) * 50;
                return "hsl(234, 70%, " + l + "%)";

            });

        bar.append("text")
            .attr("width", barWidth)
            .attr("x", barWidth / 2)
            .attr("y", function(d) {
                return Math.min(Math.max(0, y(d.value)), height - 16);
            })
            .attr("dy", "1em")
            .text(function(d) { return d.current.toFixed(1) + "/" + d.total + " " + d.unit; });
        bar.append("text")
            .attr("x", barWidth / 2)
            .attr("y", height)
            .attr("dy", "1em")
            .text(function(d) { return d.label; });
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

var DayMacrosChart = React.createClass({
    displayName: 'DayMacrosChart',
    drawChart: function() {
        var key_height = 50;
        var chart_height = 100;
        var width = 960, height = chart_height + key_height;
        d3.select("#DayMacrosChart").selectAll("*").remove();

        var graph = d3.select("#DayMacrosChart")
            .attr("width", width)
            .attr("height", height);

        var key = graph.append("g")
            .attr("height", key_height).attr("width", width);
        var chart = graph.append("g")
            .attr("height", chart_height).attr("width", width)
            .attr("transform", "translate(0, " + key_height + ")");

        var key_node_height = 10, key_node_padding = 5, text_height = 16;
        key.append("rect")
            .attr("height", 10).attr("width", 10)
            .attr("x", 0)
            .attr("y", key_node_padding + (text_height - key_node_height) / 2)
            .attr("class", "carbohydrate key");
        key.append("text")
            .attr("x", key_node_height + key_node_height)
            .attr("y", key_node_padding)
            .attr("dy", "1em")
            .text("carbohydrate");
        key.append("rect")
            .attr("height", 10).attr("width", 10)
            .attr("x", 0)
            .attr("y", key_node_height + key_node_padding * 2 + (text_height - key_node_height) / 2)
            .attr("class", "protein key");
        key.append("text")
            .attr("x", key_node_height + key_node_height)
            .attr("y", key_node_padding * 2 + key_node_height)
            .attr("dy", "1em")
            .text("protein");
        key.append("rect")
            .attr("height", 10).attr("width", 10)
            .attr("x", 0)
            .attr("y", key_node_height * 2 + key_node_padding * 3 + (text_height - key_node_height) / 2)
            .attr("class", "fat key");
        key.append("text")
            .attr("x", key_node_height + key_node_height)
            .attr("y", key_node_padding * 3 + key_node_height * 2)
            .attr("dy", "1em")
            .text("fat");

        var total_cals = this.state.data["total"]["calories"];
        var carbohydrate_width = width * this.state.data["carbohydrate"]["calories"] / total_cals;
        var protein_width = width * this.state.data["protein"]["calories"] / total_cals;
        var fat_width = width * this.state.data["fat"]["calories"] / total_cals;

        chart.append("rect")
            .attr("height", chart_height).attr("width", carbohydrate_width)
            .attr("x", 0)
            .attr("class", "carbohydrate");
        chart.append("rect")
            .attr("height", chart_height).attr("width", protein_width)
            .attr("x", carbohydrate_width)
            .attr("class", "protein");
        chart.append("rect")
            .attr("height", chart_height).attr("width", fat_width)
            .attr("x", carbohydrate_width + protein_width)
            .attr("class", "fat");
    },
    loadFromServer: function() {
        var url = '/api/graphs/day_macros';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function(response) {
                this.setState({data: response.data});
                this.drawChart({data: response.data});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function() {
        return <svg id="DayMacrosChart" height="100" width="400"></svg>
    }
});


// home page

if (document.getElementById('week-view')) {
    var home_week_view = ReactDOM.render(
        <WeekView url="/api/week"/>,
        document.getElementById('week-view')
    );
    ReactDOM.render(
        <FoodEntryView url="/api/entry" week_view={home_week_view}/>,
        document.getElementById('entry-form')
    );
}

// end hjome page
